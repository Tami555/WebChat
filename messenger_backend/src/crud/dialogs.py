from sqlalchemy import select, func, or_, and_
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


async def get_dialog_between_users(session: AsyncSession, user1_id: UUID, user2_id: UUID) -> Dialogs | None:
    """Получение диалога между двумя пользователями"""
    stmt = select(Dialogs).where(
        or_(
            and_(Dialogs.user1_id == user1_id, Dialogs.user2_id == user2_id),
            and_(Dialogs.user1_id == user2_id, Dialogs.user2_id == user1_id)
        )
    )
    response = await session.execute(stmt)
    return response.scalar_one_or_none()


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


async def create_dialog(creator_id: UUID, interlocutor_id: UUID, session: AsyncSession) -> Dialogs:
    """Создание нового диалога"""
    new_dialog = Dialogs(
        user1_id=creator_id,
        user2_id=interlocutor_id
    )
    session.add(new_dialog)
    await session.commit()
    await session.refresh(new_dialog)
    return new_dialog


async def get_dialog_by_id(dialog_id: UUID, session: AsyncSession) -> Dialogs:
    """Получение полной информации о диалоге по id"""
    stmt = select(Dialogs)\
        .where(Dialogs.id == dialog_id)\
        .options(
            joinedload(Dialogs.user1),
            joinedload(Dialogs.user2),
            joinedload(Dialogs.last_message)
        )
    dialog = await session.scalar(stmt)
    return dialog
