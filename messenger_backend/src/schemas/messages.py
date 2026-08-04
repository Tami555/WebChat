import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from fastapi import Form

from .enums import MessageType, ChatType
from .users import ShortUserResponse
from .sticker import ShortStickerResponse, StickerResponse


class ShortMessageResponse(BaseModel):
    """Схема сообщения (не полная)"""

    sender: ShortUserResponse
    type: MessageType = MessageType.TEXT
    created_at: datetime.datetime
    content: str | None = None
    sticker: ShortStickerResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(ShortMessageResponse):
    """Схема сообщения"""

    id: UUID
    file_url: str | None = None
    sticker: StickerResponse | None = None
    reply_message: ShortMessageResponse | None = None
    is_edited: bool

    model_config = ConfigDict(from_attributes=True)


class MessageCreateRequest(BaseModel):
    """Схема создания сообщения"""

    chat_id: UUID
    chat_type: ChatType
    message_type: MessageType
    content: str | None = None
    sticker_id: UUID | None = None
    reply_message_id: UUID | None = None
    file_url: str | None = None
    created_at: datetime.datetime

    @staticmethod
    def create_message_by_form(
        chat_id: UUID = Form(...),
        chat_type: ChatType = Form(...),
        message_type: MessageType = Form(...),
        content: str | None = Form(default=None),
        sticker_id: UUID | None = Form(default=None),
        reply_message_id: UUID | None = Form(default=None),
        file_url: str | None = Form(default=None),
        created_at: datetime.datetime = Form(...),
    ) -> "MessageCreateRequest":
        return MessageCreateRequest(
            chat_id=chat_id,
            chat_type=chat_type,
            message_type=message_type,
            content=content,
            sticker_id=sticker_id,
            reply_message_id=reply_message_id,
            file_url=file_url,
            created_at=created_at,
        )


class UploadMessageFileRequest(BaseModel):
    """Схема отправки файла"""

    chat_id: UUID
    chat_type: ChatType
    file_type: MessageType

    @staticmethod
    def upload_message_file_by_form(
        chat_id: UUID = Form(...),
        chat_type: ChatType = Form(...),
        file_type: MessageType = Form(...),
    ) -> "UploadMessageFileRequest":
        return UploadMessageFileRequest(
            chat_id=chat_id, chat_type=chat_type, file_type=file_type
        )


class SaveMessageFileRequest(BaseModel):
    """Схема сохранения файла"""

    chat_id: UUID
    file_type: MessageType
    username: str
