from pydantic import BaseModel

from src.models import Users


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
    def from_user(cls, user: Users):
        return cls(
            sub=user.username,
        )


class AccessTokenContent(RefreshTokenContent):
    phone: str

    @classmethod
    def from_user(cls, user: Users):
        return cls(
            sub=user.username,
            phone=user.phone
        )
