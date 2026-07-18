import json
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import UUID, uuid4

from app.core.logging import get_logger
from app.domain.repositories.base import IGenericRepository

logger = get_logger(__name__)


class AuditLogService:
    """Service responsible for asynchronous immutable tracking of sensitive user and admin mutations."""

    def __init__(self, audit_repo: IGenericRepository[Any] | None = None):
        self.audit_repo = audit_repo

    async def log_event(
        self,
        user_id: UUID | None,
        action: str,
        entity_name: str,
        entity_id: str | UUID,
        changes: Dict[str, Any] | None = None,
        ip_address: str | None = None,
        trace_id: str | None = None,
    ) -> None:
        """Record an immutable audit entry cleanly without blocking core domain flows."""
        log_entry = {
            "id": str(uuid4()),
            "user_id": str(user_id) if user_id else "SYSTEM_ANONYMOUS",
            "action": action,
            "entity_name": entity_name,
            "entity_id": str(entity_id),
            "changes": changes or {},
            "ip_address": ip_address or "UNKNOWN",
            "trace_id": trace_id or "NONE",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Log structured entry immediately to stdout (captured by Loki / cloud monitoring)
        logger.info(
            f"AUDIT_EVENT: {action} on {entity_name}:{entity_id} by user={log_entry['user_id']}",
            extra={"audit_payload": json.dumps(log_entry)},
        )

        # If database repository provided, persist entity
        if self.audit_repo:
            try:
                # Assuming audit model structure compatible or generic persistence
                await self.audit_repo.create(log_entry)
            except Exception as exc:
                logger.error(f"Failed to persist audit log to DB: {exc}")
