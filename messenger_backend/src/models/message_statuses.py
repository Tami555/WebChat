import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


if TYPE_CHECKING:
    from .users import Users
    from .messages import Messages


class MessageStatuses(Base):
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"), primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    is_read: Mapped[bool] = mapped_column(default=False, index=True)
    read_at: Mapped[datetime.datetime] = mapped_column(nullable=True)

    __table_args__ = (
        UniqueConstraint("message_id", "user_id", name="unique_message_status"),
    )
    # Отношения
    recipient: Mapped["Users"] = relationship(back_populates="message_statuses") # Получатель
    message: Mapped["Messages"] = relationship()
