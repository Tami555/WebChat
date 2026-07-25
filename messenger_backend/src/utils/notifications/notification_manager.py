from abc import ABC, abstractmethod
from src.core.config import settings
from src.schemas.messages import MessageResponse


class NotificationManager(ABC):
    """Абстрактный менеджер для push-уведомлений"""

    @staticmethod
    @abstractmethod
    async def send_new_message_notification(username: str, message: MessageResponse) -> bool:
        """Уведомление о новом сообщении"""
        pass

    @staticmethod
    @abstractmethod
    async def send_bulk_notification(usernames: list[str], message: MessageResponse) -> dict[str, bool]:
        """Массовая отправка уведомлений"""
        pass


class MockNotificationManager(NotificationManager):
    """Мок-менеджер для разработки"""

    @staticmethod
    async def send_new_message_notification(username: str, message: MessageResponse) -> bool:
        print(f"[MOCK PUSH] 🦎 To: {username}, Message from: {message.sender.username}")
        return True

    @staticmethod
    async def send_bulk_notification(usernames: list[str], message: MessageResponse) -> dict[str, bool]:
        results = {}
        for username in usernames:
            results[username] = await MockNotificationManager.send_new_message_notification(
                username, message
            )
        return results


class FirebaseNotificationManager(NotificationManager):
    """Реальный менеджер через Firebase"""

    @staticmethod
    async def send_new_message_notification(username: str,message: MessageResponse) -> bool:
        # TODO: Реальная отправка через Firebase
        print(f"[FIREBASE] 🔥 To: {username}, Message from: {message.sender.username}")
        return True

    @staticmethod
    async def send_bulk_notification(usernames: list[str], message: MessageResponse) -> dict[str, bool]:
        results = {}
        for username in usernames:
            results[username] = await FirebaseNotificationManager.send_new_message_notification(
                username, message
            )
        return results


def get_notification_manager() -> type[NotificationManager]:
    """Фабрика для получения менеджера уведомлений"""
    if settings.app.environment == "production":
        return FirebaseNotificationManager
    return MockNotificationManager
