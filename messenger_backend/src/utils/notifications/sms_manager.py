from abc import ABC, abstractmethod
from src.core.config import get_settings


class SMSManager(ABC):
    """Абстрактный менеджер для отправки SMS"""

    @staticmethod
    @abstractmethod
    async def send_code(phone: str, code: str) -> bool:
        """Отправка кода верификации"""
        pass

    @staticmethod
    @abstractmethod
    async def send_message(phone: str, message: str) -> bool:
        """Отправка произвольного сообщения"""
        pass


class MockSMSManager(SMSManager):
    """Мок-менеджер для разработки"""

    @staticmethod
    async def send_code(phone: str, code: str) -> bool:
        print(f"[MOCK SMS] 📱 To: {phone}, Code: {code}")
        return True

    @staticmethod
    async def send_message(phone: str, message: str) -> bool:
        print(f"[MOCK SMS] 📱 To: {phone}, Message: {message}")
        return True


class TwilioSMSManager(SMSManager):
    """SMS-менеджер Twilio"""

    @staticmethod
    async def send_code(phone: str, code: str) -> bool:
        # TODO: Реальная отправка через Twilio
        print(f"[TWILIO] 📱 To: {phone}, Code: {code}")
        return True

    @staticmethod
    async def send_message(phone: str, message: str) -> bool:
        # Аналогично
        print(f"[TWILIO] 📱 To: {phone}, Message: {message}")
        return True


# Выбор менеджера через настройки
def get_sms_manager() -> type[SMSManager]:
    """Фабрика для получения SMS менеджера"""
    settings = get_settings()
    if settings.app.environment == "production":
        return TwilioSMSManager
    return MockSMSManager
