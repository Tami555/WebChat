from uuid import UUID
from pydantic import BaseModel


class ShortStickerResponse(BaseModel):
    emoji: str

    class Config:
        from_attributes = True


class StickerResponse(ShortStickerResponse):
    id: UUID
    file_url: str

    class Config:
        from_attributes = True
