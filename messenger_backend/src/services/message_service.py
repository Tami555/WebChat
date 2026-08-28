import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.services import DialogService, GroupService, StickerService
from src.crud import MessageCRUD
from src.models import Messages, Users
from src.schemas.enums import ChatType, MessageType
from src.schemas import MessageCreateRequest
from src.exceptions import (
    MissedDataForMessageTypeError,
    MessageNotFoundError,
    FutureTimestampMessageError,
)


class MessageService:
    """Сервис для управления сообщениями"""

    @staticmethod
    async def check_user_is_member(
        user_id: UUID,
        chat_id: UUID,
        chat_type: ChatType,
        session: AsyncSession,
    ) -> bool:
        """Проверка, что пользователь является участником чата"""
        if chat_type is ChatType.DIALOGS:
            await DialogService.check_user_is_dialog_interlocutor(
                user_id=user_id, dialog_id=chat_id, session=session
            )
        elif chat_type is ChatType.GROUP:
            await GroupService.check_user_in_group_members(
                user_id=user_id, group_id=chat_id, session=session
            )
        return True

    @staticmethod
    async def get_messages_by_chat(
        user: Users,
        chat_id: UUID,
        chat_type: ChatType,
        page: int,
        limit: int,
        session: AsyncSession,
    ) -> list[Messages]:
        """Получение сообщений чата по типу (группа или диалог) с пагинацией"""
        await MessageService.check_user_is_member(
            user_id=user.id, chat_id=chat_id, chat_type=chat_type, session=session
        )
        messages = await MessageCRUD.messages_by_dialog_or_group(
            group_id=chat_id if chat_type is ChatType.GROUP else None,
            dialog_id=chat_id if chat_type is ChatType.DIALOGS else None,
            page=page,
            limit=limit,
            session=session,
        )
        if messages:
            # Отмечаем сообщения как прочитанные
            await MessageCRUD.mark_messages_as_read_by_chat(
                user_id=user.id,
                group_id=chat_id if chat_type is ChatType.GROUP else None,
                dialog_id=chat_id if chat_type is ChatType.DIALOGS else None,
                session=session,
            )
        return messages

    @staticmethod
    async def get_chat_participants_username(
        chat_id: UUID,
        chat_type: ChatType,
        session: AsyncSession,
    ) -> set[str]:
        """Получение username-участников чата"""
        if chat_type == ChatType.DIALOGS:
            return await DialogService.get_dialog_interlocutors_username(
                dialog_id=chat_id, session=session
            )
        elif chat_type == ChatType.GROUP:
            return await GroupService.get_group_members_username(
                group_id=chat_id, session=session
            )
        return set()

    @staticmethod
    async def create_message(
        user: Users,
        session: AsyncSession,
        message_data: MessageCreateRequest,
    ) -> Messages:
        """Создание сообщения в чате"""
        # Проверка, что отправитель является участником чата
        await MessageService.check_user_is_member(
            user_id=user.id,
            chat_id=message_data.chat_id,
            chat_type=message_data.chat_type,
            session=session,
        )
        # Проверка на тип сообщения и наличие его содержимого
        match message_data.message_type:
            case msg_type if (
                msg_type in [MessageType.TEXT, MessageType.SYSTEM]
                and message_data.content is None
            ):
                raise MissedDataForMessageTypeError(msg_type, ("content",))

            case msg_type if (
                msg_type is MessageType.STICKER and message_data.sticker_id is None
            ):
                raise MissedDataForMessageTypeError(msg_type, ("sticker_id",))

            case msg_type if (
                msg_type in [MessageType.IMAGE, MessageType.VOICE, MessageType.FILE]
                and message_data.file_url is None
            ):
                raise MissedDataForMessageTypeError(msg_type, ("message_file",))

        # Проверка существования сообщения ответа
        if message_data.reply_message_id is not None:
            reply_message = await MessageCRUD.get_message_by_id(
                message_data.reply_message_id, session
            )
            if reply_message is None:
                raise MessageNotFoundError()

        # Проверка существования стикера
        if message_data.message_type is MessageType.STICKER:
            await StickerService.get_sticker_by_id(message_data.sticker_id, session)

        # Проверка, что дата сообщения не в будущем
        if message_data.created_at > datetime.datetime.now():
            raise FutureTimestampMessageError()

        # Создание
        new_message = Messages(
            sender_id=user.id,
            dialog_id=(
                message_data.chat_id
                if message_data.chat_type is ChatType.DIALOGS
                else None
            ),
            group_id=(
                message_data.chat_id
                if message_data.chat_type is ChatType.GROUP
                else None
            ),
            type=message_data.message_type,
            content=message_data.content,
            file_url=message_data.file_url,
            sticker_id=message_data.sticker_id,
            reply_to_id=message_data.reply_message_id,
            created_at=message_data.created_at,
        )
        created_message = await MessageCRUD.create_message(new_message, session)

        # Обновляем last_message
        await MessageService.update_chat_last_message(
            chat_id=message_data.chat_id,
            chat_type=message_data.chat_type,
            last_message=created_message,
            session=session,
        )
        return await MessageCRUD.get_message_by_id_with_relationships(
            created_message.id, session
        )

    @staticmethod
    async def update_chat_last_message(
        chat_id: UUID,
        chat_type: ChatType,
        last_message: Messages,
        session: AsyncSession,
    ):
        """Обновление последнего сообщения в чате"""
        if chat_type == ChatType.DIALOGS:
            await DialogService.update_dialog_last_message(
                dialog_id=chat_id, last_message=last_message, session=session
            )
        elif chat_type == ChatType.GROUP:
            await GroupService.update_group_last_message(
                group_id=chat_id, last_message=last_message, session=session
            )

    @staticmethod
    async def create_message_statuses(
        message: Messages,
        read_users_ids: list[UUID],
        not_read_users_ids: list[UUID],
        read_at: datetime.datetime,
        session: AsyncSession,
    ) -> None:
        """Создание статусов чтения сообщения для участников"""
        return await MessageCRUD.create_message_statuses(
            message=message,
            read_users_ids=read_users_ids,
            not_read_users_ids=not_read_users_ids,
            read_at=read_at,
            session=session,
        )
