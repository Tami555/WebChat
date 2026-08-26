import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch


@pytest.fixture(scope="session")
def test_settings():
    """Настройки для тестов"""
    from src.core.config import get_settings

    return get_settings(".env.test")


@pytest.fixture(autouse=True)
def override_settings(test_settings):
    """Переопределяем глобальные настройки для всех тестов"""
    import src.core.config

    with patch.object(src.core.config, "settings", test_settings):
        yield


@pytest.fixture
async def test_db():
    """Работа с тестовой БД"""
    from src.core.database import database_helper as test_helper

    await test_helper.create_database_tables()
    yield test_helper
    await test_helper.drop_database_tables()
    await test_helper.engine.dispose()


@pytest.fixture
async def redis_connect():
    """Подключение к redis"""
    from src.core.redis import redis_manager

    await redis_manager.connect()
    yield
    await redis_manager.disconnect()


@pytest.fixture
async def client(test_db):
    """HTTP клиент для тестирования эндпоинтов"""
    from src.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        timeout=30.0,
    ) as client:
        yield client


# ФИКСТУРЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
@pytest.fixture
async def created_user_1(test_db):
    """Создает пользователя-1 в БД и возвращает его"""
    from src.crud.users import UserCRUD
    from src.schemas import CreateUserRequest
    from .fixtures.data import UserDataFactory

    user_data = UserDataFactory.user_1()
    async for db_session in test_db.create_session():
        existing = await UserCRUD.get_user_by_phone(user_data["phone"], db_session)
        if not existing:
            user = await UserCRUD.create_user(
                CreateUserRequest(
                    username=user_data["username"],
                    phone=user_data["phone"],
                    last_seen=user_data["last_seen"],
                ),
                db_session,
            )
            return user
        return existing


@pytest.fixture
async def created_user_2(test_db):
    """Создает пользователя-2 в БД и возвращает его"""
    from src.crud.users import UserCRUD
    from src.schemas import CreateUserRequest
    from .fixtures.data import UserDataFactory

    user_data = UserDataFactory.user_2()
    async for db_session in test_db.create_session():
        existing = await UserCRUD.get_user_by_phone(user_data["phone"], db_session)
        if not existing:
            user = await UserCRUD.create_user(
                CreateUserRequest(
                    username=user_data["username"],
                    phone=user_data["phone"],
                    last_seen=user_data["last_seen"],
                ),
                db_session,
            )
            return user
        return existing


@pytest.fixture
async def created_user_3(test_db):
    """Создает пользователя-3 в БД и возвращает его"""
    from src.crud.users import UserCRUD
    from src.schemas import CreateUserRequest
    from .fixtures.data import UserDataFactory

    user_data = UserDataFactory.user_3()
    async for db_session in test_db.create_session():
        existing = await UserCRUD.get_user_by_phone(user_data["phone"], db_session)
        if not existing:
            user = await UserCRUD.create_user(
                CreateUserRequest(
                    username=user_data["username"],
                    phone=user_data["phone"],
                    last_seen=user_data["last_seen"],
                ),
                db_session,
            )
            return user
        return existing


# ФИКСТУРЫ АВТОРИЗАЦИИ
@pytest.fixture
async def auth_tokens_user_1(created_user_1):
    """Возвращает JWT токен для авторизованных запросов пользователя-1"""
    from src.services import AuthService

    tokens = AuthService.create_tokens_by_user(created_user_1)
    return tokens


@pytest.fixture
async def auth_tokens_user_2(created_user_2):
    """Возвращает JWT токен для авторизованных запросов пользователя-2"""
    from src.services import AuthService

    tokens = AuthService.create_tokens_by_user(created_user_2)
    return tokens


@pytest.fixture
async def auth_client_user_1(client, auth_tokens_user_1):
    """Авторизованный HTTP-клиент пользователь-1"""
    client.headers["Authorization"] = f"Bearer {auth_tokens_user_1.access_token}"
    return client


@pytest.fixture
async def auth_client_user_2(client, auth_tokens_user_2):
    """Авторизованный HTTP-клиент пользователь-2"""
    client.headers["Authorization"] = f"Bearer {auth_tokens_user_2.access_token}"
    return client


# ФИКСТУРЫ ДЛЯ ДИАЛОГОВ
@pytest.fixture
async def created_dialog_user1_user2(test_db, created_user_1, created_user_2):
    """Создает диалог между пользователем 1 и пользователем 2"""
    from src.crud.dialogs import DialogCRUD

    async for session in test_db.create_session():
        dialog = await DialogCRUD.create_dialog(
            creator_id=created_user_1.id,
            interlocutor_id=created_user_2.id,
            session=session,
        )
        return dialog


@pytest.fixture
async def created_dialog_user1_user3(test_db, created_user_1, created_user_3):
    """Создает диалог между пользователем 1 и пользователем 3"""
    from src.crud.dialogs import DialogCRUD

    async for session in test_db.create_session():
        dialog = await DialogCRUD.create_dialog(
            creator_id=created_user_1.id,
            interlocutor_id=created_user_3.id,
            session=session,
        )
        return dialog


