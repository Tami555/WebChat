from fastapi import WebSocket, APIRouter, Depends, WebSocketDisconnect, WebSocketException

from src.models import Users
from src.api.v1.dependencies import get_current_user_ws
from src.core.websocket import websocket_manager
from src.core.redis import redis_helper


router = APIRouter()


@router.websocket('/connect')
async def create_connection(ws: WebSocket, user: Users = Depends(get_current_user_ws)):
    try: 
        # TODO: сделать нормальный сервис
        sender_user = user.username
        # подключились
        await websocket_manager.connect(
            username=sender_user,
            websocket=ws
        )
        # слушаем и отправляем сообщения
        while True:
            msg = await ws.receive_json() # получили сообщение от клиента. Нужно отправить его другим
            # Достаем id чата, получаем из БД всех отправителей и отправляем им через цикл 
            users_from_chat = set(["tamiron_post", "anna_red", "sam", "lari_milord", "tobi"]) # Типо users из чата из БД. Половина онлайн\полповина нет
            all_online_users = set(await redis_helper.client.smembers(redis_helper.namespace.users_online))

            users_online = users_from_chat & all_online_users
            users_notifications = users_from_chat - all_online_users

            print(f"В принципе онлайн: {all_online_users}; Наши онлайн: {users_online}")
            print(f"Уведомлния для: {users_notifications}")

            # Тем которые онлайн отправляем через WS
            for user in users_online:
                is_success = await websocket_manager.send_to_user(
                    from_username=sender_user,
                    to_username=user,
                    data=msg
                )
                if not is_success:
                    print(f"Уведомления для {user}")

            # Тем которые Нет отправляем уведомление
            for user in users_notifications:
                print(f"Уведомления для {user}")
        
            # Записываем сообщение в БД
    except (WebSocketDisconnect, WebSocketException):
        await websocket_manager.disconnect(sender_user)

        



