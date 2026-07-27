from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.mixins import UUIDPrimaryKey

if TYPE_CHECKING:
    from .stickers import Stickers


class StickerPacks(UUIDPrimaryKey, Base):
    """БД модель СтикерПака"""

    name: Mapped[str] = mapped_column(String(100))
    is_premium: Mapped[bool] = mapped_column(default=False)
    # Отношения
    stickers: Mapped[list["Stickers"]] = relationship(
        foreign_keys="Stickers.pack_id", back_populates="pack"
    )
