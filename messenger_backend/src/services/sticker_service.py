from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import StickerCRUD
from src.exceptions import StickerNotFoundError
from src.models import Stickers


class StickerService:
    """Сервис для управления стикерами"""

    @staticmethod
    async def get_sticker_by_id(sticker_id: UUID, session: AsyncSession) -> Stickers:
        """Получение стикера по id"""
        sticker = await StickerCRUD.get_sticker_by_id(sticker_id, session)
        if sticker is None:
            raise StickerNotFoundError()
        return sticker
