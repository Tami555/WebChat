from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import InvalidTokenError as JWTTokenInvalidError


import src.crud.users as crud
from src.models import Users

from src.utils.auth import create_access_token, create_refresh_token, check_access_token, check_refresh_token
from src.exceptions import TokenTypeMismatchError, InvalidTokenError, UserNotFoundError

from src.schemas.enums import TokenType
from src.schemas import TokenResponse


def create_tokens_by_user(
        user: Users
) -> TokenResponse:
    """ Генерация токенов для пользователя """
    access = create_access_token(user=user)
    refresh = create_refresh_token(user=user)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh
    )
    

async def get_user_by_token(
    token: str,
    session: AsyncSession,
) -> Users:
    """ Получение пользователя по токену с проверкой типа """
    try:
        payload = check_access_token(token)
        if not payload:
            raise TokenTypeMismatchError(expected=TokenType.ACCESS_TOKEN)
        
        user = await crud.get_user_by_username(payload.get("sub"), session)
        if not user:
            raise UserNotFoundError()
        
        return user
    except JWTTokenInvalidError:
        raise InvalidTokenError()
    

async def new_access_by_refresh(
    token: str,
    session: AsyncSession
) -> str:
    """Получение нового access токена по refresh токену"""
    try:
        payload = check_refresh_token(token)
        if payload is None:
            raise TokenTypeMismatchError(expected=TokenType.REFRESH_TOKEN)
          
        user = await crud.get_user_by_username(payload.get("sub"), session)
        if user is None:
            raise UserNotFoundError()
        
        return create_access_token(user)

    except (JWTTokenInvalidError, InvalidTokenError):
        raise InvalidTokenError()


async def verify_access_token(token: str) -> bool:
    """ Проверка валидности access токена """
    try:
        payload = check_access_token(token)
        if payload is None:
            raise TokenTypeMismatchError(expected=TokenType.ACCESS_TOKEN)
        return True
    except (JWTTokenInvalidError, InvalidTokenError):
        return False