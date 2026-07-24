import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import MessageCreateRequest, MessageResponse
from src.schemas.enums import ChatType
from src.services import MessageService, UserService, NotificationService
from src.models import Users
from src.core.redis import online_redis
from src.core.websocket.manager import websocket_manager


class WebsocketService:
    """Сервис Websocket"""

    @staticmethod
    async def process_message(
        sender_user: Users,
        message_data: MessageCreateRequest,
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
        all_online = await online_redis.get_all_online()
        online_users = chat_participants & all_online
        offline_users = chat_participants - all_online

        # Отправляем онлайн-пользователям через ws
        delivered_to = set()  # Доставлено
        read_by = set()  # Прочитано
        for username in online_users:
            if username != sender_user.username:  # Не отправляем отправителю
                success = await websocket_manager.send_to_user(
                    from_username=sender_user.username,
                    to_username=username,
                    data=message_response.model_dump_json()
                )
                if success:
                    delivered_to.add(username)
                    current_chat = websocket_manager.get_user_chat(username)
                    if (current_chat is not None and
                            current_chat[0] == message_data.chat_id and
                            current_chat[1] == message_data.chat_type):
                        read_by.add(username)

        # Кто не прочитал сообщение
        not_read_by = (offline_users | (online_users - read_by)) - {sender_user.username}

        # Создаем статусы чтения
        read_users_ids = await UserService.get_user_ids_by_usernames(read_by, session)
        not_read_users_ids = await UserService.get_user_ids_by_usernames(not_read_by, session)
        await MessageService.create_message_statuses(
            message=created_message,
            read_users_ids=read_users_ids,
            not_read_users_ids=not_read_users_ids,
            read_at=datetime.datetime.now(),
            session=session
        )
        # Отправляем push-уведомления офлайн-пользователям
        notification_to = (offline_users | (online_users - delivered_to)) - {sender_user.username}
        if notification_to:
            await NotificationService.send_push_notifications(
                usernames=list(notification_to),
                message=message_response
            )

        return message_response.model_dump_json()

    @staticmethod
    async def broadcast_typing_status(
        sender_username: str,
        chat_id: UUID,
        chat_type: ChatType,
        is_typing: bool,
        session: AsyncSession
    ):
        """Уведомить участников чата о статусе печатания"""
        participants = await MessageService.get_chat_participants_username(
            chat_id=chat_id,
            chat_type=chat_type,
            session=session
        )
        # Отправляем
        for participant in participants:
            if participant != sender_username:
                await websocket_manager.send_to_user(
                    from_username=sender_username,
                    to_username=participant,
                    data={
                        "type": "typing_status",
                        "username": sender_username,
                        "is_typing": is_typing,
                        "chat_id": str(chat_id),
                        "chat_type": chat_type.value
                    }
                )
