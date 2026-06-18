from asyncio import current_task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_scoped_session

from src.models import Base
from .config import settings


class DatabaseHelper:
    def __init__(self, db_url):
        self.engine = create_async_engine(
            url=db_url,
            echo=True,
            pool_size=20, 
            max_overflow=30
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )

    async def create_database(self):
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def create_session(self):
        async with self.session_factory() as session:
            yield session

    async def create_scoped_session(self):
        session = async_scoped_session(
            scopefunc=current_task,
            session_factory=self.session_factory
        )
        yield session
        await session.remove()


database_helper = DatabaseHelper(settings.db_async_url)