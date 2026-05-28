from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

try:
    from ..database import User
    from ..dependencies import get_current_user, require_admin
    from ..schemas import ChatRequest, ChatResponse
    from ..services.ticket_index import get_index
except ImportError:
    from database import User
    from dependencies import get_current_user, require_admin
    from schemas import ChatRequest, ChatResponse
    from services.ticket_index import get_index

router = APIRouter(tags=["admin-ai"])


@router.get("/plot-data")
def get_plot_data(_: User = Depends(require_admin)) -> dict[str, Any]:
    index = get_index()
    return {
        "data": index.plot_points,
        "meta": {
            "tickets": len(index.tickets),
            "embedding_dimensions": 768,
            "projection": "PCA",
        },
    }


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, _: User = Depends(require_admin)):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    return get_index().route(request.message)


@router.post("/customer/chat", response_model=ChatResponse)
def customer_chat(request: ChatRequest, _: User = Depends(get_current_user)):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    return get_index().customer_route(request.message)
