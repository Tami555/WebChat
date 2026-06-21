from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Users
from src.crud import groups as crud
from src.schemas import Chat


class GroupService:
    """Сервис групповых чатов"""
    
    @staticmethod
    async def get_groups_by_user(user: Users, session: AsyncSession) -> list[Chat]:
        """Получение всех групп, в которых состоит пользователь"""
        groups = await crud.groups_by_user(user_id=user.id, session=session)
        chats = []
        for group in groups:
            unread_count = await crud.unread_count_for_message(group_id=group.id, user_id=user.id, session=session)
            chat = Chat(
                id=group.id,
                title=group.title,
                avatar_url=group.avatar_url,
                last_message=group.last_message,
                unread_count_message=unread_count
            )
            chats.append(chat)
        return chats
    
    @staticmethod
    async def create_group(user: Users, session: AsyncSession):
        pass

    # Создание группы С пользователями
    # Добавление, удаление пользователей из группы
    # Изменение роли пользователя (нельзя лишить creater_user админства)
    # Редактирование группы (название, ава, т.д)
    # Удаление группы
    # Поиск по названию
