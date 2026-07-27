import datetime
from uuid import UUID
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.mixins import UUIDPrimaryKey
from src.models.base import Base

if TYPE_CHECKING:
    from .users import Users
    from .group_members import GroupMembers
    from .messages import Messages


class Groups(UUIDPrimaryKey, Base):
    """БД модель Группы"""

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str] = mapped_column(nullable=True)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, server_default=func.now()
    )
    is_private: Mapped[bool] = mapped_column(default=True)
    last_message_id: Mapped[UUID] = mapped_column(
        ForeignKey("messages.id", ondelete="SET NULL"), nullable=True
    )
    # Отношения
    creater_user: Mapped["Users"] = relationship(
        foreign_keys=[created_by], back_populates="create_groups"
    )  # Создатель группы
    group_members: Mapped[list["GroupMembers"]] = relationship(
        foreign_keys="GroupMembers.group_id", back_populates="group"
    )  # Участники группы
    last_message: Mapped["Messages"] = relationship(foreign_keys=[last_message_id])
    messages: Mapped[list["Messages"]] = relationship(
        foreign_keys="Messages.group_id",
        back_populates="group",
        order_by="Messages.created_at",
    )
