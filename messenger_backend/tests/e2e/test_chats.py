import uuid
from uuid import UUID

import pytest
from tests.helpers.assertions import HttpAssertions
from tests.helpers.url_builder import url_builder
from tests.fixtures.data import UserDataFactory
from src.schemas.enums import ChatType


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

    class TestGetChatMessages:
        """Тесты получения сообщений чата"""

        @staticmethod
        def get_messages_url(chat_id: UUID):
            return url_builder.chats(str(chat_id), "messages")

        class TestDialog:
            """Тесты для диалогов"""

            @pytest.mark.asyncio
            async def test_get_messages_dialog_success(
                self,
                test_db,
                auth_client_user_2,
                created_user_2,
                created_not_read_message_statuses_in_dialog_1_2,
                created_dialog_user1_user2,
            ):
                """
                Тест: успешное получение сообщений из диалога
                Ожидается: 1 сообщение, статус стал прочитанным
                """
                from src.crud.messages import MessageCRUD
                from src.schemas import MessageResponse

                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_dialog_user1_user2.id
                )
                response = await auth_client_user_2.get(
                    get_messages_url, params={"chat_type": ChatType.DIALOGS}
                )
                data = HttpAssertions.assert_success_response(
                    response=response, response_model=MessageResponse, is_list=True
                )

                assert len(data) == 1
                message = data[0]
                assert message.content == "Hello from user 1 to user 2!"
                assert message.sender.username == UserDataFactory.user_1()["username"]

                # Проверяем, что сообщение отмечено как прочитанное
                async for session in test_db.create_session():
                    statuses = await MessageCRUD.get_message_statuses(
                        message.id, session
                    )
                    for status in statuses:
                        if status.user_id == created_user_2.id:
                            assert status.is_read is True
                            assert status.read_at is not None

            @pytest.mark.asyncio
            async def test_get_messages_dialog_with_pagination(
                self,
                auth_client_user_2,
                created_multiple_messages_in_dialog_1_2,
                created_dialog_user1_user2,
            ):
                """
                Тест: получение сообщений с пагинацией (page=2, limit=3)
                Ожидается: пустой список (всего 3 сообщения)
                """
                from src.schemas import MessageResponse

                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_dialog_user1_user2.id
                )
                response = await auth_client_user_2.get(
                    get_messages_url,
                    params={
                        "chat_type": ChatType.DIALOGS,
                        "page": 2,
                        "limit": 3,
                    },
                )
                data = HttpAssertions.assert_success_response(
                    response=response, response_model=MessageResponse, is_list=True
                )
                assert len(data) == 0

            @pytest.mark.asyncio
            async def test_get_messages_dialog_with_limit_one(
                self,
                auth_client_user_2,
                created_multiple_messages_in_dialog_1_2,
                created_dialog_user1_user2,
            ):
                """
                Тест: получение сообщений с limit=1
                Ожидается: 1 сообщение (последнее)
                """
                from src.schemas import MessageResponse

                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_dialog_user1_user2.id
                )
                response = await auth_client_user_2.get(
                    get_messages_url,
                    params={
                        "chat_type": ChatType.DIALOGS,
                        "page": 1,
                        "limit": 1,
                    },
                )
                data = HttpAssertions.assert_success_response(
                    response=response, response_model=MessageResponse, is_list=True
                )
                assert len(data) == 1
                assert data[0].content == "Message 3 from user 1 to user 2!"

            @pytest.mark.asyncio
            async def test_get_messages_dialog_wrong_type(
                self, auth_client_user_2, created_dialog_user1_user2
            ):
                """Тест: передача неверного типа чата (group вместо dialog)"""
                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_dialog_user1_user2.id
                )
                response = await auth_client_user_2.get(
                    get_messages_url,
                    params={"chat_type": ChatType.GROUP},
                )
                HttpAssertions.assert_not_found_error(
                    response=response,
                    expected_message="Группа не найдена",
                )

            @pytest.mark.asyncio
            async def test_get_messages_dialog_not_member(
                self,
                auth_client_user_2,
                created_dialog_user1_user3,
            ):
                """Тест: пользователь не является участником диалога"""
                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_dialog_user1_user3.id
                )
                response = await auth_client_user_2.get(
                    get_messages_url,
                    params={"chat_type": ChatType.DIALOGS},
                )
                HttpAssertions.assert_error_response(
                    response=response,
                    expected_message="Вы не являетесь участником данного диалога",
                    expected_status=403,
                )

            @pytest.mark.asyncio
            async def test_get_messages_dialog_page_zero(
                self,
                auth_client_user_2,
                created_dialog_user1_user2,
            ):
                """Тест: page=0 (невалидное значение)"""
                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_dialog_user1_user2.id
                )
                response = await auth_client_user_2.get(
                    get_messages_url,
                    params={
                        "chat_type": ChatType.DIALOGS,
                        "page": 0,
                    },
                )
                HttpAssertions.assert_validation_error(response)

            @pytest.mark.asyncio
            async def test_get_messages_dialog_limit_zero(
                self,
                auth_client_user_2,
                created_dialog_user1_user2,
            ):
                """Тест: limit=0 (невалидное значение)"""
                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_dialog_user1_user2.id
                )
                response = await auth_client_user_2.get(
                    get_messages_url,
                    params={
                        "chat_type": ChatType.DIALOGS,
                        "limit": 0,
                    },
                )
                HttpAssertions.assert_validation_error(response)

        class TestGroup:
            """Тесты для групп"""

            @pytest.mark.asyncio
            async def test_get_messages_group_success(
                self,
                test_db,
                auth_client_user_2,
                created_user_2,
                created_group_user1_user2_user3,
                created_not_read_message_statuses_in_group_1_2_3,
            ):
                """
                Тест: успешное получение сообщений из группы
                Ожидается: 1 сообщение, статус стал прочитанным
                """
                from src.crud.messages import MessageCRUD
                from src.schemas import MessageResponse

                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_group_user1_user2_user3.id
                )
                response = await auth_client_user_2.get(
                    get_messages_url, params={"chat_type": ChatType.GROUP}
                )
                data = HttpAssertions.assert_success_response(
                    response=response, response_model=MessageResponse, is_list=True
                )
                assert len(data) == 1
                message = data[0]
                assert message.content == "Hello from user 1 in group!"
                assert message.sender.username == UserDataFactory.user_1()["username"]

                # Проверяем, что сообщение отмечено как прочитанное
                async for session in test_db.create_session():
                    statuses = await MessageCRUD.get_message_statuses(
                        message.id, session
                    )
                    for status in statuses:
                        if status.user_id == created_user_2.id:
                            assert status.is_read is True
                            assert status.read_at is not None

            @pytest.mark.asyncio
            async def test_get_messages_group_with_pagination(
                self,
                auth_client_user_2,
                created_multiple_messages_in_group_1_2_3,
                created_group_user1_user2_user3,
            ):
                """Тест: получение сообщений с пагинацией (page=2, limit=3)"""
                from src.schemas import MessageResponse

                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_group_user1_user2_user3.id
                )
                response = await auth_client_user_2.get(
                    get_messages_url,
                    params={
                        "chat_type": ChatType.GROUP,
                        "page": 2,
                        "limit": 3,
                    },
                )
                data = HttpAssertions.assert_success_response(
                    response=response, response_model=MessageResponse, is_list=True
                )
                assert len(data) == 0

            @pytest.mark.asyncio
            async def test_get_messages_group_with_limit_one(
                self,
                auth_client_user_2,
                created_multiple_messages_in_group_1_2_3,
                created_group_user1_user2_user3,
            ):
                """
                Тест: получение сообщений с limit=1
                Ожидается: 1 сообщение (последнее)
                """
                from src.schemas import MessageResponse

                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_group_user1_user2_user3.id
                )
                response = await auth_client_user_2.get(
                    get_messages_url,
                    params={
                        "chat_type": ChatType.GROUP,
                        "page": 1,
                        "limit": 1,
                    },
                )
                data = HttpAssertions.assert_success_response(
                    response=response, response_model=MessageResponse, is_list=True
                )
                assert len(data) == 1
                assert data[0].content == "Group message 3!"

            @pytest.mark.asyncio
            async def test_get_messages_group_wrong_type(
                self, auth_client_user_2, created_group_user1_user2_user3
            ):
                """Тест: передача неверного типа чата (dialog вместо group)"""
                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_group_user1_user2_user3.id
                )
                response = await auth_client_user_2.get(
                    get_messages_url,
                    params={"chat_type": ChatType.DIALOGS},
                )
                HttpAssertions.assert_not_found_error(
                    response=response,
                    expected_message="Диалог не найден",
                )

            @pytest.mark.asyncio
            async def test_get_messages_group_not_member(
                self,
                auth_client_user_2,
                created_group_user1_user3,
            ):
                """Тест: пользователь не является участником диалога"""
                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_group_user1_user3.id
                )
                response = await auth_client_user_2.get(
                    get_messages_url,
                    params={"chat_type": ChatType.GROUP},
                )
                HttpAssertions.assert_error_response(
                    response=response,
                    expected_message="Вы не являетесь участником группы",
                    expected_status=403,
                )

            @pytest.mark.asyncio
            async def test_get_messages_group_page_zero(
                self,
                auth_client_user_2,
                created_group_user1_user2_user3,
            ):
                """Тест: page=0 (невалидное значение)"""
                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_group_user1_user2_user3.id
                )
                response = await auth_client_user_2.get(
                    get_messages_url,
                    params={
                        "chat_type": ChatType.GROUP,
                        "page": 0,
                    },
                )
                HttpAssertions.assert_validation_error(response)

            @pytest.mark.asyncio
            async def test_get_messages_dialog_limit_zero(
                self,
                auth_client_user_2,
                created_group_user1_user2_user3,
            ):
                """Тест: limit=0 (невалидное значение)"""
                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_group_user1_user2_user3.id
                )
                response = await auth_client_user_2.get(
                    get_messages_url,
                    params={
                        "chat_type": ChatType.GROUP,
                        "limit": 0,
                    },
                )
                HttpAssertions.assert_validation_error(response)

        class TestCommon:
            """Общие тесты для всех чатов"""

            @pytest.mark.asyncio
            async def test_get_messages_unauthorized(
                self,
                client,
                created_dialog_user1_user2,
            ):
                """Тест: получение сообщений без авторизации"""
                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_dialog_user1_user2.id
                )
                response = await client.get(
                    get_messages_url, params={"chat_type": ChatType.DIALOGS}
                )
                HttpAssertions.assert_unauthorized_error(
                    response=response,
                    expected_message="Вы не авторизованы! Войдите пожалуйста в аккаунт",
                )

            @pytest.mark.asyncio
            async def test_get_messages_invalid_token(
                self,
                client,
                created_dialog_user1_user2,
            ):
                """Тест: получение сообщений с невалидным токеном"""
                client.headers["Authorization"] = "Bearer invalid_token"

                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    created_dialog_user1_user2.id
                )
                response = await client.get(
                    get_messages_url, params={"chat_type": ChatType.DIALOGS}
                )
                HttpAssertions.assert_unauthorized_error(
                    response=response,
                    expected_message="Невалидный токен",
                )

            @pytest.mark.asyncio
            async def test_get_messages_non_existent_chat(
                self,
                auth_client_user_1,
            ):
                """Тест: получение сообщений из несуществующего чата"""
                uuid.uuid4()
                get_messages_url = TestChats.TestGetChatMessages.get_messages_url(
                    uuid.uuid4()
                )
                response = await auth_client_user_1.get(
                    get_messages_url, params={"chat_type": ChatType.DIALOGS}
                )
                HttpAssertions.assert_not_found_error(
                    response=response,
                    expected_message="Диалог не найден",
                )
