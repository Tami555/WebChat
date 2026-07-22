from src.core.redis.manager import redis_manager


class BaseRedisRepository:
    """Redis: Базовый класс (общие методы)"""

    def __init__(self):
        self.client = redis_manager  # Прокси через __getattr__

    def _key(self, namespace: str, *parts: str) -> str:
        """Формирование ключа с namespace"""
        return ":".join([namespace, *parts])
