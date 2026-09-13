import os
import pytest
from httpx import AsyncClient, ASGITransport

os.environ["WEBCHAT_ENV_FILE"] = ".env.test"


@pytest.fixture(autouse=True)
def override_settings():
    from src.core.config import get_settings

    os.environ["WEBCHAT_ENV_FILE"] = ".env.test"
    get_settings.cache_clear()
    yield
    os.environ.pop("WEBCHAT_ENV_FILE", None)
    get_settings.cache_clear()


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
async def auth_client_user_1(auth_tokens_user_1):
    """Авторизованный HTTP-клиент пользователь-1"""
    from src.main import app

    # новый клиент
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        timeout=30.0,
        headers={"Authorization": f"Bearer {auth_tokens_user_1.access_token}"},
    ) as auth_client:
        yield auth_client


@pytest.fixture
async def auth_client_user_2(auth_tokens_user_2):
    """Авторизованный HTTP-клиент пользователь-2"""
    from src.main import app

    # новый клиент
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        timeout=30.0,
        headers={"Authorization": f"Bearer {auth_tokens_user_2.access_token}"},
    ) as auth_client:
        yield auth_client


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


@pytest.fixture
async def created_group_user1_user3(test_db, created_user_1, created_user_3):
    """Создает группу с пользователем 1 (админ) и участником 3"""
    from src.crud.groups import GroupCRUD
    from tests.fixtures.data import GroupsDataFactory

    group_data = GroupsDataFactory.group_data()
    group_data["created_by"] = created_user_1.id

    async for session in test_db.create_session():
        group = await GroupCRUD.create_group(
            creator_id=created_user_1.id,
            group_data=group_data,
            members_list=[created_user_3.id],
            session=session,
        )
        return group


# ФИКСТУРЫ ДЛЯ СООБЩЕНИЙ
@pytest.fixture
async def created_message_in_dialog_1_2(
    test_db, created_user_1, created_dialog_user1_user2
):
    """Создает сообщение в диалоге, от 1-го пользователя ко 2-му"""
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


@pytest.fixture
async def created_multiple_messages_in_dialog_1_2(
    test_db,
    created_user_1,
    created_user_2,
    created_dialog_user1_user2,
):
    """Создает 3 сообщения в диалоге от 1-го пользователя ко 2-му (все непрочитанные)"""
    from src.crud import MessageCRUD, DialogCRUD
    from src.models.messages import Messages
    from tests.fixtures.data import MessagesDataFactory
    from datetime import datetime

    messages = []
    async for session in test_db.create_session():
        for i in range(3):
            message_data = MessagesDataFactory.message_data(
                content=f"Message {i + 1} from user 1 to user 2!"
            )
            message = Messages(
                sender_id=created_user_1.id,
                dialog_id=created_dialog_user1_user2.id,
                **message_data,
            )
            created_message = await MessageCRUD.create_message(message, session)
            messages.append(created_message)

            await MessageCRUD.create_message_statuses(
                message=created_message,
                read_users_ids=[],
                not_read_users_ids=[created_user_2.id],
                read_at=datetime.now(),
                session=session,
            )
        await DialogCRUD.set_last_message(
            created_dialog_user1_user2, messages[-1], session
        )
    return messages


@pytest.fixture
async def created_multiple_messages_in_group_1_2_3(
    test_db, created_user_1, created_user_2, created_group_user1_user2_user3
):
    """Создает 3 сообщения в группе от 1-го пользователя (все непрочитанные)"""
    from src.crud import MessageCRUD, GroupCRUD
    from src.models.messages import Messages
    from tests.fixtures.data import MessagesDataFactory
    from datetime import datetime

    messages = []
    async for session in test_db.create_session():
        for i in range(3):
            message_data = MessagesDataFactory.message_data(
                content=f"Group message {i+1}!"
            )
            message = Messages(
                sender_id=created_user_1.id,
                group_id=created_group_user1_user2_user3.id,
                **message_data,
            )
            created_message = await MessageCRUD.create_message(message, session)
            messages.append(created_message)

            await MessageCRUD.create_message_statuses(
                message=created_message,
                read_users_ids=[],
                not_read_users_ids=[created_user_2.id],
                read_at=datetime.now(),
                session=session,
            )
        await GroupCRUD.set_last_message(
            created_group_user1_user2_user3, messages[-1], session
        )
    return messages


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


# ФИКСТУРЫ ДЛЯ СТИКЕРОВ
@pytest.fixture
async def created_sticker_pack(test_db):
    """Создает стикерпак"""
    from src.crud import StickerCRUD
    from src.schemas import CreateStickerPackRequest
    from tests.fixtures.data import StickerDataFactory

    pack_data = StickerDataFactory.sticker_pack_data()
    async for session in test_db.create_session():
        pack = await StickerCRUD.create_sticker_pack(
            CreateStickerPackRequest(**pack_data), session
        )
        return pack


@pytest.fixture
async def created_sticker(test_db, created_sticker_pack):
    """Создает стикер"""
    from src.crud.stickers import StickerCRUD
    from src.schemas import CreateStickerRequest
    from tests.fixtures.data.stickers import StickerDataFactory

    sticker_data = StickerDataFactory.sticker_data()
    sticker_data["pack_id"] = created_sticker_pack.id
    async for session in test_db.create_session():
        sticker = await StickerCRUD.create_sticker(
            CreateStickerRequest(**sticker_data), session
        )
        return sticker


# ФИКСТУРЫ ДЛЯ ТЕСТОВЫХ ФАЙЛОВ
@pytest.fixture
def test_text_file():
    """Создает временный текстовый файл для тестов"""
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Test file content for message")
        file_path = Path(f.name)

    yield file_path

    # Удаляем после теста
    if file_path.exists():
        file_path.unlink()


@pytest.fixture
def test_image_file():
    """Создает временный image-файл для тестов"""
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".jpg", delete=False) as f:
        # Записываем простой заглушечный jpg
        f.write(b"\xff\xd8\xff\xdb\x00\x00\x00\x00\xff\xd9")
        file_path = Path(f.name)

    yield file_path

    if file_path.exists():
        file_path.unlink()


@pytest.fixture
def test_audio_file():
    """Создает временный audio-файл для тестов"""
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".mp3", delete=False) as f:
        f.write(b"\xff\xfb\x90\x00\x00\x00\x00\x00")
        file_path = Path(f.name)

    yield file_path

    if file_path.exists():
        file_path.unlink()
