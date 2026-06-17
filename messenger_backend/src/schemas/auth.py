from pydantic import BaseModel

from src.models import Users


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


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
