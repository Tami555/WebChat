import logging
import os
from functools import lru_cache

from pydantic import BaseModel
from pathlib import Path
from pydantic_settings import SettingsConfigDict, BaseSettings

logger = logging.getLogger(__name__)
BASE_PATH = Path(__file__).parent.parent.parent.parent


class BaseAppConfig(BaseModel):
    """Базовая конфигурация всего приложения"""

    environment: str = ""


class LoggingConfig(BaseModel):
    """Конфигурация логирования"""

    level: str = "INFO"
    format: str = "[%(asctime)s] - %(levelname)s - %(module) -> %(message)s"
    datefmt: str = "%Y-%m-%d %H:%M:%S"

    def get_level(self) -> int:
        return getattr(logging, self.level.upper(), logging.INFO)


class VerificationConfig(BaseModel):
    """Конфигурация верификации номера телефона"""

    code_ttl: int = 300  # 5 минут
    max_attempts: int = 3


class DatabaseConfig(BaseModel):
    """Конфигурация Базы данных"""

    user: str = ""
    password: str = ""
    name: str = ""
    host: str = "localhost"
    port: str = 5432
    echo: bool = True

    @property
    def db_async_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class AuthenticationConfig(BaseModel):
    """Конфигурация Авторизации/Аутентификации"""

    app_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    expire_access_token_minutes: int = 60  # 1 час
    expire_refresh_token_minutes: int = 43200  # 30 дней


class RedisNamespaces(BaseModel):
    """Названия ключей Redis"""

    phone_verification: str = "phone:verification"
    users_online: str = "online:users"
    ws_server_user: str = "ws:server"
    pubsub_server: str = "pubsub:server"


class RedisConfig(BaseModel):
    """Конфигурация Redis"""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    namespaces: RedisNamespaces = RedisNamespaces()

    @property
    def url(self) -> str:
        """URL для подключения к Redis"""
        return f"redis://{self.host}:{self.port}/{self.db}"


class Settings(BaseSettings):
    app: BaseAppConfig = BaseAppConfig()
    logging: LoggingConfig = LoggingConfig()
    verification: VerificationConfig = VerificationConfig()
    db: DatabaseConfig = DatabaseConfig()
    auth: AuthenticationConfig = AuthenticationConfig()
    redis: RedisConfig = RedisConfig()

    model_config = SettingsConfigDict(
        env_file=BASE_PATH / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="WEBCHAT_",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Получить настройки (кэшируется)"""
    env_file = os.getenv("WEBCHAT_ENV_FILE", ".env")
    logger.debug(f"Используется файл {env_file}")
    env_path = BASE_PATH / env_file
    return Settings(_env_file=env_path)
