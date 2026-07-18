from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class LostItem:
    """Domain entity tracking Lost and Found items within a cultural venue."""
    id: UUID
    venue_id: UUID
    title: str
    description: str
    status: str  # "lost", "found", "claimed"
    created_at: datetime
    updated_at: datetime
