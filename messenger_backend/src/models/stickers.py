from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.mixins import UUIDPrimaryKey

if TYPE_CHECKING:
    from .sticker_packs import StickerPacks
    from .messages import Messages


class Stickers(UUIDPrimaryKey, Base):
    """БД модель Стикера"""

    name: Mapped[str] = mapped_column(String(100))
    file_url: Mapped[str]
    emoji: Mapped[str] = mapped_column(String(5), default="⭐")
    pack_id: Mapped[int] = mapped_column(
        ForeignKey("sticker_packs.id", ondelete="CASCADE")
    )
    # Отношения
    pack: Mapped["StickerPacks"] = relationship(
        foreign_keys=[pack_id], back_populates="stickers"
    )
    messages: Mapped[list["Messages"]] = relationship(
        foreign_keys="Messages.sticker_id", back_populates="sticker"
    )
