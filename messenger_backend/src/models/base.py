from sqlalchemy.orm import DeclarativeBase, declared_attr

from src.utils.strings import pascal_to_snake


class Base(DeclarativeBase):
    """Базовая БД модель"""

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return pascal_to_snake(cls.__name__)
