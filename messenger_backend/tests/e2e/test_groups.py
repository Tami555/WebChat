import pytest
from uuid import uuid4
from datetime import datetime
from httpx import AsyncClient

from src.schemas import ChatResponse, GroupResponse
from src.models.groups import Groups
from src.models.group_members import GroupMembers
from tests.helpers.assertions import HttpAssertions, GroupDatabaseAssertions
from tests.helpers.url_builder import url_builder
from tests.fixtures.data import UserDataFactory, GroupsDataFactory


class TestGroups:
    """Тесты групп"""

    # URLs
    get_groups_url = url_builder.groups("chats")
    create_group_url = url_builder.groups("create")

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
            """Тест: успешное создание группы с участниками"""
            members = [created_user_2.id, created_user_3.id]
            data = {
                "group": GroupsDataFactory.create_group_custom(
                    created_at=str(datetime.now())
                ),
                "members": [str(m) for m in members],
            }

            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                json=data,
            )

            group_data = HttpAssertions.assert_success_response(
                response=response,
                response_model=GroupResponse,
            )

            assert group_data.id is not None
            assert group_data.title == "Test Group"
            assert group_data.is_private is False

            # Проверяем, что группа появилась в БД
            async for session in test_db.create_session():
                group = await GroupDatabaseAssertions.assert_group_exists(
                    session=session,
                    group_id=group_data.id,
                    expected_title="Test Group",
                    expected_created_by=created_user_1.id,
                )
                # Проверяем, что все участники добавлены
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
            data = {
                "group": GroupsDataFactory.create_group_custom(
                    created_at=str(datetime.now())
                ),
                "members": [str(created_user_1.id), str(created_user_2.id)],
            }
            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                json=data,
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
            data = {
                "group": GroupsDataFactory.create_group_custom(
                    created_at=str(datetime.now())
                ),
                "members": [
                    str(created_user_2.id),
                    str(created_user_3.id),
                    str(created_user_2.id),
                ],
            }

            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                json=data,
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
            data = {
                "group": GroupsDataFactory.create_group_custom(
                    created_at=str(datetime.now())
                ),
                "members": [str(created_user_2.id), str(non_existent_id)],
            }

            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                json=data,
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
            data = {
                "group": GroupsDataFactory.create_group_custom(
                    created_at=str(datetime.now())
                ),
                "members": [str(created_user_2.id), str(created_user_3.id)],
            }

            response = await client.post(
                TestGroups.create_group_url,
                json=data,
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
            """
            Тест: создание группы с невалидным токеном"""
            client.headers["Authorization"] = "Bearer invalid_token"
            data = {
                "group": {
                    "title": "Test Group",
                    "description": "Test group description",
                    "is_private": False,
                },
                "members": [str(created_user_2.id), str(created_user_3.id)],
            }

            response = await client.post(
                TestGroups.create_group_url,
                json=data,
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
            """
            Тест: создание группы без заголовка
            Ожидается: ошибка 422
            """
            data = {
                "group": {
                    "description": "Test group description",
                    "is_private": False,
                },
                "members": [str(created_user_2.id), str(created_user_3.id)],
            }

            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                json=data,
            )
            HttpAssertions.assert_validation_error(response)

        @pytest.mark.asyncio
        async def test_create_group_missing_members_success(
            self, auth_client_user_1, created_user_1, test_db
        ):
            """
            Тест: создание группы без участников
            Ожидается успех
            """
            data = {
                "group": GroupsDataFactory.create_group_custom(
                    created_at=str(datetime.now())
                ),
                "members": [],
            }
            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                json=data,
            )

            group_data = HttpAssertions.assert_success_response(
                response=response,
                response_model=GroupResponse,
            )

            # Проверяем, что группа появилась в БД
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
            """Тест: создание группы с неверным типом members"""
            data = {
                "group": {
                    "title": "Test Group",
                    "description": "Test group description",
                    "is_private": False,
                },
                "members": ["username"],
            }

            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                json=data,
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
            data = {
                "group": GroupsDataFactory.create_group_custom(
                    is_private=True,
                    title="Private Group",
                    created_at=str(datetime.now()),
                ),
                "members": [str(created_user_2.id), str(created_user_3.id)],
            }

            response = await auth_client_user_1.post(
                TestGroups.create_group_url,
                json=data,
            )

            group_data = HttpAssertions.assert_success_response(
                response=response,
                response_model=GroupResponse,
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
