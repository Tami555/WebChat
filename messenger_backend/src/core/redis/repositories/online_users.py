from typing import Optional, Set
from src.core.redis.repositories.base import BaseRedisRepository
from src.core.config import settings


class OnlineUsersRedisRepository(BaseRedisRepository):
    """Redis: Репозиторий для онлайн-пользователей"""

    ONLINE_NAMESPACE = settings.redis.namespaces.users_online
    SERVER_NAMESPACE = settings.redis.namespaces.ws_server_user

    async def add_user(self, username: str, server_id: str) -> None:
        """Добавить пользователя в онлайн"""
        # Сохраняем на каком сервере
        server_key = self._key(self.SERVER_NAMESPACE, username)
        await self.client.set(server_key, server_id)
        # Добавляем в множество онлайн
        await self.client.sadd(self.ONLINE_NAMESPACE, username)

    async def remove_user(self, username: str) -> None:
        """Убрать пользователя из онлайн"""
        server_key = self._key(self.SERVER_NAMESPACE, username)
        await self.client.delete(server_key)
        await self.client.srem(self.ONLINE_NAMESPACE, username)

    async def get_all_online(self) -> Set[str]:
        """Получить всех онлайн пользователей"""
        return await self.client.smembers(self.ONLINE_NAMESPACE)

    async def get_user_server(self, username: str) -> Optional[str]:
        """На каком сервере находится пользователь"""
        key = self._key(self.SERVER_NAMESPACE, username)
        return await self.client.get(key)

    async def is_online(self, username: str) -> bool:
        """Проверить онлайн ли пользователь"""
        return await self.client.sismember(self.ONLINE_NAMESPACE, username)


online_redis = OnlineUsersRedisRepository()
