from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

try:
    from .auth import hash_password
    from .database import User, get_db, init_db
    from .routes.ai_routes import router as ai_router
    from .routes.auth_routes import router as auth_router
    from .routes.review_routes import router as review_router
    from .services.ticket_index import get_index
except ImportError:
    from auth import hash_password
    from database import User, get_db, init_db
    from routes.ai_routes import router as ai_router
    from routes.auth_routes import router as auth_router
    from routes.review_routes import router as review_router
    from services.ticket_index import get_index


app = FastAPI(
    title="Customer Support Analyzer API",
    description="Full-stack support reviews, JWT auth, admin AI, and vector visualization",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(review_router)
app.include_router(ai_router)


def seed_demo_users(db: Session) -> None:
    if db.query(User).filter(User.email == "admin@example.com").first():
        return
    db.add_all(
        [
            User(
                name="Admin User",
                email="admin@example.com",
                password_hash=hash_password("admin123"),
                role="admin",
            ),
            User(
                name="Demo Customer",
                email="user@example.com",
                password_hash=hash_password("user123"),
                role="user",
            ),
        ]
    )
    db.commit()


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    db = next(get_db())
    try:
        seed_demo_users(db)
        # Seed reviews automatically if there are none
        from .database import Review
        if db.query(Review).count() == 0:
            try:
                from .seed_reviews import seed as seed_reviews
            except ImportError:
                from seed_reviews import seed as seed_reviews
            seed_reviews()
    finally:
        db.close()


@app.get("/health")
def health_check():
    index = get_index()
    return {"status": "ok", "tickets": len(index.tickets), "embedding_dimensions": 768}
