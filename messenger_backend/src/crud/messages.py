from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models import Messages


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