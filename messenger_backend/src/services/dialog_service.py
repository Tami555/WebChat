from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Users
from src.crud import dialogs as crud
from src.schemas import Chat


class DialogService:
    """Сервис чатов для двоих (диалогов)"""
    
    @staticmethod
    async def get_dialogs_by_user(user: Users, session: AsyncSession) -> list[Chat]:
        """Получение всех чатов-диалогов, в которых состоит пользователь"""
        dialogs = await crud.dialogs_by_user(user_id=user.id, session=session)
        print("ДИАЛОГИ", dialogs)
        chats = []
        for dialog in dialogs:
            unread_count = await crud.unread_count_for_message(dialog_id=dialog.id, user_id=user.id, session=session)
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
    
    # Создание чата, Удаление