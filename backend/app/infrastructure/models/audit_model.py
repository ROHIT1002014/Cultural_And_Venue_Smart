from datetime import datetime, timezone
from typing import Any, Dict
from uuid import UUID, uuid4
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.models.base import Base, JSONType, UUIDType


class AuditLogORM(Base):
    """SQLAlchemy ORM mapping for AuditLog persistence."""
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    entity_name: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    changes: Mapped[Dict[str, Any]] = mapped_column(JSONType, default=dict)
    ip_address: Mapped[str] = mapped_column(String(64), default="UNKNOWN")
    trace_id: Mapped[str] = mapped_column(String(100), default="NONE")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
