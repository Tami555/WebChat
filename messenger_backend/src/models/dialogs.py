import datetime
from uuid import UUID
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.mixins import UUIDPrimaryKey


if TYPE_CHECKING:
    from .users import Users
    from .messages import Messages


class Dialogs(UUIDPrimaryKey, Base):
    user1_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user2_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now,
        server_default=func.now()
    )
    last_message_id: Mapped[UUID] = mapped_column(ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    __table_args__ = (
        UniqueConstraint('user1_id', 'user2_id', name='unique_dialog_pair'),
        UniqueConstraint('user2_id', 'user1_id', name='unique_dialog_pair_reverse'),
    )
    # Отношения
    user1: Mapped["Users"] = relationship(foreign_keys=[user1_id], back_populates="dialogs_as_user1")
    user2: Mapped["Users"] = relationship(foreign_keys=[user2_id], back_populates="dialogs_as_user2")
    last_message: Mapped["Messages"] = relationship(foreign_keys=[last_message_id])
    messages: Mapped[list["Messages"]] = relationship(foreign_keys="Messages.dialog_id", back_populates="dialog")