from src.core.redis import verification_redis


class VerificationRedisAssertions:
    """Проверки для Redis-верификации"""

    @staticmethod
    async def assert_has_code(phone: str, expected_code: str) -> dict:
        """Проверяет, что в Redis сохранен код верификации"""
        data = await verification_redis.get(phone)
        assert data is not None
        assert "code" in data
        assert data["code"] == expected_code
        return data

    @staticmethod
    async def assert_no_data(phone: str) -> None:
        """Проверяет, что данные отсутствуют в Redis"""
        data = await verification_redis.get(phone)
        assert data is None

    @staticmethod
    async def assert_attempts_count(phone: str, expected_attempts: int) -> dict:
        """Проверяет количество попыток в Redis"""
        data = await verification_redis.get(phone)
        assert data is not None
        assert "attempts" in data
        assert int(data["attempts"]) == expected_attempts
        return data
