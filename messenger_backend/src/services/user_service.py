from uuid import UUID
from typing import Iterable
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import UserCRUD
from src.exceptions import UserNotFoundError
from src.models import Users


class UserService:
    """Сервис для управления пользователями"""

    @staticmethod
    async def get_user_by_id(user_id: UUID, session: AsyncSession) -> Users:
        """Получение пользователя по id"""
        user = await UserCRUD.get_user_by_id(user_id, session)
        if user is None:
            raise UserNotFoundError()
        return user

    @staticmethod
    async def get_users_by_ids(
        users_ids: list[UUID], session: AsyncSession
    ) -> list[Users]:
        """Получение списка пользователей по id"""
        users = await UserCRUD.get_users_by_ids(users_ids, session)
        found_ids = {u.id for u in users}
        for user_id in users_ids:
            if user_id not in found_ids:
                raise UserNotFoundError(user_id=user_id)
        return users

    @staticmethod
    async def get_user_ids_by_usernames(
        usernames: Iterable[str], session: AsyncSession
    ) -> list[UUID]:
        """Получение ID пользователей по их username"""
        if not usernames:
            return []
        return await UserCRUD.get_user_ids_by_usernames(usernames, session)

    @staticmethod
    async def check_users_exist(members: list[UUID], session: AsyncSession):
        """Проверка, что все пользователи существуют"""
        if not await UserCRUD.check_users_exist(session, members):
            raise UserNotFoundError()
