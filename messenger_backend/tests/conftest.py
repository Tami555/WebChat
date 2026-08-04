import pytest
from httpx import AsyncClient, ASGITransport


@pytest.fixture
def test_db_url():
    from src.core.config import settings

    db_name = "web_chat_testing_db"
    config_db = settings.db
    return f"postgresql+asyncpg://{config_db.user}:{config_db.password}@{config_db.host}:{config_db.port}/{db_name}"


@pytest.fixture
async def test_db(test_db_url):
    """Работа с тестовой БД"""
    from src.core.database import DatabaseHelper

    test_helper = DatabaseHelper(test_db_url)
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
async def client(test_db, db_session):
    """HTTP клиент для тестирования эндпоинтов"""
    from src.main import app
    from src.core.database import database_helper

    async def override_get_db():
        yield db_session

    # Переопределяем зависимость в приложении
    app.dependency_overrides[database_helper.create_scoped_session] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        timeout=30.0,
    ) as client:
        yield client

    # Очищаем переопределения после теста
    app.dependency_overrides.clear()


@pytest.fixture
def user_data():
    """Пользовательские данные"""
    import datetime

    return {
        "username": "tami",
        "phone": "+79171234567",
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
