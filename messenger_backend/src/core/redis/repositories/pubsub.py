import json
from src.core.redis.repositories.base import BaseRedisRepository
from src.core.config import get_settings


class PubSubRedisRepository(BaseRedisRepository):
    """Redis: Репозиторий для Pub/Sub"""

    settings = get_settings()

    PUBSUB_NAMESPACE = settings.redis.namespaces.pubsub_server

    async def publish_to_server(self, server_id: str, data: dict) -> None:
        """Опубликовать сообщение для конкретного сервера"""
        channel = self._key(self.PUBSUB_NAMESPACE, server_id)
        await self.client.publish(channel, json.dumps(data))

    def get_pubsub(self):
        """Получить pubsub объект для подписки"""
        return self.client.pubsub()

    def get_channel(self, server_id: str) -> str:
        """Получить имя канала для сервера"""
        return self._key(self.PUBSUB_NAMESPACE, server_id)


pubsub_redis = PubSubRedisRepository()
