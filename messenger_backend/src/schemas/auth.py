from typing import Annotated, Union, TYPE_CHECKING
from pydantic import BaseModel, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from src.core.config import settings


if TYPE_CHECKING:
    from src.models import Users  


# === РЕГИСТРАЦИЯ ===
class RegistrationUser(BaseModel):
    username: str
    phone: Annotated[Union[str, PhoneNumber], PhoneNumberValidator(default_region='RU')]


class LoginUser(BaseModel):
    phone: Annotated[Union[str, PhoneNumber], PhoneNumberValidator(default_region='RU')]


# === ВЕРИФИКАЦИЯ ===
class PhoneVerificationRequest(BaseModel):
    phone: Annotated[Union[str, PhoneNumber], PhoneNumberValidator(default_region='RU')]
    code: str
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError('Код должен состоять из 6 символов')
        return v
    

class VerificationCodeResponse(BaseModel):
    message: str = "Verification code sent"
    expires_in: int = settings.verification.code_ttl // 60
 

# === ТОКЕНЫ ===
class TokenRequest(BaseModel):
    token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class TokenVerifyResponse(BaseModel):
    is_verify_token: bool


class RefreshTokenContent(BaseModel):
    sub: str

    @classmethod
    def from_user(cls, user: "Users"):
        return cls(
            sub=user.username,
        )


class AccessTokenContent(RefreshTokenContent):
    phone: str

    @classmethod
    def from_user(cls, user: "Users"):
        return cls(
            sub=user.username,
            phone=user.phone
        )