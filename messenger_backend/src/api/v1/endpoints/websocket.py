from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import WebSocket, APIRouter, Depends, WebSocketDisconnect, WebSocketException

from src.models import Users
from src.api.v1.dependencies import get_current_user_ws
from src.core.database import database_helper
from src.core.websocket import websocket_manager, WebSocketDispatcher


router = APIRouter()
# Диспетчер
dispatcher = WebSocketDispatcher()


# TODO: При чтении списка сообщений, те у кого в status_message read=False, должно измениться на True


@router.websocket('/connect')
async def create_connection(
    ws: WebSocket,
    user: Users = Depends(get_current_user_ws),
    session: AsyncSession = Depends(database_helper.create_scoped_session)
):
    """WebSocket соединение для чата"""
    sender_username = user.username

    try:
        await websocket_manager.connect(username=sender_username, websocket=ws)

        while True:
            try:
                raw_data = await ws.receive_json()
                await dispatcher.dispatch(raw_data, ws, user, session)

            except (WebSocketDisconnect, WebSocketException):
                break
            except Exception as e:
                # TODO: заменить на логирование
                print(f"Error: {e}")
                await ws.send_json({
                    "status": "error",
                    "error": str(e)
                })
    except (WebSocketDisconnect, WebSocketException):
        print(f"User {sender_username} disconnected")
    finally:
        await websocket_manager.disconnect(sender_username)
