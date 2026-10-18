"""Authentication and user validation schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class LoginRequest(BaseModel):
    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Username or email",
        json_schema_extra={"example": "student1"},
    )
    password: str = Field(
        ...,
        min_length=1,
        description="Plaintext password",
        json_schema_extra={"example": "Password123!"},
    )


class UserCreate(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "user@campus.edu"})
    username: str = Field(..., min_length=3, max_length=50, json_schema_extra={"example": "student1"})
    full_name: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Alice Student"})
    password: str = Field(..., min_length=6, json_schema_extra={"example": "secret123"})
    role: UserRole = Field(default=UserRole.STUDENT, json_schema_extra={"example": "student"})


class UserRead(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
