import uuid
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column


class UUIDPrimaryKey:
    """Первичный ключ на основе UUID"""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )


class IntPrimaryKey:
    """Целочисленный первичный ключ"""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
