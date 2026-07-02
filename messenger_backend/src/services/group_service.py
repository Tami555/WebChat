from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Users, Groups
from src.crud import groups as group_crud, users as user_crud
from src.schemas import Chat, CreateGroupWithMembers
from src.exceptions import CreatorIsNotMember, RecurringMembers, UserNotFoundError


class GroupService:
    """Сервис групповых чатов"""
    
    @staticmethod
    async def get_groups_by_user(user: Users, session: AsyncSession) -> list[Chat]:
        """Получение всех групп, в которых состоит пользователь"""
        groups = await group_crud.groups_by_user(user_id=user.id, session=session)
        chats = []
        for group in groups:
            unread_count = await group_crud.unread_count_for_message(group_id=group.id, user_id=user.id, session=session)
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
    async def create_group(creator: Users, create_group_data: CreateGroupWithMembers, session: AsyncSession) -> Groups:
        """Создание группы с участниками"""
        group_data = create_group_data.group.model_dump()
        group_data["created_by"] = creator.id

        # проверка, что создателя нет в участниках
        if creator.id in create_group_data.members:
            raise CreatorIsNotMember()
        # проверка, что все участники уникальны
        if len(create_group_data.members) != len(set(create_group_data.members)):
            raise RecurringMembers()
        # проверка, что все участники (id) существуют
        if not await user_crud.check_users_exist(session, create_group_data.members):
            raise UserNotFoundError()
        
        return await group_crud.create_group(
                creator_id=creator.id,
                group_data=group_data,
                members_list=create_group_data.members,
                session=session
            )

    # Добавление, удаление пользователей из группы
    # Изменение роли пользователя (нельзя лишить creater_user админства)
    # Редактирование группы (название, ава, т.д)
    # Удаление группы
    # Поиск по названию
    # Получение всей инфы
