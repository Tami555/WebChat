from uuid import UUID
from pydantic import BaseModel
from fastapi import Form

from .enums import MessageType, ChatType


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


class DownloadMessageFileRequest(BaseModel):
    """Схема скачивания файла"""

    file_path: str
    chat_id: UUID
    chat_type: ChatType


class DeleteMessageFileRequest(DownloadMessageFileRequest):
    """Схема удаления файла"""

    pass
