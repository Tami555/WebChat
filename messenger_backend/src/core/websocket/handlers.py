from uuid import UUID
import datetime
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import Users
from src.schemas import MessageCreateRequest
from src.schemas.enums import ChatType
from src.core.websocket.manager import websocket_manager
from src.core.websocket.service import WebsocketService


class WebSocketHandlers:
    """Обработчики WebSocket сообщений"""

    @staticmethod
    async def handle_join_chat(user: Users, data: dict, **kwargs):
        """Обработчик входа в чат"""
        chat_id = UUID(data["chat_id"])
        chat_type = ChatType(data["chat_type"])
        websocket_manager.set_user_chat(user.username, chat_id, chat_type)

    @staticmethod
    async def handle_leave_chat(user: Users, **kwargs):
        """Обработчик выхода из чата"""
        websocket_manager.clear_user_chat(user.username)

    @staticmethod
    async def handle_typing(user: Users, session: AsyncSession, data: dict):
        """Обработчик статуса печатания"""
        chat_id = UUID(data["chat_id"])
        chat_type = ChatType(data["chat_type"])
        is_typing = data.get("is_typing", True)

        await WebsocketService.broadcast_typing_status(
            sender_username=user.username,
            chat_id=chat_id,
            chat_type=chat_type,
            is_typing=is_typing,
            session=session,
        )

    @staticmethod
    async def handle_message(
        ws: WebSocket,
        user: Users,
        session: AsyncSession,
        data: dict,
    ):
        """Обработчик создания сообщения"""
        message_data = MessageCreateRequest(**data)
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
        await ws.send_json(
            {
                "status": "pong",
                "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            }
        )
