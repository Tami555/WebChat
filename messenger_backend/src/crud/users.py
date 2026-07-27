from typing import Iterable
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models import Users


class UserCRUD:
    """SQL-запросы (CRUD) для Пользователей"""

    @staticmethod
    async def get_user_by_id(user_id: UUID, session: AsyncSession) -> Users | None:
        """Получение пользователя по id"""
        stmt = select(Users).where(Users.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_ids_by_usernames(
        usernames: Iterable[str], session: AsyncSession
    ) -> list[UUID]:
        """Получение id пользователей по их именам"""
        stmt = select(Users.id).where(Users.username.in_(usernames))
        result = await session.execute(stmt)
        return [row[0] for row in result.all()]

    @staticmethod
    async def get_user_by_username(
        username: str, session: AsyncSession
    ) -> Users | None:
        """Получение пользователя по username"""
        stmt = select(Users).where(Users.username == username)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username_with_relationships(
        username: str, session: AsyncSession
    ) -> Users | None:
        """Получение пользователя по username со связями"""
        stmt = (
            select(Users)
            .where(Users.username == username)
            .options(
                selectinload(Users.dialogs_as_user1),
                selectinload(Users.dialogs_as_user2),
                selectinload(Users.member_groups),
                selectinload(Users.contacts),
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_phone(phone: str, session: AsyncSession) -> Users | None:
        """Получение пользователя по телефону"""
        stmt = select(Users).where(Users.phone == phone)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(user_data: dict, session: AsyncSession) -> Users:
        """Создание пользователя"""
        new_user = Users(**user_data)
        session.add(new_user)
        await session.commit()
        return new_user

    @staticmethod
    async def check_users_exist(session: AsyncSession, user_ids: list[UUID]) -> bool:
        """Проверить, что все пользователи существуют"""
        stmt = select(func.count()).where(Users.id.in_(user_ids))
        count = await session.scalar(stmt)
        return count == len(user_ids)
