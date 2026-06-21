from sqlalchemy import select, func, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models import Dialogs, Messages, MessageStatuses


async def dialogs_by_user(user_id: UUID, session: AsyncSession) -> list[Dialogs]:
    """Получение всех чатов-диалгов, в которых состоит пользователь"""
    stmt = select(Dialogs
        ).where(or_(Dialogs.user1_id == user_id, Dialogs.user2_id == user_id)
        ).options(
            joinedload(Dialogs.user1),
            joinedload(Dialogs.user2),
            joinedload(Dialogs.last_message)
        )
    dialogs = await session.scalars(stmt)
    return dialogs.all()


async def unread_count_for_message(dialog_id: int, user_id: int, session: AsyncSession) -> int:
    """Количество непрочитанных сообщений для пользователя в диалоге"""
    stmt = select(func.count()
    ).select_from(
        Messages
    ).where(
        Messages.dialog_id == dialog_id,
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