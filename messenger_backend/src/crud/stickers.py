from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.schemas import CreateStickerPackRequest, CreateStickerRequest
from src.models import Stickers, StickerPacks


class StickerCRUD:
    """SQL-запросы (CRUD) для Стикеров"""

    @staticmethod
    async def get_sticker_by_id(
        sticker_id: UUID, session: AsyncSession
    ) -> Stickers | None:
        """Получение стикера по id"""
        stmt = select(Stickers).where(Stickers.id == sticker_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_sticker(
        sticker_data: CreateStickerRequest,
        session: AsyncSession,
    ) -> Stickers:
        """Создание стикера"""
        sticker = Stickers(**sticker_data.model_dump())
        session.add(sticker)
        await session.commit()
        return sticker

    @staticmethod
    async def create_sticker_pack(
        sticker_pack_data: CreateStickerPackRequest,
        session: AsyncSession,
    ) -> StickerPacks:
        """Создание СтикерПака"""
        sticker_pack = StickerPacks(**sticker_pack_data.model_dump())
        session.add(sticker_pack)
        await session.commit()
        return sticker_pack
