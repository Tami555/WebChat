from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ShortStickerResponse(BaseModel):
    """Схема стикера (не полная)"""

    emoji: str

    model_config = ConfigDict(from_attributes=True)


class StickerResponse(ShortStickerResponse):
    """Схема стикера"""

    id: UUID
    file_url: str

    model_config = ConfigDict(from_attributes=True)
