from fastapi import WebSocket, APIRouter, Depends, WebSocketDisconnect, WebSocketException

from src.models import Users
from src.api.v1.dependencies import get_current_user_ws
from src.core.websocket import websocket_manager
from src.core.redis import redis_helper
from src.schemas import MessageCreate


router = APIRouter()


@router.websocket('/connect')
async def create_connection(ws: WebSocket, user: Users = Depends(get_current_user_ws)):
    sender_user = user.username
    try: 
        # TODO: сделать нормальный сервис
        # подключились
        await websocket_manager.connect(
            username=sender_user,
            websocket=ws
        )
        # слушаем и отправляем сообщения
        while True:
            msg = await ws.receive_json()  # получили сообщение от клиента. Нужно отправить его другим

            create_msg_data = MessageCreate(**msg)
            print(f"Create message: {create_msg_data}")

            # Достаем id чата, получаем из БД всех отправителей и отправляем им через цикл
            users_from_chat = set(["tamiron_post", "anna_red", "sam", "lari_milord", "tobi"]) # Типо users из чата из БД. Половина онлайн\полповина нет
            all_online_users = set(await redis_helper.client.smembers(redis_helper.namespace.users_online))

            users_online = users_from_chat & all_online_users
            users_notifications = users_from_chat - all_online_users

            print(f"В принципе онлайн: {all_online_users}; Наши онлайн: {users_online}")
            print(f"Уведомлния для: {users_notifications}")

            # Тем которые онлайн отправляем через WS
            success_send_users = [] # Список тех кто прям реально прочитал: для message_statuses, is_read = True
            for user in users_online:
                is_success = await websocket_manager.send_to_user(
                    from_username=sender_user,
                    to_username=user,
                    data=msg
                )
                if not is_success:
                    users_notifications.add(user)
                else:
                    success_send_users.append(user)
            # Записываем сообщение в БД

            # Тем которые Нет отправляем уведомление
            for user in users_notifications:
                print(f"Уведомления для {user}")

    except (WebSocketDisconnect, WebSocketException):
        await websocket_manager.disconnect(sender_user)

        



