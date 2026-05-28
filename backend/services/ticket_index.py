from __future__ import annotations

from collections import Counter
from functools import lru_cache
import os
from pathlib import Path
import re
from types import SimpleNamespace
from typing import Any
from urllib import request as url_request
from urllib.error import URLError
import json

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
    from ..database import SessionLocal, Review
except ImportError:
    from schemas import ChatResponse
    from database import SessionLocal, Review


class LocalOllamaLLM:
    def __init__(self) -> None:
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")

    def invoke(self, messages: list[Any]) -> SimpleNamespace:
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {
                    "role": self._role_for_message(message),
                    "content": str(message.content),
                }
                for message in messages
            ],
        }
        body = json.dumps(payload).encode("utf-8")
        req = url_request.Request(
            f"{self.base_url}/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with url_request.urlopen(req, timeout=45) as response:
                data = json.loads(response.read().decode("utf-8"))
        except URLError as exc:
            raise RuntimeError("Ollama is not running or the model is unavailable") from exc

        return SimpleNamespace(content=data.get("message", {}).get("content", ""))

    @staticmethod
    def _role_for_message(message: Any) -> str:
        name = message.__class__.__name__.lower()
        if "system" in name:
            return "system"
        if "ai" in name:
            return "assistant"
        return "user"


class TicketIndex:
    def __init__(self) -> None:
        with SessionLocal() as db:
            reviews = db.query(Review).all()
        
        self.tickets = []
        for r in reviews:
            self.tickets.append({
                "id": f"REV-{r.id:04d}",
                "category": r.category,
                "title": f"Review {r.id}",
                "text": r.comment,
                "severity": f"{r.rating} star(s)",
                "channel": "web",
                "admin_response": r.admin_response,
            })
            
        if not self.tickets:
            self.tickets = [{
                "id": "REV-0000",
                "category": "None",
                "title": "No Reviews",
                "text": "There are no reviews in the database yet.",
                "severity": "0 star(s)",
                "channel": "web",
            }]
            

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
        self.llm = self._build_llm()
        self.tools = self._build_tools()

    def _build_llm(self) -> Any | None:
        provider = os.getenv("LLM_PROVIDER", "auto").lower()

        if provider in {"gemini", "google"} or (provider == "auto" and os.getenv("GOOGLE_API_KEY")):
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI

                return ChatGoogleGenerativeAI(
                    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                    temperature=0.2,
                )
            except Exception:
                if provider in {"gemini", "google"}:
                    raise

        if provider in {"openai"} or (provider == "auto" and os.getenv("OPENAI_API_KEY")):
            try:
                from langchain_openai import ChatOpenAI

                return ChatOpenAI(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    temperature=0.2,
                )
            except Exception:
                if provider == "openai":
                    raise

        if provider in {"auto", "ollama", "local", "free"}:
            return LocalOllamaLLM()

        return None

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
                            "admin_response": ticket.get("admin_response") or "",
                        }
                        for _, ticket in new_tickets
                    ],
                    embeddings=[
                        self.embeddings[index].tolist() for index, _ in new_tickets
                    ],
                )

        return collection

    def _project_to_2d(self) -> list[dict[str, Any]]:
        if len(self.tickets) < 2:
            return [
                {
                    "id": ticket["id"],
                    "x": 0.0,
                    "y": 0.0,
                    "label": ticket["category"],
                    "title": ticket["title"],
                    "text": ticket["text"],
                    "severity": ticket["severity"],
                    "channel": ticket["channel"],
                }
                for ticket in self.tickets
            ]
            
        pca = PCA(n_components=2, random_state=7)
        coords = pca.fit_transform(self.embeddings)
        
        # Add random jitter to scatter overlapping data points
        np.random.seed(42)
        jitter = np.random.normal(loc=0.0, scale=0.05, size=coords.shape)
        coords = self._normalize(coords + jitter)

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
                "admin_response": ticket.get("admin_response"),
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

        results = self.semantic_search(message, limit=8)
        if self.llm is not None:
            try:
                return ChatResponse(
                    reply=self._answer_with_llm(message, results),
                    tool_used="RAG Insight Tool (LLM + ChromaDB)",
                )
            except Exception as e:
                fallback = self._fallback_semantic_answer(results)
                fallback.reply = (
                    f"LLM request failed, so I used vector search fallback.\n\n"
                    + fallback.reply
                )
                return fallback

        return self._fallback_semantic_answer(results)

    def _answer_with_llm(self, question: str, tickets: list[dict[str, Any]]) -> str:
        from langchain_core.messages import HumanMessage, SystemMessage

        category_counts = Counter(ticket["category"] for ticket in self.tickets)
        severity_counts = Counter(ticket["severity"] for ticket in self.tickets)
        context = "\n".join(
            (
                f"{ticket['id']} | {ticket['category']} | {ticket['severity']} | "
                f"score={ticket.get('score', 0)} | Problem: {ticket['text']} | "
                f"Help Offered: {ticket.get('admin_response') or 'None'}"
            )
            for ticket in tickets
        )
        corpus_summary = (
            f"Category counts: {dict(category_counts)}\n"
            f"Severity counts: {dict(severity_counts)}"
        )

        messages = [
            SystemMessage(
                content=(
                    "You are an admin analytics assistant for a customer support team. "
                    "Use only the retrieved review context and corpus summary. "
                    "Give practical insights, patterns, likely root causes, and next actions. "
                    "Focus on the actual classifications, sentiments, and content rather than just citing IDs. "
                    "If the context is not enough, say what extra data is needed."
                )
            ),
            HumanMessage(
                content=(
                    f"Admin question:\n{question}\n\n"
                    f"Corpus summary:\n{corpus_summary}\n\n"
                    f"Retrieved vector context from ChromaDB:\n{context}"
                )
            ),
        ]

        response = self.llm.invoke(messages)
        return str(response.content)

    def _fallback_semantic_answer(self, results: list[dict[str, Any]]) -> ChatResponse:
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

    def customer_route(self, message: str) -> ChatResponse:
        results = self.semantic_search(message, limit=5)
        if self.llm is not None:
            try:
                return ChatResponse(
                    reply=self._answer_with_llm_customer(message, results),
                    tool_used="Customer Support AI",
                )
            except Exception as e:
                return ChatResponse(
                    reply="I'm having trouble connecting to my AI brain right now, but a human agent will review your issue soon!",
                    tool_used="Fallback Message",
                )
        return ChatResponse(
            reply="AI is currently unavailable.",
            tool_used="Fallback Message",
        )

    def _answer_with_llm_customer(self, question: str, tickets: list[dict[str, Any]]) -> str:
        from langchain_core.messages import HumanMessage, SystemMessage

        context = "\n".join(
            (
                f"Past Problem: {ticket['text']}\n"
                f"Help that was offered: {ticket.get('admin_response') or 'No response yet'}"
            )
            for ticket in tickets
        )

        messages = [
            SystemMessage(
                content=(
                    "You are a helpful customer support chatbot. "
                    "A customer has a complaint or issue. "
                    "Use the retrieved 'Past Problem' and 'Help that was offered' context to give them a short, helpful answer. "
                    "Do not mention ticket IDs or internal metrics. Just provide the help they need based on what we offered before."
                )
            ),
            HumanMessage(
                content=(
                    f"Customer issue:\n{question}\n\n"
                    f"Retrieved context from similar past problems:\n{context}"
                )
            ),
        ]

        response = self.llm.invoke(messages)
        return str(response.content)

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

def refresh_index() -> None:
    get_index.cache_clear()
