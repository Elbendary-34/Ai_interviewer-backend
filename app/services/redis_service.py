# Async Redis Service
import redis.asyncio as aioredis
import json
from app.core.config import settings

class RedisService:
    def __init__(self):
        self.redis = None

    async def connect(self):
        if not self.redis:
            self.redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def increment_counter(self, key: str, ttl: int = 60) -> int:
        await self.connect()
        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, ttl)
            results = await pipe.execute()
        return results[0]

    async def reset_counter(self, key: str):
        await self.connect()
        await self.redis.delete(key)

    async def store_session_state(self, session_id: str, data: dict, ttl: int = 3600):
        await self.connect()
        await self.redis.set(f"session:{session_id}:state", json.dumps(data), ex=ttl)

redis_service = RedisService()