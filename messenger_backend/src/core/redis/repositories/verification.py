import json
from typing import Optional
from src.core.redis.repositories.base import BaseRedisRepository
from src.core.config import get_settings


class VerificationRedisRepository(BaseRedisRepository):
    """Redis: Репозиторий для верификации"""

    settings = get_settings()

    NAMESPACE = settings.redis.namespaces.phone_verification
    CODE_TTL = settings.verification.code_ttl

    async def save(self, phone: str, code: str, data: dict) -> None:
        """Сохранить верификационный код"""
        key = self._key(self.NAMESPACE, phone)
        await self.client.hset(
            key,
            mapping={
                "code": code,
                "data": json.dumps(data),
                "attempts": 0,
            },
        )
        await self.client.expire(key, self.CODE_TTL)

    async def get(self, phone: str) -> Optional[dict]:
        """Получить данные верификации"""
        key = self._key(self.NAMESPACE, phone)
        data = await self.client.hgetall(key)
        if not data:
            return None
        return data

    async def delete(self, phone: str) -> None:
        """Удалить верификацию"""
        key = self._key(self.NAMESPACE, phone)
        await self.client.delete(key)

    async def increment_attempts(self, phone: str) -> int:
        """Увеличить счетчик попыток"""
        key = self._key(self.NAMESPACE, phone)
        return await self.client.hincrby(key, "attempts", 1)


verification_redis = VerificationRedisRepository()
