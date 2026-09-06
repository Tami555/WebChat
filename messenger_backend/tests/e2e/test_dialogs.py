import pytest
from uuid import uuid4

from src.schemas import ChatResponse, DialogDetailResponse
from tests.helpers.assertions import (
    HttpAssertions,
    DialogDatabaseAssertions,
)
from tests.helpers.url_builder import url_builder
from tests.fixtures.data import UserDataFactory, DialogDataFactory


class TestDialogs:
    """Тесты диалогов"""

    # URLs
    get_dialogs_url = url_builder.dialogs("chats")
    create_dialog_url = url_builder.dialogs("create")

    class TestGetDialogs:
        """Тесты получения списка диалогов"""

        @pytest.mark.asyncio
        async def test_get_dialogs_empty(self, auth_client_user_1):
            """Тест: получение списка диалогов у пользователя без диалогов"""
            response = await auth_client_user_1.get(TestDialogs.get_dialogs_url)
            data = HttpAssertions.assert_success_response(
                response=response, response_model=ChatResponse, is_list=True
            )
            assert data == []

        @pytest.mark.asyncio
        async def test_get_dialogs_with_one_dialog(
            self,
            auth_client_user_1,
            created_dialog_user1_user2,
        ):
            """Тест: получение списка диалогов с одним диалогом"""
            response = await auth_client_user_1.get(TestDialogs.get_dialogs_url)
            data = HttpAssertions.assert_success_response(
                response=response, response_model=ChatResponse, is_list=True
            )
            assert len(data) == 1
            dialog = data[0]
            assert dialog.id == created_dialog_user1_user2.id
            assert dialog.unread_count_message == 0
            assert dialog.last_message is None
            # Проверяем, что заголовок = username собеседника (user2)
            user2_data = UserDataFactory.user_2()
            assert dialog.title == user2_data["username"]

        @pytest.mark.asyncio
        async def test_get_dialogs_with_two_dialogs(
            self,
            auth_client_user_1,
            created_dialog_user1_user2,
            created_dialog_user1_user3,
        ):
            """Тест: получение списка диалогов с двумя диалогами"""
            response = await auth_client_user_1.get(TestDialogs.get_dialogs_url)
            data = HttpAssertions.assert_success_response(
                response=response, response_model=ChatResponse, is_list=True
            )
            assert len(data) == 2
            # Проверяем, что оба диалога есть
            dialog_ids = [d.id for d in data]
            assert created_dialog_user1_user2.id in dialog_ids
            assert created_dialog_user1_user3.id in dialog_ids

        @pytest.mark.asyncio
        async def test_get_dialogs_with_unread_messages(
            self,
            auth_client_user_2,
            created_not_read_message_statuses_in_dialog_1_2,
        ):
            """Тест: получение списка диалогов с непрочитанным сообщением"""
            response = await auth_client_user_2.get(TestDialogs.get_dialogs_url)
            data = HttpAssertions.assert_success_response(
                response=response, response_model=ChatResponse, is_list=True
            )

            assert len(data) == 1
            dialog = data[0]
            assert dialog.unread_count_message == 1
            assert dialog.last_message is not None
            assert dialog.last_message.content == "Hello from user 1 to user 2!"

        @pytest.mark.asyncio
        async def test_get_dialogs_with_read_messages(
            self,
            auth_client_user_2,
            created_read_message_statuses_in_dialog_1_2,
        ):
            """Тест: получение списка диалогов с прочитанным сообщением"""
            from src.schemas import ChatResponse

            response = await auth_client_user_2.get(TestDialogs.get_dialogs_url)
            data = HttpAssertions.assert_success_response(
                response=response, response_model=ChatResponse, is_list=True
            )

            assert len(data) == 1
            dialog = data[0]
            assert dialog.unread_count_message == 0
            assert dialog.last_message is not None
            assert dialog.last_message.content == "Hello from user 1 to user 2!"

        @pytest.mark.asyncio
        async def test_get_dialogs_unauthorized_error(self, client):
            """Тест: получение диалогов без авторизации"""
            response = await client.get(TestDialogs.get_dialogs_url)

            HttpAssertions.assert_unauthorized_error(
                response=response,
                expected_message="Вы не авторизованы! Войдите пожалуйста в аккаунт",
            )

        @pytest.mark.asyncio
        async def test_get_dialogs_with_invalid_token(self, client):
            """Тест: получение диалогов с невалидным токеном"""
            client.headers["Authorization"] = "Bearer invalid_token"
            response = await client.get(TestDialogs.get_dialogs_url)

            HttpAssertions.assert_unauthorized_error(
                response=response,
                expected_message="Невалидный токен",
            )

    class TestCreateDialog:
        """Тесты создания диалога"""

        @pytest.mark.asyncio
        async def test_create_dialog_success(
            self,
            auth_client_user_1,
            created_user_1,
            created_user_2,
            test_db,
        ):
            """Тест: успешное создание диалога между user_1 и user_2"""
            data = DialogDataFactory.create_dialog(created_user_2.id)

            response = await auth_client_user_1.post(
                TestDialogs.create_dialog_url,
                json=data,
            )
            dialog_data = HttpAssertions.assert_success_response(
                response=response,
                response_model=DialogDetailResponse,
            )

            assert dialog_data.user1.username == created_user_1.username
            assert dialog_data.user2.username == created_user_2.username
            assert dialog_data.created_at is not None

            # Проверяем, что диалог в БД
            async for session in test_db.create_session():
                await DialogDatabaseAssertions.assert_dialog_exists(
                    session=session,
                    user1_id=created_user_1.id,
                    user2_id=created_user_2.id,
                )

        @pytest.mark.asyncio
        async def test_create_dialog_with_self(
            self,
            auth_client_user_1,
            created_user_1,
        ):
            """Тест: создание диалога с самим собой"""
            data = DialogDataFactory.create_dialog(created_user_1.id)

            response = await auth_client_user_1.post(
                TestDialogs.create_dialog_url,
                json=data,
            )

            HttpAssertions.assert_error_response(
                response=response,
                expected_message="Диалог с одним пользователем не может существовать",
                expected_status=400,
            )

        @pytest.mark.asyncio
        async def test_create_dialog_with_non_existent_user(
            self,
            auth_client_user_1,
        ):
            """Тест: создание диалога с несуществующим пользователем"""
            data = DialogDataFactory.create_dialog(uuid4())

            response = await auth_client_user_1.post(
                TestDialogs.create_dialog_url,
                json=data,
            )
            HttpAssertions.assert_not_found_error(
                response=response,
                expected_message="Пользователь не найден",
            )

        @pytest.mark.asyncio
        async def test_create_dialog_already_exists(
            self,
            auth_client_user_1,
            created_user_2,
            created_dialog_user1_user2,
        ):
            """Тест: создание уже существующего диалога"""
            data = DialogDataFactory.create_dialog(created_user_2.id)
            response = await auth_client_user_1.post(
                TestDialogs.create_dialog_url,
                json=data,
            )

            HttpAssertions.assert_error_response(
                response=response,
                expected_message="Диалог с таким пользователем уже существует",
                expected_status=409,
            )

        @pytest.mark.asyncio
        async def test_create_dialog_unauthorized(
            self,
            client,
            created_user_2,
        ):
            """Тест: создание диалога без авторизации"""
            data = DialogDataFactory.create_dialog(created_user_2.id)

            response = await client.post(
                TestDialogs.create_dialog_url,
                json=data,
            )
            HttpAssertions.assert_unauthorized_error(
                response=response,
                expected_message="Вы не авторизованы! Войдите пожалуйста в аккаунт",
            )

        @pytest.mark.asyncio
        async def test_create_dialog_invalid_token(
            self,
            client,
            created_user_2,
        ):
            """Тест: создание диалога с невалидным токеном"""
            client.headers["Authorization"] = "Bearer invalid_token"
            data = {
                "interlocutor": str(created_user_2.id),
            }

            response = await client.post(
                TestDialogs.create_dialog_url,
                json=data,
            )

            HttpAssertions.assert_unauthorized_error(
                response=response,
                expected_message="Невалидный токен",
            )

        @pytest.mark.asyncio
        async def test_create_dialog_missing_interlocutor(
            self,
            auth_client_user_1,
        ):
            """Тест: создание диалога без указания собеседника"""
            data = {}

            response = await auth_client_user_1.post(
                TestDialogs.create_dialog_url,
                json=data,
            )

            HttpAssertions.assert_validation_error(response)

        @pytest.mark.asyncio
        async def test_create_dialog_wrong_interlocutor_type(
            self,
            auth_client_user_1,
        ):
            """Тест: создание диалога с неверным типом interlocutor"""
            data = DialogDataFactory.create_dialog("user_2")

            response = await auth_client_user_1.post(
                TestDialogs.create_dialog_url,
                json=data,
            )

            HttpAssertions.assert_validation_error(
                response=response,
                expected_message="Невалидные данные  !!!",
            )

        @pytest.mark.asyncio
        async def test_create_dialog_reverse_order_already_exists(
            self,
            auth_client_user_1,
            auth_client_user_2,
            created_user_1,
            created_user_2,
            test_db,
        ):
            """
            Тест: создание диалога от второго пользователя к первому (обратный порядок)
            Ожидается: диалог создан (или найден существующий), проверка уникальности
            """
            # Сначала создаем диалог от user_1 к user_2
            data_1_2 = DialogDataFactory.create_dialog(created_user_2.id)

            response = await auth_client_user_1.post(
                TestDialogs.create_dialog_url,
                json=data_1_2,
            )
            # Проверяем, что диалог создался
            HttpAssertions.assert_success_response(
                response=response,
                response_model=DialogDetailResponse,
            )
            async for session in test_db.create_session():
                await DialogDatabaseAssertions.assert_dialog_exists(
                    session=session,
                    user1_id=created_user_1.id,
                    user2_id=created_user_2.id,
                )

            # Пытаемся создать диалог наоборот от user_2 к user_1
            data_2_1 = DialogDataFactory.create_dialog(created_user_1.id)
            response = await auth_client_user_2.post(
                TestDialogs.create_dialog_url,
                json=data_2_1,
            )
            HttpAssertions.assert_error_response(
                response=response,
                expected_message="Диалог с таким пользователем уже существует",
                expected_status=409,
            )
