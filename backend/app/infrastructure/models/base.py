from sqlalchemy import JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy 2.0 ORM tables."""
    pass


# Cross-database variant types so production uses high-performance Postgres JSONB/UUID while SQLite tests render cleanly
JSONType = JSON().with_variant(JSONB, "postgresql")
UUIDType = Uuid().with_variant(PG_UUID(as_uuid=True), "postgresql")
