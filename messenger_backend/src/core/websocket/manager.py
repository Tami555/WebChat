import asyncio
import json
from uuid import UUID
from fastapi import WebSocket

from src.core.redis import redis_helper
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
        self.pubsub = redis_helper.client.pubsub()
        asyncio.create_task(self._listen_to_pubsub())
        self._initialized = True

    async def connect(self, username: str, websocket: WebSocket):
        """Подключение пользователя к WebSocket соединению"""
        await websocket.accept()
        self.active_connections[username] = websocket
        self.user_current_chat[username] = None
        # Работа с Redis
        user_server_key = redis_helper.create_key(redis_helper.namespace.ws_server_user, username)
        await redis_helper.client.set(user_server_key, self.server_id)  # на каком user сервере (PUB\SUB)
        await redis_helper.client.sadd(redis_helper.namespace.users_online, username)  # в redis, что user в онлайне

    async def disconnect(self, username: str):
        """Отключение пользователя от WebSocket соединения"""
        if username in self.active_connections:
            del self.active_connections[username]
        if username in self.user_current_chat:
            del self.user_current_chat[username]
        # Работа с Redis
        user_server_key = redis_helper.create_key(redis_helper.namespace.ws_server_user, username)
        await redis_helper.client.delete(user_server_key) # удаляем с PUB\SUB
        await redis_helper.client.srem(redis_helper.namespace.users_online, username) # Не онлайн

    async def send_to_user(self, from_username: str, to_username: str, data: dict) -> bool:
        """Отправляет сообщение через WebSocket если пользователь онлайн"""
        # Если пользователь на этом же сервере
        if to_username in self.active_connections:
            await self.active_connections[to_username].send_json(data)
            return True
        else: 
            # Выяснеем на каком сервере получатель и отправляем туда
            to_user_server_key = redis_helper.create_key(redis_helper.namespace.ws_server_user, to_username)
            server = await redis_helper.client.get(to_user_server_key)
            if server:
                to_pubsub_server_key = redis_helper.create_key(redis_helper.namespace.pubsub_server, server)
                # Публикуем в канал этого сервера
                await redis_helper.client.publish(
                    to_pubsub_server_key,
                    json.dumps({"to_username": to_username, "data": data})
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
        pubsub_server_key = redis_helper.create_key(redis_helper.namespace.pubsub_server, self.server_id)
        await self.pubsub.subscribe(pubsub_server_key)

        async for message in self.pubsub.listen():
            if message.get("type", "") == "subscribe":
                continue
            # Отправляем локальному пользователю
            data = json.loads(message["data"])
            if (username := data["to_username"]) in self.active_connections:
                await self.active_connections[username].send_json(data["data"])


websocket_manager = WebsocketManager()