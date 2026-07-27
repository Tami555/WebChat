from uuid import UUID
from pydantic import BaseModel


class ShortStickerResponse(BaseModel):
    """Схема стикера (не полная)"""

    emoji: str

    class Config:
        from_attributes = True


class StickerResponse(ShortStickerResponse):
    """Схема стикера"""

    id: UUID
    file_url: str

    class Config:
        from_attributes = True
