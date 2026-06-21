from enum import StrEnum as PyEnum


class MessageTypes(PyEnum):
    TEXT = "text" # текстовое сообщени
    IMAGE = "image" # картинка
    VOICE = "voice" # голосове сообщение
    STICKER= "sticker" # стикер
    FILE = "file" # файл
    SYSTEM = "system" # системное сообщение