from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models import Groups, GroupMembers, Messages
from src.schemas.enums import GroupMemberRole


class GroupCRUD:
    """SQL-запросы (CRUD) для Групп"""

    @staticmethod
    async def groups_by_user(user_id: UUID, session: AsyncSession) -> list[Groups]:
        """Получение всех групп, в которых состоит пользователь"""
        stmt = (
            select(Groups)
            .join(GroupMembers, GroupMembers.group_id == Groups.id)
            .options(
                selectinload(Groups.group_members),
                joinedload(Groups.last_message).joinedload(Messages.sender),
                joinedload(Groups.last_message).joinedload(Messages.sticker),
            )
            .where(GroupMembers.user_id == user_id)
        )
        groups = await session.scalars(stmt)
        return list(groups.all())

    @staticmethod
    async def create_group(
        creator_id: UUID,
        group_data: dict,
        members_list: list[UUID],
        session: AsyncSession,
    ) -> Groups:
        """Создание группы с участниками"""
        try:
            new_group = Groups(**group_data)
            session.add(new_group)
            for member_id in members_list:
                new_group.group_members.append(GroupMembers(user_id=member_id))
            new_group.group_members.append(
                GroupMembers(user_id=creator_id, role=GroupMemberRole.ADMIN)
            )
            await session.commit()
            return new_group

        except Exception as e:
            await session.rollback()
            raise e

    @staticmethod
    async def get_group_by_id(group_id: UUID, session: AsyncSession) -> Groups | None:
        """Получение группы по id"""
        stmt = select(Groups).where(Groups.id == group_id)
        group = await session.execute(stmt)
        return group.scalar_one_or_none()

    @staticmethod
    async def get_group_with_members(
        group_id: UUID, session: AsyncSession
    ) -> Groups | None:
        """Получение группы по id с участниками"""
        stmt = (
            select(Groups)
            .options(selectinload(Groups.group_members).joinedload(GroupMembers.member))
            .where(Groups.id == group_id)
        )
        group = await session.execute(stmt)
        return group.scalar_one_or_none()

    @staticmethod
    async def check_member_group(
        group_id: UUID,
        user_id: UUID,
        session: AsyncSession,
    ) -> bool:
        """Проверка явления пользователя участником группы"""
        stmt = select(GroupMembers).where(
            GroupMembers.group_id == group_id,
            GroupMembers.user_id == user_id,
        )
        member = await session.execute(stmt)
        return member.scalar_one_or_none() is not None

    @staticmethod
    async def set_last_message(
        group: Groups,
        last_message: Messages,
        session: AsyncSession,
    ) -> None:
        """Установка последнего сообщения в группе"""
        group.last_message = last_message
        session.add(group)
        await session.commit()
