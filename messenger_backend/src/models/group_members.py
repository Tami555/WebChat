import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, func, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.schemas.enums import RolesMemberGroups
from src.models.base import Base


if TYPE_CHECKING:
    from .users import Users
    from .groups import Groups


class GroupMembers(Base):
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[RolesMemberGroups] = mapped_column(
        SQLEnum(RolesMemberGroups, name="roles_member_groups"),
        default=RolesMemberGroups.MEMBER
    )
    joined_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now, server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="unique_group_user"),
    )
    # Отношения
    group: Mapped["Groups"] = relationship(back_populates="group_members")
    member: Mapped["Users"] = relationship(back_populates="member_groups")
