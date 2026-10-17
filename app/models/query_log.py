"""Query log model for operational auditing and performance metrics."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(36), index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_role: Mapped[str] = mapped_column(String(50), nullable=False)
    question_length: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    retrieval_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    retrieval_latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    generation_latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    outcome: Mapped[str] = mapped_column(String(50), nullable=False)  # answered, insufficient_evidence, error
    error_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<QueryLog(req_id='{self.request_id}', role='{self.user_role}', outcome='{self.outcome}', latency={self.total_latency_ms}ms)>"
