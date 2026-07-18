from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base, UUIDType


class ParkingLotORM(Base):
    """SQLAlchemy ORM mapping for ParkingLot."""
    __tablename__ = "parking_lots"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    venue_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("venues.id", ondelete="CASCADE"), index=True, nullable=False)
    lot_name: Mapped[str] = mapped_column(String(100), nullable=False)
    total_spots: Mapped[int] = mapped_column(Integer, default=500, nullable=False)
    available_spots: Mapped[int] = mapped_column(Integer, default=500, nullable=False)
    accessible_spots_total: Mapped[int] = mapped_column(Integer, default=25, nullable=False)
    accessible_spots_available: Mapped[int] = mapped_column(Integer, default=25, nullable=False)
    has_ev_charging: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )


class ParkingReservationORM(Base):
    """SQLAlchemy ORM mapping for ParkingReservation."""
    __tablename__ = "parking_reservations"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    lot_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("parking_lots.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    vehicle_license: Mapped[str] = mapped_column(String(20), nullable=False)
    check_in_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    check_out_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
