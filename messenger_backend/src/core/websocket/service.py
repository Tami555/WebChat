import datetime
import logging
from pathlib import Path
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.enums import ChatType
from src.schemas import (
    MessageCreateRequest,
    MessageResponse,
    TypingStatusResponse,
    SystemMessageCreateRequest,
    SystemMessageResponse,
    BroadcastResult,
)
from src.services import MessageService, UserService
from src.models import Users
from src.core.redis import online_redis
from src.core.websocket.manager import websocket_manager
from src.utils.files import get_file_manager
from src.utils.notifications import get_notification_manager
from src.exceptions import BaseAppException

logger = logging.getLogger(__name__)


class WebsocketService:
    """Сервис Websocket"""

    @staticmethod
    async def _broadcast_to_chat_participants(
        chat_id: UUID,
        chat_type: ChatType,
        message_response,
        session: AsyncSession,
        sender_username: str | None = None,
    ) -> BroadcastResult:
        """
        Рассылка сообщения участникам чата.
        Возвращает результат: кто онлайн, кто офлайн, кому доставлено, кто прочитал.
        """
        # Получаем участников и онлайн-статус
        chat_participants = await MessageService.get_chat_participants_username(
            chat_id=chat_id, chat_type=chat_type, session=session
        )
        all_online = await online_redis.get_all_online()

        online_users = chat_participants & all_online
        offline_users = chat_participants - all_online

        delivered_to = set()
        read_by = set()
        # Рассылка
        for username in online_users:
            if username == sender_username:
                continue  # Отправителю не отправляем

            success = await websocket_manager.send_to_user(
                to_username=username,
                data=message_response.model_dump_json(),
            )
            if success:
                delivered_to.add(username)
                # Проверяем, находится ли пользователь сейчас в этом чате
                current_chat = websocket_manager.get_user_chat(username)
                if (
                    current_chat is not None
                    and current_chat[0] == chat_id
                    and current_chat[1] == chat_type
                ):
                    read_by.add(username)

        return BroadcastResult(
            online_users=online_users,
            offline_users=offline_users,
            delivered_to=delivered_to,
            read_by=read_by,
        )

    @staticmethod
    async def process_message(
        sender_user: Users,
        message_data: MessageCreateRequest,
        session: AsyncSession,
    ) -> dict | str:
        """Основной метод обработки входящего сообщения"""
        # Создаем сообщение в БД
        try:
            created_message = await MessageService.create_message(
                user=sender_user,
                session=session,
                message_data=message_data,
            )
        except (BaseAppException, Exception) as err:
            if message_data.file_url is not None:
                # удаляем файл
                file_path = Path(message_data.file_url)
                logger.warning("Файл сообщения будет удален")
                file_manager = get_file_manager()
                await file_manager.delete_file(file_path)
            raise err

        message_response = MessageResponse.model_validate(created_message)

        # Рассылаем
        result = await WebsocketService._broadcast_to_chat_participants(
            chat_id=message_data.chat_id,
            chat_type=message_data.chat_type,
            message_response=message_response,
            session=session,
            sender_username=sender_user.username,
        )
        # Кто не прочитал сообщение
        not_read_by = result.not_read_by - {sender_user.username}

        # Создаем статусы чтения
        read_users_ids = await UserService.get_user_ids_by_usernames(
            result.read_by, session
        )
        not_read_users_ids = await UserService.get_user_ids_by_usernames(
            not_read_by, session
        )
        await MessageService.create_message_statuses(
            message=created_message,
            read_users_ids=read_users_ids,
            not_read_users_ids=not_read_users_ids,
            read_at=datetime.datetime.now(),
            session=session,
        )
        # Отправляем push-уведомления офлайн-пользователям
        notification_to = (
            result.offline_users | (result.online_users - result.delivered_to)
        ) - {sender_user.username}
        if notification_to:
            notification_manager = get_notification_manager()
            await notification_manager.send_bulk_notification(
                usernames=list(notification_to),
                message=message_response,
            )

        return message_response.model_dump_json()

    @staticmethod
    async def process_system_message(
        system_message_data: SystemMessageCreateRequest,
        session: AsyncSession,
    ) -> dict | str:
        """Создание и отправка системного сообщения всем участникам"""

        created_message = await MessageService.create_system_message(
            session=session,
            message_data=system_message_data,
        )
        message_response = SystemMessageResponse.model_validate(created_message)

        # Рассылка
        await WebsocketService._broadcast_to_chat_participants(
            chat_id=system_message_data.chat_id,
            chat_type=system_message_data.chat_type,
            message_response=message_response,
            session=session,
        )
        return message_response.model_dump_json()

    @staticmethod
    async def broadcast_typing_status(
        sender_user: Users,
        chat_id: UUID,
        chat_type: ChatType,
        is_typing: bool,
        session: AsyncSession,
    ):
        """Уведомить участников чата о статусе печатания"""
        await MessageService.check_user_is_member(
            user_id=sender_user.id,
            chat_id=chat_id,
            chat_type=chat_type,
            session=session,
        )

        sender_username = sender_user.username
        message_response = TypingStatusResponse(
            chat_id=chat_id,
            chat_type=chat_type,
            is_typing=is_typing,
            username=sender_username,
        )
        # Рассылка
        await WebsocketService._broadcast_to_chat_participants(
            chat_id=chat_id,
            chat_type=chat_type,
            message_response=message_response,
            session=session,
            sender_username=sender_username,
        )

    @staticmethod
    async def join_to_chat(
        sender_user: Users,
        chat_id: UUID,
        chat_type: ChatType,
        session: AsyncSession,
    ):
        """Войти в чат (находиться в сети чата)"""
        await MessageService.check_user_is_member(
            user_id=sender_user.id,
            chat_id=chat_id,
            chat_type=chat_type,
            session=session,
        )
        websocket_manager.set_user_chat(sender_user.username, chat_id, chat_type)
