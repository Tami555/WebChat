from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models import Stickers


async def get_sticker_by_id(sticker_id: UUID, session: AsyncSession) -> Stickers | None:
    """ Получение стикера по id """
    stmt = select(Stickers).where(Stickers.id == sticker_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()