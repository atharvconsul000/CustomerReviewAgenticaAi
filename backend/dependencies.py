from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

try:
    from .auth import decode_access_token
    from .database import User, get_db
    from .schemas import ReviewResponse, UserResponse
except ImportError:
    from auth import decode_access_token
    from database import User, get_db
    from schemas import ReviewResponse, UserResponse


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_access_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def serialize_user(user: User) -> UserResponse:
    return UserResponse(id=user.id, name=user.name, email=user.email, role=user.role)


def serialize_review(review, include_user: bool = False) -> ReviewResponse:
    return ReviewResponse(
        id=review.id,
        rating=review.rating,
        category=review.category,
        comment=review.comment,
        admin_response=review.admin_response,
        status=review.status,
        user_id=review.user_id,
        created_at=review.created_at.isoformat(),
        user_name=review.user.name if include_user and review.user else None,
        user_email=review.user.email if include_user and review.user else None,
    )
