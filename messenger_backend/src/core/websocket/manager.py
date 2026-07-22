import asyncio
import json
from uuid import UUID
from fastapi import WebSocket

from src.core.redis import online_redis, pubsub_redis
from src.schemas.enums import ChatTypes


class WebsocketManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.user_current_chat: dict[str, tuple[UUID, ChatTypes] | None] = {}
        self.server_id = None
        self.pubsub = None
        self._initialized = False
    
    async def initialize(self, server_id: str = "server-1"):
        """Инициализация сервера, где доступны WebSocket соединения"""
        if self._initialized:
            return
        self.server_id = server_id
        self.pubsub = pubsub_redis.get_pubsub()
        asyncio.create_task(self._listen_to_pubsub())
        self._initialized = True

    async def connect(self, username: str, websocket: WebSocket):
        """Подключение пользователя к WebSocket соединению"""
        await websocket.accept()
        self.active_connections[username] = websocket
        self.user_current_chat[username] = None
        # Работа с Redis
        await online_redis.add_user(username=username, server_id=self.server_id)

    async def disconnect(self, username: str):
        """Отключение пользователя от WebSocket соединения"""
        if username in self.active_connections:
            del self.active_connections[username]
        if username in self.user_current_chat:
            del self.user_current_chat[username]
        # Работа с Redis
        await online_redis.remove_user(username)

    async def send_to_user(self, from_username: str, to_username: str, data: dict) -> bool:
        """Отправляет сообщение через WebSocket если пользователь онлайн"""
        # Если пользователь на этом же сервере
        if to_username in self.active_connections:
            await self.active_connections[to_username].send_json(data)
            return True
        else: 
            # Выясняем на каком сервере получатель и отправляем туда
            server = await online_redis.get_user_server(username=to_username)
            if server:
                await pubsub_redis.publish_to_server(
                    server_id=server,
                    data={"to_username": to_username, "data": data}
                )
                return True
            return False

    def set_user_chat(self, username: str, chat_id: UUID, chat_type: ChatTypes):
        """Установить текущий чат пользователя"""
        if username in self.user_current_chat:
            self.user_current_chat[username] = (chat_id, chat_type)
            return True
        return False

    def clear_user_chat(self, username: str):
        """Очистить текущий чат пользователя (вышел из чата)"""
        if username in self.user_current_chat:
            self.user_current_chat[username] = None
            return True
        return False

    def get_user_chat(self, username: str) -> tuple[UUID, ChatTypes] | None:
        """Получить текущий чат пользователя"""
        return self.user_current_chat.get(username)

    async def _listen_to_pubsub(self):
        pubsub_server_key = pubsub_redis.get_channel(server_id=self.server_id)
        await self.pubsub.subscribe(pubsub_server_key)

        async for message in self.pubsub.listen():
            if message.get("type", "") == "subscribe":
                continue
            # Отправляем локальному пользователю
            data = json.loads(message["data"])
            if (username := data["to_username"]) in self.active_connections:
                await self.active_connections[username].send_json(data["data"])


websocket_manager = WebsocketManager()
