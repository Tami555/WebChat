import json

from src.core.redis import redis_helper
from src.core.config import settings
from src.utils.code_generator import VerificationCodeGenerator
from src.exceptions import (
    VerificationCodeExpiredError,
    InvalidVerificationCodeError,
    TooManyAttemptsError
)
from src.services.sms_service import SMSService, MockSMSService


class VerificationService:
    """Сервис для работы с верификацией телефона"""
    
    NAMESPACE = settings.redis.namespaces.phone_verification
    CODE_TTL = settings.verification.code_ttl
    MAX_ATTEMPTS = settings.verification.max_attempts
    SMS_SERVICE :SMSService = MockSMSService()

    # def __init__(self, sms_service: Optional[SMSService] = None):
    #     self.sms_service = sms_service or MockSMSService()
    
    @staticmethod
    async def create_verification(
        phone: str,
        data: dict,
    ) -> str:
        """Создание верификационного кода"""
        # Генерируем код
        code = VerificationCodeGenerator.generate_from_phone(phone)
        
        # Отправляем SMS
        await VerificationService.SMS_SERVICE.send_code(phone, code)

        # Сохраняем в Redis
        key = redis_helper.create_key(VerificationService.NAMESPACE, phone)
        data = {
            "code": code,
            "data": json.dumps(data),
            "attempts": 0
        }
        await redis_helper.client.hset(key, mapping=data)
        await redis_helper.client.expire(key, VerificationService.CODE_TTL)
        return code
    
    @staticmethod
    async def verify_code(
        phone: str,
        code: str
    ) -> dict:
        """ Проверка кода верификации """
        # Получаем данные из Redis
        key = redis_helper.create_key(VerificationService.NAMESPACE, phone)
        data = await redis_helper.client.hgetall(key)
        
        if not data:
            raise VerificationCodeExpiredError()
        
        # Проверяем количество попыток
        attempts = int(data.get("attempts", 0))
        if attempts >= VerificationService.MAX_ATTEMPTS:
            await redis_helper.client.delete(key)
            raise TooManyAttemptsError()
        
        # Проверяем код
        stored_code = data.get("code")
        if stored_code != code:
            attempts += 1
            data["attempts"] = attempts
            await redis_helper.client.hset(key, mapping=data)
            await redis_helper.client.expire(key, VerificationService.CODE_TTL)
            raise InvalidVerificationCodeError(attempts=VerificationService.MAX_ATTEMPTS - attempts)
        
        # Код верный
        user_data = json.loads(data.get("data", {}))
        await redis_helper.client.delete(key)
        return user_data
