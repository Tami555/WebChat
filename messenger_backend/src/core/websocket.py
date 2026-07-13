import asyncio
import json
from fastapi import WebSocket

from src.core.redis import redis_helper


class WebsocketManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.server_id = None
        self.pubsub = None
        self._initialized = False
    
    async def initialize(self, server_id: str = "server-1"):
        if self._initialized:
            return
        self.server_id = server_id
        self.pubsub = redis_helper.client.pubsub()
        asyncio.create_task(self._listen_to_pubsub())
        self._initialized = True

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket
        # Работа с Redis
        user_server_key = redis_helper.create_key(redis_helper.namespace.ws_server_user, username)
        await redis_helper.client.set(user_server_key, self.server_id) # на каком user сервере (PUB\SUB)
        await redis_helper.client.sadd(redis_helper.namespace.users_online, username) # в redis, что user в онлайне

    async def disconnect(self, username: str):
        del self.active_connections[username]
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