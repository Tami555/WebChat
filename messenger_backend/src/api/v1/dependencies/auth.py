from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import database_helper
from src.services import auth_service
from src.models import Users


http_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(database_helper.create_scope_session)
) -> Users | None:
    """ Получение пользователя по токену """
    token = credentials.credentials
    return await auth_service.get_user_by_token(token, session)