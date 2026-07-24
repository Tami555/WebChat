from enum import StrEnum as PyEnum


class MessageType(PyEnum):
    """ Типы сообщений """
    TEXT = "text"   # текстовое сообщение
    IMAGE = "image"     # картинка
    VOICE = "voice"     # голосовое сообщение
    STICKER = "sticker"  # стикер
    FILE = "file"   # файл
    SYSTEM = "system"   # системное сообщение
