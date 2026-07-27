import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, func, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.schemas.enums import GroupMemberRole
from src.models.base import Base

if TYPE_CHECKING:
    from .users import Users
    from .groups import Groups


class GroupMembers(Base):
    """БД модель Группа-Участник"""

    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[GroupMemberRole] = mapped_column(
        SQLEnum(GroupMemberRole, name="roles_member_groups"),
        default=GroupMemberRole.MEMBER,
    )
    joined_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="unique_group_user"),
    )
    # Отношения
    group: Mapped["Groups"] = relationship(
        foreign_keys=[group_id], back_populates="group_members"
    )
    member: Mapped["Users"] = relationship(
        foreign_keys=[user_id], back_populates="member_groups"
    )
