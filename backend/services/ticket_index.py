from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
import re
from typing import Any

import numpy as np
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from langchain.tools import Tool
except Exception:
    Tool = None

try:
    from ..schemas import ChatResponse
    from ..ticket_data import generate_support_tickets
except ImportError:
    from schemas import ChatResponse
    from ticket_data import generate_support_tickets


class TicketIndex:
    def __init__(self) -> None:
        self.tickets = generate_support_tickets()
        self.vectorizer = HashingVectorizer(
            n_features=768,
            alternate_sign=False,
            norm="l2",
            stop_words="english",
        )
        self.embeddings = self.vectorizer.transform(
            [ticket["text"] for ticket in self.tickets]
        ).toarray()
        self.collection = self._build_vector_store()
        self.plot_points = self._project_to_2d()
        self.tools = self._build_tools()

    def _build_vector_store(self) -> Any | None:
        try:
            import chromadb
            from chromadb.config import Settings
        except Exception:
            return None

        db_path = Path(__file__).resolve().parent.parent / "data" / "chroma"
        db_path.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(
            path=str(db_path),
            settings=Settings(anonymized_telemetry=False),
        )
        collection = client.get_or_create_collection(name="support_tickets")

        if collection.count() < len(self.tickets):
            existing = set(collection.get()["ids"])
            new_tickets = [
                (index, ticket)
                for index, ticket in enumerate(self.tickets)
                if ticket["id"] not in existing
            ]
            if new_tickets:
                collection.add(
                    ids=[ticket["id"] for _, ticket in new_tickets],
                    documents=[ticket["text"] for _, ticket in new_tickets],
                    metadatas=[
                        {
                            "category": ticket["category"],
                            "title": ticket["title"],
                            "severity": ticket["severity"],
                            "channel": ticket["channel"],
                        }
                        for _, ticket in new_tickets
                    ],
                    embeddings=[
                        self.embeddings[index].tolist() for index, _ in new_tickets
                    ],
                )

        return collection

    def _project_to_2d(self) -> list[dict[str, Any]]:
        pca = PCA(n_components=2, random_state=7)
        coords = self._normalize(pca.fit_transform(self.embeddings))

        return [
            {
                "id": ticket["id"],
                "x": float(coord[0]),
                "y": float(coord[1]),
                "label": ticket["category"],
                "title": ticket["title"],
                "text": ticket["text"],
                "severity": ticket["severity"],
                "channel": ticket["channel"],
            }
            for ticket, coord in zip(self.tickets, coords)
        ]

    @staticmethod
    def _normalize(coords: np.ndarray) -> np.ndarray:
        mins = coords.min(axis=0)
        maxes = coords.max(axis=0)
        span = np.where(maxes - mins == 0, 1, maxes - mins)
        return ((coords - mins) / span) * 20 - 10

    def semantic_search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        query_embedding = self.vectorizer.transform([query]).toarray()
        if self.collection is not None:
            results = self.collection.query(
                query_embeddings=[query_embedding[0].tolist()],
                n_results=limit,
                include=["documents", "metadatas", "distances"],
            )
            tickets_by_id = {ticket["id"]: ticket for ticket in self.tickets}
            return [
                {
                    **tickets_by_id[ticket_id],
                    "score": round(1 / (1 + float(distance)), 3),
                }
                for ticket_id, distance in zip(results["ids"][0], results["distances"][0])
            ]

        scores = cosine_similarity(query_embedding, self.embeddings)[0]
        ranked_indexes = np.argsort(scores)[::-1][:limit]
        return [
            {
                **self.tickets[int(index)],
                "score": round(float(scores[int(index)]), 3),
            }
            for index in ranked_indexes
        ]

    def count_mentions(self, query: str) -> dict[str, Any]:
        keyword = self._extract_count_keyword(query)
        pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
        matches = [ticket for ticket in self.tickets if pattern.search(ticket["text"])]
        by_category = Counter(ticket["category"] for ticket in matches)
        return {"keyword": keyword, "count": len(matches), "by_category": dict(by_category)}

    @staticmethod
    def _extract_count_keyword(query: str) -> str:
        quoted = re.search(r"['\"]([^'\"]+)['\"]", query)
        if quoted:
            return quoted.group(1).strip()

        lowered = query.lower()
        for marker in ("mention", "mentions", "about", "for", "with"):
            if marker in lowered:
                words = re.findall(r"[a-z0-9]+", lowered.split(marker, 1)[1])
                if words:
                    return words[0]

        ignored = {"how", "many", "count", "tickets", "ticket", "are", "there"}
        words = [word for word in re.findall(r"[a-z0-9]+", lowered) if word not in ignored]
        return words[-1] if words else lowered.strip()

    def route(self, message: str) -> ChatResponse:
        count_intent = re.search(
            r"\b(how many|count|number of|mentions?|occurrences?)\b",
            message,
            re.IGNORECASE,
        )
        if count_intent:
            result = self.count_mentions(message)
            category_details = ", ".join(
                f"{category}: {count}"
                for category, count in sorted(result["by_category"].items())
            )
            details = f" Breakdown: {category_details}." if category_details else ""
            return ChatResponse(
                reply=(
                    f"I found {result['count']} tickets mentioning "
                    f"'{result['keyword']}'.{details}"
                ),
                tool_used="Ticket Counter Tool",
            )

        results = self.semantic_search(message)
        categories = Counter(ticket["category"] for ticket in results)
        top_lines = [
            f"{ticket['id']} ({ticket['category']}, score {ticket['score']}): {ticket['text']}"
            for ticket in results[:3]
        ]
        return ChatResponse(
            reply=(
                "The most relevant historical tickets are:\n"
                + "\n".join(top_lines)
                + f"\n\nCluster signal: {dict(categories)}"
            ),
            tool_used="Semantic Search Tool",
        )

    def _build_tools(self) -> list[Any]:
        if Tool is None:
            return []
        return [
            Tool(
                name="semantic_search",
                func=lambda query: self.semantic_search(query),
                description="Finds support tickets that are semantically similar to a query.",
            ),
            Tool(
                name="ticket_counter",
                func=lambda query: self.count_mentions(query),
                description="Counts tickets mentioning a keyword or phrase.",
            ),
        ]


@lru_cache(maxsize=1)
def get_index() -> TicketIndex:
    return TicketIndex()
