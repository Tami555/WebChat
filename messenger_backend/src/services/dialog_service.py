from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Users, Dialogs, Messages
from src.crud import DialogCRUD, MessageCRUD
from src.schemas import Chat, CreateDialog
from src.exceptions import DialogAlreadyExistsError, DialogWithOneUserError, DialogNotFoundError, UserIsNotDialogInterlocutorError
from .user_service import UserService


class DialogService:
    """Сервис чатов для двоих (диалогов)"""
    @staticmethod
    async def get_dialog_by_id(dialog_id: UUID, session: AsyncSession) -> Dialogs:
        """Получение диалога по id"""
        dialog = await DialogCRUD.get_dialog_by_id(dialog_id, session)
        if dialog is None:
            raise DialogNotFoundError()
        return dialog

    @staticmethod
    async def check_user_is_dialog_interlocutor(
        user_id: UUID,
        dialog_id: UUID,
        session: AsyncSession
    ) -> bool:
        """Проверка, что пользователь является одним из собеседников диаолга"""
        # проверка что диалог существует
        dialog = await DialogService.get_dialog_by_id(dialog_id, session)
        # проверка, является ли пользователь одним из собеседников
        if dialog.user1_id != user_id and dialog.user2_id != user_id:
            raise UserIsNotDialogInterlocutorError()
        return True

    @staticmethod
    async def get_dialog_interlocutors_username(dialog_id: UUID, session: AsyncSession) -> set[str]:
        """Получение username-ов участников диалога"""
        dialog = await DialogCRUD.get_dialog_by_id_with_relationships(dialog_id, session)
        return {dialog.user1.username, dialog.user2.username}

    @staticmethod
    async def get_dialogs_by_user(user: Users, session: AsyncSession) -> list[Chat]:
        """Получение всех чатов-диалогов, в которых состоит пользователь"""
        dialogs = await DialogCRUD.dialogs_by_user(user_id=user.id, session=session)
        chats = []
        for dialog in dialogs:
            unread_count = await MessageCRUD.unread_count_message_by_chat(dialog_id=dialog.id, user_id=user.id, session=session)
            interlocutor = dialog.user2 if dialog.user1_id == user.id else dialog.user1 # TODO: кастомное имя
            chat = Chat(
                id=dialog.id,
                title=interlocutor.first_name or interlocutor.username,
                avatar_url=interlocutor.avatar_url,
                last_message=dialog.last_message,
                unread_count_message=unread_count
            )
            chats.append(chat)
        return chats
    
    @staticmethod
    async def create_dialog(creator: Users, dialog_data: CreateDialog, session: AsyncSession) -> Dialogs:
        """Создание диалога"""
        # проверка что собеседник не равен автору
        if creator.id == dialog_data.interlocutor:
            raise DialogWithOneUserError()
        # проверка существования собеседника
        await UserService.get_user_by_id(user_id=dialog_data.interlocutor, session=session)
        # проверка на уже имеющийся диалог
        if await DialogCRUD.get_dialog_between_users(user1_id=creator.id, user2_id=dialog_data.interlocutor, session=session) is not None:
            raise DialogAlreadyExistsError()

        new_dialog = await DialogCRUD.create_dialog(
            creator_id=creator.id,
            interlocutor_id=dialog_data.interlocutor,
            session=session
        )
        return await DialogCRUD.get_dialog_by_id_with_relationships(new_dialog.id, session)

    @staticmethod
    async def update_dialog_last_message(
        dialog_id: UUID,
        last_message: Messages,
        session: AsyncSession
    ):
        """Обновление последнего сообщения в диалоге"""
        dialog = await DialogService.get_dialog_by_id(dialog_id, session)
        await DialogCRUD.set_last_message(dialog, last_message, session)

    # Удаление
    # Получение всей инфы