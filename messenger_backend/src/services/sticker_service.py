from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

import src.crud.stickers as crud
from src.exceptions import StickerNotFoundError
from src.models import Stickers


class StickerService:
    """Сервис для управления стикерами"""

    @staticmethod
    async def get_sticker_by_id(sticker_id: UUID, session: AsyncSession) -> Stickers:
        """Получение стикера по id"""
        sticker = await crud.get_sticker_by_id(sticker_id, session)
        if sticker is None:
            raise StickerNotFoundError()
        return sticker