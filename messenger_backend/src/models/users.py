import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .mixins import UUIDPrimaryKey
from .base import Base


if TYPE_CHECKING:
    from .dialogs import Dialogs
    from .groups import Groups
    from .group_members import GroupMembers
    from .messages import Messages
    from .message_statuses import MessageStatuses
    from .user_contacts import UserContacts


class Users(UUIDPrimaryKey, Base):
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    birthday: Mapped[datetime.datetime] = mapped_column(nullable=True)
    avatar_url: Mapped[str] = mapped_column(nullable=True)
    last_seen: Mapped[datetime.datetime]
    is_online: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now, server_default=func.now())
    # Отношения
    dialogs_as_user1: Mapped[list["Dialogs"]] = relationship(back_populates="user1") # Чаты диалога
    dialogs_as_user2: Mapped[list["Dialogs"]] = relationship(back_populates="user2")
    create_groups: Mapped[list["Groups"]] = relationship(back_populates="creater_user") # Созданные группы
    member_groups: Mapped[list["GroupMembers"]] = relationship(back_populates="member") # Чаты групп
    messages: Mapped[list["Messages"]] = relationship(back_populates="sender") # Сообщения (отправитель)
    message_statuses: Mapped[list["MessageStatuses"]] = relationship(back_populates="recipient") # Статусы сообщений (получатель)
    contacts: Mapped[list["UserContacts"]] = relationship(back_populates="user") # записанные контакты