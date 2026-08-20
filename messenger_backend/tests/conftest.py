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


@pytest.fixture
async def created_user_1(test_db):
    """Создает пользователя (№1) в БД и возвращает его"""
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
async def auth_tokens_user_1(created_user_1):
    """Возвращает JWT токен для авторизованных запросов (Пользователя №1)"""
    from src.services import AuthService

    tokens = AuthService.create_tokens_by_user(created_user_1)
    return tokens


@pytest.fixture
async def auth_client_user_1(client, auth_tokens_user_1):
    """Авторизованный HTTP-клиент (Пользователь №1)"""
    client.headers["Authorization"] = f"Bearer {auth_tokens_user_1.access_token}"
    return client
