from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Users, Groups, Messages
from src.crud import GroupCRUD, UserCRUD, MessageCRUD
from src.schemas import (
    ChatResponse,
    CreateGroupWithMembersRequest,
    GroupResponse,
    UserInGroupResponse,
    UpdateGroupRequest,
    AddGroupMembersRequest,
    UpdateMemberRoleRequest,
)
from src.schemas.enums import MessageType
from src.exceptions import (
    CreatorIsNotMemberError,
    RecurringMembersError,
    UserNotFoundError,
    GroupNotFoundError,
    UserIsNotGroupMemberError,
    UserIsNotGroupAdminError,
    MemberAlreadyExistsError,
    CannotModifyGroupCreatorError,
    GroupMemberNotFoundError,
    GroupIsPrivateError,
)
from src.services.file_service import FileService
from src.services.user_service import UserService


class GroupService:
    """Сервис групповых чатов"""

    @staticmethod
    async def get_group_by_id(group_id: UUID, session: AsyncSession) -> Groups:
        """Получение группы по id"""
        group = await GroupCRUD.get_group_by_id(group_id, session)
        if group is None:
            raise GroupNotFoundError()
        return group

    @staticmethod
    async def get_group_with_members(group_id: UUID, session: AsyncSession):
        """Получение группы с участниками"""
        group = await GroupCRUD.get_group_with_members(group_id, session)
        if group is None:
            raise GroupNotFoundError()
        return group

    @staticmethod
    async def check_user_in_group_members(
        user_id: UUID, group_id: UUID, session: AsyncSession
    ) -> bool:
        """Проверка, что пользователь является участником группы"""
        # проверка, что группа существует
        await GroupService.get_group_by_id(group_id, session)
        # проверка, является ли пользователь участником группы
        if not await GroupCRUD.check_member_group(
            group_id=group_id, user_id=user_id, session=session
        ):
            raise UserIsNotGroupMemberError()
        return True

    @staticmethod
    async def check_user_is_admin(
        user_id: UUID, group: Groups, session: AsyncSession
    ) -> None:
        """Проверка, что пользователь является админом группы"""
        is_admin = await GroupCRUD.check_admin_group(group.id, user_id, session)
        if not is_admin:
            raise UserIsNotGroupAdminError()

    @staticmethod
    async def get_groups_by_user(
        user: Users, session: AsyncSession
    ) -> list[ChatResponse]:
        """Получение всех групп, в которых состоит пользователь"""
        groups = await GroupCRUD.groups_by_user(user_id=user.id, session=session)
        chats = []
        for group in groups:
            unread_count = await MessageCRUD.unread_count_message_by_chat(
                group_id=group.id, user_id=user.id, session=session
            )
            chat = ChatResponse(
                id=group.id,
                title=group.title,
                avatar_url=group.avatar_url,
                last_message=group.last_message,
                unread_count_message=unread_count,
            )
            chats.append(chat)
        return chats

    @staticmethod
    async def get_group_members_username(
        group_id: UUID, session: AsyncSession
    ) -> set[str]:
        """Получение username-участников группы"""
        group = await GroupService.get_group_with_members(group_id, session)
        return {member.member.username for member in group.group_members}

    @staticmethod
    async def create_group(
        creator: Users,
        create_group_data: CreateGroupWithMembersRequest,
        avatar: UploadFile | None,
        session: AsyncSession,
    ) -> Groups:
        """Создание группы с участниками"""
        group_data = create_group_data.model_dump(exclude={"members"})
        group_data["created_by"] = creator.id

        # проверка, что создателя нет в участниках
        if creator.id in create_group_data.members:
            raise CreatorIsNotMemberError()
        # проверка, что все участники уникальны
        if len(create_group_data.members) != len(set(create_group_data.members)):
            raise RecurringMembersError()
        # проверка, что все участники (id) существуют
        if not await UserCRUD.check_users_exist(session, create_group_data.members):
            raise UserNotFoundError()

        new_group = await GroupCRUD.create_group(
            creator_id=creator.id,
            group_data=group_data,
            members_list=create_group_data.members,
            session=session,
        )

        # Сохраняем аву, если передана
        if avatar is not None:
            saved_url = await FileService.upload_group_avatar(
                group_id=new_group.id,
                avatar=avatar,
            )
            new_group = await GroupCRUD.update_group_avatar_url(
                group=new_group,
                avatar_url=saved_url,
                session=session,
            )
        return new_group

    @staticmethod
    async def update_group_last_message(
        group_id: UUID,
        last_message: Messages,
        session: AsyncSession,
    ):
        """Обновление последнего сообщения в группе"""
        group = await GroupService.get_group_by_id(group_id, session)
        await GroupCRUD.set_last_message(group, last_message, session)

    @staticmethod
    async def get_group_detail(
        user_id: UUID, group_id: UUID, session: AsyncSession
    ) -> GroupResponse:
        """Получение полной информации о группе"""
        group = await GroupService.get_group_with_members(group_id, session)
        if group.is_private:
            await GroupService.check_user_in_group_members(user_id, group_id, session)
        media = await GroupCRUD.get_group_media(group_id, session)

        members = []
        media_files = {"images": [], "voices": [], "files": []}
        for m in group.group_members:
            members.append(
                UserInGroupResponse(
                    username=m.member.username,
                    avatar_url=m.member.avatar_url,
                    is_online=m.member.is_online,
                    last_seen=m.member.last_seen,
                    role=m.role,
                )
            )

        for m in media:
            match m.type:
                case MessageType.IMAGE:
                    media_files["images"].append(m.file_url)
                case MessageType.VOICE:
                    media_files["voices"].append(m.file_url)
                case MessageType.FILE:
                    media_files["files"].append(m.file_url)

        return GroupResponse(
            id=group.id,
            title=group.title,
            is_private=group.is_private,
            description=group.description,
            avatar_url=group.avatar_url,
            created_at=group.created_at,
            members=members,
            media=media_files,
        )

    @staticmethod
    async def update_group_info(
        user: Users,
        group_id: UUID,
        update_data: UpdateGroupRequest,
        session: AsyncSession,
    ) -> Groups:
        """Обновление текстовой информации о группе (только админ)"""
        group = await GroupService.get_group_by_id(group_id, session)
        await GroupService.check_user_is_admin(user.id, group, session)

        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return group

        return await GroupCRUD.update_group(group, update_dict, session)

    @staticmethod
    async def update_group_avatar(
        user: Users,
        group_id: UUID,
        avatar: UploadFile,
        session: AsyncSession,
    ) -> Groups:
        """Обновление аватарки группы (только админ)"""
        group = await GroupService.get_group_by_id(group_id, session)
        await GroupService.check_user_is_admin(user.id, group, session)

        # Удаляем старую, сохраняем новую
        if group.avatar_url:
            await FileService.delete_group_avatar(group.avatar_url)
        avatar_group = await FileService.upload_group_avatar(
            group_id=group.id,
            avatar=avatar,
        )
        return await GroupCRUD.update_group_avatar_url(group, avatar_group, session)

    @staticmethod
    async def delete_group_avatar(
        user: Users,
        group_id: UUID,
        session: AsyncSession,
    ) -> Groups:
        """Удаление аватарки группы (только админ)"""
        group = await GroupService.get_group_by_id(group_id, session)
        await GroupService.check_user_is_admin(user.id, group, session)

        if group.avatar_url:
            await FileService.delete_group_avatar(group.avatar_url)
            group = await GroupCRUD.update_group_avatar_url(group, None, session)
        return group

    @staticmethod
    async def add_members(
        user: Users,
        group_id: UUID,
        data: AddGroupMembersRequest,
        session: AsyncSession,
    ) -> None:
        """Добавление участников (только админ)"""
        group = await GroupService.get_group_with_members(group_id, session)
        await GroupService.check_user_is_admin(user.id, group, session)
        # Проверяем, что пользователи существуют
        await UserService.check_users_exist(data.members, session)

        # Фильтруем тех, кто уже в группе
        existing_members = {m.user_id for m in group.group_members}
        for uid in data.members:
            if uid in existing_members:
                raise MemberAlreadyExistsError(uid)

        await GroupCRUD.add_members(group_id, data.members, session)

    @staticmethod
    async def remove_member(
        user: Users,
        group_id: UUID,
        target_user_id: UUID,
        session: AsyncSession,
    ) -> None:
        """Удаление участника (только админ)"""
        group = await GroupService.get_group_by_id(group_id, session)
        await GroupService.check_user_is_admin(user.id, group, session)

        # Проверяем, есть ли такой участник
        target_member = await GroupCRUD.get_group_member(
            group_id, target_user_id, session
        )
        if not target_member:
            raise GroupMemberNotFoundError()

        # Защита создателя
        if target_user_id == group.created_by:
            raise CannotModifyGroupCreatorError()

        await GroupCRUD.remove_member(group_id, target_user_id, session)

    @staticmethod
    async def update_member_role(
        user: Users,
        group_id: UUID,
        target_user_id: UUID,
        data: UpdateMemberRoleRequest,
        session: AsyncSession,
    ) -> None:
        """Изменение роли участника (только админ)"""
        group = await GroupService.get_group_by_id(group_id, session)
        await GroupService.check_user_is_admin(user.id, group, session)

        target_member = await GroupCRUD.get_group_member(
            group_id, target_user_id, session
        )
        if not target_member:
            raise GroupMemberNotFoundError()

        # Защита создателя
        if target_user_id == group.created_by:
            raise CannotModifyGroupCreatorError()

        await GroupCRUD.update_member_role(group_id, target_user_id, data.role, session)

    @staticmethod
    async def join_public_group(
        user: Users,
        group_id: UUID,
        session: AsyncSession,
    ) -> None:
        """Самостоятельное присоединение к публичной группе"""
        group = await GroupService.get_group_with_members(group_id, session)
        if group.is_private:
            raise GroupIsPrivateError()

        # Проверка, что ещё не в группе
        existing = await GroupCRUD.get_group_member(group_id, user.id, session)
        if existing:
            raise MemberAlreadyExistsError(user.id)

        await GroupCRUD.add_members(group_id, [user.id], session)

    @staticmethod
    async def leave_group(
        user: Users,
        group_id: UUID,
        session: AsyncSession,
    ) -> None:
        """Самостоятельный выход из группы"""
        group = await GroupService.get_group_by_id(group_id, session)

        member = await GroupCRUD.get_group_member(group_id, user.id, session)
        if not member:
            raise UserIsNotGroupMemberError()

        # Защита создателя
        if user.id == group.created_by:
            raise CannotModifyGroupCreatorError()

        await GroupCRUD.remove_member(group_id, user.id, session)

    # TODO:
    # Удаление группы
