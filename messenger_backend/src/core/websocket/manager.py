import logging
import asyncio
import json
import redis
from uuid import UUID
from fastapi import WebSocket

from src.core.redis import online_redis, pubsub_redis
from src.schemas.enums import ChatType

logger = logging.getLogger(__name__)


class WebsocketManager:
    """Менеджер работы с Websockets"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.user_current_chat: dict[str, tuple[UUID, ChatType] | None] = {}
        self.server_id = None
        self.pubsub = None
        self._initialized = False
        self._listen_task = None
        self._running = False

    async def initialize(self, server_id: str = "server-1"):
        """Инициализация сервера, где доступны WebSocket соединения"""
        if self._initialized:
            return
        self.server_id = server_id
        self.pubsub = pubsub_redis.get_pubsub()
        self._running = True
        self._listen_task = asyncio.create_task(self._listen_to_pubsub())
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

    async def send_to_user(self, to_username: str, data: dict) -> bool:
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
                    data={
                        "to_username": to_username,
                        "data": data,
                    },
                )
                return True
            return False

    def set_user_chat(self, username: str, chat_id: UUID, chat_type: ChatType):
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

    def get_user_chat(self, username: str) -> tuple[UUID, ChatType] | None:
        """Получить текущий чат пользователя"""
        return self.user_current_chat.get(username)

    async def _listen_to_pubsub(self):
        """Слушает сообщения из Redis PubSub"""
        pubsub_server_key = pubsub_redis.get_channel(server_id=self.server_id)

        while self._running:
            try:
                await self.pubsub.subscribe(pubsub_server_key)
                logger.info(f"Подписка на канал {pubsub_server_key} установлена")

                # Слушаем сообщения
                async for message in self.pubsub.listen():
                    if not self._running:
                        break
                    if message.get("type", "") == "subscribe":
                        continue
                    try:
                        data = json.loads(message["data"])
                        username = data.get("to_username")
                        message_data = data.get("data")

                        if username and username in self.active_connections:
                            await self.active_connections[username].send_json(
                                message_data
                            )
                    except Exception as e:
                        logger.error(f"Ошибка обработки сообщения: {e}")

            except asyncio.CancelledError:
                logger.info("Задача _listen_to_pubsub отменена")
                break

            except redis.exceptions.TimeoutError:
                logger.debug("Ожидание сообщений PubSub (таймаут)")
                continue

            except Exception as e:
                logger.error(f"PubSub Error: {e}")
                await asyncio.sleep(1)  # задержка перед повтором

        logger.info("Прослушивание PubSub остановлено")

    async def shutdown(self):
        """Остановка работы WebSocket соединений"""
        self._running = False

        if self.pubsub:
            try:
                await self.pubsub.unsubscribe()
                await self.pubsub.close()
            except Exception as e:
                logger.error(f"Ошибка при закрытии PubSub: {e}")

        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

        # Закрываем все WebSocket соединения
        for username, websocket in list(self.active_connections.items()):
            try:
                await websocket.close()
            except Exception:
                pass
        self.active_connections.clear()
        self.user_current_chat.clear()
        logger.info("WebsocketManager завершил работу")


websocket_manager = WebsocketManager()
