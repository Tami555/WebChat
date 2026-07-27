from src.schemas.enums import MessageType


def determining_file_type(file_content_type: str) -> MessageType | None:
    """Определяет тип файла для сообщения"""
    content_type = file_content_type.strip().split("/")[0]
    match content_type:
        case "audio":
            return MessageType.VOICE

        case file_type if file_type in ["image", "video"]:
            return MessageType.IMAGE

        case file_type if file_type in ["text", "application", "font"]:
            return MessageType.FILE

        case _:
            return None
