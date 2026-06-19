from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import (
    RegistrationUser, TokenResponse, LoginUser,
    TokenRequest, TokenVerifyResponse, PhoneVerificationRequest,
    VerificationCodeResponse
)
from src.core.database import database_helper
from src.services import AuthService


router = APIRouter()


@router.post("/register")
async def register_request(
    user_data: RegistrationUser,
    session: AsyncSession = Depends(database_helper.create_scoped_session)
) -> VerificationCodeResponse:
    """Запрос на регистрацию: Отправляет код верификации на телефон"""
    await AuthService.request_registration(session, user_data)
    return VerificationCodeResponse()


@router.post("/verify-registration", response_model=TokenResponse)
async def complete_registration(
    verification_data: PhoneVerificationRequest,
    session: AsyncSession = Depends(database_helper.create_scoped_session)
) -> TokenResponse:
    """Завершение регистрации: Подтверждение кода и создание пользователя"""
    return await AuthService.complete_registration(session, verification_data)


@router.post("/login")
async def login_request(
    user_data: LoginUser,
    session: AsyncSession = Depends(database_helper.create_scoped_session)
) -> VerificationCodeResponse:
    """Запрос на вход: Отправляет код верификации на телефон
    """
    await AuthService.request_login(session, user_data)
    return VerificationCodeResponse()


@router.post("/verify-login", response_model=TokenResponse)
async def complete_login(
    verification_data: PhoneVerificationRequest,
    session: AsyncSession = Depends(database_helper.create_scoped_session)
) -> TokenResponse:
    """Завершение входа: Подтверждение кода и выдача токенов"""
    return await AuthService.complete_login(session, verification_data)


@router.post("/refresh", response_model=TokenResponse, response_model_exclude_none=True)
async def get_new_tokens(
    credentials: TokenRequest,
    session: AsyncSession = Depends(database_helper.create_scoped_session)
) -> TokenResponse:
    """ Генерация нового access токена по refresh токену """
    access = await AuthService.new_access_by_refresh(credentials.token, session)
    return TokenResponse(access_token=access)


@router.post("/verify", response_model=TokenVerifyResponse)
async def verify_tokens(
    credentials: TokenRequest
) -> TokenVerifyResponse:
    """ Проверка валидности access токена """
    is_verify = await AuthService.verify_access_token(credentials.token)
    return TokenVerifyResponse(is_verify_token=is_verify)
