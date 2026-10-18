import pytest
from uuid import uuid4
from datetime import datetime
from httpx import AsyncClient

from src.schemas import ChatResponse, ShortGroupResponse
from src.models.groups import Groups
from src.models.group_members import GroupMembers
from tests.helpers.assertions import HttpAssertions, GroupDatabaseAssertions
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

                # Проверяем media
                assert data.media.images == []
                assert data.media.voices == []
                assert data.media.files == []

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

            @pytest.mark.asyncio
            async def test_get_private_group_with_media(
                self,
                auth_client_user_1,
                created_private_group_user1_user3,
                created_message_in_private_group,
            ):
                """Тест: получение инфы о группе с медиа-сообщениями"""
                from src.schemas import GroupResponse

                group_id = created_private_group_user1_user3.id
                response = await auth_client_user_1.get(
                    TestGroups.get_group_detail_url(group_id)
                )

                data = HttpAssertions.assert_success_response(
                    response=response,
                    response_model=GroupResponse,
                )

                assert len(data.media.images) == 1
                assert data.media.images[0] == "/test/media/image.jpg"
                assert data.media.voices == []
                assert data.media.files == []

        class TestPublicGroup:
            """Тесты для публичной группы"""

            @pytest.mark.asyncio
            async def test_get_public_group_success_as_member(
                self,
                auth_client_user_1,
                created_group_user1_user3,
            ):
                """Тест: участник получает инфу о публичной группе"""
                from src.schemas import GroupResponse

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
                from src.schemas import GroupResponse

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
                from uuid import uuid4

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
            from uuid import uuid4

            non_existent_id = uuid4()
            data = GroupsDataFactory.update_group_json(title="Ghost")

            response = await auth_client_user_1.patch(
                TestGroups.update_group_url(non_existent_id),
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
