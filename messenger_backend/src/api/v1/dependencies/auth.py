from typing import Annotated
from fastapi import Depends, Header, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import database_helper
from src.services import AuthService
from src.models import Users


http_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(database_helper.create_scoped_session)
) -> Users | None:
    """ Получение пользователя по токену """
    token = credentials.credentials
    return await AuthService.get_user_by_token(token, session)


async def get_current_user_ws(
    token: Annotated[str, Query()],
    session: AsyncSession = Depends(database_helper.create_scoped_session)
) -> Users:
    """Получение текущего пользователя по токену для WebSocket"""
    user = await AuthService.get_user_by_token(token, session)
    return user