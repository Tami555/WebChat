from fastapi import APIRouter, Depends

from src.models import Users
from src.schemas import UserResponse
import src.api.v1.dependencies as dependencies


router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user(user: Users = Depends(dependencies.get_current_user)) -> UserResponse:
    """ Получить всю информацию о текущем авторизованном пользователе"""
    return user
