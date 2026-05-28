from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

try:
    from ..database import Review, User, get_db
    from ..dependencies import get_current_user, require_admin, serialize_review
    from ..schemas import ReviewCreate, ReviewRespond, ReviewResponse, ReviewUpdate
    from ..services.ticket_index import refresh_index
except ImportError:
    from database import Review, User, get_db
    from dependencies import get_current_user, require_admin, serialize_review
    from schemas import ReviewCreate, ReviewRespond, ReviewResponse, ReviewUpdate
    from services.ticket_index import refresh_index

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
    refresh_index()
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


@router.put("/reviews/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    request: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = db.query(Review).filter(Review.id == review_id, Review.user_id == current_user.id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    if request.rating is not None:
        review.rating = request.rating
    if request.category is not None:
        review.category = request.category.strip()
    if request.comment is not None:
        review.comment = request.comment.strip()
        
    db.commit()
    db.refresh(review)
    refresh_index()
    return serialize_review(review)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = db.query(Review).filter(Review.id == review_id, Review.user_id == current_user.id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    db.delete(review)
    db.commit()
    refresh_index()
    return None


@router.get("/admin/reviews", response_model=list[ReviewResponse])
def admin_reviews(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    reviews = db.query(Review).join(User).order_by(Review.created_at.desc()).all()
    return [serialize_review(review, include_user=True) for review in reviews]


@router.delete("/admin/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_review(
    review_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    db.delete(review)
    db.commit()
    refresh_index()
    return None


@router.put("/admin/reviews/{review_id}/respond", response_model=ReviewResponse)
def admin_respond_review(
    review_id: int,
    request: ReviewRespond,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    review.admin_response = request.admin_response.strip() if request.admin_response.strip() else None
    if review.admin_response:
        review.status = "responded"
        
    db.commit()
    db.refresh(review)
    refresh_index()
    return serialize_review(review, include_user=True)


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
