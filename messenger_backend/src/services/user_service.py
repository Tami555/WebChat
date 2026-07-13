from uuid import UUID
from typing import Iterable
from sqlalchemy.ext.asyncio import AsyncSession

import src.crud.users as crud
from src.exceptions import UserNotFoundError
from src.models import Users


class UserService:
    """Сервис для управления пользователями"""

    @staticmethod
    async def get_user_by_id(user_id: UUID, session: AsyncSession) -> Users:
        """Получение пользователя по id"""
        user = await crud.get_user_by_id(user_id, session)
        if user is None:
            raise UserNotFoundError()
        return user

    @staticmethod
    async def get_user_ids_by_usernames(
        usernames: Iterable[str],
        session: AsyncSession
    ) -> list[UUID]:
        """Получение ID пользователей по их именам"""
        if not usernames:
            return []
        return await crud.get_user_ids_by_usernames(usernames, session)