"""Authentication API endpoints: Login and Me."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserRead
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user with username/email and password, returning signed JWT."""
    user = (
        db.query(User)
        .filter((User.username == request.username) | (User.email == request.username))
        .first()
    )

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    token = create_access_token(subject=str(user.id), role=user.role.value)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserRead.model_validate(user),
    )


@router.get("/me", response_model=UserRead)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Return the profile and verified role of the currently authenticated user."""
    return UserRead.model_validate(current_user)
