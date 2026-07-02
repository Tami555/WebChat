from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import messages as msg_crud, dialogs as dialogs_crud, groups as group_crud
from src.models import Messages, Users
from src.schemas.enums import ChatTypes
from src.exceptions import DialogNotFoundError, UserIsNotDialogInterlocutor, GroupNotFoundError, UserIsNotGroupMember


class MessageService:
    """Сервис для управления сообщениями"""

    @staticmethod
    async def get_messages_by_dialog(
        user: Users,
        dialog_id: UUID,
        page: int,
        limit: int,
        session: AsyncSession
    ) -> list[Messages]:
        """Получение сообщений диалога с пагинацией"""

        # проверка что диалог существует
        dialog = await dialogs_crud.get_dialog_by_id(dialog_id, session)
        if dialog is None:
            raise DialogNotFoundError()
        # проверка, является ли пользователь одним из собеседников
        if dialog.user1_id != user.id and dialog.user2_id != user.id:
            raise UserIsNotDialogInterlocutor()

        messages = await msg_crud.messages_by_dialog_or_group(
            dialog_id = dialog_id,
            page = page,
            limit = limit,
            session = session
        )
        return messages
    
    @staticmethod
    async def get_messages_by_group(
        user: Users,
        group_id: UUID,
        page: int,
        limit: int,
        session: AsyncSession
    ) -> list[Messages]:
        """Получение сообщений группы с пагинацией"""
        
        # проверка что группа существует
        group = await group_crud.get_group_by_id(group_id, session)
        if group is None:
            raise GroupNotFoundError()
        
        # проверка, является ли пользователь участником группы
        if not group_crud.check_member_group(group_id=group_id, user_id=user.id, session=session):
            raise UserIsNotGroupMember()

        messages = await msg_crud.messages_by_dialog_or_group(
            group_id = group_id,
            page = page,
            limit = limit,
            session = session
        )
        return messages
    
    @staticmethod
    async def get_messages_by_chat(
        user: Users,
        chat_id: UUID,
        chat_type: ChatTypes,
        page: int,
        limit: int,
        session: AsyncSession
    ) -> list[Messages]:
        """Получение сообщений чата по типу (группа или диалог) с пагинацией"""
        match chat_type:
            case ChatTypes.DIALOGS:
                return await MessageService.get_messages_by_dialog(
                    user=user,
                    dialog_id=chat_id,
                    page=page,
                    limit=limit,
                    session=session
                )
            case ChatTypes.GROUP:
                return await MessageService.get_messages_by_group(
                    user=user,
                    group_id=chat_id,
                    page=page,
                    limit=limit,
                    session=session
                )
            case _:
                return []