from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

try:
    from ..auth import create_access_token, hash_password, verify_password
    from ..database import User, get_db
    from ..dependencies import get_current_user, serialize_user
    from ..schemas import AuthResponse, LoginRequest, SignupRequest, UserResponse
except ImportError:
    from auth import create_access_token, hash_password, verify_password
    from database import User, get_db
    from dependencies import get_current_user, serialize_user
    from schemas import AuthResponse, LoginRequest, SignupRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == request.email.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        name=request.name,
        email=request.email.lower(),
        password_hash=hash_password(request.password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthResponse(
        access_token=create_access_token(user.email, user.role),
        user=serialize_user(user),
    )


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email.lower()).first()
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return AuthResponse(
        access_token=create_access_token(user.email, user.role),
        user=serialize_user(user),
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return serialize_user(current_user)
