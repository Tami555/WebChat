from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models import Groups, GroupMembers, Messages, MessageStatuses, Users
from src.schemas.enums import RolesMemberGroups


async def groups_by_user(user_id: UUID, session: AsyncSession) -> list[Groups]:
    """Получение всех групп, в которых состоит пользователь"""
    stmt = select(Groups).join(GroupMembers, GroupMembers.group_id == Groups.id).options(
        selectinload(Groups.group_members),
        joinedload(Groups.last_message).joinedload(Messages.sender),
        joinedload(Groups.last_message).joinedload(Messages.sticker),
    ).where(GroupMembers.user_id == user_id)
    groups = await session.scalars(stmt)
    return groups.all()


async def unread_count_for_message(group_id: int, user_id: int, session: AsyncSession) -> int:
    """Количество непрочитанных сообщений для пользователя в группе"""
    stmt = select(func.count()
    ).select_from(
        Messages
    ).where(
        Messages.group_id == group_id,
        Messages.sender_id != user_id,
        Messages.is_deleted == False
    ).join(
        MessageStatuses,
        MessageStatuses.message_id == Messages.id
    ).where(
            MessageStatuses.user_id == user_id,
            MessageStatuses.is_read == False
        )
    count_messages = await session.execute(stmt)
    return count_messages.scalar() or 0


async def create_group(creator_id: UUID, group_data: dict, members_list: list[UUID], session: AsyncSession) -> Groups:
    """Создание группы c участниками"""
    try:
        new_group = Groups(**group_data)
        session.add(new_group)
        for member_id in members_list:
            new_group.group_members.append(GroupMembers(user_id=member_id))
        new_group.group_members.append(GroupMembers(user_id=creator_id, role=RolesMemberGroups.ADMIN))
        await session.commit()
        return new_group
    
    except Exception as e:
        await session.rollback()
        raise e
    

async def get_group_by_id(group_id: UUID, session: AsyncSession) -> Groups | None:
    """Получение диалога по id"""
    stmt = select(Groups).where(Groups.id == group_id)
    group = await session.execute(stmt)
    return group.scalar_one_or_none()


async def check_member_group(group_id: UUID, user_id: UUID, session: AsyncSession) -> bool:
    """Проверка явления пользователя участником группы"""
    stmt = select(GroupMembers).where(GroupMembers.group_id == group_id, GroupMembers.user_id == user_id)
    member = await session.execute(stmt)
    return member.scalar_one_or_none() is not None