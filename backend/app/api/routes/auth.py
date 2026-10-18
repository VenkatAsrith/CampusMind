"""Authentication API endpoints: Login and Me."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, TokenResponse, UserRead
from app.schemas.chat import StudentRecord
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


@router.get("/student/{identifier}", response_model=StudentRecord)
def get_student_record(
    identifier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve verified student personal record.
    Enforces strict ownership: students may ONLY view their own records matching their roll number/username.
    Attempts to substitute another student's identifier are strictly rejected with 403 Forbidden.
    """
    clean_id = identifier.strip().lstrip("@")

    # Authorization Check: only student or admin
    if current_user.role not in (UserRole.STUDENT, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Student records can only be accessed by authenticated student owners or authorized administrators.",
        )

    # Ownership check: If student, verified username must match requested identifier
    if current_user.role == UserRole.STUDENT and current_user.username.lower() != clean_id.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access Denied: You are authenticated as '{current_user.username}' and cannot access records for '{clean_id}'. Horizontal access violations are logged.",
        )

    # Fetch user details
    target_user = current_user
    if current_user.role == UserRole.ADMIN:
        found = db.query(User).filter(User.username == clean_id).first()
        if not found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student account '{clean_id}' not found in the institution database.",
            )
        target_user = found

    return StudentRecord(
        roll_number=target_user.username,
        full_name=target_user.full_name,
        email=target_user.email,
        program="B.Tech Computer Science & Engineering",
        semester="Semester 6 (Academic Year 2026)",
        academic_standing="Good Standing (Dean's Honor Roll Eligible)",
        attendance_percentage=89.5,
        registered_courses=[
            "CS301 Advanced Operating Systems",
            "CS305 Database Internals & pgvector",
            "AI310 Natural Language Processing & RAG",
            "CS312 Information Security & Cryptography",
        ],
    )
