from sqlalchemy import select, func
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models import Users


async def get_user_by_id(id: UUID, session: AsyncSession) -> Users | None:
    """ Получение пользователя по id """
    stmt = select(Users).where(Users.id == id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username(username: str, session: AsyncSession) -> Users | None:
    """ Получение пользователя по username """
    stmt = select(Users).where(Users.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username_with_relationships(username: str, session: AsyncSession) -> Users | None:
    """ Получение пользователя по username с подгрузкой связей """
    stmt = select(Users)\
        .where(Users.username == username)\
        .options(
            selectinload(Users.dialogs_as_user1),
            selectinload(Users.dialogs_as_user2),
            selectinload(Users.member_groups),
            selectinload(Users.contacts),
        )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_phone(phone: str, session: AsyncSession) -> Users | None:
    """ Получение пользователя по телефону """
    stmt = select(Users).where(Users.phone == phone)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(user_data: dict, session: AsyncSession) -> Users:
    """ Создание пользователя """
    new_user = Users(**user_data)
    session.add(new_user)
    await session.commit()
    return new_user


async def check_users_exist(session: AsyncSession, user_ids: list[UUID]) -> bool:
    """Проверить, что все пользователи существуют"""
    stmt = select(func.count()).where(Users.id.in_(user_ids))
    count = await session.scalar(stmt)
    return count == len(user_ids)