from enum import StrEnum as PyEnum


class WebSocketMessageType(PyEnum):
    """Типы WebSocket сообщений"""

    JOIN_CHAT = "join_chat"  # Вход в чат
    LEAVE_CHAT = "leave_chat"  # Выход из чата
    TYPING = "typing"  # Статус печатания сообщения
    PING = "ping"  # Ping запрос на проверку
    MESSAGE = "message"  # Создать сообщение
