import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import (
    WebSocket,
    APIRouter,
    Depends,
    WebSocketDisconnect,
    WebSocketException,
)

from src.models import Users
from src.api.v1.dependencies import get_current_user_ws
from src.core.database import database_helper
from src.core.websocket import websocket_manager, WebSocketDispatcher

logger = logging.getLogger(__name__)

router = APIRouter()
dispatcher = WebSocketDispatcher()


@router.websocket("/connect")
async def create_connection(
    ws: WebSocket,
    user: Users = Depends(get_current_user_ws),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
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
                logger.exception("Ошибка WebSocket:", exc_info=e)
                await ws.send_json({"status": "error", "error": str(e)})
    except (WebSocketDisconnect, WebSocketException) as e:
        logger.exception("Ошибка WebSocket:", exc_info=e)
        logger.info("Пользователь %s отключен", (sender_username,))
    finally:
        await websocket_manager.disconnect(sender_username)
