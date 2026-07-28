from typing import Dict, Callable
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

import src.schemas.websocket as schemas
from src.schemas.enums import WebSocketMessageType
from src.models.users import Users
from src.core.websocket.handlers import WebSocketHandlers
from src.exceptions import WebSocketMessageTypeNotFoundError


class WebSocketDispatcher:
    """Диспетчер для маршрутизации WebSocket сообщений"""

    def __init__(self):
        """Обработчики WebSocket-сообщений (функция обработчик, схема данных)"""
        self._handlers: Dict[str, tuple] = {
            WebSocketMessageType.JOIN_CHAT: (
                WebSocketHandlers.handle_join_chat,
                schemas.JoinChatMessageRequest,
            ),
            WebSocketMessageType.LEAVE_CHAT: (
                WebSocketHandlers.handle_leave_chat,
                schemas.LeaveChatMessageRequest,
            ),
            WebSocketMessageType.TYPING: (
                WebSocketHandlers.handle_typing,
                schemas.TypingMessageRequest,
            ),
            WebSocketMessageType.PING: (
                WebSocketHandlers.handle_ping,
                schemas.PingMessageRequest,
            ),
            WebSocketMessageType.MESSAGE: (
                WebSocketHandlers.handle_message,
                schemas.MessageContentRequest,
            ),
        }
        # Дефолтный обработчик "message"
        self._default_handler = WebSocketHandlers.handle_message

    def register(
        self,
        msg_type: WebSocketMessageType | str,
        handler: tuple[Callable, schemas.WebSocketMessageRequest],
    ):
        """Регистрация нового обработчика"""
        self._handlers[msg_type] = handler

    async def dispatch(
        self,
        raw_data: dict,
        ws: WebSocket,
        user: Users,
        session: AsyncSession,
    ):
        """Маршрутизация сообщения"""
        msg_type = raw_data.get("type")
        if msg_type is None or msg_type not in self._handlers:
            raise WebSocketMessageTypeNotFoundError()
        handler, schema = self._handlers.get(msg_type, self._default_handler)
        await handler(
            ws=ws,
            user=user,
            session=session,
            data=schema(**raw_data),
        )
