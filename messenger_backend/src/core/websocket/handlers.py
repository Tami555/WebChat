import datetime
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import Users
from src.schemas import (
    JoinChatMessageRequest,
    TypingMessageRequest,
    MessageContentRequest,
    PongMessageResponse,
)
from src.core.websocket.manager import websocket_manager
from src.core.websocket.service import WebsocketService


class WebSocketHandlers:
    """Обработчики WebSocket сообщений"""

    @staticmethod
    async def handle_join_chat(user: Users, data: JoinChatMessageRequest, **kwargs):
        """Обработчик входа в чат"""
        websocket_manager.set_user_chat(user.username, data.chat_id, data.chat_type)

    @staticmethod
    async def handle_leave_chat(user: Users, **kwargs):
        """Обработчик выхода из чата"""
        websocket_manager.clear_user_chat(user.username)

    @staticmethod
    async def handle_typing(
        user: Users,
        session: AsyncSession,
        data: TypingMessageRequest,
        **kwargs,
    ):
        """Обработчик статуса печатания"""
        await WebsocketService.broadcast_typing_status(
            sender_user=user,
            chat_id=data.chat_id,
            chat_type=data.chat_type,
            is_typing=data.is_typing,
            session=session,
        )

    @staticmethod
    async def handle_message(
        ws: WebSocket,
        user: Users,
        session: AsyncSession,
        data: MessageContentRequest,
        **kwargs,
    ):
        """Обработчик создания сообщения (с контентом)"""

        message_data = data.message
        message_data.created_at = datetime.datetime.now()
        result = await WebsocketService.process_message(
            sender_user=user,
            message_data=message_data,
            session=session,
        )
        await ws.send_json(result)

    @staticmethod
    async def handle_ping(ws: WebSocket, **kwargs):
        """Обработчик ping (keep-alive)"""
        await ws.send_json(PongMessageResponse().model_dump_json())
