"""Database initialization and seeding with default roles and campus documents."""

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.security import get_password_hash
from app.core.logging import logger
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.user import User, UserRole
from app.models.document import Document
from app.ingestion.service import ingest_document

# Sample campus documentation for realistic seeding and testing
SAMPLE_STUDENT_POLICY = """# Campus Academic Calendar and Policies 2026
The fall semester starts on August 24, 2026.
The last day for students to add or drop courses without penalty is September 8, 2026.
Tuition payment deadline for enrolled students is September 15, 2026.
Final examinations will take place from December 14 to December 18, 2026.
Students with a GPA of 3.5 or above are eligible for Dean's Honor Roll recognition.
For counseling and mental health services, students can visit the Health Center in Building B, Room 204.
"""

SAMPLE_FACULTY_HANDBOOK = """# Faculty Evaluation and Research Sabbatical Guidelines
Tenure-track faculty members undergo formal review at the end of their third and fifth probationary years.
Applications for sabbatical leave during the 2027 academic year must be submitted to the Dean by October 15, 2026.
Departmental grading curves must adhere to Academic Senate Resolution 42-B.
Faculty travel reimbursement requests require submission of original receipts within 30 days of conference completion.
Grade submissions for graduating seniors are strictly due within 48 hours of the scheduled final exam.
"""

SAMPLE_ADMIN_PROTOCOL = """# Administrative Governance and Facility Protocols
Campus emergency response protocols are activated by the Vice Chancellor of Operations.
Administrative salary bands for confidential executive personnel follow Pay Scale Band IX.
Keycard access revocation for terminated administrative staff must execute within 2 hours of departure notification.
Data center physical security audits are conducted quarterly by external compliance evaluators.
Budget reallocation requests exceeding $50,000 require dual authorization from the CFO and Chancellor.
"""


def init_database(db: Session) -> None:
    """Initialize schema and seed essential test users for all three roles."""
    # Ensure pgvector extension on PostgreSQL
    if db.bind and db.bind.dialect.name == "postgresql":
        try:
            db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            db.commit()
            logger.info("Verified PostgreSQL pgvector extension.")
        except Exception as exc:
            logger.warning("Could not execute CREATE EXTENSION vector: %s", exc)

    Base.metadata.create_all(bind=engine)

    # 1. Seed Student Users
    student_user = db.query(User).filter(User.username == "student1").first()
    if not student_user:
        student_user = User(
            email="student1@campus.edu",
            username="student1",
            full_name="Alex Student",
            hashed_password=get_password_hash("Password123!"),
            role=UserRole.STUDENT,
            is_active=True,
        )
        db.add(student_user)

    roll_student = db.query(User).filter(User.username == "23SS1A0535").first()
    if not roll_student:
        roll_student = User(
            email="23ss1a0535@campus.edu",
            username="23SS1A0535",
            full_name="Aarav Sharma (23SS1A0535)",
            hashed_password=get_password_hash("Password123!"),
            role=UserRole.STUDENT,
            is_active=True,
        )
        db.add(roll_student)

    # 2. Seed Faculty User
    faculty_user = db.query(User).filter(User.username == "faculty1").first()
    if not faculty_user:
        faculty_user = User(
            email="faculty1@campus.edu",
            username="faculty1",
            full_name="Dr. Taylor Faculty",
            hashed_password=get_password_hash("Password123!"),
            role=UserRole.FACULTY,
            is_active=True,
        )
        db.add(faculty_user)

    # 3. Seed Admin and Principal Users
    admin_user = db.query(User).filter(User.username == "admin1").first()
    if not admin_user:
        admin_user = User(
            email="admin1@campus.edu",
            username="admin1",
            full_name="Jordan Administrator",
            hashed_password=get_password_hash("AdminPassword123!"),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin_user)

    principal_user = db.query(User).filter(User.username == "principal").first()
    if not principal_user:
        principal_user = User(
            email="principal@campus.edu",
            username="principal",
            full_name="Dr. Evelyn Vance - Principal & Executive Dean",
            hashed_password=get_password_hash("Principal123!"),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(principal_user)

    db.commit()
    db.refresh(admin_user)
    logger.info("Default seed users verified (student1, 23SS1A0535, faculty1, admin1, principal).")

    # 4. Seed initial campus documents if none exist
    doc_count = db.query(Document).count()
    if doc_count == 0:
        logger.info("Seeding initial campus documents across all three audience roles...")
        # Student Document
        ingest_document(
            db=db,
            filename="academic_policies_2026.txt",
            content=SAMPLE_STUDENT_POLICY.encode("utf-8"),
            uploader_id=admin_user.id,
            audience_role=UserRole.STUDENT,
            custom_title="Campus Academic Calendar & Policies 2026",
        )
        # Faculty Document
        ingest_document(
            db=db,
            filename="faculty_handbook_2026.txt",
            content=SAMPLE_FACULTY_HANDBOOK.encode("utf-8"),
            uploader_id=admin_user.id,
            audience_role=UserRole.FACULTY,
            custom_title="Faculty Evaluation & Sabbatical Guidelines",
        )
        # Admin Document
        ingest_document(
            db=db,
            filename="admin_protocol_2026.txt",
            content=SAMPLE_ADMIN_PROTOCOL.encode("utf-8"),
            uploader_id=admin_user.id,
            audience_role=UserRole.ADMIN,
            custom_title="Administrative Governance & Facility Protocols",
        )
        logger.info("Initial documents seeded successfully across Student, Faculty, and Admin levels.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        init_database(db)
        print("Database initialization and seeding completed successfully.")
    finally:
        db.close()
