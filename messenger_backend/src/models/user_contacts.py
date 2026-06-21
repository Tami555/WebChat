import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.mixins import UUIDPrimaryKey


if TYPE_CHECKING:
    from .users import Users


class UserContacts(UUIDPrimaryKey, Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    contact_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    custom_name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "contact_user_id", name="unique_user_contact"),
    )
    # Отношения
    user: Mapped["Users"] = relationship(back_populates="contacts")
    contact: Mapped["Users"] = relationship()