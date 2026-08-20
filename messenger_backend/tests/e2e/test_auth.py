import pytest


class TestAuth:
    """Тесты авторизации"""

    class TestRegistration:
        """Тесты регистрации"""

        class TestRequest:
            """Тесты запроса на регистрацию"""

            registration_request_url = "/api/v1/auth/register"

            @pytest.mark.asyncio
            async def test_request_registration_success(self, redis_connect, client):
                """Тест на успешный запрос регистрации"""
                from src.schemas import VerificationCodeResponse
                from src.core.redis import verification_redis
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.registration_request_url,
                    json={
                        "username": user_data["username"],
                        "phone": user_data["phone"],
                    },
                )

                assert response.status_code == 200
                VerificationCodeResponse(**response.json())

                redis_data = await verification_redis.get(user_data["phone"])
                assert redis_data is not None
                assert "data" in redis_data
                assert redis_data.get("code") == user_data["code"]

            @pytest.mark.asyncio
            async def test_request_registration_with_existing_phone(
                self, created_user_1, redis_connect, client
            ):
                """Тест запроса регистрации с существующим телефоном"""
                from tests.fixtures.data import UserDataFactory

                user_data_1 = UserDataFactory.user_1()
                user_data_2 = UserDataFactory.user_2()

                response = await client.post(
                    self.registration_request_url,
                    json={
                        "username": user_data_2["username"],
                        "phone": user_data_1["phone"],
                    },
                )
                assert response.status_code == 409
                data = response.json()
                assert data["error"] is True
                assert (
                    data["message"] == "Пользователь с таким телефоном уже существует"
                )

            @pytest.mark.asyncio
            async def test_request_registration_with_existing_username(
                self, created_user_1, redis_connect, client
            ):
                """Тест запроса регистрации с существующим username"""
                from tests.fixtures.data import UserDataFactory

                user_data_1 = UserDataFactory.user_1()
                user_data_2 = UserDataFactory.user_2()

                response = await client.post(
                    self.registration_request_url,
                    json={
                        "username": user_data_1["username"],
                        "phone": user_data_2["phone"],
                    },
                )
                assert response.status_code == 409
                data = response.json()
                assert data["error"] is True
                assert data["message"] == "Пользователь с таким username уже существует"

            @pytest.mark.asyncio
            async def test_request_registration_without_phone(self, client):
                """Тест запроса регистрации без указания телефона"""
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.registration_request_url,
                    json={"username": user_data["username"]},
                )
                assert response.status_code == 422
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True
                assert data["message"] == "Невалидные данные  !!!"

            @pytest.mark.asyncio
            async def test_request_registration_without_username(self, client):
                """Тест запроса регистрации без указания username"""
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.registration_request_url,
                    json={"phone": user_data["phone"]},
                )
                assert response.status_code == 422
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True
                assert data["message"] == "Невалидные данные  !!!"

        class TestComplete:
            """Тесты подтверждения регистрации"""

            registration_verify_url = "/api/v1/auth/verify-registration"

            @pytest.mark.asyncio
            async def test_complete_registration_success(
                self, redis_connect, client, test_db
            ):
                """Тест на успешное подтверждение регистрации и создание пользователя"""
                from src.core.redis import verification_redis
                from src.schemas import TokenResponse
                from src.crud import UserCRUD
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                phone, code, username = (
                    user_data["phone"],
                    user_data["code"],
                    user_data["username"],
                )
                # Сохраняем данные в Redis
                await verification_redis.save(
                    phone,
                    code,
                    {
                        "username": username,
                        "phone": phone,
                    },
                )
                # Запрос подтверждения
                response = await client.post(
                    self.registration_verify_url,
                    json={"code": code, "phone": phone},
                )
                assert response.status_code == 200
                TokenResponse(**response.json())

                # Проверяем наличие пользователя в БД
                async for db_session in test_db.create_session():
                    new_user = await UserCRUD.get_user_by_phone(phone, db_session)
                    assert new_user is not None
                    assert new_user.username == username
                    assert new_user.phone == phone

                # Проверка, что в Redis значение удалено
                redis_data = await verification_redis.get(phone)
                assert redis_data is None

            @pytest.mark.asyncio
            async def test_complete_registration_without_redis_data(
                self, redis_connect, client
            ):
                """Тест запроса подтверждения регистрации, без данных в Redis"""
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.registration_verify_url,
                    json={"code": user_data["code"], "phone": user_data["phone"]},
                )
                assert response.status_code == 400
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True
                assert data["message"] == "Время действия кода верификации истекло"

            @pytest.mark.asyncio
            async def test_complete_registration_with_too_many_attempts(
                self, redis_connect, client
            ):
                """Тест запроса подтверждения регистрации, с большим количеством попыток"""
                from src.core.redis import verification_redis
                from src.core.config import settings
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                # Сохраняем данные в Redis
                await verification_redis.save(
                    user_data["phone"],
                    user_data["code"],
                    {
                        "username": user_data["username"],
                        "phone": user_data["phone"],
                    },
                )
                # Увеличиваем попытки
                for att in range(settings.verification.max_attempts):
                    await verification_redis.increment_attempts(user_data["phone"])

                # Запрос подтверждения
                response = await client.post(
                    self.registration_verify_url,
                    json={"code": user_data["code"], "phone": user_data["phone"]},
                )
                assert response.status_code == 400
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True
                assert data["message"] == "Слишком много попыток"

            @pytest.mark.asyncio
            async def test_complete_registration_with_invalid_code(
                self, redis_connect, client
            ):
                """Тест запроса подтверждения регистрации с неправильным кодом"""
                from src.core.redis import verification_redis
                from tests.fixtures.data import UserDataFactory

                user_data_1 = UserDataFactory.user_1()
                user_data_2 = UserDataFactory.user_2()

                # Сохраняем данные в Redis
                await verification_redis.save(
                    user_data_1["phone"],
                    user_data_1["code"],
                    {
                        "username": user_data_1["username"],
                        "phone": user_data_1["phone"],
                    },
                )
                # Запрос подтверждения с неверным кодом
                response = await client.post(
                    self.registration_verify_url,
                    json={"code": user_data_2["code"], "phone": user_data_1["phone"]},
                )
                assert response.status_code == 400
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True

                # Проверка, что попытки увеличились
                redis_data = await verification_redis.get(user_data_1["phone"])
                assert redis_data is not None
                assert redis_data["code"] == user_data_1["code"]
                assert int(redis_data["attempts"]) == 1

            @pytest.mark.asyncio
            async def test_complete_registration_without_redis_user_data(
                self, redis_connect, client
            ):
                """Тест запроса подтверждения регистрации, с пустыми данными о пользователе в Redis"""
                from pydantic import ValidationError

                from src.core.redis import verification_redis
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                # Сохраняем данные в Redis (без данных о пользователе)
                await verification_redis.save(user_data["phone"], user_data["code"], {})
                with pytest.raises(ValidationError):
                    # Запрос подтверждения
                    response = await client.post(
                        self.registration_verify_url,
                        json={
                            "code": user_data["code"],
                            "phone": user_data["phone"],
                        },
                    )
                    assert response.status_code == 422
                    data = response.json()
                    assert "error" in data and "message" in data
                    assert data["error"] is True
                    assert data["message"] == "Невалидные данные  !!!"

            @pytest.mark.asyncio
            async def test_complete_registration_without_phone(self, client):
                """Тест запроса подтверждения регистрации без указания телефона"""
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.registration_verify_url,
                    json={"code": user_data["code"]},
                )
                assert response.status_code == 422
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True
                assert data["message"] == "Невалидные данные  !!!"

            @pytest.mark.asyncio
            async def test_complete_registration_without_code(self, client):
                """Тест запроса подтверждения регистрации без указания кода"""
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.registration_verify_url,
                    json={"phone": user_data["phone"]},
                )
                assert response.status_code == 422
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True
                assert data["message"] == "Невалидные данные  !!!"

            @pytest.mark.asyncio
            async def test_complete_registration_with_incorrect_code(self, client):
                """Тест запроса подтверждения регистрации с некорректным кодом"""
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.registration_verify_url,
                    json={"code": "", "phone": user_data["phone"]},
                )
                assert response.status_code == 422
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True
                assert data["message"] == "Невалидные данные  !!!"
                assert "Код должен состоять из 6 символов" in data["detail"]

        @pytest.mark.asyncio
        async def test_full_registration_success(self, redis_connect, client):
            """Тест на полную успешную регистрацию"""
            from tests.fixtures.data import UserDataFactory

            user_data = UserDataFactory.user_1()

            reg = await client.post(
                self.TestRequest.registration_request_url,
                json={"username": user_data["username"], "phone": user_data["phone"]},
            )
            assert reg.status_code == 200

            ver = await client.post(
                self.TestComplete.registration_verify_url,
                json={"code": user_data["code"], "phone": user_data["phone"]},
            )
            assert ver.status_code == 200

    class TestLogin:
        """Тесты входа (авторизации)"""

        class TestRequest:
            """Тесты запроса на вход"""

            login_request_url = "/api/v1/auth/login"

            @pytest.mark.asyncio
            async def test_request_login_success(
                self, redis_connect, created_user_1, client
            ):
                """Тест на успешный запрос входа"""
                from src.schemas import VerificationCodeResponse
                from src.core.redis import verification_redis
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.login_request_url,
                    json={"phone": user_data["phone"]},
                )

                assert response.status_code == 200
                VerificationCodeResponse(**response.json())

                redis_data = await verification_redis.get(user_data["phone"])
                assert redis_data is not None
                assert "data" in redis_data
                assert redis_data.get("code") == user_data["code"]

            @pytest.mark.asyncio
            async def test_request_login_with_not_existing_user(self, client):
                """Тест запроса входа для несуществующего пользователя"""
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.login_request_url,
                    json={"phone": user_data["phone"]},
                )

                assert response.status_code == 404
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True
                assert data["message"] == "Пользователь не найден"

            @pytest.mark.asyncio
            async def test_request_login_without_phone(self, client):
                """Тест запроса входа без указания телефона"""

                response = await client.post(
                    self.login_request_url,
                    json={},
                )
                assert response.status_code == 422
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True
                assert data["message"] == "Невалидные данные  !!!"

        class TestComplete:
            """Тесты подтверждения входа"""

            login_verify_url = "/api/v1/auth/verify-login"

            @pytest.mark.asyncio
            async def test_complete_login_success(
                self, redis_connect, created_user_1, client
            ):
                """Тест на успешное подтверждение входа"""
                from src.core.redis import verification_redis
                from src.schemas import TokenResponse
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                # Сохраняем данные в Redis
                await verification_redis.save(
                    user_data["phone"],
                    user_data["code"],
                    {"username": user_data["username"], "phone": user_data["phone"]},
                )
                # Запрос подтверждения
                response = await client.post(
                    self.login_verify_url,
                    json={"code": user_data["code"], "phone": user_data["phone"]},
                )
                assert response.status_code == 200
                TokenResponse(**response.json())

                # Проверка, что в Redis значение удалено
                redis_data = await verification_redis.get(user_data["phone"])
                assert redis_data is None

            @pytest.mark.asyncio
            async def test_complete_login_without_redis_data(
                self, redis_connect, created_user_1, client
            ):
                """Тест запроса подтверждения входа, без данных в Redis"""
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.login_verify_url,
                    json={"code": user_data["code"], "phone": user_data["phone"]},
                )
                assert response.status_code == 400
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True
                assert data["message"] == "Время действия кода верификации истекло"

            @pytest.mark.asyncio
            async def test_complete_login_with_too_many_attempts(
                self, redis_connect, created_user_1, client
            ):
                """Тест запроса подтверждения входа, с большим количеством попыток"""
                from src.core.redis import verification_redis
                from src.core.config import settings
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                # Сохраняем данные в Redis
                await verification_redis.save(
                    user_data["phone"],
                    user_data["code"],
                    {"username": user_data["username"], "phone": user_data["phone"]},
                )
                # Увеличиваем попытки
                for att in range(settings.verification.max_attempts):
                    await verification_redis.increment_attempts(user_data["phone"])

                # Запрос подтверждения
                response = await client.post(
                    self.login_verify_url,
                    json={"code": user_data["code"], "phone": user_data["phone"]},
                )
                assert response.status_code == 400
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True
                assert data["message"] == "Слишком много попыток"

            @pytest.mark.asyncio
            async def test_complete_login_with_invalid_code(
                self, redis_connect, created_user_1, client
            ):
                """Тест запроса подтверждения входа с неправильным кодом"""
                from src.core.redis import verification_redis
                from tests.fixtures.data import UserDataFactory

                user_data_1 = UserDataFactory.user_1()
                user_data_2 = UserDataFactory.user_2()

                # Сохраняем данные в Redis
                await verification_redis.save(
                    user_data_1["phone"],
                    user_data_1["code"],
                    {
                        "username": user_data_1["username"],
                        "phone": user_data_1["phone"],
                    },
                )
                # Запрос подтверждения с неверным кодом
                response = await client.post(
                    self.login_verify_url,
                    json={"code": user_data_2["code"], "phone": user_data_1["phone"]},
                )
                assert response.status_code == 400
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True

                # Проверка, что попытки увеличились
                redis_data = await verification_redis.get(user_data_1["phone"])
                assert redis_data is not None
                assert redis_data["code"] == user_data_1["code"]
                assert int(redis_data["attempts"]) == 1

            @pytest.mark.asyncio
            async def test_complete_login_with_empty_redis_user_data(
                self, redis_connect, created_user_1, client
            ):
                """Тест запроса подтверждения входа, с пустыми данными о пользователе в Redis"""
                from src.core.redis import verification_redis
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                # Сохраняем данные в Redis (без данных о пользователе)
                await verification_redis.save(user_data["phone"], user_data["code"], {})

                # Запрос подтверждения
                response = await client.post(
                    self.login_verify_url,
                    json={"code": user_data["code"], "phone": user_data["phone"]},
                )
                assert response.status_code == 404
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True
                assert data["message"] == "Пользователь не найден"

            @pytest.mark.asyncio
            async def test_complete_login_without_phone(self, client):
                """Тест запроса подтверждения входа без указания телефона"""
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.login_verify_url,
                    json={"code": user_data["code"]},
                )
                assert response.status_code == 422
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True
                assert data["message"] == "Невалидные данные  !!!"

            @pytest.mark.asyncio
            async def test_complete_login_without_code(self, client):
                """Тест запроса подтверждения входа без указания кода"""
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.login_verify_url,
                    json={"phone": user_data["phone"]},
                )
                assert response.status_code == 422
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True
                assert data["message"] == "Невалидные данные  !!!"

            @pytest.mark.asyncio
            async def test_complete_login_with_incorrect_code(self, client):
                """Тест запроса подтверждения входа с некорректным кодом"""
                from tests.fixtures.data import UserDataFactory

                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.login_verify_url,
                    json={"code": "", "phone": user_data["phone"]},
                )
                assert response.status_code == 422
                data = response.json()
                assert "error" in data and "message" in data
                assert data["error"] is True
                assert data["message"] == "Невалидные данные  !!!"
                assert "Код должен состоять из 6 символов" in data["detail"]

        @pytest.mark.asyncio
        async def test_full_login_success(self, redis_connect, created_user_1, client):
            """Тест на полную успешную авторизацию"""
            from tests.fixtures.data import UserDataFactory

            user_data = UserDataFactory.user_1()

            reg = await client.post(
                self.TestRequest.login_request_url,
                json={"phone": user_data["phone"]},
            )
            assert reg.status_code == 200

            ver = await client.post(
                self.TestComplete.login_verify_url,
                json={"code": user_data["code"], "phone": user_data["phone"]},
            )
            assert ver.status_code == 200

    class TestRefreshToken:
        """Тесты получения нового access (jwt) токена"""

        refresh_token_url = "/api/v1/auth/refresh"

        @pytest.mark.asyncio
        async def test_get_new_token_success(self, auth_tokens_user_1, client):
            """Тест на успешное получение нового access токена по refresh"""
            from src.schemas import TokenResponse

            response = await client.post(
                self.refresh_token_url, json={"token": auth_tokens_user_1.refresh_token}
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data and "token_type" in data
            assert data["token_type"] == "Bearer"
            TokenResponse(**data)

        @pytest.mark.asyncio
        async def test_get_new_token_by_access_token(self, auth_tokens_user_1, client):
            """Тест запроса на получение нового access токена по access. Неверный тип токена"""
            response = await client.post(
                self.refresh_token_url, json={"token": auth_tokens_user_1.access_token}
            )
            assert response.status_code == 401
            data = response.json()
            assert "error" in data and "message" in data
            assert data["error"] is True
            assert data["message"] == "Неверный тип токена. Ожидался: refresh"

        @pytest.mark.asyncio
        async def test_get_new_token_by_refresh_token_not_existing_user(self, client):
            """Тест запроса на получение нового access токена по refresh, не существующего пользователя"""
            from src.core.config import settings
            from src.core.security.tokens import create_jwt_token
            from src.schemas.enums import TokenType

            refresh_token = create_jwt_token(
                type_token=TokenType.REFRESH_TOKEN,
                payload={"sub": "user-1"},
                expire_minutes=settings.auth.expire_refresh_token_minutes,
            )
            response = await client.post(
                self.refresh_token_url, json={"token": refresh_token}
            )
            assert response.status_code == 404
            data = response.json()
            assert "error" in data and "message" in data
            assert data["error"] is True
            assert data["message"] == "Пользователь не найден"

        @pytest.mark.asyncio
        async def test_get_new_token_by_expired_refresh_token(
            self, created_user_1, client
        ):
            """Тест запроса на получение нового access токена по refresh, истекшему по времени"""
            from src.core.security.tokens import create_jwt_token
            from src.schemas.enums import TokenType
            from tests.fixtures.data import UserDataFactory

            user_data = UserDataFactory.user_1()

            refresh_token = create_jwt_token(
                type_token=TokenType.REFRESH_TOKEN,
                payload={"sub": user_data["username"]},
                expire_minutes=0,
            )

            response = await client.post(
                self.refresh_token_url, json={"token": refresh_token}
            )
            assert response.status_code == 401
            data = response.json()
            assert "error" in data and "message" in data
            assert data["error"] is True
            assert data["message"] == "Невалидный токен"

        @pytest.mark.asyncio
        async def test_get_new_token_without_refresh_token(self, client):
            """Тест запроса на получение нового access токена, без refresh токена"""

            response = await client.post(self.refresh_token_url, json={})
            assert response.status_code == 422
            data = response.json()
            assert "error" in data and "message" in data
            assert data["error"] is True
            assert data["message"] == "Невалидные данные  !!!"

    class TestVerifyToken:
        verify_token_url = "/api/v1/auth/verify"

        @pytest.mark.asyncio
        async def test_verify_token_success(self, auth_tokens_user_1, client):
            """Тест на успешную проверку валидности access токена"""
            from src.schemas import TokenVerifyResponse

            response = await client.post(
                self.verify_token_url, json={"token": auth_tokens_user_1.access_token}
            )
            assert response.status_code == 200
            data = TokenVerifyResponse(**response.json())
            assert data.is_verify_token is True

        @pytest.mark.asyncio
        async def test_verify_token_by_refresh_token(self, auth_tokens_user_1, client):
            """Тест запроса на проверку валидности access токена по refresh токену (Неверный тип токена)"""

            response = await client.post(
                self.verify_token_url, json={"token": auth_tokens_user_1.refresh_token}
            )
            assert response.status_code == 401
            data = response.json()
            assert "error" in data and "message" in data
            assert data["error"] is True
            assert data["message"] == "Неверный тип токена. Ожидался: access"

        @pytest.mark.asyncio
        async def test_verify_token_by_expired_access_token(self, client):
            """Тест запроса на проверку валидности access токена истекшему по времени"""
            from src.core.security.tokens import create_jwt_token
            from src.schemas import TokenVerifyResponse, enums
            from tests.fixtures.data import UserDataFactory

            user_data = UserDataFactory.user_1()

            access_token = create_jwt_token(
                type_token=enums.TokenType.ACCESS_TOKEN,
                payload={"sub": user_data["username"]},
                expire_minutes=0,
            )

            response = await client.post(
                self.verify_token_url, json={"token": access_token}
            )
            assert response.status_code == 200
            data = TokenVerifyResponse(**response.json())
            assert data.is_verify_token is False

        @pytest.mark.asyncio
        async def test_verify_token_without_access_token(self, client):
            """Тест запроса на проверку валидности access токена, без access токена"""

            response = await client.post(self.verify_token_url, json={})
            assert response.status_code == 422
            data = response.json()
            assert "error" in data and "message" in data
            assert data["error"] is True
            assert data["message"] == "Невалидные данные  !!!"
