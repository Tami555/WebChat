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


class CreateStickerRequest(BaseModel):
    """Схема создания стикера"""

    name: str
    file_url: str
    emoji: str
    pack_id: UUID


class CreateStickerPackRequest(BaseModel):
    """Схема создания СтикерПака"""

    name: str
    is_premium: bool = False
