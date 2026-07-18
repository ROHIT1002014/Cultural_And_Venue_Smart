from datetime import datetime, timezone
from typing import Any, Dict
from uuid import UUID, uuid4
from sqlalchemy import Boolean, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.models.base import Base, JSONType, UUIDType


class VenueORM(Base):
    """SQLAlchemy ORM mapping for Venue."""
    __tablename__ = "venues"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    address: Mapped[str] = mapped_column(String(300), nullable=False)
    boundary_coordinates: Mapped[Dict[str, Any]] = mapped_column(JSONType, default=dict)
    total_capacity: Mapped[int] = mapped_column(Integer, default=5000, nullable=False)
    current_occupancy: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )


class PointOfInterestORM(Base):
    """SQLAlchemy ORM mapping for PointOfInterest."""
    __tablename__ = "points_of_interest"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    venue_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("venues.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    coordinates: Mapped[Dict[str, Any]] = mapped_column(JSONType, default=dict)
    floor_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_accessible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
