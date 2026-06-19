from pydantic import BaseModel
from pathlib import Path
from pydantic_settings import SettingsConfigDict, BaseSettings


BASE_PATH = Path(__file__).parent.parent.parent.parent


class VerificationConfig(BaseModel):
    code_ttl: int =  300
    max_attempts: int = 3


class RedisNamespaces(BaseSettings):
    phone_verification: str = "phone:verification"
    user_online: str = "user:online"


class RedisConfig(BaseSettings):    
    host: str = "localhost"
    port: int = 6379
    db: int = 0    
    namespaces: RedisNamespaces = RedisNamespaces()
    
    @property
    def url(self) -> str:
        """URL для подключения к Redis"""
        return f"redis://{self.host}:{self.port}/{self.db}"


class Settings(BaseSettings):
    # Database
    db_user: str
    db_password: str
    db_name: str
    db_host: str = "localhost"
    db_port: str = 5432

    @property
    def db_async_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # JWT Authentication
    app_secret_key: str
    jwt_algorithm: str = "HS256"
    expire_access_token_minutes: int = 60 # 1 час
    expire_refresh_token_minutes: int = 43200 # 30 дней

    # Redis
    redis: RedisConfig = RedisConfig()

    # Верификация номера телефона
    verification: VerificationConfig = VerificationConfig()

    model_config = SettingsConfigDict(
        env_file=BASE_PATH / ".env",
        env_file_encoding="utf-8"
    )


settings = Settings()