from typing import Annotated, Union, TYPE_CHECKING
from pydantic import BaseModel, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from src.core.config import settings


if TYPE_CHECKING:
    from src.models import Users  


class RegistrationUserRequest(BaseModel):
    """ Схема регистрации (создание) пользователя """
    username: str
    phone: Annotated[Union[str, PhoneNumber], PhoneNumberValidator(default_region='RU')]


class LoginUserRequest(BaseModel):
    """ Схема входа (авторизации) пользователя """
    phone: Annotated[Union[str, PhoneNumber], PhoneNumberValidator(default_region='RU')]


class PhoneVerificationRequest(BaseModel):
    """ Схема подтверждения телефона пользователя """
    phone: Annotated[Union[str, PhoneNumber], PhoneNumberValidator(default_region='RU')]
    code: str
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError('Код должен состоять из 6 символов')
        return v
    

class VerificationCodeResponse(BaseModel):
    """ Схема успешно отправленного кода проверки телефона  """
    message: str = "Verification code sent"
    expires_in: int = settings.verification.code_ttl // 60
 

class TokenRequest(BaseModel):
    """ Схема отправки токена  """
    token: str


class TokenResponse(BaseModel):
    """ Схема получения токенов """
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class TokenVerifyResponse(BaseModel):
    """ Схема проверки валидности токена """
    is_verify_token: bool


class RefreshTokenContent(BaseModel):
    """ Схема refresh токена """
    sub: str

    @classmethod
    def from_user(cls, user: "Users"):
        return cls(
            sub=user.username,
        )


class AccessTokenContent(RefreshTokenContent):
    """ Схема access токена """
    phone: str

    @classmethod
    def from_user(cls, user: "Users"):
        return cls(
            sub=user.username,
            phone=user.phone
        )
