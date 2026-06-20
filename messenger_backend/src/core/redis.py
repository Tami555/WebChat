import redis.asyncio as aioredis
from typing import Optional

from src.core.config import settings


class RedisHelper:
    def __init__(self):
        self.client: Optional[aioredis.Redis] = None
        self.namespace = settings.redis.namespaces
    
    async def connect(self):
        """Подключение к Redis"""
        self.client = await aioredis.from_url(
            settings.redis.url,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        """Отключение от Redis"""
        if self.client:
            await self.client.close()
    
    def create_key(self, namespace: str, key: str) -> str:
        """Формирование ключа с namespace"""
        return f"{namespace}:{key}"
    

redis_helper = RedisHelper()