from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models import Groups, GroupMembers, Messages, MessageStatuses


async def groups_by_user(user_id: UUID, session: AsyncSession) -> list[Groups]:
    """Получение всех групп, в которых состоит пользователь"""
    stmt = select(Groups).join(GroupMembers, GroupMembers.group_id == Groups.id).options(
        selectinload(Groups.group_members),
        joinedload(Groups.last_message).joinedload(Messages.sender)
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