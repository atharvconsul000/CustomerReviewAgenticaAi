from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

try:
    from ..database import Review, User, get_db
    from ..dependencies import get_current_user, require_admin, serialize_review
    from ..schemas import ReviewCreate, ReviewResponse
except ImportError:
    from database import Review, User, get_db
    from dependencies import get_current_user, require_admin, serialize_review
    from schemas import ReviewCreate, ReviewResponse

router = APIRouter(tags=["reviews"])


@router.post("/reviews", response_model=ReviewResponse)
def create_review(
    request: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = Review(
        user_id=current_user.id,
        rating=request.rating,
        category=request.category.strip(),
        comment=request.comment.strip(),
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return serialize_review(review)


@router.get("/reviews", response_model=list[ReviewResponse])
def my_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reviews = (
        db.query(Review)
        .filter(Review.user_id == current_user.id)
        .order_by(Review.created_at.desc())
        .all()
    )
    return [serialize_review(review) for review in reviews]


@router.get("/admin/reviews", response_model=list[ReviewResponse])
def admin_reviews(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    reviews = db.query(Review).join(User).order_by(Review.created_at.desc()).all()
    return [serialize_review(review, include_user=True) for review in reviews]


@router.get("/admin/reviews/analysis")
def admin_review_analysis(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    total = db.query(func.count(Review.id)).scalar() or 0
    average = db.query(func.avg(Review.rating)).scalar()
    categories = (
        db.query(Review.category, func.count(Review.id), func.avg(Review.rating))
        .group_by(Review.category)
        .order_by(func.count(Review.id).desc())
        .all()
    )
    status_counts = (
        db.query(Review.status, func.count(Review.id))
        .group_by(Review.status)
        .order_by(func.count(Review.id).desc())
        .all()
    )

    return {
        "total_reviews": total,
        "average_rating": round(float(average), 2) if average is not None else 0,
        "categories": [
            {"category": category, "count": count, "average_rating": round(float(avg), 2)}
            for category, count, avg in categories
        ],
        "statuses": [
            {"status": status_name, "count": count}
            for status_name, count in status_counts
        ],
    }
