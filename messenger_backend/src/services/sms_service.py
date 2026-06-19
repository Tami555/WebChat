# TODO: Реальная отправка кода через SMS-провайдера
from abc import ABC, abstractmethod


class SMSService(ABC):
    """Абстрактный сервис для отправки SMS"""
    
    @abstractmethod
    async def send_code(self, phone: str, code: str) -> bool:
        """Отправка кода на телефон"""
        pass
    
    @abstractmethod
    async def send_message(self, phone: str, message: str) -> bool:
        """Отправка произвольного сообщения"""
        pass


class MockSMSService(SMSService):
    """Мок-сервис для разработки"""
    
    async def send_code(self, phone: str, code: str) -> bool:
        """Имитация отправки кода"""
        print(f"[MOCK SMS] 📱 To: {phone}, Code: {code}")
        return True
    
    async def send_message(self, phone: str, message: str) -> bool:
        """Имитация отправки сообщения"""
        print(f"[MOCK SMS] 📱 To: {phone}, Message: {message}")
        return True