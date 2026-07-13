import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import MessageCreate, MessageResponse
from src.services import MessageService, UserService, NotificationService
from src.models import Users
from src.core.redis import redis_helper
from src.core.websocket import websocket_manager


class WebsocketService:
    """Сервис Websocket"""

    @staticmethod
    async def process_message(
        sender_user: Users,
        message_data: MessageCreate,
        session: AsyncSession
    ) -> dict | str:
        """ Основной метод обработки входящего сообщения """
        # Создаем сообщение в БД
        created_message = await MessageService.create_message(
            user=sender_user,
            session=session,
            message_data=message_data
        )
        message_response = MessageResponse.model_validate(created_message)

        # Получаем участников чата. Кто онлайн/офлайн
        chat_participants = await MessageService.get_chat_participants_username(
            chat_id=message_data.chat_id,
            chat_type=message_data.chat_type,
            session=session
        )
        all_online = await redis_helper.client.smembers(redis_helper.namespace.users_online)
        online_users = chat_participants & all_online
        offline_users = chat_participants - all_online

        # Отправляем онлайн-пользователям через ws
        successfully_sent = []
        for username in online_users:
            if username != sender_user.username:  # Не отправляем отправителю
                success = await websocket_manager.send_to_user(
                    from_username=sender_user.username,
                    to_username=username,
                    data=message_response.model_dump_json()
                )
                if success:  # TODO: разделить: просто получил по онлайн (successfully_sent) и тех кто прям прочитал
                    successfully_sent.append(username)

        # Кто не получил (офлайн или не дошло)
        not_received = (offline_users | (online_users - set(successfully_sent))) - {sender_user.username}

        # Создаем статусы чтения
        read_users_ids = await UserService.get_user_ids_by_usernames(successfully_sent, session)
        not_read_users_ids = await UserService.get_user_ids_by_usernames(not_received, session)
        await MessageService.create_message_statuses(
            message=created_message,
            read_users_ids=read_users_ids,
            not_read_users_ids=not_read_users_ids,
            read_at=datetime.datetime.now(),
            session=session
        )

        # Отправляем push-уведомления офлайн-пользователям
        if not_received:
            await NotificationService.send_push_notifications(
                usernames=list(not_received),
                message=message_response
            )

        return message_response.model_dump_json()
