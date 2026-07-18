import json
from uuid import UUID

from app.infrastructure.redis_client import get_redis


class RedisMemory:
    """Redis-backed session memory and conversation history manager with window compaction."""

    @classmethod
    async def append_message(cls, session_id: UUID, role: str, content: str) -> None:
        """Append a message exchange to the session history in Redis with 24h expiration."""
        redis = await get_redis()
        key = f"memory:session:{session_id}"
        entry = json.dumps({"role": role, "content": content})
        await redis.rpush(key, entry)
        await redis.expire(key, 86400)  # 24 hours TTL

    @classmethod
    async def get_conversation_window(cls, session_id: UUID, max_messages: int = 10) -> list[dict[str, str]]:
        """Retrieve the most recent conversation messages cleanly."""
        redis = await get_redis()
        key = f"memory:session:{session_id}"
        raw_list = await redis.lrange(key, -max_messages, -1)
        return [json.loads(item) for item in raw_list]

    @classmethod
    async def clear_session_memory(cls, session_id: UUID) -> None:
        """Clear cached conversation memory upon session completion or explicit reset."""
        redis = await get_redis()
        await redis.delete(f"memory:session:{session_id}")
