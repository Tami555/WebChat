import redis.asyncio as aioredis

from src.core.config import get_settings


class RedisManager:
    def __init__(self):
        self._client = None

    async def connect(self):
        settings = get_settings()

        self._client = await aioredis.from_url(
            settings.redis.url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=10,
            socket_keepalive=True,
            retry_on_timeout=True,
            max_connections=50,
            health_check_interval=25,
        )

    async def disconnect(self):
        if self._client:
            await self._client.aclose()

    def __getattr__(self, name):
        if self._client is None:
            raise RuntimeError("Redis not connected")
        return getattr(self._client, name)


redis_manager = RedisManager()
