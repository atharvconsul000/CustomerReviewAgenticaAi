from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    tool_used: str


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    category: str = Field(min_length=2, max_length=80)
    comment: str = Field(min_length=5, max_length=1200)


class ReviewResponse(BaseModel):
    id: int
    rating: int
    category: str
    comment: str
    status: str
    user_id: int
    created_at: str
    user_name: str | None = None
    user_email: str | None = None
