import pytest
from httpx import AsyncClient, ASGITransport

from unittest.mock import patch
from src.core.config import get_settings


@pytest.fixture(scope="session")
def test_settings():
    """Настройки для тестов"""
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
async def db_session(test_db):
    """Создание сессии БД"""
    async for session in test_db.create_session():
        yield session


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
def user_data():
    """Пользовательские данные"""
    import datetime

    return {
        "username": "tami",
        "phone": "+7-917-123-45-67",
        "code": "234567",
        "last_seen": datetime.datetime.now(),
    }


@pytest.fixture
async def created_user(user_data, db_session):
    """Создает пользователя в БД и возвращает его"""
    from src.crud.users import UserCRUD

    existing = await UserCRUD.get_user_by_phone(user_data["phone"], db_session)
    if not existing:
        user = await UserCRUD.create_user(
            {
                "username": user_data["username"],
                "phone": user_data["phone"],
                "last_seen": user_data["last_seen"],
            },
            db_session,
        )
        return user
    return existing


@pytest.fixture
async def auth_token(created_user):
    """Возвращает JWT токен для авторизованных запросов"""
    from src.services import AuthService

    tokens = AuthService.create_tokens_by_user(created_user)
    return tokens.access_token


@pytest.fixture
async def auth_client(client, auth_token):
    """Авторизованный HTTP-клиент"""
    client.headers["Authorization"] = f"Bearer {auth_token}"
    return client
