from src.core.config import settings
from src.core.security.tokens import create_jwt_token
from src.schemas.enums import TokenType


def create_homemade_jwt_token(
    username: str,
    is_access: bool = True,
    expired: bool = False,
) -> bytes:
    """Создает самодельный jwt токен"""
    return create_jwt_token(
        type_token=TokenType.ACCESS_TOKEN if is_access else TokenType.REFRESH_TOKEN,
        payload={"sub": username},
        expire_minutes=0 if expired else settings.auth.expire_refresh_token_minutes,
    )
