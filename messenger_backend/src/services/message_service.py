import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, Depends

from pathlib import Path

from src.services import DialogService, GroupService, StickerService
from src.crud import messages as msg_crud
from src.models import Messages, Users
from src.schemas.enums import ChatTypes, MessageTypes
from src.schemas import MessageCreate
from src.exceptions import MissedDataForMessageType, NotCorrectMessageTypeForFileType, MessageNotFoundError, FutureTimestampMessageError
from src.utils.files import determining_file_type


class MessageService:
    """Сервис для управления сообщениями"""

    @staticmethod
    async def check_user_is_member(user_id: UUID, chat_id: UUID, chat_type: ChatTypes, session: AsyncSession) -> bool:
        """Проверка, что пользователь является участником чата"""
        if chat_type is ChatTypes.DIALOGS:
            await DialogService.check_user_is_dialog_interlocutor(user_id=user_id, dialog_id=chat_id, session=session)
        elif chat_type is ChatTypes.GROUP:
            await GroupService.check_user_in_group_members(user_id=user_id, group_id=chat_id, session=session)
        return True

    @staticmethod
    async def get_messages_by_chat(
        user: Users,
        chat_id: UUID,
        chat_type: ChatTypes,
        page: int,
        limit: int,
        session: AsyncSession
    ) -> list[Messages]:
        """Получение сообщений чата по типу (группа или диалог) с пагинацией"""
        await MessageService.check_user_is_member(
            user_id=user.id,
            chat_id=chat_id,
            chat_type=chat_type,
            session=session
        )
        messages = await msg_crud.messages_by_dialog_or_group(
            group_id = chat_id if chat_type is ChatTypes.GROUP else None,
            dialog_id = chat_id if chat_type is ChatTypes.DIALOGS else None,
            page = page,
            limit = limit,
            session = session
        )
        return messages
            
    @staticmethod
    async def create_message(
        user: Users,
        session: AsyncSession,
        # users_already_read_message: list[UUID | str],
        message_data: MessageCreate,
        message_file: UploadFile | None = None,
    ) -> Messages:
        """Создание сообщения в чате"""
        # Проверка что отправитель является участником чата
        await MessageService.check_user_is_member(
            user_id=user.id,
            chat_id=message_data.chat_id,
            chat_type=message_data.chat_type,
            session=session
        )
        # Проверка на тип сообщения и наличие его содержимого (TEXT -> content и т.д)
        match message_data.message_type:
            case msg_type if msg_type in [MessageTypes.TEXT, MessageTypes.SYSTEM] and message_data.content is None:
                raise MissedDataForMessageType(msg_type, ('content',))
            
            case msg_type if msg_type is MessageTypes.STICKER and message_data.sticker_id is None:
                raise MissedDataForMessageType(msg_type, ('sticker_id',))
            
            case msg_type if msg_type in [MessageTypes.IMAGE, MessageTypes.VOICE, MessageTypes.FILE] and\
                message_file is None:
                raise MissedDataForMessageType(msg_type, ('message_file',))
            
        # Проверка существования сообщения ответа
        if message_data.reply_message_id is not None and\
            await msg_crud.get_message_by_id(message_data.reply_message_id, session):
            raise MessageNotFoundError()
        
        # Проверка существования стикера
        if message_data.message_type is MessageTypes.STICKER:
            await StickerService.get_sticker_by_id(message_data.sticker_id, session)

        # Проверка, что дата сообщения не в будущем
        if message_data.created_at > datetime.datetime.now():
            raise FutureTimestampMessageError()

        # Сохранение файла. TODO: отдельный сервис для работы с файлами
        USER_FILE_PATH = None
        if message_file is not None:
            # Проверка на тип сообщения и тип файла
            real_file_type = determining_file_type(message_file.content_type)
            if real_file_type != message_data.message_type:
                raise NotCorrectMessageTypeForFileType(message_data.message_type, message_file.content_type)
            
            # Записываем файл (пока что на локалку). TODO: запись файла в S3
            BASE_FILES_PATH = Path(__file__).parent.parent.parent / "user_files" / "chats"
            USER_FILE_PATH = BASE_FILES_PATH / f"{message_data.chat_id}" / message_data.message_type / message_file.filename
            USER_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

            with open(USER_FILE_PATH, "wb") as f:
                f.write(message_file.file.read())

        # Cоздание
        new_message = Messages(
            sender_id=user.id,
            dialog_id=message_data.chat_id if message_data.chat_type is ChatTypes.DIALOGS else None,
            group_id=message_data.chat_id if message_data.chat_type is ChatTypes.GROUP else None,
            type=message_data.message_type,
            content=message_data.content,
            file_url=str(USER_FILE_PATH) if USER_FILE_PATH else None,
            sticker_id=message_data.sticker_id,
            reply_to_id=message_data.reply_message_id,
            created_at=message_data.created_at
        )
        # TODO: добавить список получателей для Message_Status
        # TODO: сообщение должно стать последним в чате
        return await msg_crud.create_message(new_message, session)