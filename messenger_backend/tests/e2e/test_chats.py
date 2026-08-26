import pytest
from tests.helpers.assertions import HttpAssertions
from tests.helpers.url_builder import url_builder


class TestChats:
    """Тесты чатов"""

    class TestGetChats:
        """Тесты получения списка чатов"""

        get_chats_url = url_builder.chats("/")

        @pytest.mark.asyncio
        async def test_get_chats_empty(self, auth_client_user_1):
            """Тест на получение пустого списка чатов"""
            from src.schemas import AllChatsResponse

            response = await auth_client_user_1.get(self.get_chats_url)
            data = HttpAssertions.assert_success_response(
                response=response,
                response_model=AllChatsResponse,
            )
            assert data.dialogs == []
            assert data.groups == []

        @pytest.mark.asyncio
        async def test_get_chats_with_one_dialog(
            self, auth_client_user_1, created_dialog_user1_user2
        ):
            """Тест на получение списка с одним диалогом"""
            from src.schemas import AllChatsResponse

            response = await auth_client_user_1.get(self.get_chats_url)
            data = HttpAssertions.assert_success_response(
                response=response,
                response_model=AllChatsResponse,
            )
            assert len(data.dialogs) == 1
            dialog = data.dialogs[0]
            assert dialog.id == created_dialog_user1_user2.id
            assert dialog.unread_count_message == 0
            assert dialog.last_message is None
            assert data.groups == []

        @pytest.mark.asyncio
        async def test_get_chats_with_one_group(
            self, auth_client_user_1, created_group_user1_user2_user3
        ):
            """Тест на получение списка с одной группой"""
            from src.schemas import AllChatsResponse

            response = await auth_client_user_1.get(self.get_chats_url)
            data = HttpAssertions.assert_success_response(
                response=response,
                response_model=AllChatsResponse,
            )
            assert len(data.groups) == 1
            group = data.groups[0]
            assert group.id == created_group_user1_user2_user3.id
            assert group.unread_count_message == 0
            assert group.last_message is None
            assert data.dialogs == []

        @pytest.mark.asyncio
        async def test_get_chats_with_dialog_and_group(
            self,
            auth_client_user_1,
            created_dialog_user1_user2,
            created_group_user1_user2_user3,
        ):
            """Тест на получение списка с диалогом и группой (без сообщений)"""
            from src.schemas import AllChatsResponse

            response = await auth_client_user_1.get(self.get_chats_url)
            data = HttpAssertions.assert_success_response(
                response=response,
                response_model=AllChatsResponse,
            )
            assert len(data.dialogs) == 1
            assert data.dialogs[0].id == created_dialog_user1_user2.id

            assert len(data.groups) == 1
            assert data.groups[0].id == created_group_user1_user2_user3.id

        @pytest.mark.asyncio
        async def test_get_chats_with_read_messages_in_dialog(
            self, auth_client_user_2, created_read_message_statuses_in_dialog_1_2
        ):
            """Тест на получение списка с прочитанными сообщениями в диалоге"""
            from src.schemas import AllChatsResponse

            response = await auth_client_user_2.get(self.get_chats_url)

            data = HttpAssertions.assert_success_response(
                response=response,
                response_model=AllChatsResponse,
            )
            assert len(data.dialogs) == 1
            dialog = data.dialogs[0]
            assert dialog.unread_count_message == 0
            assert dialog.last_message is not None
            assert dialog.last_message.content == "Hello from user 1 to user 2!"

        @pytest.mark.asyncio
        async def test_get_chats_with_read_messages_in_group(
            self, auth_client_user_2, created_read_message_statuses_in_group_1_2_3
        ):
            """Тест на получение списка с прочитанными сообщениями в группе"""
            from src.schemas import AllChatsResponse

            response = await auth_client_user_2.get(self.get_chats_url)

            data = HttpAssertions.assert_success_response(
                response=response,
                response_model=AllChatsResponse,
            )
            assert len(data.groups) == 1
            group = data.groups[0]
            assert group.unread_count_message == 0
            assert group.last_message is not None
            assert group.last_message.content == "Hello from user 1 in group!"

        @pytest.mark.asyncio
        async def test_get_chats_with_read_messages_in_dialog_and_group(
            self,
            auth_client_user_2,
            created_read_message_statuses_in_dialog_1_2,
            created_read_message_statuses_in_group_1_2_3,
        ):
            """Тест на получение списка с прочитанными сообщениями в диалоге и группе"""
            from src.schemas import AllChatsResponse

            response = await auth_client_user_2.get(self.get_chats_url)
            data = HttpAssertions.assert_success_response(
                response=response,
                response_model=AllChatsResponse,
            )
            assert len(data.dialogs) == 1
            dialog = data.dialogs[0]
            assert dialog.unread_count_message == 0
            assert dialog.last_message is not None
            assert dialog.last_message.content == "Hello from user 1 to user 2!"

            assert len(data.groups) == 1
            group = data.groups[0]
            assert group.unread_count_message == 0
            assert group.last_message is not None
            assert group.last_message.content == "Hello from user 1 in group!"

        @pytest.mark.asyncio
        async def test_get_chats_with_unread_messages_in_dialog(
            self, auth_client_user_2, created_not_read_message_statuses_in_dialog_1_2
        ):
            """Тест на получение списка с непрочитанными сообщениями в диалоге"""
            from src.schemas import AllChatsResponse

            response = await auth_client_user_2.get(self.get_chats_url)

            data = HttpAssertions.assert_success_response(
                response=response,
                response_model=AllChatsResponse,
            )
            assert len(data.dialogs) == 1
            dialog = data.dialogs[0]
            assert dialog.unread_count_message == 1
            assert dialog.last_message is not None
            assert dialog.last_message.content == "Hello from user 1 to user 2!"

        @pytest.mark.asyncio
        async def test_get_chats_with_unread_messages_in_group(
            self, auth_client_user_2, created_not_read_message_statuses_in_group_1_2_3
        ):
            """Тест на получение списка с непрочитанными сообщениями в группе"""
            from src.schemas import AllChatsResponse

            response = await auth_client_user_2.get(self.get_chats_url)

            data = HttpAssertions.assert_success_response(
                response=response,
                response_model=AllChatsResponse,
            )
            assert len(data.groups) == 1
            group = data.groups[0]
            assert group.unread_count_message == 1
            assert group.last_message is not None
            assert group.last_message.content == "Hello from user 1 in group!"

        @pytest.mark.asyncio
        async def test_get_chats_with_unread_messages_in_dialog_and_group(
            self,
            auth_client_user_2,
            created_not_read_message_statuses_in_dialog_1_2,
            created_not_read_message_statuses_in_group_1_2_3,
        ):
            """Тест на получение списка с непрочитанными сообщениями в диалоге и группе"""
            from src.schemas import AllChatsResponse

            response = await auth_client_user_2.get(self.get_chats_url)
            data = HttpAssertions.assert_success_response(
                response=response,
                response_model=AllChatsResponse,
            )
            assert len(data.dialogs) == 1
            dialog = data.dialogs[0]
            assert dialog.unread_count_message == 1
            assert dialog.last_message is not None
            assert dialog.last_message.content == "Hello from user 1 to user 2!"

            assert len(data.groups) == 1
            group = data.groups[0]
            assert group.unread_count_message == 1
            assert group.last_message is not None
            assert group.last_message.content == "Hello from user 1 in group!"

        @pytest.mark.asyncio
        async def test_get_chats_with_read_messages_in_dialog_and_unread_messages_in_group(
            self,
            auth_client_user_2,
            created_read_message_statuses_in_dialog_1_2,
            created_not_read_message_statuses_in_group_1_2_3,
        ):
            """Тест на получение списка с прочитанными сообщениями в диалоге и непрочитанными группе"""
            from src.schemas import AllChatsResponse

            response = await auth_client_user_2.get(self.get_chats_url)
            data = HttpAssertions.assert_success_response(
                response=response,
                response_model=AllChatsResponse,
            )
            assert len(data.dialogs) == 1
            dialog = data.dialogs[0]
            assert dialog.unread_count_message == 0
            assert dialog.last_message is not None
            assert dialog.last_message.content == "Hello from user 1 to user 2!"

            assert len(data.groups) == 1
            group = data.groups[0]
            assert group.unread_count_message == 1
            assert group.last_message is not None
            assert group.last_message.content == "Hello from user 1 in group!"

        @pytest.mark.asyncio
        async def test_get_chats_with_unread_messages_in_dialog_and_read_messages_in_group(
            self,
            auth_client_user_2,
            created_not_read_message_statuses_in_dialog_1_2,
            created_read_message_statuses_in_group_1_2_3,
        ):
            """Тест на получение списка с непрочитанными сообщениями в диалоге и прочитанными группе"""
            from src.schemas import AllChatsResponse

            response = await auth_client_user_2.get(self.get_chats_url)
            data = HttpAssertions.assert_success_response(
                response=response,
                response_model=AllChatsResponse,
            )
            assert len(data.dialogs) == 1
            dialog = data.dialogs[0]
            assert dialog.unread_count_message == 1
            assert dialog.last_message is not None
            assert dialog.last_message.content == "Hello from user 1 to user 2!"

            assert len(data.groups) == 1
            group = data.groups[0]
            assert group.unread_count_message == 0
            assert group.last_message is not None
            assert group.last_message.content == "Hello from user 1 in group!"

        @pytest.mark.asyncio
        async def test_get_chats_unauthorized_error(self, client):
            """Тест на получение чатов без авторизации"""
            response = await client.get(self.get_chats_url)

            HttpAssertions.assert_unauthorized_error(
                response=response,
                expected_message="Вы не авторизованы! Войдите пожалуйста в аккаунт",
            )

        @pytest.mark.asyncio
        async def test_get_chats_with_invalid_token(self, client):
            """Тест на получение чатов с невалидным токеном"""
            client.headers["Authorization"] = "Bearer invalid_token"
            response = await client.get(self.get_chats_url)

            HttpAssertions.assert_unauthorized_error(
                response=response,
                expected_message="Невалидный токен",
            )
