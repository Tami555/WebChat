import datetime
from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .mixins import UUIDPrimaryKey
from .base import Base


class Users(UUIDPrimaryKey, Base):
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    birthday: Mapped[datetime.datetime] = mapped_column(nullable=True)
    avatar_url: Mapped[str] = mapped_column(nullable=True)
    last_seen: Mapped[datetime.datetime]
    is_online: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now,
        server_default=func.now()
    )