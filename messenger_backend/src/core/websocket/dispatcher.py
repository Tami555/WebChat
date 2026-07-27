from typing import Dict, Callable
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.users import Users
from src.core.websocket.handlers import WebSocketHandlers


class WebSocketDispatcher:
    """Диспетчер для маршрутизации WebSocket сообщений"""

    def __init__(self):
        """Регистрируем обработчики ("message" - дефолтный обработчик)"""
        self._handlers: Dict[str, Callable] = {
            "join_chat": WebSocketHandlers.handle_join_chat,
            "leave_chat": WebSocketHandlers.handle_leave_chat,
            "typing": WebSocketHandlers.handle_typing,
            "ping": WebSocketHandlers.handle_ping,
        }

    def register(self, msg_type: str, handler: Callable):
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
        msg_type = raw_data.get("type", "message")
        handler = self._handlers.get(msg_type, WebSocketHandlers.handle_message)
        await handler(ws=ws, user=user, session=session, data=raw_data)
