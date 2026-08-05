from asyncio import current_task
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
)

from src.models import Base
from .config import settings


class DatabaseHelper:
    """Помощник работы с БД"""

    def __init__(self, db_url):
        """Инициализация: создание движка БД и фабрики сессий"""
        self.engine = create_async_engine(
            url=db_url,
            echo=settings.db.echo,
            pool_size=20,
            max_overflow=30,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    async def create_database_tables(self):
        """Создание таблиц в базе данных"""
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def drop_database_tables(self):
        """Удаление таблиц в базе данных"""
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)

    async def create_session(self):
        """Создание сессии с базой данных"""
        async with self.session_factory() as session:
            yield session

    async def create_scoped_session(self):
        """Создание scoped-сессии с базой данных"""
        session = async_scoped_session(
            scopefunc=current_task,
            session_factory=self.session_factory,
        )
        yield session
        await session.remove()


database_helper = DatabaseHelper(settings.db.db_async_url)
