"""Pytest fixtures for database, test client, authenticated headers, and mock services."""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["USE_MOCK_EMBEDDINGS"] = "true"
os.environ["USE_MOCK_LLM"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.db.base import Base
from app.db.session import get_db
from app.core.security import get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.models.document import Document, ProcessingStatus
from app.models.chunk import DocumentChunk
from app.models.conversation import Conversation, Message
from app.main import app

# In-memory SQLite engine for tests
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables in memory once for the test session."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Yield an isolated transactional database session for each test function."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def student_user(db_session) -> User:
    user = User(
        email="test_student@campus.edu",
        username="test_student",
        full_name="Test Student",
        hashed_password=get_password_hash("Password123!"),
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def faculty_user(db_session) -> User:
    user = User(
        email="test_faculty@campus.edu",
        username="test_faculty",
        full_name="Dr. Test Faculty",
        hashed_password=get_password_hash("Password123!"),
        role=UserRole.FACULTY,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session) -> User:
    user = User(
        email="test_admin@campus.edu",
        username="test_admin",
        full_name="Test Administrator",
        hashed_password=get_password_hash("AdminPassword123!"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_token(student_user) -> str:
    return create_access_token(subject=str(student_user.id), role=student_user.role.value)


@pytest.fixture
def faculty_token(faculty_user) -> str:
    return create_access_token(subject=str(faculty_user.id), role=faculty_user.role.value)


@pytest.fixture
def admin_token(admin_user) -> str:
    return create_access_token(subject=str(admin_user.id), role=admin_user.role.value)


@pytest.fixture
def student_headers(student_token) -> dict:
    return {"Authorization": f"Bearer {student_token}"}


@pytest.fixture
def faculty_headers(faculty_token) -> dict:
    return {"Authorization": f"Bearer {faculty_token}"}


@pytest.fixture
def admin_headers(admin_token) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}
