import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import WebSocket, APIRouter, Depends, WebSocketDisconnect, WebSocketException

from src.models import Users
from src.api.v1.dependencies import get_current_user_ws
from src.core.websocket import websocket_manager
from src.core.database import database_helper
from src.schemas import MessageCreate
from src.services import WebsocketService


router = APIRouter()

# TODO: Поделить пользователей онлайн, кто находился просто в сети (read=False) и
#  кто был прям в том же чате и точно прочитал сообщение (для status_message)

# TODO: При чтении списка сообщений, те у кого в status_message read=False, должно измениться на True


@router.websocket('/connect')
async def create_connection(
    ws: WebSocket,
    user: Users = Depends(get_current_user_ws),
    session: AsyncSession = Depends(database_helper.create_scoped_session)
):
    """WebSocket соединение для чата"""
    sender_user = user
    sender_username = user.username
    try:
        # Подключаем пользователя
        await websocket_manager.connect(
            username=sender_username,
            websocket=ws
        )
        # Основной цикл обработки сообщений
        while True:
            try:
                # сообщение от клиента
                raw_data = await ws.receive_json()
                message_data = MessageCreate(**raw_data)
                message_data.created_at = datetime.datetime.now()

                # Обрабатываем сообщение
                result = await WebsocketService.process_message(
                    sender_user=sender_user,
                    message_data=message_data,
                    session=session
                )
                # Отправляем подтверждение отправителю
                await ws.send_json(result)

            except (WebSocketDisconnect, WebSocketException):
                break
            except Exception as e:
                # TODO: заменить на логирование
                print(f"Ошибка отправке сообщения: {e}")
                await ws.send_json({
                    "status": "error",
                    "error": str(e)
                })
    except (WebSocketDisconnect, WebSocketException):
        print(f"User {sender_username} disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Отключаем пользователя
        await websocket_manager.disconnect(sender_username)
