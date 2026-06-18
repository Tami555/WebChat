import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import InvalidTokenError as JWTTokenInvalidError

import src.crud.users as crud
from src.models import Users
from src.core.security import create_access_token, create_refresh_token, check_access_token, check_refresh_token
from src.exceptions import auth as auth_exc, users as users_exc
from src.schemas.enums import TokenType
from src.schemas import TokenResponse, RegistrationUser, LoginUser


class AuthService:
    """Сервис аутентификации"""

    @staticmethod
    async def register_user(
        session: AsyncSession,
        user_data: RegistrationUser
    ) -> TokenResponse:
        """Регистрация нового пользователя"""
        if await crud.get_user_by_phone(user_data.phone, session) is not None:
            raise users_exc.PhoneAlreadyExistsError()
    
        if await crud.get_user_by_username(user_data.username, session) is not None:
            raise users_exc.UsernameAlreadyExistsError()
    
        # (Будет реализовано) Отправка sms на подтверждение номера телефона
        # После успешного подтверждения -> создаем

        data = user_data.model_dump()
        data["last_seen"] = datetime.datetime.now()
        new_user = await crud.create_user(user_data=data, session=session)
        return AuthService.create_tokens_by_user(user=new_user)
    
    @staticmethod
    async def login_user(
        session: AsyncSession,
        user_data: LoginUser
    ) -> TokenResponse:
        """ Вход пользователя по номеру телефона"""
        login_user = await crud.get_user_by_phone(user_data.phone, session)
        if login_user is None:
            raise users_exc.UserNotFoundError()
    
        # (Будет реализовано) Отправка sms на подтверждение номера телефона
        # После успешного подтверждения -> токены
        return AuthService.create_tokens_by_user(user=login_user)
    
    @staticmethod
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
    
    @staticmethod
    async def get_user_by_token(
        token: str,
        session: AsyncSession,
    ) -> Users:
        """ Получение пользователя по токену с проверкой типа """
        try:
            payload = check_access_token(token)
            if not payload:
                raise auth_exc.TokenTypeMismatchError(expected=TokenType.ACCESS_TOKEN)
        
            user = await crud.get_user_by_username(payload.get("sub"), session)
            if not user:
                raise users_exc.UserNotFoundError()
        
            return user
        except JWTTokenInvalidError:
            raise auth_exc.InvalidTokenError()
    
    @staticmethod
    async def new_access_by_refresh(
        token: str,
        session: AsyncSession
    ) -> str:
        """Получение нового access токена по refresh токену"""
        try:
            payload = check_refresh_token(token)
            if payload is None:
                raise auth_exc.TokenTypeMismatchError(expected=TokenType.REFRESH_TOKEN)
          
            user = await crud.get_user_by_username(payload.get("sub"), session)
            if user is None:
                raise users_exc.UserNotFoundError()
        
            return create_access_token(user)

        except (JWTTokenInvalidError, auth_exc.InvalidTokenError):
            raise auth_exc.InvalidTokenError()

    @staticmethod
    async def verify_access_token(token: str) -> bool:
        """ Проверка валидности access токена """
        try:
            payload = check_access_token(token)
            if payload is None:
                raise auth_exc.TokenTypeMismatchError(expected=TokenType.ACCESS_TOKEN)
            return True
        except (JWTTokenInvalidError, auth_exc.InvalidTokenError):
            return False