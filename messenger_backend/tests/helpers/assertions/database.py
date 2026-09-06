from uuid import UUID
from typing import Optional, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Users, Messages, Dialogs, Groups
from src.crud import MessageCRUD

T = TypeVar("T")


class DatabaseAssertions:
    """Базовые проверки БД"""

    @staticmethod
    async def assert_exists(
        session: AsyncSession, model_class: T, **filters
    ) -> Optional[T]:
        """Проверяет, что запись существует в БД"""
        from sqlalchemy import select

        stmt = select(model_class).filter_by(**filters)
        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()

        assert obj is not None
        return obj

    @staticmethod
    async def assert_not_exists(
        session: AsyncSession, model_class: T, **filters
    ) -> None:
        """Проверяет, что запись НЕ существует в БД"""
        from sqlalchemy import select

        stmt = select(model_class).filter_by(**filters)
        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()

        assert obj is None


class UserDatabaseAssertions:
    """Проверки для пользователей в БД"""

    @staticmethod
    async def assert_user_exists(
        session: AsyncSession,
        phone: str,
        expected_username: Optional[str] = None,
    ) -> Users | None:
        """Проверяет, что пользователь существует и возвращает его"""
        user = await DatabaseAssertions.assert_exists(session, Users, phone=phone)
        if expected_username:
            assert user.username == expected_username
        assert user.phone == phone
        return user

    @staticmethod
    async def assert_user_not_exists(session: AsyncSession, phone: str) -> None:
        """Проверяет, что пользователь НЕ существует"""
        await DatabaseAssertions.assert_not_exists(session, Users, phone=phone)


class MessageDatabaseAssertions:
    """Проверки для сообщений в БД"""

    @staticmethod
    async def assert_message_exists(
        session: AsyncSession,
        message_id: UUID,
        sender_id: UUID,
        content: Optional[str] = None,
    ) -> Messages | None:
        """Проверяет, что сообщение существует и возвращает его"""
        message = await DatabaseAssertions.assert_exists(
            session, Messages, id=message_id
        )
        assert message.content == content
        assert message.sender_id == sender_id
        return message

    @staticmethod
    async def assert_message_is_read(
        session: AsyncSession,
        message_id: UUID,
        user_id: UUID,
    ):
        """Проверяет, что сообщение имеет статус "прочитано" для пользователя c user_id"""
        statuses = await MessageCRUD.get_message_statuses(message_id, session)
        for status in statuses:
            if status.user_id == user_id:
                assert status.is_read is True
                assert status.read_at is not None

    @staticmethod
    async def assert_reply_to_message(
        session: AsyncSession,
        message_id: UUID,
        reply_to_id: UUID,
        content: Optional[str] = None,
    ):
        """Проверяет, что сообщение имеет reply_to_id (id ответного сообщения)"""
        message = await MessageCRUD.get_message_by_id(message_id, session)
        assert message.content == content
        assert message.reply_to_id == reply_to_id

    @staticmethod
    async def assert_sticker_message(
        session: AsyncSession,
        message_id: UUID,
        sticker_id: UUID,
    ):
        """Проверяет, что сообщение типа STICKER имеет sticker_id"""
        from src.schemas.enums import MessageType

        message = await MessageCRUD.get_message_by_id(message_id, session)
        assert message.type == MessageType.STICKER
        assert message.sticker_id == sticker_id


class DialogDatabaseAssertions:
    """Проверки для диалогов в БД"""

    @staticmethod
    async def assert_dialog_exists(
        session: AsyncSession,
        user1_id: UUID,
        user2_id: UUID,
    ):
        """Проверяет, что диалог существует и возвращает его"""
        dialog = await DatabaseAssertions.assert_exists(
            session,
            Dialogs,
            user1_id=user1_id,
            user2_id=user2_id,
        )
        assert dialog is not None
        return dialog

    @staticmethod
    async def assert_last_message(
        session: AsyncSession,
        dialog_id: UUID,
        last_message_id: UUID,
    ):
        """Проверяет, последнее сообщение в диалоге по его id"""
        dialog = await DatabaseAssertions.assert_exists(session, Dialogs, id=dialog_id)
        assert dialog.last_message_id == last_message_id


class GroupDatabaseAssertions:
    """Проверки для группы в БД"""

    @staticmethod
    async def assert_last_message(
        session: AsyncSession, group_id: UUID, last_message_id: UUID
    ):
        """Проверяет, последнее сообщение в группе по его id"""
        group = await DatabaseAssertions.assert_exists(session, Groups, id=group_id)
        assert group.last_message_id == last_message_id
