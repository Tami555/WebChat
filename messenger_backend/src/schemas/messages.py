import datetime
from uuid import UUID
from pydantic import BaseModel
from fastapi import Form

from .enums import MessageTypes, ChatTypes
from .users import ShortUserResponse
from .sticker import ShortStickerResponse, StickerResponse


class ShortMessageResponse(BaseModel):
    sender: ShortUserResponse
    type: MessageTypes = MessageTypes.TEXT
    created_at: datetime.datetime
    content: str | None = None
    sticker: ShortStickerResponse | None = None

    class Config:
        from_attributes = True


class MessageResponse(ShortMessageResponse):
    id: UUID
    file_url: str | None = None
    sticker: StickerResponse | None = None
    reply_message: ShortMessageResponse | None = None
    is_edited: bool

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    chat_id: UUID
    chat_type: ChatTypes
    message_type: MessageTypes
    content: str | None = None
    sticker_id: UUID | None = None
    reply_message_id: UUID | None = None
    file_url: str | None = None
    created_at: datetime.datetime

    @staticmethod
    def create_message_by_form(
        chat_id: UUID = Form(...),
        chat_type: ChatTypes = Form(...),
        message_type: MessageTypes = Form(...),
        content: str | None = Form(default=None),
        sticker_id: UUID | None = Form(default=None),
        reply_message_id: UUID | None = Form(default=None),
        file_url: str | None = Form(default=None),
        created_at: datetime.datetime = Form(...),
    ) -> "MessageCreate":
        return MessageCreate(
            chat_id=chat_id,
            chat_type=chat_type,
            message_type=message_type,
            content=content,
            sticker_id=sticker_id,
            reply_message_id=reply_message_id,
            file_url=file_url,
            created_at=created_at
        )


class UploadMessageFile(BaseModel):
    chat_id: UUID
    chat_type: ChatTypes
    file_type: MessageTypes

    @staticmethod
    def upload_message_file_by_form(
        chat_id: UUID = Form(...),
        chat_type: ChatTypes = Form(...),
        file_type: MessageTypes = Form(...)
    ) -> "UploadMessageFile":
        return UploadMessageFile(
            chat_id=chat_id,
            chat_type=chat_type,
            file_type=file_type
        )


class SaveMessageFile(BaseModel):
    chat_id: UUID
    file_type: MessageTypes
    username: str
