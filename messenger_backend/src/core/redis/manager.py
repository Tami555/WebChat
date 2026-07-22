import redis.asyncio as aioredis

from src.core.config import settings


class RedisManager:
    def __init__(self):
        self._client = None

    async def connect(self):
        self._client = await aioredis.from_url(settings.redis.url, decode_responses=True)

    async def disconnect(self):
        if self._client:
            await self._client.close()

    def __getattr__(self, name):
        if self._client is None:
            raise RuntimeError("Redis not connected")
        return getattr(self._client, name)


redis_manager = RedisManager()
