import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import InvalidTokenError as JWTTokenInvalidError

from src.crud import UserCRUD
from src.models import Users
from src.core.security import (
    create_access_token,
    create_refresh_token,
    check_access_token,
    check_refresh_token,
)
from src.exceptions.errors import auth as auth_exc, users as users_exc
from src.schemas.enums import TokenType
from src.schemas import (
    TokenResponse,
    RegistrationUserRequest,
    LoginUserRequest,
    PhoneVerificationRequest,
)
from src.services.verification_service import VerificationService


class AuthService:
    """Сервис аутентификации"""

    @staticmethod
    async def request_registration(
        session: AsyncSession, user_data: RegistrationUserRequest
    ) -> str:
        """Запрос на регистрацию - отправка кода"""
        if await UserCRUD.get_user_by_phone(user_data.phone, session) is not None:
            raise users_exc.PhoneAlreadyExistsError()

        if await UserCRUD.get_user_by_username(user_data.username, session) is not None:
            raise users_exc.UsernameAlreadyExistsError()

        # Отправляем код
        return await VerificationService.create_verification(
            phone=user_data.phone,
            data={"username": user_data.username, "phone": user_data.phone},
        )

    @staticmethod
    async def complete_registration(
        session: AsyncSession, verification_data: PhoneVerificationRequest
    ) -> TokenResponse:
        """Завершение регистрации - подтверждение кода и создание пользователя"""
        # Проверяем код
        user_data = await VerificationService.verify_code(
            phone=verification_data.phone, code=verification_data.code
        )
        # Создаем пользователя
        user_data["last_seen"] = datetime.datetime.now()
        new_user = await UserCRUD.create_user(user_data=user_data, session=session)
        # Отдаем токены
        return AuthService.create_tokens_by_user(new_user)

    @staticmethod
    async def request_login(session: AsyncSession, user_data: LoginUserRequest) -> str:
        """Запрос на вход - отправка кода"""
        # Проверяем существование пользователя
        user = await UserCRUD.get_user_by_phone(user_data.phone, session)
        if not user:
            raise users_exc.UserNotFoundError()

        # Отправляем код
        return await VerificationService.create_verification(
            phone=user_data.phone,
            data={"username": user.username, "phone": user_data.phone},
        )

    @staticmethod
    async def complete_login(
        session: AsyncSession, verification_data: PhoneVerificationRequest
    ) -> TokenResponse:
        """Завершение входа - подтверждение кода и выдача токенов"""
        # Проверяем код
        user_data = await VerificationService.verify_code(
            phone=verification_data.phone, code=verification_data.code
        )
        # Получаем пользователя
        user = await UserCRUD.get_user_by_username(
            username=user_data.get("username"), session=session
        )
        if not user:
            raise users_exc.UserNotFoundError()
        # Обновляем вход
        user.last_seen = datetime.datetime.now()
        await session.commit()
        # Отдаем токены
        return AuthService.create_tokens_by_user(user)

    @staticmethod
    def create_tokens_by_user(user: Users) -> TokenResponse:
        """Генерация токенов для пользователя"""
        access = create_access_token(user=user)
        refresh = create_refresh_token(user=user)
        return TokenResponse(access_token=access, refresh_token=refresh)

    @staticmethod
    async def get_user_by_token(
        token: str,
        session: AsyncSession,
    ) -> Users:
        """Получение пользователя по токену с проверкой типа"""
        try:
            payload = check_access_token(token)
            if not payload:
                raise auth_exc.TokenTypeMismatchError(expected=TokenType.ACCESS_TOKEN)

            user = await UserCRUD.get_user_by_username(payload.get("sub"), session)
            if not user:
                raise users_exc.UserNotFoundError()

            return user
        except JWTTokenInvalidError:
            raise auth_exc.InvalidTokenError()

    @staticmethod
    async def new_access_by_refresh(token: str, session: AsyncSession) -> str:
        """Получение нового access токена по refresh токену"""
        try:
            payload = check_refresh_token(token)
            if payload is None:
                raise auth_exc.TokenTypeMismatchError(expected=TokenType.REFRESH_TOKEN)

            user = await UserCRUD.get_user_by_username(payload.get("sub"), session)
            if user is None:
                raise users_exc.UserNotFoundError()

            return create_access_token(user)

        except (JWTTokenInvalidError, auth_exc.InvalidTokenError):
            raise auth_exc.InvalidTokenError()

    @staticmethod
    async def verify_access_token(token: str) -> bool:
        """Проверка валидности access токена"""
        try:
            payload = check_access_token(token)
            if payload is None:
                raise auth_exc.TokenTypeMismatchError(expected=TokenType.ACCESS_TOKEN)
            return True
        except (JWTTokenInvalidError, auth_exc.InvalidTokenError):
            return False
