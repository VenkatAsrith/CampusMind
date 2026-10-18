"""FastAPI dependencies for Authentication, RBAC, and Database sessions."""

from typing import List, Optional
import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.core.exceptions import AuthenticationError, AuthorizationError, InactiveUserError
from app.db.session import get_db
from app.models.user import User, UserRole

# HTTP Bearer scheme
security_scheme = HTTPBearer(auto_error=True)

# Role hierarchy levels for permission evaluation
ROLE_HIERARCHY = {
    UserRole.STUDENT: 1,
    UserRole.FACULTY: 2,
    UserRole.ADMIN: 3,
}


def get_authorized_roles(user_role: UserRole) -> List[UserRole]:
    """Return list of document audience roles that the user is authorized to retrieve.

    - STUDENT: [STUDENT]
    - FACULTY: [STUDENT, FACULTY]
    - ADMIN:   [STUDENT, FACULTY, ADMIN]
    """
    user_level = ROLE_HIERARCHY.get(user_role, 1)
    return [role for role, level in ROLE_HIERARCHY.items() if level <= user_level]


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate JWT token, check expiration, and retrieve active user from database.

    Never trusts client-supplied user headers or body fields.
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.PyJWTError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(exc)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id_str)
        user = db.query(User).filter(User.id == user_id).first()
    except ValueError:
        # If subject was username
        user = db.query(User).filter(User.username == user_id_str).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


def require_role(min_role: UserRole):
    """Factory creating a FastAPI dependency that verifies the user has at least the required role."""
    required_level = ROLE_HIERARCHY[min_role]

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_level = ROLE_HIERARCHY.get(current_user.role, 0)
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires minimum role of '{min_role.value}'. Current role: '{current_user.role.value}'",
            )
        return current_user

    return role_checker


# Commonly used role dependencies
require_student = require_role(UserRole.STUDENT)
require_faculty = require_role(UserRole.FACULTY)
require_admin = require_role(UserRole.ADMIN)
