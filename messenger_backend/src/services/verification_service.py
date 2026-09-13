import json

from src.core.redis import verification_redis
from src.core.config import get_settings
from src.utils.verifications import VerificationCodeGenerator
from src.exceptions import (
    VerificationCodeExpiredError,
    InvalidVerificationCodeError,
    TooManyAttemptsError,
)
from src.utils.notifications import get_sms_manager


class VerificationService:
    """Сервис для работы с верификацией телефона"""

    settings = get_settings()

    MAX_ATTEMPTS = settings.verification.max_attempts

    @staticmethod
    async def create_verification(phone: str, data: dict) -> str:
        """Создание верификационного кода"""
        # Генерируем код
        code = VerificationCodeGenerator.generate_from_phone(phone)
        # Отправляем SMS
        sms_manager = get_sms_manager()
        await sms_manager.send_code(phone, code)
        # Сохраняем в Redis
        await verification_redis.save(phone, code, data)
        return code

    @staticmethod
    async def verify_code(phone: str, code: str) -> dict:
        """Проверка кода верификации"""

        # Получаем данные из Redis
        redis_data = await verification_redis.get(phone)
        if redis_data is None:
            raise VerificationCodeExpiredError()

        # Проверяем количество попыток
        attempts = int(redis_data.get("attempts", 0))
        if attempts >= VerificationService.MAX_ATTEMPTS:
            await verification_redis.delete(phone)
            raise TooManyAttemptsError()

        # Проверяем код
        stored_code = redis_data.get("code")
        if stored_code != code:
            new_attempts = await verification_redis.increment_attempts(phone)
            raise InvalidVerificationCodeError(
                attempts=VerificationService.MAX_ATTEMPTS - new_attempts
            )

        # Код верный
        user_data = json.loads(redis_data.get("data", {}))
        await verification_redis.delete(phone)
        return user_data
