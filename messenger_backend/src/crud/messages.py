from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models import Messages, MessageStatuses


async def unread_count_message_by_chat(
        session: AsyncSession,
        user_id: UUID,
        dialog_id: UUID | None = None,
        group_id: UUID | None = None,
) -> int:
    """Количество непрочитанных сообщений пользователя в чате"""
    stmt = select(func.count()
    ).select_from(
        Messages
    ).where(
        Messages.dialog_id == dialog_id,
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


async def messages_by_dialog_or_group(
    page: int,
    limit: int,
    session: AsyncSession,
    dialog_id: UUID | None = None,
    group_id: UUID | None = None
) -> list[Messages]:
    """Получение сообщений чатов (группы или диалога) с пагинацией"""
    stmt = select(Messages)\
        .where(Messages.dialog_id == dialog_id, Messages.group_id == group_id, Messages.is_deleted == False)\
        .options(
            joinedload(Messages.sender),
            joinedload(Messages.reply_message),
            joinedload(Messages.sticker)
        )\
        .limit(limit * page)\
        .order_by(Messages.created_at)\
        .offset((page - 1) * limit)
    messages = await session.scalars(stmt)
    return messages.all()


async def get_message_by_id(message_id: UUID, session: AsyncSession) -> Messages | None:
    """ Получение сообщения по id """
    stmt = select(Messages).where(Messages.id == message_id)
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def create_message(message: Messages, session: AsyncSession) -> Messages:
    """Создание сообщения cо статусами для получателей"""
    session.add(message)
    await session.commit()

    # TODO: статусы чтения сообщения для всех получателей
    # TODO: сообщение должно стать последним в чате


