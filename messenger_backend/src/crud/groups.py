from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models import Groups, GroupMembers, Messages
from src.schemas.enums import GroupMemberRole, MessageType


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

    @staticmethod
    async def get_group_media(group_id: UUID, session: AsyncSession) -> list:
        """Получение медиа (файлы) группы"""
        stmt = select(Messages.type, Messages.file_url).where(
            Messages.group_id == group_id
            and Messages.type.in_(
                [MessageType.IMAGE, MessageType.VOICE, MessageType.FILE]
            )
        )
        messages = await session.execute(stmt)
        return list(messages.all())

    @staticmethod
    async def update_group_avatar_url(
        group: Groups,
        avatar_url: str | None,
        session: AsyncSession,
    ) -> Groups:
        """Обновление url-аватарки группы через ORM-объект"""
        group.avatar_url = avatar_url
        session.add(group)
        await session.commit()
        await session.refresh(group)
        return group

    @staticmethod
    async def update_group(
        group: Groups,
        update_data: dict,
        session: AsyncSession,
    ) -> Groups:
        """Обновление полей группы в БД"""
        for field, value in update_data.items():
            setattr(group, field, value)

        session.add(group)
        await session.commit()
        await session.refresh(group)
        return group

    @staticmethod
    async def check_admin_group(
        group_id: UUID, user_id: UUID, session: AsyncSession
    ) -> bool:
        """Проверка, является ли пользователь админом группы"""
        stmt = select(GroupMembers).where(
            GroupMembers.group_id == group_id,
            GroupMembers.user_id == user_id,
            GroupMembers.role == GroupMemberRole.ADMIN,
        )
        member = await session.execute(stmt)
        return member.scalar_one_or_none() is not None

    @staticmethod
    async def get_group_member(
        group_id: UUID, user_id: UUID, session: AsyncSession
    ) -> GroupMembers | None:
        """Получение записи участника группы"""
        stmt = select(GroupMembers).where(
            GroupMembers.group_id == group_id,
            GroupMembers.user_id == user_id,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def add_members(
        group_id: UUID, user_ids: list[UUID], session: AsyncSession
    ) -> None:
        """Добавление участников в группу"""
        group = await GroupCRUD.get_group_by_id(group_id, session)
        for uid in user_ids:
            group.group_members.append(GroupMembers(user_id=uid))
        session.add(group)
        await session.commit()

    @staticmethod
    async def remove_member(
        group_id: UUID, user_id: UUID, session: AsyncSession
    ) -> None:
        """Удаление участника из группы"""
        stmt = delete(GroupMembers).where(
            GroupMembers.group_id == group_id,
            GroupMembers.user_id == user_id,
        )
        await session.execute(stmt)
        await session.commit()

    @staticmethod
    async def update_member_role(
        group_id: UUID, user_id: UUID, new_role: GroupMemberRole, session: AsyncSession
    ) -> GroupMembers:
        """Изменение роли участника"""
        member = await GroupCRUD.get_group_member(group_id, user_id, session)
        member.role = new_role
        session.add(member)
        await session.commit()
        await session.refresh(member)
        return member

    @staticmethod
    async def delete_group(group_id: UUID, session: AsyncSession) -> None:
        """Удаление группы (каскадно удалятся участники)"""
        stmt = delete(Groups).where(Groups.id == group_id)
        await session.execute(stmt)
        await session.commit()
