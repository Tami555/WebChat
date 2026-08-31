import pytest
from uuid import UUID, uuid4
from pathlib import Path

from src.schemas.enums import ChatType, MessageType
from tests.helpers.assertions import (
    HttpAssertions,
    MessageDatabaseAssertions,
    GroupDatabaseAssertions,
    DialogDatabaseAssertions,
)
from tests.helpers import url_builder, FileFactory
from tests.fixtures.data import UserDataFactory, MessagesDataFactory


class TestChats:
    """Тесты чатов"""

    # URLs
    @staticmethod
    def get_messages_url(chat_id: UUID):
        return url_builder.chats(str(chat_id), "messages")

    get_chats_url = url_builder.chats("/")
    create_message_url = url_builder.chats("messages", "create")

    class TestGetChats:
        """Тесты получения списка чатов"""

        @pytest.mark.asyncio
        async def test_get_chats_empty(self, auth_client_user_1):
            """Тест на получение пустого списка чатов"""
            from src.schemas import AllChatsResponse

            response = await auth_client_user_1.get(TestChats.get_chats_url)
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

            response = await auth_client_user_1.get(TestChats.get_chats_url)
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

            response = await auth_client_user_1.get(TestChats.get_chats_url)
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

            response = await auth_client_user_1.get(TestChats.get_chats_url)
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

            response = await auth_client_user_2.get(TestChats.get_chats_url)

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

            response = await auth_client_user_2.get(TestChats.get_chats_url)

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

            response = await auth_client_user_2.get(TestChats.get_chats_url)
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

            response = await auth_client_user_2.get(TestChats.get_chats_url)

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

            response = await auth_client_user_2.get(TestChats.get_chats_url)

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

            response = await auth_client_user_2.get(TestChats.get_chats_url)
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

            response = await auth_client_user_2.get(TestChats.get_chats_url)
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

            response = await auth_client_user_2.get(TestChats.get_chats_url)
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
            response = await client.get(TestChats.get_chats_url)

            HttpAssertions.assert_unauthorized_error(
                response=response,
                expected_message="Вы не авторизованы! Войдите пожалуйста в аккаунт",
            )

        @pytest.mark.asyncio
        async def test_get_chats_with_invalid_token(self, client):
            """Тест на получение чатов с невалидным токеном"""
            client.headers["Authorization"] = "Bearer invalid_token"
            response = await client.get(TestChats.get_chats_url)

            HttpAssertions.assert_unauthorized_error(
                response=response,
                expected_message="Невалидный токен",
            )

    class TestGetChatMessages:
        """Тесты получения сообщений чата"""

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
                from src.schemas import MessageResponse

                get_messages_url = TestChats.get_messages_url(
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

                async for session in test_db.create_session():
                    await MessageDatabaseAssertions.assert_message_is_read(
                        session, message.id, created_user_2.id
                    )

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

                get_messages_url = TestChats.get_messages_url(
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

                get_messages_url = TestChats.get_messages_url(
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
                get_messages_url = TestChats.get_messages_url(
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
                get_messages_url = TestChats.get_messages_url(
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
                get_messages_url = TestChats.get_messages_url(
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
                get_messages_url = TestChats.get_messages_url(
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

                get_messages_url = TestChats.get_messages_url(
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
                    await MessageDatabaseAssertions.assert_message_is_read(
                        session, message.id, created_user_2.id
                    )

            @pytest.mark.asyncio
            async def test_get_messages_group_with_pagination(
                self,
                auth_client_user_2,
                created_multiple_messages_in_group_1_2_3,
                created_group_user1_user2_user3,
            ):
                """Тест: получение сообщений с пагинацией (page=2, limit=3)"""
                from src.schemas import MessageResponse

                get_messages_url = TestChats.get_messages_url(
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

                get_messages_url = TestChats.get_messages_url(
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
                get_messages_url = TestChats.get_messages_url(
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
                get_messages_url = TestChats.get_messages_url(
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
                get_messages_url = TestChats.get_messages_url(
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
            async def test_get_messages_group_limit_zero(
                self,
                auth_client_user_2,
                created_group_user1_user2_user3,
            ):
                """Тест: limit=0 (невалидное значение)"""
                get_messages_url = TestChats.get_messages_url(
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
                get_messages_url = TestChats.get_messages_url(
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

                get_messages_url = TestChats.get_messages_url(
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
                get_messages_url = TestChats.get_messages_url(uuid4())
                response = await auth_client_user_1.get(
                    get_messages_url, params={"chat_type": ChatType.DIALOGS}
                )
                HttpAssertions.assert_not_found_error(
                    response=response,
                    expected_message="Диалог не найден",
                )

    class TestCreateMessage:
        """Тесты создания сообщений"""

        class TestWithoutFile:
            """Тесты создания сообщения без файла"""

            class TestDialog:
                """Тесты для диалогов"""

                @pytest.mark.asyncio
                async def test_create_text_message_in_dialog_success(
                    self,
                    auth_client_user_1,
                    created_user_1,
                    created_dialog_user1_user2,
                    test_db,
                ):
                    """Тест: создание текстового сообщения в диалоге"""
                    from src.crud import DialogCRUD
                    from src.crud.messages import MessageCRUD

                    chat_id = created_dialog_user1_user2.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.DIALOGS, chat_id=str(chat_id)
                    )
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    assert response.status_code == 200
                    result = response.json()
                    assert result["status"] == "created"
                    assert "message_id" in result

                    # Проверяем, что сообщение создано
                    async for session in test_db.create_session():
                        message = await MessageDatabaseAssertions.assert_message_exists(
                            session=session,
                            message_id=result["message_id"],
                            sender_id=created_user_1.id,
                            content=data["content"],
                        )
                        await DialogDatabaseAssertions.assert_last_message(
                            session=session,
                            dialog_id=chat_id,
                            last_message_id=message.id,
                        )

                @pytest.mark.asyncio
                async def test_create_text_message_with_reply_in_dialog_success(
                    self,
                    auth_client_user_1,
                    created_dialog_user1_user2,
                    created_message_in_dialog_1_2,
                    test_db,
                ):
                    """Тест: создание сообщения с ответом на другое сообщение"""
                    from src.crud import MessageCRUD

                    chat_id = created_dialog_user1_user2.id
                    reply_to_id = created_message_in_dialog_1_2.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.DIALOGS,
                        chat_id=str(chat_id),
                        reply_message_id=reply_to_id,
                    )
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    assert response.status_code == 200
                    result = response.json()

                    async for session in test_db.create_session():
                        await MessageDatabaseAssertions.assert_reply_to_message(
                            session=session,
                            message_id=result["message_id"],
                            reply_to_id=reply_to_id,
                            content=data["content"],
                        )

                @pytest.mark.asyncio
                async def test_create_message_with_sticker_in_dialog_success(
                    self,
                    auth_client_user_1,
                    created_dialog_user1_user2,
                    created_sticker,
                    test_db,
                ):
                    """Тест: создание сообщения со стикером"""
                    from src.crud.messages import MessageCRUD

                    chat_id = created_dialog_user1_user2.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.DIALOGS,
                        chat_id=str(chat_id),
                        message_type=MessageType.STICKER,
                        sticker_id=str(created_sticker.id),
                    )
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    assert response.status_code == 200
                    result = response.json()
                    async for session in test_db.create_session():
                        await MessageDatabaseAssertions.assert_sticker_message(
                            session=session,
                            message_id=result["message_id"],
                            sticker_id=created_sticker.id,
                        )

                @pytest.mark.asyncio
                async def test_create_message_with_sticker_and_reply_in_dialog_success(
                    self,
                    auth_client_user_1,
                    created_dialog_user1_user2,
                    created_sticker,
                    created_message_in_dialog_1_2,
                    test_db,
                ):
                    """Тест: создание сообщения со стикером и ответом"""
                    from src.crud.messages import MessageCRUD

                    chat_id = created_dialog_user1_user2.id
                    reply_to_id = created_message_in_dialog_1_2.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.DIALOGS,
                        chat_id=str(chat_id),
                        message_type=MessageType.STICKER,
                        sticker_id=str(created_sticker.id),
                        reply_message_id=reply_to_id,
                    )
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    assert response.status_code == 200
                    result = response.json()

                    async for session in test_db.create_session():
                        await MessageDatabaseAssertions.assert_reply_to_message(
                            session=session,
                            message_id=result["message_id"],
                            reply_to_id=reply_to_id,
                            content=data["content"],
                        )
                        await MessageDatabaseAssertions.assert_sticker_message(
                            session=session,
                            message_id=result["message_id"],
                            sticker_id=created_sticker.id,
                        )

                @pytest.mark.asyncio
                async def test_create_message_in_dialog_not_member(
                    self,
                    auth_client_user_2,
                    created_dialog_user1_user3,
                ):
                    """Тест: создание сообщения в диалоге, где пользователь не участник"""
                    chat_id = created_dialog_user1_user3.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.DIALOGS, chat_id=str(chat_id)
                    )
                    response = await auth_client_user_2.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    HttpAssertions.assert_error_response(
                        response=response,
                        expected_message="Вы не являетесь участником данного диалога",
                        expected_status=403,
                    )

            class TestGroup:
                """Тесты для групп"""

                @pytest.mark.asyncio
                async def test_create_text_message_in_group_success(
                    self,
                    auth_client_user_1,
                    created_user_1,
                    created_group_user1_user2_user3,
                    test_db,
                ):
                    """Тест: создание текстового сообщения в группе"""
                    from src.crud import GroupCRUD
                    from src.crud.messages import MessageCRUD

                    chat_id = created_group_user1_user2_user3.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.GROUP, chat_id=str(chat_id)
                    )
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    assert response.status_code == 200
                    result = response.json()
                    assert result["status"] == "created"
                    assert "message_id" in result

                    # Проверяем, что сообщение создано
                    async for session in test_db.create_session():
                        message = await MessageDatabaseAssertions.assert_message_exists(
                            session=session,
                            message_id=result["message_id"],
                            sender_id=created_user_1.id,
                            content=data["content"],
                        )
                        await GroupDatabaseAssertions.assert_last_message(
                            session=session,
                            group_id=chat_id,
                            last_message_id=message.id,
                        )

                @pytest.mark.asyncio
                async def test_create_text_message_with_reply_in_group_success(
                    self,
                    auth_client_user_1,
                    created_group_user1_user2_user3,
                    created_message_in_group_1_2_3,
                    test_db,
                ):
                    """Тест: создание сообщения с ответом на другое сообщение"""
                    from src.crud import MessageCRUD

                    chat_id = created_group_user1_user2_user3.id
                    reply_to_id = created_message_in_group_1_2_3.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.GROUP,
                        chat_id=str(chat_id),
                        reply_message_id=reply_to_id,
                    )
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    assert response.status_code == 200
                    result = response.json()

                    # Проверяем reply_to_id
                    async for session in test_db.create_session():
                        await MessageDatabaseAssertions.assert_reply_to_message(
                            session=session,
                            message_id=result["message_id"],
                            reply_to_id=reply_to_id,
                            content=data["content"],
                        )

                @pytest.mark.asyncio
                async def test_create_message_with_sticker_in_group_success(
                    self,
                    auth_client_user_1,
                    created_group_user1_user2_user3,
                    created_sticker,
                    test_db,
                ):
                    """Тест: создание сообщения со стикером"""
                    from src.crud.messages import MessageCRUD

                    chat_id = created_group_user1_user2_user3.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.GROUP,
                        chat_id=str(chat_id),
                        message_type=MessageType.STICKER,
                        sticker_id=str(created_sticker.id),
                    )
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    assert response.status_code == 200
                    result = response.json()
                    async for session in test_db.create_session():
                        await MessageDatabaseAssertions.assert_sticker_message(
                            session=session,
                            message_id=result["message_id"],
                            sticker_id=created_sticker.id,
                        )

                @pytest.mark.asyncio
                async def test_create_message_with_sticker_and_reply_in_group_success(
                    self,
                    auth_client_user_1,
                    created_group_user1_user2_user3,
                    created_sticker,
                    created_message_in_group_1_2_3,
                    test_db,
                ):
                    """Тест: создание сообщения со стикером и ответом"""
                    from src.crud.messages import MessageCRUD

                    chat_id = created_group_user1_user2_user3.id
                    reply_to_id = created_message_in_group_1_2_3.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.GROUP,
                        chat_id=str(chat_id),
                        message_type=MessageType.STICKER,
                        sticker_id=str(created_sticker.id),
                        reply_message_id=reply_to_id,
                    )
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    assert response.status_code == 200
                    result = response.json()

                    async for session in test_db.create_session():
                        await MessageDatabaseAssertions.assert_reply_to_message(
                            session=session,
                            message_id=result["message_id"],
                            reply_to_id=reply_to_id,
                            content=data["content"],
                        )
                        await MessageDatabaseAssertions.assert_sticker_message(
                            session=session,
                            message_id=result["message_id"],
                            sticker_id=created_sticker.id,
                        )

                @pytest.mark.asyncio
                async def test_create_message_in_group_not_member(
                    self,
                    auth_client_user_2,
                    created_group_user1_user3,
                ):
                    """Тест: создание сообщения в группе, где пользователь не участник"""
                    chat_id = created_group_user1_user3.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.GROUP, chat_id=str(chat_id)
                    )
                    response = await auth_client_user_2.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    HttpAssertions.assert_error_response(
                        response=response,
                        expected_message="Вы не являетесь участником группы",
                        expected_status=403,
                    )

            class TestCommon:
                """Общие тесты для всех чатов"""

                @pytest.mark.asyncio
                async def test_create_message_unauthorized(
                    self,
                    client,
                    created_dialog_user1_user2,
                ):
                    """Тест: создание сообщения без авторизации"""
                    chat_id = created_dialog_user1_user2.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.DIALOGS, chat_id=str(chat_id)
                    )
                    response = await client.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    HttpAssertions.assert_unauthorized_error(
                        response=response,
                        expected_message="Вы не авторизованы! Войдите пожалуйста в аккаунт",
                    )

                @pytest.mark.asyncio
                async def test_create_message_invalid_token(
                    self,
                    client,
                    created_dialog_user1_user2,
                ):
                    """Тест: создание сообщения с невалидным токеном"""
                    client.headers["Authorization"] = "Bearer invalid_token"
                    chat_id = created_dialog_user1_user2.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.DIALOGS, chat_id=str(chat_id)
                    )
                    response = await client.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    HttpAssertions.assert_unauthorized_error(
                        response=response,
                        expected_message="Невалидный токен",
                    )

                @pytest.mark.asyncio
                async def test_create_message_non_existent_chat(
                    self,
                    auth_client_user_1,
                ):
                    """Тест: создание сообщения в несуществующем чате"""
                    chat_id = uuid4()
                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.DIALOGS, chat_id=str(chat_id)
                    )
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    HttpAssertions.assert_not_found_error(
                        response=response,
                        expected_message="Диалог не найден",
                    )

                @pytest.mark.asyncio
                async def test_create_message_text_without_content(
                    self,
                    auth_client_user_1,
                    created_dialog_user1_user2,
                ):
                    """Тест: создание текстового сообщения без content"""
                    chat_id = created_dialog_user1_user2.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.DIALOGS, chat_id=str(chat_id), content=None
                    )
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    HttpAssertions.assert_validation_error(
                        response=response,
                        expected_message="Для типа сообщения text, необходимо указать данные content",
                    )

                @pytest.mark.asyncio
                async def test_create_message_sticker_without_sticker_id(
                    self,
                    auth_client_user_1,
                    created_dialog_user1_user2,
                ):
                    """Тест: создание сообщения со стикером без sticker_id"""
                    chat_id = created_dialog_user1_user2.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.DIALOGS,
                        chat_id=str(chat_id),
                        message_type=MessageType.STICKER,
                        sticker_id=None,
                    )
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    HttpAssertions.assert_validation_error(
                        response=response,
                        expected_message="Для типа сообщения sticker, необходимо указать данные sticker_id",
                    )

                @pytest.mark.asyncio
                async def test_create_message_file_without_file_url(
                    self,
                    auth_client_user_1,
                    created_dialog_user1_user2,
                ):
                    """Тест: создание сообщения со стикером без sticker_id"""
                    chat_id = created_dialog_user1_user2.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.DIALOGS,
                        chat_id=str(chat_id),
                        message_type=MessageType.FILE,
                        file_url=None,
                    )
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    HttpAssertions.assert_validation_error(
                        response=response,
                        expected_message="Для типа сообщения file, необходимо указать данные message_file",
                    )

                @pytest.mark.asyncio
                async def test_create_message_with_non_existent_reply(
                    self,
                    auth_client_user_1,
                    created_dialog_user1_user2,
                ):
                    """Тест: создание сообщения с несуществующим reply_message_id"""
                    chat_id = created_dialog_user1_user2.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.DIALOGS,
                        chat_id=str(chat_id),
                        reply_message_id=str(uuid4()),
                    )
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    HttpAssertions.assert_not_found_error(
                        response=response,
                        expected_message="Сообщение не найдено",
                    )

                @pytest.mark.asyncio
                async def test_create_message_with_non_existent_sticker(
                    self,
                    auth_client_user_1,
                    created_dialog_user1_user2,
                ):
                    """Тест: создание сообщения с несуществующим sticker_id"""
                    chat_id = created_dialog_user1_user2.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.DIALOGS,
                        chat_id=str(chat_id),
                        message_type=MessageType.STICKER,
                        sticker_id=str(uuid4()),
                    )
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    HttpAssertions.assert_not_found_error(
                        response=response,
                        expected_message="Стикер не найден",
                    )

                @pytest.mark.asyncio
                async def test_create_message_with_future_timestamp(
                    self,
                    auth_client_user_1,
                    created_dialog_user1_user2,
                ):
                    """Тест: создание сообщения с датой в будущем"""
                    from datetime import datetime, timedelta

                    future_time = datetime.now() + timedelta(days=1)
                    chat_id = created_dialog_user1_user2.id

                    data = MessagesDataFactory.create_message_data(
                        chat_type=ChatType.DIALOGS,
                        chat_id=str(chat_id),
                        created_at=future_time,
                    )
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                    )
                    HttpAssertions.assert_error_response(
                        response=response,
                        expected_message="Дата сообщения не может быть в будущем",
                        expected_status=400,
                    )

        class TestWithFile:
            """Тесты создания сообщения с файлом"""

            base_path = Path(__file__).parent.parent.parent / "test_media"

            @pytest.mark.asyncio
            async def test_create_file_message_with_file_success(
                self,
                created_user_1,
                auth_client_user_1,
                created_dialog_user1_user2,
                test_text_file,
                test_db,
            ):
                """Тест: создание сообщения с типом FILE и файлом text/plain"""
                chat_id = created_dialog_user1_user2.id
                data = MessagesDataFactory.create_message_data(
                    chat_type=ChatType.DIALOGS,
                    chat_id=str(chat_id),
                    message_type=MessageType.FILE,
                    content=None,
                )

                with open(test_text_file, "rb") as f:
                    files = {"message_file": ("test.txt", f, "text/plain")}
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                        files=files,
                    )
                assert response.status_code == 200
                result = response.json()

                async for session in test_db.create_session():
                    message = await MessageDatabaseAssertions.assert_message_exists(
                        session=session,
                        message_id=result["message_id"],
                        sender_id=created_user_1.id,
                    )
                    assert message.type == MessageType.FILE
                    assert message.file_url is not None

                    # Проверяем, что файл сохранен и удаляем его
                    assert (self.base_path / Path(str(message.file_url))).exists()
                    FileFactory.cleanup_test_messages_files(chat_id)

            @pytest.mark.asyncio
            async def test_create_image_message_with_file_success(
                self,
                created_user_1,
                auth_client_user_1,
                created_dialog_user1_user2,
                test_image_file,
                test_db,
            ):
                """Тест: создание сообщения с типом IMAGE и файлом image/jpg"""
                chat_id = created_dialog_user1_user2.id

                data = MessagesDataFactory.create_message_data(
                    chat_type=ChatType.DIALOGS,
                    chat_id=str(chat_id),
                    message_type=MessageType.IMAGE,
                    content=None,
                )
                with open(test_image_file, "rb") as f:
                    files = {"message_file": ("test.jpg", f, "image/jpeg")}
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                        files=files,
                    )
                assert response.status_code == 200
                result = response.json()

                async for session in test_db.create_session():
                    message = await MessageDatabaseAssertions.assert_message_exists(
                        session=session,
                        message_id=result["message_id"],
                        sender_id=created_user_1.id,
                    )
                    assert message.type == MessageType.IMAGE
                    assert message.file_url is not None

                    # Проверяем, что файл сохранен и удаляем его
                    assert (self.base_path / Path(str(message.file_url))).exists()
                    FileFactory.cleanup_test_messages_files(chat_id)

            @pytest.mark.asyncio
            async def test_create_voice_message_with_file_success(
                self,
                created_user_1,
                auth_client_user_1,
                created_dialog_user1_user2,
                test_audio_file,
                test_db,
            ):
                """Тест: создание сообщения с типом VOICE и файлом audio/mpeg"""
                chat_id = created_dialog_user1_user2.id
                data = MessagesDataFactory.create_message_data(
                    chat_type=ChatType.DIALOGS,
                    chat_id=str(chat_id),
                    message_type=MessageType.VOICE,
                    content=None,
                )

                with open(test_audio_file, "rb") as f:
                    files = {"message_file": ("test.mp3", f, "audio/mpeg")}
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                        files=files,
                    )

                HttpAssertions.assert_success_response(response, dict, 200)
                result = response.json()

                async for session in test_db.create_session():
                    message = await MessageDatabaseAssertions.assert_message_exists(
                        session=session,
                        message_id=result["message_id"],
                        sender_id=created_user_1.id,
                    )
                    assert message.type == MessageType.VOICE
                    assert message.file_url is not None

                    # Проверяем, что файл сохранен и удаляем его
                    assert (self.base_path / Path(str(message.file_url))).exists()
                    FileFactory.cleanup_test_messages_files(chat_id)

            @pytest.mark.asyncio
            async def test_create_text_message_with_file_wrong_type(
                self,
                auth_client_user_1,
                created_dialog_user1_user2,
                test_text_file,
            ):
                """Тест: создание сообщения с типом TEXT, но с файлом"""
                chat_id = created_dialog_user1_user2.id

                data = MessagesDataFactory.create_message_data(
                    chat_type=ChatType.DIALOGS,
                    chat_id=str(chat_id),
                )
                with open(test_text_file, "rb") as f:
                    files = {"message_file": ("test.txt", f, "text/plain")}
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                        files=files,
                    )
                HttpAssertions.assert_error_response(
                    response=response,
                    expected_message="Для типа сообщения text, не подходит тип файла text/plain",
                    expected_status=415,
                )

            @pytest.mark.asyncio
            async def test_create_image_message_with_file_wrong_type(
                self,
                auth_client_user_1,
                created_dialog_user1_user2,
                test_text_file,
            ):
                """Тест: создание сообщения с типом IMAGE, но с txt файлом"""
                chat_id = created_dialog_user1_user2.id

                data = MessagesDataFactory.create_message_data(
                    chat_type=ChatType.DIALOGS,
                    chat_id=str(chat_id),
                    message_type=MessageType.IMAGE,
                )

                with open(test_text_file, "rb") as f:
                    files = {"message_file": ("test.txt", f, "text/plain")}
                    response = await auth_client_user_1.post(
                        TestChats.create_message_url,
                        data=data,
                        files=files,
                    )

                HttpAssertions.assert_error_response(
                    response=response,
                    expected_message="Для типа сообщения image, не подходит тип файла text/plain",
                    expected_status=415,
                )
