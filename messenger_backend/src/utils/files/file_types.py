from src.schemas.enums import MessageTypes


def determining_file_type(file_content_type: str) -> MessageTypes | None:
    """Определяет тип файла для сообщения"""
    content_type = file_content_type.strip().split("/")[0]
    match content_type:     
        case "audio":
            return MessageTypes.VOICE
        
        case type if type in ["image", "video"]:
            return MessageTypes.IMAGE
        
        case type if type in ["text", "application", "font"]:
            return MessageTypes.FILE
        
        case _:
            return None
