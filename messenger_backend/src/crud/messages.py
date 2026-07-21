import datetime
from typing import Iterable
from sqlalchemy import select, func, update
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
        .where(Messages.dialog_id == dialog_id,
               Messages.group_id == group_id,
               Messages.is_deleted == False)\
        .options(
            joinedload(Messages.sender),
            joinedload(Messages.reply_message),
            joinedload(Messages.sticker)
        )\
        .limit(limit * page)\
        .order_by(Messages.created_at)\
        .offset((page - 1) * limit)
    messages = await session.scalars(stmt)
    return list(messages.all())


async def mark_messages_as_read_by_chat(
    user_id: UUID,
    session: AsyncSession,
    dialog_id: UUID | None = None,
    group_id: UUID | None = None,
):
    """Отметить все непрочитанные сообщения в чате как прочитанные"""
    stmt = (
        update(MessageStatuses)
        .where(
            MessageStatuses.user_id == user_id,
            MessageStatuses.is_read == False,
            MessageStatuses.message_id.in_(
                select(Messages.id)
                .where(
                    Messages.dialog_id == dialog_id,
                    Messages.group_id == group_id,
                    Messages.sender_id != user_id
                )
            )
        )
        .values(
            is_read=True,
            read_at=datetime.datetime.now()
        )
    )
    await session.execute(stmt)
    await session.commit()


async def get_message_by_id(message_id: UUID, session: AsyncSession) -> Messages | None:
    """ Получение сообщения по id """
    stmt = select(Messages).where(Messages.id == message_id)
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def get_message_by_id_with_relationships(message_id: UUID, session: AsyncSession) -> Messages | None:
    """ Получение сообщения по id с подгрузкой связей"""
    stmt = select(Messages).where(Messages.id == message_id).options(
        joinedload(Messages.sender),
        joinedload(Messages.sticker),
        joinedload(Messages.reply_message).joinedload(Messages.sender),
        joinedload(Messages.reply_message).joinedload(Messages.sticker),
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def create_message(message: Messages, session: AsyncSession) -> Messages:
    """Создание сообщения cо статусами для получателей"""
    session.add(message)
    await session.commit()
    return message


async def create_message_statuses(
        message: Messages,
        read_users_ids: Iterable[UUID],
        not_read_users_ids: Iterable[UUID],
        read_at: datetime.datetime,
        session: AsyncSession
) -> None:
    """Создание статусов чтения для сообщения"""
    statuses = []
    for user_id in read_users_ids:
        statuses.append(MessageStatuses(
            message_id=message.id,
            user_id=user_id,
            is_read=True,
            read_at=read_at
        ))
    for user_id in not_read_users_ids:
        statuses.append(MessageStatuses(
            message_id=message.id,
            user_id=user_id,
            is_read=False,
            read_at=None
        ))
    if statuses:
        session.add_all(statuses)
        await session.commit()

