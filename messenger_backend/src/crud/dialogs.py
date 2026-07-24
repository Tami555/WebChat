from sqlalchemy import select, or_, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models import Dialogs, Messages


class DialogCRUD:
    """SQL-запросы (CRUD) для Диалогов """

    @staticmethod
    async def dialogs_by_user(user_id: UUID, session: AsyncSession) -> list[Dialogs]:
        """Получение всех чатов-диалгов, в которых состоит пользователь"""
        stmt = select(Dialogs
            ).where(or_(Dialogs.user1_id == user_id, Dialogs.user2_id == user_id)
            ).options(
                joinedload(Dialogs.user1),
                joinedload(Dialogs.user2),
                joinedload(Dialogs.last_message).joinedload(Messages.sticker),
            )
        dialogs = await session.scalars(stmt)
        return list(dialogs.all())

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    async def get_dialog_by_id(dialog_id: UUID, session: AsyncSession) -> Dialogs | None:
        """Получение диалога по id"""
        stmt = select(Dialogs).where(Dialogs.id == dialog_id)
        dialog = await session.execute(stmt)
        return dialog.scalar_one_or_none()

    @staticmethod
    async def get_dialog_by_id_with_relationships(dialog_id: UUID, session: AsyncSession) -> Dialogs:
        """Получение диалога по id со связями"""
        stmt = select(Dialogs)\
            .where(Dialogs.id == dialog_id)\
            .options(
                joinedload(Dialogs.user1),
                joinedload(Dialogs.user2),
                joinedload(Dialogs.last_message).joinedload(Messages.sticker),
            )
        dialog = await session.scalar(stmt)
        return dialog

    @staticmethod
    async def set_last_message(dialog: Dialogs, last_message: Messages, session: AsyncSession) -> None:
        """Установка последнего сообщения в диалоге"""
        dialog.last_message = last_message
        session.add(dialog)
        await session.commit()
