from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Users


async def get_user_by_username(username: str, session: AsyncSession) -> Users | None:
    """ Получение пользователя по username """
    stmt = select(Users).where(Users.username == username)
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