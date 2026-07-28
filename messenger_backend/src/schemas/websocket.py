from datetime import datetime
from uuid import UUID
from typing import Literal, Optional
from pydantic import BaseModel, Field

from src.schemas.enums import WebSocketMessageType, ChatType
from .messages import MessageCreateRequest


class WebSocketMessageRequest(BaseModel):
    """Схема базового WebSocket сообщения"""

    type: WebSocketMessageType

    class Config:
        from_attributes = True
        use_enum_values = True


class JoinChatMessageRequest(WebSocketMessageRequest):
    """Схема сообщения входа в чат"""

    type: Literal[WebSocketMessageType.JOIN_CHAT] = WebSocketMessageType.JOIN_CHAT
    chat_id: UUID
    chat_type: ChatType


class LeaveChatMessageRequest(WebSocketMessageRequest):
    """Схема сообщения выхода из чата"""

    type: Literal[WebSocketMessageType.LEAVE_CHAT] = WebSocketMessageType.LEAVE_CHAT


class TypingMessageRequest(WebSocketMessageRequest):
    """Схема сообщения о статусе печатания"""

    type: Literal[WebSocketMessageType.TYPING] = WebSocketMessageType.TYPING
    chat_id: UUID
    chat_type: ChatType
    is_typing: bool = True


class TypingStatusResponse(TypingMessageRequest):
    """Схема ответа о статусе печатания"""

    username: str
    timestamp: datetime = Field(default_factory=datetime.now)


class PingMessageRequest(WebSocketMessageRequest):
    """Схема Ping сообщение (keep-alive)"""

    type: Literal[WebSocketMessageType.PING] = WebSocketMessageType.PING
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class PongMessageResponse(WebSocketMessageRequest):
    """Схема ответа Pong на сообщение Ping (keep-alive)"""

    status: Literal["pong"] = "pong"
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class MessageContentRequest(WebSocketMessageRequest):
    """Схема создания сообщения (с содержимым: текст, файл и т.д.)"""

    type: Literal[WebSocketMessageType.MESSAGE] = WebSocketMessageType.MESSAGE
    message: MessageCreateRequest
