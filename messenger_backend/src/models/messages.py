import datetime
from uuid import UUID
from typing import TYPE_CHECKING
from sqlalchemy import Text, ForeignKey, func, Enum as SQLEnum, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.mixins import UUIDPrimaryKey
from src.schemas.enums import MessageType


if TYPE_CHECKING:
    from .users import Users
    from .groups import Groups
    from .dialogs import Dialogs
    from .stickers import Stickers
    from .message_statuses import MessageStatuses


class Messages(UUIDPrimaryKey, Base):
    sender_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    dialog_id: Mapped[UUID] = mapped_column(ForeignKey("dialogs.id", ondelete="CASCADE"), index=True, nullable=True)
    group_id: Mapped[UUID] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), index=True, nullable=True)
    type: Mapped[MessageType] = mapped_column(
        SQLEnum(MessageType, name="message_types"),
        default=MessageType.TEXT
    )
    content: Mapped[str] = mapped_column(Text, nullable=True)
    file_url: Mapped[str] = mapped_column(nullable=True)
    sticker_id: Mapped[UUID] = mapped_column(ForeignKey("stickers.id", ondelete="CASCADE"), nullable=True)
    reply_to_id: Mapped[UUID] = mapped_column(ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now, server_default=func.now(), index=True)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    is_edited: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (
        CheckConstraint(
            "(dialog_id IS NOT NULL AND group_id IS NULL) OR (dialog_id IS NULL AND group_id IS NOT NULL)",
            name="message_target_check"
        ),
        CheckConstraint(
            "(type = 'SYSTEM' AND sender_id IS NULL) OR (type != 'SYSTEM' AND sender_id IS NOT NULL)",
            name="system_message_check"
        ),
        CheckConstraint(
            "type != 'STICKER' OR sticker_id IS NOT NULL",
            name="sticker_required"
        ),
        CheckConstraint(
            "type NOT IN ('IMAGE', 'VOICE', 'FILE') OR file_url IS NOT NULL",
            name="file_url_required"
        ),
    )
    # Отношения
    sender: Mapped["Users"] = relationship(foreign_keys=[sender_id], back_populates="messages")
    dialog: Mapped["Dialogs | None"] = relationship(foreign_keys=[dialog_id], back_populates="messages")
    group: Mapped["Groups | None"] = relationship(foreign_keys=[group_id], back_populates="messages")
    reply_message: Mapped["Messages | None"] = relationship(foreign_keys=[reply_to_id], remote_side="Messages.id")
    sticker: Mapped["Stickers | None"] = relationship(foreign_keys=[sticker_id], back_populates="messages")
    statuses: Mapped[list["MessageStatuses"]] = relationship(foreign_keys="MessageStatuses.message_id", back_populates="message")
