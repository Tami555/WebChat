import pytest
from uuid import uuid4
from datetime import datetime
from httpx import AsyncClient

from src.schemas import ChatResponse, ShortGroupResponse, GroupResponse
from src.schemas.enums import GroupMemberRole
from src.models import Groups, GroupMembers, Messages

from tests.helpers.assertions import (
    HttpAssertions,
    DatabaseAssertions,
    GroupDatabaseAssertions,
)
from tests.helpers.url_builder import url_builder
from tests.fixtures.data import UserDataFactory, GroupsDataFactory
from tests.helpers.factories import FileFactory


class TestGroups:
    """Тесты групп"""

    # URLs
    get_groups_url = url_builder.groups("chats")
    create_group_url = url_builder.groups("create")

    @staticmethod
    def get_group_detail_url(group_id):
        return url_builder.groups(str(group_id))

    @staticmethod
    def update_group_url(group_id):
        return url_builder.groups(str(group_id))

    @staticmethod
    def delete_group_url(group_id):
        return url_builder.groups(str(group_id))

    @staticmethod
    def add_members_url(group_id):
        return url_builder.groups(str(group_id), "members")

    @staticmethod
    def delete_member_url(group_id, user_id):
        return url_builder.groups(str(group_id), "members", str(user_id))

    @staticmethod
    def update_member_role_url(group_id, user_id):
        return url_builder.groups(str(group_id), "members", str(user_id), "role")

    @staticmethod
    def get_transfer_owner_url(group_id):
        return url_builder.groups(str(group_id), "transfer-owner")

    @staticmethod
    def get_join_url(group_id):
        return url_builder.groups(str(group_id), "join")

    @staticmethod
    def get_leave_url(group_id):
        return url_builder.groups(str(group_id), "leave")

    class TestGetGroups:
        """Тесты получения списка групп"""

        @pytest.mark.asyncio
        async def test_get_groups_empty(self, auth_client_user_1):
            """Тест: получение списка групп у пользователя без групп"""
            response = await auth_client_user_1.get(TestGroups.get_groups_url)
            data = HttpAssertions.assert_success_response(
                response=response, response_model=ChatResponse, is_list=True
            )
            assert data == []

        @pytest.mark.asyncio
        async def test_get_groups_with_one_group(
            self,
            auth_client_user_1,
            created_group_user1_user2_user3,
        ):
            """Тест: получение списка групп с одной группой"""
            response = await auth_client_user_1.get(TestGroups.get_groups_url)
            data = HttpAssertions.assert_success_response(
                response=response, response_model=ChatResponse, is_list=True
            )
            assert len(data) == 1
            group = data[0]
            assert group.id == created_group_user1_user2_user3.id
            assert group.unread_count_message == 0
            assert group.last_message is None
            assert group.title == "Test Group"

        @pytest.mark.asyncio
        async def test_get_groups_with_two_groups(
            self,
            auth_client_user_1,
            created_group_user1_user2_user3,
            created_group_user1_user3,
        ):
            """Тест: получение списка групп с двумя группами"""
            response = await auth_client_user_1.get(TestGroups.get_groups_url)
            data = HttpAssertions.assert_success_response(
                response=response, response_model=ChatResponse, is_list=True
            )

            assert len(data) == 2
            group_ids = [g.id for g in data]
            assert created_group_user1_user2_user3.id in group_ids
            assert created_group_user1_user3.id in group_ids

        @pytest.mark.asyncio
        async def test_get_groups_with_unread_messages(
            self,
            auth_client_user_2,
            created_not_read_message_statuses_in_group_1_2_3,
        ):
            """Тест: получение списка групп с непрочитанным сообщением"""
            response = await auth_client_user_2.get(TestGroups.get_groups_url)
            data = HttpAssertions.assert_success_response(
                response=response, response_model=ChatResponse, is_list=True
            )

            assert len(data) == 1
            group = data[0]
            assert group.unread_count_message == 1
            assert group.last_message is not None
            assert group.last_message.content == "Hello from user 1 in group!"

        @pytest.mark.asyncio
        async def test_get_groups_with_read_messages(
            self,
            auth_client_user_2,
            created_read_message_statuses_in_group_1_2_3,
        ):
            """Тест: получение списка групп с прочитанным сообщением"""
            response = await auth_client_user_2.get(TestGroups.get_groups_url)
            data = HttpAssertions.assert_success_response(
                response=response, response_model=ChatResponse, is_list=True
            )

            assert len(data) == 1
            group = data[0]
            assert group.unread_count_message == 0
            assert group.last_message is not None
            assert group.last_message.content == "Hello from user 1 in group!"

        @pytest.mark.asyncio
        async def test_get_groups_unauthorized_error(self, client):
            """Тест: получение групп без авторизации"""
            response = await client.get(TestGroups.get_groups_url)

            HttpAssertions.assert_unauthorized_error(
                response=response,
                expected_message="Вы не авторизованы! Войдите пожалуйста в аккаунт",
            )

        @pytest.mark.asyncio
        async def test_get_groups_with_invalid_token(self, client):
            """Тест: получение групп с невалидным токеном"""
            client.headers["Authorization"] = "Bearer invalid_token"
            response = await client.get(TestGroups.get_groups_url)

            HttpAssertions.assert_unauthorized_error(
                response=response,
                expected_message="Невалидный токен",
            )

    class TestCreateGroup:
        """Тесты создания группы"""

        @pytest.mark.asyncio
        async def test_create_group_success(
            self,
            auth_client_user_1,
            created_user_1,
            created_user_2,
            created_user_3,
            test_db,
        ):
            """Тест: успешное создание группы с участниками (без аватарки)"""
            members = [created_user_2.id, created_user_3.id]

            data = GroupsDataFactory.group_form_data(
                members=[str(m) for m in members],
            )

            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                data=data,
            )

            group_data = HttpAssertions.assert_success_response(
                response=response,
                response_model=ShortGroupResponse,
            )

            assert group_data.id is not None
            assert group_data.title == "Test Group"
            assert group_data.is_private is False

            async for session in test_db.create_session():
                group = await GroupDatabaseAssertions.assert_group_exists(
                    session=session,
                    group_id=group_data.id,
                    expected_title="Test Group",
                    expected_created_by=created_user_1.id,
                )
                assert group.avatar_url is None

                all_members = [created_user_1.id] + members
                for user_id in all_members:
                    await GroupDatabaseAssertions.assert_member_in_group(
                        session=session, group_id=group.id, user_id=user_id
                    )

        @pytest.mark.asyncio
        async def test_create_group_with_creator_in_members(
            self,
            auth_client_user_1,
            created_user_1,
            created_user_2,
        ):
            """Тест: создание группы, где создатель указан в участниках"""
            data = GroupsDataFactory.group_form_data(
                members=[str(created_user_1.id), str(created_user_2.id)],
            )

            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                data=data,
            )

            HttpAssertions.assert_error_response(
                response=response,
                expected_message="Создатель группы не может указываться в качестве участника, т.к он по умолчанию является Админом",
                expected_status=422,
            )

        @pytest.mark.asyncio
        async def test_create_group_with_recurring_members(
            self,
            auth_client_user_1,
            created_user_2,
            created_user_3,
        ):
            """Тест: создание группы с повторяющимися участниками"""
            data = GroupsDataFactory.group_form_data(
                members=[
                    str(created_user_2.id),
                    str(created_user_3.id),
                    str(created_user_2.id),
                ],
            )

            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                data=data,
            )

            HttpAssertions.assert_error_response(
                response=response,
                expected_message="Участники не могут повторяться",
                expected_status=409,
            )

        @pytest.mark.asyncio
        async def test_create_group_with_non_existent_user(
            self,
            auth_client_user_1,
            created_user_2,
        ):
            """Тест: создание группы с несуществующим пользователем"""
            non_existent_id = uuid4()
            data = GroupsDataFactory.group_form_data(
                members=[str(created_user_2.id), str(non_existent_id)],
            )

            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                data=data,
            )

            HttpAssertions.assert_not_found_error(
                response=response,
                expected_message="Пользователь не найден",
            )

        @pytest.mark.asyncio
        async def test_create_group_unauthorized(
            self,
            client,
            created_user_2,
            created_user_3,
        ):
            """Тест: создание группы без авторизации"""
            data = GroupsDataFactory.group_form_data(
                members=[str(created_user_2.id), str(created_user_3.id)],
            )

            response = await client.post(
                TestGroups.create_group_url,
                data=data,
            )

            HttpAssertions.assert_unauthorized_error(
                response=response,
                expected_message="Вы не авторизованы! Войдите пожалуйста в аккаунт",
            )

        @pytest.mark.asyncio
        async def test_create_group_invalid_token(
            self,
            client,
            created_user_2,
            created_user_3,
        ):
            """Тест: создание группы с невалидным токеном"""
            client.headers["Authorization"] = "Bearer invalid_token"
            data = GroupsDataFactory.group_form_data(
                members=[str(created_user_2.id), str(created_user_3.id)],
            )

            response = await client.post(
                TestGroups.create_group_url,
                data=data,
            )

            HttpAssertions.assert_unauthorized_error(
                response=response,
                expected_message="Невалидный токен",
            )

        @pytest.mark.asyncio
        async def test_create_group_missing_title(
            self,
            auth_client_user_1,
            created_user_2,
            created_user_3,
        ):
            """Тест: создание группы без заголовка (422)"""
            data = {
                "description": "Test group description",
                "is_private": "false",
                "members": [str(created_user_2.id), str(created_user_3.id)],
            }

            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                data=data,
            )
            HttpAssertions.assert_validation_error(response)

        @pytest.mark.asyncio
        async def test_create_group_missing_members_success(
            self, auth_client_user_1, created_user_1, test_db
        ):
            """Тест: создание группы без участников — успех"""
            data = GroupsDataFactory.group_form_data(members=[])

            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                data=data,
            )

            group_data = HttpAssertions.assert_success_response(
                response=response,
                response_model=ShortGroupResponse,
            )

            async for session in test_db.create_session():
                await GroupDatabaseAssertions.assert_group_exists(
                    session=session,
                    group_id=group_data.id,
                    expected_title="Test Group",
                    expected_created_by=created_user_1.id,
                )

        @pytest.mark.asyncio
        async def test_create_group_wrong_member_type(
            self,
            auth_client_user_1,
        ):
            """Тест: создание группы с невалидным UUID в members"""
            data = GroupsDataFactory.group_form_data(
                members=["not-a-uuid"],
            )

            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                data=data,
            )

            HttpAssertions.assert_validation_error(
                response=response,
                expected_message="Невалидные данные  !!!",
            )

        @pytest.mark.asyncio
        async def test_create_private_group_success(
            self,
            auth_client_user_1,
            created_user_1,
            created_user_2,
            created_user_3,
            test_db,
        ):
            """Тест: создание приватной группы"""
            data = GroupsDataFactory.group_form_data(
                title="Private Group",
                is_private=True,
                members=[str(created_user_2.id), str(created_user_3.id)],
            )

            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                data=data,
            )

            group_data = HttpAssertions.assert_success_response(
                response=response,
                response_model=ShortGroupResponse,
            )

            assert group_data.id is not None
            assert group_data.title == "Private Group"
            assert group_data.is_private is True

            async for session in test_db.create_session():
                group = await GroupDatabaseAssertions.assert_group_exists(
                    session=session,
                    group_id=group_data.id,
                    expected_title="Private Group",
                    expected_created_by=created_user_1.id,
                )
                assert group.is_private is True

        @pytest.mark.asyncio
        async def test_create_group_with_avatar_success(
            self,
            created_user_1,
            auth_client_user_1,
            created_user_2,
            test_image_file,
            test_db,
        ):
            """Тест: создание группы с аватаркой"""
            data = GroupsDataFactory.group_form_data(
                members=[str(created_user_2.id)],
            )

            with open(test_image_file, "rb") as f:
                files = {"avatar": ("avatar.jpg", f, "image/jpeg")}
                response = await auth_client_user_1.post(
                    TestGroups.create_group_url,
                    data=data,
                    files=files,
                )

            group_data = HttpAssertions.assert_success_response(
                response=response,
                response_model=ShortGroupResponse,
            )

            # Проверяем, что ава сохранена в БД
            async for session in test_db.create_session():
                group = await GroupDatabaseAssertions.assert_group_exists(
                    session=session,
                    group_id=group_data.id,
                    expected_title="Test Group",
                    expected_created_by=created_user_1.id,
                )
                assert group.avatar_url is not None

            # Очищаем сохранённый файл
            FileFactory.cleanup_group_avatar(group_data.id)

        @pytest.mark.asyncio
        async def test_create_group_with_invalid_avatar(
            self,
            auth_client_user_1,
            created_user_2,
            test_text_file,
        ):
            """Тест: создание группы с невалидной аватаркой (не картинка)"""
            data = GroupsDataFactory.group_form_data(
                members=[str(created_user_2.id)],
            )

            with open(test_text_file, "rb") as f:
                files = {"avatar": ("file.txt", f, "text/plain")}
                response = await auth_client_user_1.post(
                    TestGroups.create_group_url,
                    data=data,
                    files=files,
                )

            HttpAssertions.assert_error_response(
                response=response,
                expected_message="Аватар должен быть изображением, получен: text/plain",
                expected_status=415,
            )

    class TestGetGroupDetail:
        """Тесты получения полной информации о группе"""

        class TestPrivateGroup:
            """Тесты для приватной группы"""

            @pytest.mark.asyncio
            async def test_get_private_group_success(
                self,
                created_user_1,
                created_user_3,
                auth_client_user_1,
                created_private_group_user1_user3,
            ):
                """Тест: получение инфы о приватной группе (админ)"""
                from src.schemas import GroupResponse

                group_id = created_private_group_user1_user3.id
                response = await auth_client_user_1.get(
                    TestGroups.get_group_detail_url(group_id)
                )

                data = HttpAssertions.assert_success_response(
                    response=response,
                    response_model=GroupResponse,
                )

                assert data.id == group_id
                assert data.title == "Private Group"
                assert data.is_private is True
                assert data.description == "Private group desc"

                # Проверяем участников
                assert len(data.members) == 2

                # Проверяем роли
                admin = next(
                    m for m in data.members if m.username == created_user_1.username
                )
                assert admin.role.value == "admin"
                member = next(
                    m for m in data.members if m.username == created_user_3.username
                )
                assert member.role.value == "member"

            @pytest.mark.asyncio
            async def test_get_private_group_success_as_member(
                self,
                auth_client_user_3,
                created_private_group_user1_user3,
            ):
                """Тест: участник (member) тоже может получить инфу"""
                from src.schemas import GroupResponse

                group_id = created_private_group_user1_user3.id
                response = await auth_client_user_3.get(
                    TestGroups.get_group_detail_url(group_id)
                )

                data = HttpAssertions.assert_success_response(
                    response=response,
                    response_model=GroupResponse,
                )
                assert data.id == group_id

            @pytest.mark.asyncio
            async def test_get_private_group_not_member(
                self,
                auth_client_user_2,
                created_private_group_user1_user3,
            ):
                """Тест: НЕ участник не может получить инфу о приватной группе"""
                group_id = created_private_group_user1_user3.id
                response = await auth_client_user_2.get(
                    TestGroups.get_group_detail_url(group_id)
                )

                HttpAssertions.assert_error_response(
                    response=response,
                    expected_message="Вы не являетесь участником группы",
                    expected_status=403,
                )

        class TestPublicGroup:
            """Тесты для публичной группы"""

            @pytest.mark.asyncio
            async def test_get_public_group_success_as_member(
                self,
                auth_client_user_1,
                created_group_user1_user3,
            ):
                """Тест: участник получает инфу о публичной группе"""
                group_id = created_group_user1_user3.id
                response = await auth_client_user_1.get(
                    TestGroups.get_group_detail_url(group_id)
                )

                data = HttpAssertions.assert_success_response(
                    response=response,
                    response_model=GroupResponse,
                )

                assert data.id == group_id
                assert data.is_private is False

            @pytest.mark.asyncio
            async def test_get_public_group_success_as_non_member(
                self,
                auth_client_user_2,
                created_group_user1_user3,
            ):
                """Тест: НЕ участник может получить инфу о публичной группе"""
                group_id = created_group_user1_user3.id
                response = await auth_client_user_2.get(
                    TestGroups.get_group_detail_url(group_id)
                )

                data = HttpAssertions.assert_success_response(
                    response=response,
                    response_model=GroupResponse,
                )
                assert data.id == group_id
                assert data.is_private is False

        class TestCommon:
            """Общие тесты для типов групп"""

            @pytest.mark.asyncio
            async def test_get_group_not_exists(
                self,
                auth_client_user_1,
            ):
                """Тест: получение инфы о несуществующей группе"""
                non_existent_id = uuid4()
                response = await auth_client_user_1.get(
                    TestGroups.get_group_detail_url(non_existent_id)
                )
                HttpAssertions.assert_not_found_error(
                    response=response,
                    expected_message="Группа не найдена",
                )

            @pytest.mark.asyncio
            async def test_get_group_invalid_uuid(
                self,
                auth_client_user_1,
            ):
                """Тест: невалидный UUID в path"""
                response = await auth_client_user_1.get(
                    url_builder.groups("not-a-uuid")
                )
                HttpAssertions.assert_validation_error(response)

            @pytest.mark.asyncio
            async def test_get_public_group_success_unauthorized(
                self,
                client,
                created_group_user1_user3,
            ):
                """Тест: неавторизованный не может получить инфу (даже о публичной)"""
                group_id = created_group_user1_user3.id
                response = await client.get(TestGroups.get_group_detail_url(group_id))

                HttpAssertions.assert_unauthorized_error(
                    response=response,
                    expected_message="Вы не авторизованы! Войдите пожалуйста в аккаунт",
                )

            @pytest.mark.asyncio
            async def test_get_group_invalid_token(
                self,
                client,
                created_private_group_user1_user3,
            ):
                """Тест: невалидный токен"""
                client.headers["Authorization"] = "Bearer invalid_token"
                group_id = created_private_group_user1_user3.id
                response = await client.get(TestGroups.get_group_detail_url(group_id))

                HttpAssertions.assert_unauthorized_error(
                    response=response,
                    expected_message="Невалидный токен",
                )

    class TestUpdateGroup:
        """Тесты редактирования информации о группе"""

        @pytest.mark.asyncio
        async def test_update_title_only_success(
            self,
            auth_client_user_1,
            created_group_user1_user2_user3,
            test_db,
        ):
            """Тест: обновление только названия"""
            group_id = created_group_user1_user2_user3.id
            data = GroupsDataFactory.update_group_json(title="New Title Only")

            response = await auth_client_user_1.patch(
                TestGroups.update_group_url(group_id),
                json=data,
            )
            HttpAssertions.assert_success_response(response, ShortGroupResponse)

            async for session in test_db.create_session():
                await GroupDatabaseAssertions.assert_group_updated(
                    session=session,
                    group_id=group_id,
                    expected_title="New Title Only",
                    expected_description="Test group description",
                    expected_is_private=False,
                )

        @pytest.mark.asyncio
        async def test_update_all_fields_success(
            self,
            auth_client_user_1,
            created_group_user1_user2_user3,
            test_db,
        ):
            """Тест: обновление всех полей группы"""
            group_id = created_group_user1_user2_user3.id
            data = GroupsDataFactory.update_group_json(
                title="Totally New",
                description="New Description",
                is_private=True,
            )

            response = await auth_client_user_1.patch(
                TestGroups.update_group_url(group_id),
                json=data,
            )
            HttpAssertions.assert_success_response(response, ShortGroupResponse)

            async for session in test_db.create_session():
                await GroupDatabaseAssertions.assert_group_updated(
                    session=session,
                    group_id=group_id,
                    expected_title="Totally New",
                    expected_description="New Description",
                    expected_is_private=True,
                )

        @pytest.mark.asyncio
        async def test_update_empty_title(
            self,
            auth_client_user_1,
            created_group_user1_user2_user3,
        ):
            """Тест: попытка установить пустое название"""
            group_id = created_group_user1_user2_user3.id
            data = GroupsDataFactory.update_group_json(title="   ")

            response = await auth_client_user_1.patch(
                TestGroups.update_group_url(group_id),
                json=data,
            )
            HttpAssertions.assert_validation_error(response)

        @pytest.mark.asyncio
        async def test_update_not_admin(
            self,
            auth_client_user_2,
            created_group_user1_user2_user3,
        ):
            """Тест: попытка обновить группу не админом (1 - админ, 2 - участник)"""
            group_id = created_group_user1_user2_user3.id
            data = GroupsDataFactory.update_group_json(title="Hacked")

            response = await auth_client_user_2.patch(
                TestGroups.update_group_url(group_id),
                json=data,
            )

            HttpAssertions.assert_error_response(
                response=response,
                expected_message="Только администратор группы может выполнять это действие",
                expected_status=403,
            )

        @pytest.mark.asyncio
        async def test_update_group_not_found(
            self,
            auth_client_user_1,
        ):
            """Тест: обновление несуществующей группы"""
            data = GroupsDataFactory.update_group_json(title="Ghost")

            response = await auth_client_user_1.patch(
                TestGroups.update_group_url(uuid4()),
                json=data,
            )

            HttpAssertions.assert_not_found_error(
                response=response,
                expected_message="Группа не найдена",
            )

        @pytest.mark.asyncio
        async def test_update_unauthorized(
            self,
            client,
            created_group_user1_user2_user3,
        ):
            """Тест: обновление без авторизации -> 401"""
            group_id = created_group_user1_user2_user3.id
            data = GroupsDataFactory.update_group_json(title="Anon")

            response = await client.patch(
                TestGroups.update_group_url(group_id),
                json=data,
            )

            HttpAssertions.assert_unauthorized_error(
                response=response,
                expected_message="Вы не авторизованы! Войдите пожалуйста в аккаунт",
            )

    class TestGroupMembers:
        """Тесты управления участниками группы"""

        class TestAddMembers:
            """Тесты на добавление участников в группу"""

            @pytest.mark.asyncio
            async def test_add_members_success(
                self,
                redis_connect,
                auth_client_user_1,
                created_group_user1_user3,
                created_user_2,
                test_db,
            ):
                """Тест: успешное добавление участников админом"""

                data = GroupsDataFactory.add_members_json([str(created_user_2.id)])
                response = await auth_client_user_1.post(
                    TestGroups.add_members_url(created_group_user1_user3.id),
                    json=data,
                )

                HttpAssertions.assert_success_response(response, dict)

                async for session in test_db.create_session():
                    await GroupDatabaseAssertions.assert_member_in_group(
                        session, created_group_user1_user3.id, created_user_2.id
                    )
                    # Проверка системного сообщения
                    await GroupDatabaseAssertions.assert_group_last_message_is_system(
                        session,
                        created_group_user1_user3.id,
                        f"{created_user_2.username} добавлен(а) в группу",
                    )

            @pytest.mark.asyncio
            async def test_add_members_not_admin(
                self,
                auth_client_user_3,  # Простой участник
                created_group_user1_user3,
                created_user_2,
            ):
                """Тест: добавление участников не админом"""
                data = GroupsDataFactory.add_members_json([str(created_user_2.id)])
                response = await auth_client_user_3.post(
                    TestGroups.add_members_url(created_group_user1_user3.id),
                    json=data,
                )
                HttpAssertions.assert_error_response(
                    response,
                    "Только администратор группы может выполнять это действие",
                    403,
                )

            @pytest.mark.asyncio
            async def test_add_members_already_exists(
                self,
                auth_client_user_1,
                group_with_roles,
                created_user_2,
            ):
                """Тест: добавление того, кто уже в группе"""
                data = GroupsDataFactory.add_members_json([str(created_user_2.id)])
                response = await auth_client_user_1.post(
                    TestGroups.add_members_url(group_with_roles.id),
                    json=data,
                )
                HttpAssertions.assert_error_response(
                    response,
                    f"Участник с таким {created_user_2.id} уже есть в группе",
                    409,
                )

            @pytest.mark.asyncio
            async def test_add_members_user_not_found(
                self,
                auth_client_user_1,
                group_with_roles,
            ):
                """Тест: добавление несуществующего пользователя"""
                data = GroupsDataFactory.add_members_json([str(uuid4())])
                response = await auth_client_user_1.post(
                    TestGroups.add_members_url(group_with_roles.id),
                    json=data,
                )
                HttpAssertions.assert_not_found_error(
                    response, "Пользователь не найден"
                )

            @pytest.mark.asyncio
            async def test_add_members_group_not_found(
                self,
                auth_client_user_1,
            ):
                """Тест: добавление участников в несуществующую группу"""
                data = GroupsDataFactory.add_members_json([str(uuid4())])

                response = await auth_client_user_1.post(
                    TestGroups.add_members_url(uuid4()),
                    json=data,
                )
                HttpAssertions.assert_not_found_error(response, "Группа не найдена")

        class TestRemoveMember:
            """Тесты на удаление участников из группы"""

            @pytest.mark.asyncio
            async def test_remove_member_success(
                self,
                redis_connect,
                auth_client_user_1,  # Главный админ
                group_with_roles,
                created_user_3,  # Простой участник
                test_db,
            ):
                """Тест: успешное удаление участника админом"""
                response = await auth_client_user_1.delete(
                    TestGroups.delete_member_url(group_with_roles.id, created_user_3.id)
                )
                HttpAssertions.assert_success_response(response, dict)

                async for session in test_db.create_session():
                    await GroupDatabaseAssertions.assert_member_not_in_group(
                        session, group_with_roles.id, created_user_3.id
                    )
                    # Проверка системного сообщения
                    await GroupDatabaseAssertions.assert_group_last_message_is_system(
                        session,
                        group_with_roles.id,
                        f"{created_user_3.username} исключен(а) из группы",
                    )

            @pytest.mark.asyncio
            async def test_remove_other_admin_success(
                self,
                redis_connect,
                auth_client_user_1,  # Главный админ
                group_with_roles,
                created_user_2,  # Другой админ
                test_db,
            ):
                """Тест: админ может удалить другого админа (не создателя)"""
                response = await auth_client_user_1.delete(
                    TestGroups.delete_member_url(group_with_roles.id, created_user_2.id)
                )
                HttpAssertions.assert_success_response(response, dict)

                async for session in test_db.create_session():
                    await GroupDatabaseAssertions.assert_member_not_in_group(
                        session, group_with_roles.id, created_user_2.id
                    )
                    # Проверка системного сообщения
                    await GroupDatabaseAssertions.assert_group_last_message_is_system(
                        session,
                        group_with_roles.id,
                        f"{created_user_2.username} исключен(а) из группы",
                    )

            @pytest.mark.asyncio
            async def test_remove_creator_fail(
                self,
                auth_client_user_2,  # Назначенный админ
                group_with_roles,
                created_user_1,  # Создатель
            ):
                """Тест: нельзя удалить создателя группы"""
                response = await auth_client_user_2.delete(
                    TestGroups.delete_member_url(group_with_roles.id, created_user_1.id)
                )
                HttpAssertions.assert_error_response(
                    response, "Нельзя изменить роль или удалить создателя группы", 403
                )

            @pytest.mark.asyncio
            async def test_remove_member_not_admin(
                self,
                auth_client_user_3,  # Простой участник
                group_with_roles,
                created_user_2,
            ):
                """Тест: удаление участника не админом"""
                response = await auth_client_user_3.delete(
                    TestGroups.delete_member_url(group_with_roles.id, created_user_2.id)
                )
                HttpAssertions.assert_error_response(
                    response,
                    "Только администратор группы может выполнять это действие",
                    403,
                )

            @pytest.mark.asyncio
            async def test_remove_member_not_in_group(
                self,
                auth_client_user_1,
                group_with_roles,
            ):
                """Тест: удаление пользователя, которого нет в группе"""
                response = await auth_client_user_1.delete(
                    TestGroups.delete_member_url(group_with_roles.id, uuid4())
                )
                HttpAssertions.assert_not_found_error(
                    response, "Участник не найден в этой группе"
                )

    class TestUpdateMemberRole:
        """Тесты на редактирование ролей участников группы"""

        @pytest.mark.asyncio
        async def test_update_role_to_admin_success(
            self,
            auth_client_user_1,
            group_with_roles,
            created_user_3,  # Простой участник
            test_db,
        ):
            """Тест: повышение участника до админа"""
            from tests.helpers.assertions import GroupDatabaseAssertions

            data = GroupsDataFactory.update_role_json("admin")
            response = await auth_client_user_1.put(
                TestGroups.update_member_role_url(
                    group_with_roles.id, created_user_3.id
                ),
                json=data,
            )
            HttpAssertions.assert_success_response(response, dict)

            async for session in test_db.create_session():
                await GroupDatabaseAssertions.assert_member_role(
                    session,
                    group_with_roles.id,
                    created_user_3.id,
                    GroupMemberRole.ADMIN,
                )

        @pytest.mark.asyncio
        async def test_update_role_to_member_success(
            self,
            auth_client_user_1,  # Главный админ
            group_with_roles,
            created_user_2,  # Другой админ
            test_db,
        ):
            """Тест: понижение другого админа до участника"""
            data = GroupsDataFactory.update_role_json("member")
            response = await auth_client_user_1.put(
                TestGroups.update_member_role_url(
                    group_with_roles.id, created_user_2.id
                ),
                json=data,
            )
            HttpAssertions.assert_success_response(response, dict)

            async for session in test_db.create_session():
                await GroupDatabaseAssertions.assert_member_role(
                    session,
                    group_with_roles.id,
                    created_user_2.id,
                    GroupMemberRole.MEMBER,
                )

        @pytest.mark.asyncio
        async def test_demote_creator_fail(
            self,
            auth_client_user_2,  # Назначенный админ
            group_with_roles,
            created_user_1,  # Создатель
        ):
            """Тест: нельзя понизить создателя группы"""
            data = GroupsDataFactory.update_role_json("member")
            response = await auth_client_user_2.put(
                TestGroups.update_member_role_url(
                    group_with_roles.id, created_user_1.id
                ),
                json=data,
            )
            HttpAssertions.assert_error_response(
                response, "Нельзя изменить роль или удалить создателя группы", 403
            )

        @pytest.mark.asyncio
        async def test_update_role_not_admin(
            self,
            auth_client_user_3,  # Простой участник
            group_with_roles,
            created_user_2,
        ):
            """Тест: изменение роли не админом"""
            data = GroupsDataFactory.update_role_json("admin")
            response = await auth_client_user_3.put(
                TestGroups.update_member_role_url(
                    group_with_roles.id, created_user_2.id
                ),
                json=data,
            )
            HttpAssertions.assert_error_response(
                response,
                "Только администратор группы может выполнять это действие",
                403,
            )

        @pytest.mark.asyncio
        async def test_update_role_member_not_found(
            self,
            auth_client_user_1,
            group_with_roles,
        ):
            """Тест: изменение роли пользователя, которого нет в группе -> 404"""
            non_existent_id = uuid4()
            data = GroupsDataFactory.update_role_json("admin")

            response = await auth_client_user_1.put(
                TestGroups.update_member_role_url(group_with_roles.id, non_existent_id),
                json=data,
            )
            HttpAssertions.assert_not_found_error(
                response, "Участник не найден в этой группе"
            )

    class TestGroupJoin:
        """Тесты присоединения к публичной группе"""

        @pytest.mark.asyncio
        async def test_join_public_group_success(
            self,
            redis_connect,
            created_user_2,
            auth_client_user_2,  # Свободный пользователь
            created_group_user1_user3,  # Публичная группа
            test_db,
        ):
            """Тест: успешное присоединение к публичной группе"""
            response = await auth_client_user_2.post(
                TestGroups.get_join_url(created_group_user1_user3.id)
            )
            HttpAssertions.assert_success_response(response, dict)

            async for session in test_db.create_session():
                await GroupDatabaseAssertions.assert_member_in_group(
                    session, created_group_user1_user3.id, created_user_2.id
                )
                # Проверка системного сообщения
                await GroupDatabaseAssertions.assert_group_last_message_is_system(
                    session,
                    created_group_user1_user3.id,
                    f"{created_user_2.username} присоединился(ась) к группе",
                )

        @pytest.mark.asyncio
        async def test_join_private_group_fail(
            self,
            auth_client_user_2,  # Свободный пользователь
            created_private_group_user1_user3,  # Приватная группа
        ):
            """Тест: нельзя присоединиться к приватной группе -> 403"""
            response = await auth_client_user_2.post(
                TestGroups.get_join_url(created_private_group_user1_user3.id)
            )
            HttpAssertions.assert_error_response(
                response, "Группа является приватной. Вы не имейте к ней доступ", 403
            )

        @pytest.mark.asyncio
        async def test_join_already_member_fail(
            self,
            auth_client_user_3,  # Уже в группе
            created_group_user1_user3,
        ):
            """Тест: нельзя присоединиться, если уже в группе -> 409"""
            response = await auth_client_user_3.post(
                TestGroups.get_join_url(created_group_user1_user3.id)
            )
            HttpAssertions.assert_error_response(
                response, "Вы уже являетесь участником этой группы", 409
            )

        @pytest.mark.asyncio
        async def test_join_group_not_found(
            self,
            auth_client_user_2,
        ):
            """Тест: присоединение к несуществующей группе -> 404"""
            response = await auth_client_user_2.post(TestGroups.get_join_url(uuid4()))
            HttpAssertions.assert_not_found_error(response, "Группа не найдена")

    class TestGroupLeave:
        """Тесты выхода из группы"""

        @pytest.mark.asyncio
        async def test_leave_group_success(
            self,
            redis_connect,
            created_user_3,
            auth_client_user_3,  # Участник
            created_group_user1_user3,
            test_db,
        ):
            """Тест: успешный выход из группы"""
            response = await auth_client_user_3.delete(
                TestGroups.get_leave_url(created_group_user1_user3.id)
            )
            HttpAssertions.assert_success_response(response, dict)

            async for session in test_db.create_session():
                await GroupDatabaseAssertions.assert_member_not_in_group(
                    session, created_group_user1_user3.id, created_user_3.id
                )
                # Проверка системного сообщения
                await GroupDatabaseAssertions.assert_group_last_message_is_system(
                    session,
                    created_group_user1_user3.id,
                    f"{created_user_3.username} покинул(а) группу",
                )

        @pytest.mark.asyncio
        async def test_leave_group_not_member_fail(
            self,
            auth_client_user_2,  # Не в группе
            created_group_user1_user3,
        ):
            """Тест: нельзя выйти из группы, если не в ней"""
            response = await auth_client_user_2.delete(
                TestGroups.get_leave_url(created_group_user1_user3.id)
            )
            HttpAssertions.assert_error_response(
                response, "Вы не являетесь участником группы", 403
            )

        @pytest.mark.asyncio
        async def test_creator_leave_group_fail(
            self,
            auth_client_user_1,  # Создатель
            created_group_user1_user3,
        ):
            """Тест: создатель не может выйти из группы"""
            response = await auth_client_user_1.delete(
                TestGroups.get_leave_url(created_group_user1_user3.id)
            )
            HttpAssertions.assert_error_response(
                response, "Нельзя изменить роль или удалить создателя группы", 403
            )

        @pytest.mark.asyncio
        async def test_leave_group_not_found(
            self,
            auth_client_user_3,
        ):
            """Тест: выход из несуществующей группы"""
            response = await auth_client_user_3.delete(
                TestGroups.get_leave_url(uuid4())
            )
            HttpAssertions.assert_not_found_error(response, "Группа не найдена")

    class TestDeleteGroup:
        """Тесты удаления группы"""

        @pytest.mark.asyncio
        async def test_delete_group_success(
            self,
            auth_client_user_1,  # Создатель
            created_group_user1_user3,
            test_db,
        ):
            """Тест: создатель удаляет группу (с участниками)"""
            group_id = created_group_user1_user3.id

            response = await auth_client_user_1.delete(
                TestGroups.delete_group_url(group_id)
            )
            data = HttpAssertions.assert_success_response(response, dict)
            assert data["deleted_messages"] == 0

            # Проверяем, что группы нет
            async for session in test_db.create_session():
                await GroupDatabaseAssertions.assert_group_not_exists(session, group_id)
                # Проверяем, что участники тоже удалены
                await DatabaseAssertions.assert_not_exists(
                    session, GroupMembers, group_id=group_id
                )

        @pytest.mark.asyncio
        async def test_delete_group_with_messages_and_avatar_success(
            self,
            auth_client_user_1,
            group_with_avatar_and_messages,
            test_db,
        ):
            """Тест: удаление группы с сообщениями и аватаркой"""
            group_id = group_with_avatar_and_messages.id

            response = await auth_client_user_1.delete(
                TestGroups.delete_group_url(group_id)
            )
            data = HttpAssertions.assert_success_response(response, dict)

            assert data["deleted_messages"] == 3
            async for session in test_db.create_session():
                # Группа удалена
                await GroupDatabaseAssertions.assert_group_not_exists(session, group_id)
                # Сообщения удалены
                await DatabaseAssertions.assert_not_exists(
                    session, Messages, group_id=group_id
                )

        @pytest.mark.asyncio
        async def test_delete_group_not_creator_fail(
            self,
            auth_client_user_3,  # Участник, не создатель
            created_group_user1_user3,
        ):
            """Тест: не-создатель не может удалить группу"""
            response = await auth_client_user_3.delete(
                TestGroups.delete_group_url(created_group_user1_user3.id)
            )
            HttpAssertions.assert_error_response(
                response, "Только создатель может выполнить данное действие", 403
            )

        @pytest.mark.asyncio
        async def test_delete_group_not_admin_fail(
            self,
            auth_client_user_2,  # Не в группе
            created_group_user1_user3,
        ):
            """Тест: не-участник не может удалить группу"""
            response = await auth_client_user_2.delete(
                TestGroups.delete_group_url(created_group_user1_user3.id)
            )
            HttpAssertions.assert_error_response(
                response, "Только создатель может выполнить данное действие", 403
            )

        @pytest.mark.asyncio
        async def test_delete_group_not_found(
            self,
            auth_client_user_1,
        ):
            """Тест: удаление несуществующей группы -> 404"""
            response = await auth_client_user_1.delete(
                TestGroups.delete_group_url(uuid4())
            )
            HttpAssertions.assert_not_found_error(response, "Группа не найдена")

    class TestTransferOwnership:
        """Тесты передачи прав создателя группы"""

        @pytest.mark.asyncio
        async def test_transfer_ownership_success(
            self,
            redis_connect,
            created_user_1,
            auth_client_user_1,  # Создатель
            created_group_user1_user3,
            created_user_3,  # Новый создатель
            test_db,
        ):
            """Тест: успешная передача прав создателя"""
            group_id = created_group_user1_user3.id
            data = {"new_creator_id": str(created_user_3.id)}

            response = await auth_client_user_1.post(
                TestGroups.get_transfer_owner_url(group_id),
                json=data,
            )
            HttpAssertions.assert_success_response(response, ShortGroupResponse)

            async for session in test_db.create_session():
                # Проверяем, что в БД сменился создатель
                group = await DatabaseAssertions.assert_exists(
                    session, Groups, id=group_id
                )
                assert group.created_by == created_user_3.id

                # Проверяем, что новый создатель — админ
                await GroupDatabaseAssertions.assert_member_role(
                    session, group_id, created_user_3.id, GroupMemberRole.ADMIN
                )
                # Проверяем, что старый создатель стал просто админом
                await GroupDatabaseAssertions.assert_member_role(
                    session, group_id, created_user_1.id, GroupMemberRole.ADMIN
                )
                # Проверяем системное сообщение
                await GroupDatabaseAssertions.assert_group_last_message_is_system(
                    session,
                    group_id,
                    f"{created_user_1.username} передал(а) права создателя группы пользователю {created_user_3.username}",
                )

        @pytest.mark.asyncio
        async def test_transfer_ownership_to_self_fail(
            self,
            auth_client_user_1,  # Создатель
            created_group_user1_user3,
            created_user_1,
        ):
            """Тест: нельзя передать права самому себе"""
            group_id = created_group_user1_user3.id
            data = {"new_creator_id": str(created_user_1.id)}

            response = await auth_client_user_1.post(
                TestGroups.get_transfer_owner_url(group_id),
                json=data,
            )
            HttpAssertions.assert_error_response(
                response, "Вы уже являетесь создателем этой группы", 400
            )

        @pytest.mark.asyncio
        async def test_transfer_ownership_not_creator_fail(
            self,
            auth_client_user_3,  # Участник, не создатель
            created_group_user1_user3,
            created_user_1,
        ):
            """Тест: только создатель может передать права"""
            group_id = created_group_user1_user3.id
            data = {"new_creator_id": str(created_user_1.id)}

            response = await auth_client_user_3.post(
                TestGroups.get_transfer_owner_url(group_id),
                json=data,
            )
            HttpAssertions.assert_error_response(
                response, "Только создатель может выполнить данное действие", 403
            )

        @pytest.mark.asyncio
        async def test_transfer_ownership_new_creator_not_member_fail(
            self,
            auth_client_user_1,  # Создатель
            created_group_user1_user3,
            created_user_2,  # НЕ участник группы
        ):
            """Тест: нельзя передать права пользователю, который не в группе"""
            group_id = created_group_user1_user3.id
            data = {"new_creator_id": str(created_user_2.id)}

            response = await auth_client_user_1.post(
                TestGroups.get_transfer_owner_url(group_id),
                json=data,
            )
            HttpAssertions.assert_not_found_error(
                response, "Участник не найден в этой группе"
            )

        @pytest.mark.asyncio
        async def test_transfer_ownership_group_not_found(
            self,
            auth_client_user_1,
            created_user_3,
        ):
            """Тест: передача прав в несуществующей группе"""
            group_id = uuid4()
            data = {"new_creator_id": str(created_user_3.id)}

            response = await auth_client_user_1.post(
                TestGroups.get_transfer_owner_url(group_id),
                json=data,
            )
            HttpAssertions.assert_not_found_error(response, "Группа не найдена")

        @pytest.mark.asyncio
        async def test_transfer_ownership_then_old_creator_can_leave(
            self,
            redis_connect,
            auth_client_user_1,  # Бывший создатель
            created_group_user1_user3,
            created_user_3,  # Новый создатель
            created_user_1,
            test_db,
        ):
            """Тест: после передачи прав старый создатель может выйти из группы"""
            group_id = created_group_user1_user3.id

            # Передаём права
            data = {"new_creator_id": str(created_user_3.id)}
            response = await auth_client_user_1.post(
                TestGroups.get_transfer_owner_url(group_id),
                json=data,
            )
            HttpAssertions.assert_success_response(response, ShortGroupResponse)

            # Старый создатель выходит из группы
            response = await auth_client_user_1.delete(
                TestGroups.get_leave_url(group_id)
            )
            HttpAssertions.assert_success_response(response, dict)

            async for session in test_db.create_session():
                await GroupDatabaseAssertions.assert_member_not_in_group(
                    session, group_id, created_user_1.id
                )