# ФИКСТУРЫ ДЛЯ ГРУПП
@pytest.fixture
async def created_group_user1_user2_user3(
    test_db, created_user_1, created_user_2, created_user_3
):
    """Создает группу с пользователем 1 (админ) и участниками 2, 3"""
    from src.crud.groups import GroupCRUD
    from tests.fixtures.data import GroupsDataFactory

    group_data = GroupsDataFactory.group_data()
    group_data["created_by"] = created_user_1.id

    async for session in test_db.create_session():
        group = await GroupCRUD.create_group(
            creator_id=created_user_1.id,
            group_data=group_data,
            members_list=[created_user_2.id, created_user_3.id],
            session=session,
        )
        return group


# ФИКСТУРЫ ДЛЯ СООБЩЕНИЙ
@pytest.fixture
async def created_message_in_dialog_1_2(
    test_db, created_user_1, created_dialog_user1_user2
):
    """Создает сообщение в диалоге пользователей 1 и 2. Сообщение от 1-го к 2-му"""
    from src.crud import MessageCRUD, DialogCRUD
    from src.models.messages import Messages
    from tests.fixtures.data import MessagesDataFactory

    message_data = MessagesDataFactory.message_data(
        content="Hello from user 1 to user 2!"
    )
    async for session in test_db.create_session():
        message = Messages(
            sender_id=created_user_1.id,
            dialog_id=created_dialog_user1_user2.id,
            **message_data,
        )
        created_message = await MessageCRUD.create_message(message, session)
        await DialogCRUD.set_last_message(
            created_dialog_user1_user2, created_message, session
        )
        return created_message


@pytest.fixture
async def created_message_in_group_1_2_3(
    test_db, created_user_1, created_group_user1_user2_user3
):
    """Создает сообщение в группе пользователей 1, 2, 3 от пользователя 1"""
    from src.crud import MessageCRUD, GroupCRUD
    from src.models.messages import Messages
    from tests.fixtures.data import MessagesDataFactory

    message_data = MessagesDataFactory.message_data(
        content="Hello from user 1 in group!"
    )
    async for session in test_db.create_session():
        message = Messages(
            sender_id=created_user_1.id,
            group_id=created_group_user1_user2_user3.id,
            **message_data,
        )
        created_message = await MessageCRUD.create_message(message, session)
        await GroupCRUD.set_last_message(
            created_group_user1_user2_user3, created_message, session
        )
        return created_message


# ФИКСТУРЫ ДЛЯ СТАТУСОВ СООБЩЕНИЙ
@pytest.fixture
async def created_read_message_statuses_in_dialog_1_2(
    test_db, created_message_in_dialog_1_2, created_user_2
):
    """Создает статус для сообщения: прочитано (для user 2)"""
    from src.crud.messages import MessageCRUD
    from datetime import datetime

    async for session in test_db.create_session():
        await MessageCRUD.create_message_statuses(
            message=created_message_in_dialog_1_2,
            read_users_ids=[created_user_2.id],
            not_read_users_ids=[],
            read_at=datetime.now(),
            session=session,
        )
        return created_message_in_dialog_1_2


@pytest.fixture
async def created_not_read_message_statuses_in_dialog_1_2(
    test_db, created_message_in_dialog_1_2, created_user_2
):
    """Создает статус для сообщения: НЕ прочитано (для user 2)"""
    from src.crud.messages import MessageCRUD
    from datetime import datetime

    async for session in test_db.create_session():
        await MessageCRUD.create_message_statuses(
            message=created_message_in_dialog_1_2,
            read_users_ids=[],
            not_read_users_ids=[created_user_2.id],
            read_at=datetime.now(),
            session=session,
        )
        return created_message_in_dialog_1_2


@pytest.fixture
async def created_read_message_statuses_in_group_1_2_3(
    test_db, created_message_in_group_1_2_3, created_user_2, created_user_3
):
    """Создает статус для сообщения: прочитано для всех участников группы (2, 3)"""
    from src.crud.messages import MessageCRUD
    from datetime import datetime

    async for session in test_db.create_session():
        await MessageCRUD.create_message_statuses(
            message=created_message_in_group_1_2_3,
            read_users_ids=[created_user_2.id, created_user_3.id],
            not_read_users_ids=[],
            read_at=datetime.now(),
            session=session,
        )
        return created_message_in_group_1_2_3


@pytest.fixture
async def created_not_read_message_statuses_in_group_1_2_3(
    test_db, created_message_in_group_1_2_3, created_user_2, created_user_3
):
    """Создает статус для сообщения: НЕ прочитано для всех участников группы (2, 3)"""
    from src.crud.messages import MessageCRUD
    from datetime import datetime

    async for session in test_db.create_session():
        await MessageCRUD.create_message_statuses(
            message=created_message_in_group_1_2_3,
            read_users_ids=[],
            not_read_users_ids=[created_user_2.id, created_user_3.id],
            read_at=datetime.now(),
            session=session,
        )
        return created_message_in_group_1_2_3
