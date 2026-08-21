from typing import Optional, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.users import Users

T = TypeVar("T")


class DatabaseAssertions:
    """Базовые проверки БД"""

    @staticmethod
    async def assert_exists(
        session: AsyncSession, model_class: T, **filters
    ) -> Optional[T]:
        """Проверяет, что запись существует в БД"""
        from sqlalchemy import select

        stmt = select(model_class).filter_by(**filters)
        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()

        assert obj is not None
        return obj

    @staticmethod
    async def assert_not_exists(
        session: AsyncSession, model_class: T, **filters
    ) -> None:
        """Проверяет, что запись НЕ существует в БД"""
        from sqlalchemy import select

        stmt = select(model_class).filter_by(**filters)
        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()

        assert obj is None


class UserDatabaseAssertions:
    """Проверки для пользователей в БД"""

    @staticmethod
    async def assert_user_exists(
        session: AsyncSession, phone: str, expected_username: Optional[str] = None
    ) -> Users | None:
        """Проверяет, что пользователь существует и возвращает его"""
        user = await DatabaseAssertions.assert_exists(session, Users, phone=phone)
        if expected_username:
            assert user.username == expected_username
        assert user.phone == phone
        return user

    @staticmethod
    async def assert_user_not_exists(session: AsyncSession, phone: str) -> None:
        """Проверяет, что пользователь НЕ существует"""
        await DatabaseAssertions.assert_not_exists(session, Users, phone=phone)
