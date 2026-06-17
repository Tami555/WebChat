import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import src.crud.users as crud
from src.schemas import UserCreate, TokenResponse, UserLogin, TokenRequest, TokenVerifyResponse
from src.core.database import database_helper
from src.exceptions import PhoneAlreadyExistsError, UsernameAlreadyExistsError, UserNotFoundError
from src.services import auth_service


router = APIRouter()


@router.post('/registration')
async def create_user(
    user: UserCreate,
    session: AsyncSession = Depends(database_helper.create_scope_session)
) -> TokenResponse:
    """ Создание нового пользователя """
    if await crud.get_user_by_phone(user.phone, session) is not None:
        raise PhoneAlreadyExistsError()
    
    if await crud.get_user_by_username(user.username, session) is not None:
        raise UsernameAlreadyExistsError()
    
    # (Будет реализовано) Отправка sms на подтверждение номера телефона
    # После успешного подтверждения -> создаем

    data = user.model_dump()
    data["last_seen"] = datetime.datetime.now()

    new_user = await crud.create_user(user_data=data, session=session)
    return auth_service.create_tokens_by_user(user=new_user)


@router.post('/login')
async def login_user(
    user: UserLogin,
    session: AsyncSession = Depends(database_helper.create_scope_session)
) -> TokenResponse:
    """ Вход (аутентификация) пользователя по номеру телефона"""
    login_user = await crud.get_user_by_phone(user.phone, session)
    if login_user is None:
        raise UserNotFoundError()
    
    # (Будет реализовано) Отправка sms на подтверждение номера телефона
    # После успешного подтверждения -> токены

    return auth_service.create_tokens_by_user(user=login_user)


@router.post("/refresh", response_model=TokenResponse, response_model_exclude_none=True)
async def get_new_tokens(
    credentials: TokenRequest,
    session: AsyncSession = Depends(database_helper.create_scope_session)
) -> TokenResponse:
    """ Генерация нового access токена по refresh токену """
    access = await auth_service.new_access_by_refresh(credentials.token, session)
    return TokenResponse(access_token=access)


@router.post("/verify/", response_model=TokenVerifyResponse)
async def verify_tokens(
    credentials: TokenRequest
) -> TokenVerifyResponse:
    """ Проверка валидности access токена """
    is_verify = await auth_service.verify_access_token(credentials.token)
    return TokenVerifyResponse(is_verify_token=is_verify)
