from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import RegistrationUser, TokenResponse, LoginUser, TokenRequest, TokenVerifyResponse
from src.core.database import database_helper
from src.services import AuthService


router = APIRouter()


@router.post('/registration')
async def register_user(
    user_data: RegistrationUser,
    session: AsyncSession = Depends(database_helper.create_scoped_session)
) -> TokenResponse:
    """ Регистрация пользователя """
    return await AuthService.register_user(session=session, user_data=user_data)


@router.post('/login')
async def login_user(
    user_data: LoginUser,
    session: AsyncSession = Depends(database_helper.create_scoped_session)
) -> TokenResponse:
    """ Вход пользователя """
    return await AuthService.login_user(session=session, user_data=user_data)


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
