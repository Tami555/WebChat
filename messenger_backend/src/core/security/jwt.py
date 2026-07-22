import jwt
from datetime import datetime, timedelta, timezone

from src.core.config import settings


def encode_jwt(
    payload: dict,
    expire_minutes: int,
    key: str = settings.auth.app_secret_key,
    algorithm: str = settings.auth.jwt_algorithm,
) -> bytes | str:
    """ Из данных пользователя формируем токен"""
    now = datetime.now(timezone.utc)
    payload["iat"] = now
    payload["exp"] = now + timedelta(minutes=expire_minutes)

    encode = jwt.encode(payload, key, algorithm)
    return encode


def decode_jwt(
    token: str | bytes,
    key: str = settings.auth.app_secret_key,
    algorithm: str = settings.auth.jwt_algorithm
) -> dict:
    """ Из токена получаем данные пользователя """
    decode = jwt.decode(token, key, algorithms=[algorithm,])
    return decode