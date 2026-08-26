import pytest

from src.core.redis import verification_redis
from src.core.config import settings
from tests.fixtures.data import UserDataFactory
from tests.helpers import url_builder, TokenFactory
from tests.helpers.assertions import (
    HttpAssertions,
    VerificationRedisAssertions,
    UserDatabaseAssertions,
)


class TestAuth:
    """Тесты авторизации"""

    class TestRegistration:
        """Тесты регистрации"""

        class TestRequest:
            """Тесты запроса на регистрацию"""

            registration_request_url = url_builder.auth("register")

            @pytest.mark.asyncio
            async def test_request_registration_success(self, redis_connect, client):
                """Тест на успешный запрос регистрации"""
                from src.schemas import VerificationCodeResponse

                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.registration_request_url,
                    json={
                        "username": user_data["username"],
                        "phone": user_data["phone"],
                    },
                )
                HttpAssertions.assert_success_response(
                    response=response, response_model=VerificationCodeResponse
                )
                await VerificationRedisAssertions.assert_has_code(
                    user_data["phone"], user_data["code"]
                )

            @pytest.mark.asyncio
            async def test_request_registration_with_existing_phone(
                self, created_user_1, redis_connect, client
            ):
                """Тест запроса регистрации с существующим телефоном"""
                user_data_1 = UserDataFactory.user_1()
                user_data_2 = UserDataFactory.user_2()

                response = await client.post(
                    self.registration_request_url,
                    json={
                        "username": user_data_2["username"],
                        "phone": user_data_1["phone"],
                    },
                )
                HttpAssertions.assert_conflict_error(
                    response=response,
                    expected_message="Пользователь с таким телефоном уже существует",
                )

            @pytest.mark.asyncio
            async def test_request_registration_with_existing_username(
                self, created_user_1, redis_connect, client
            ):
                """Тест запроса регистрации с существующим username"""
                user_data_1 = UserDataFactory.user_1()
                user_data_2 = UserDataFactory.user_2()

                response = await client.post(
                    self.registration_request_url,
                    json={
                        "username": user_data_1["username"],
                        "phone": user_data_2["phone"],
                    },
                )
                HttpAssertions.assert_conflict_error(
                    response=response,
                    expected_message="Пользователь с таким username уже существует",
                )

            @pytest.mark.asyncio
            async def test_request_registration_without_phone(self, client):
                """Тест запроса регистрации без указания телефона"""
                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.registration_request_url,
                    json={"username": user_data["username"]},
                )
                HttpAssertions.assert_validation_error(response)

            @pytest.mark.asyncio
            async def test_request_registration_without_username(self, client):
                """Тест запроса регистрации без указания username"""
                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.registration_request_url,
                    json={"phone": user_data["phone"]},
                )
                HttpAssertions.assert_validation_error(response)

        class TestComplete:
            """Тесты подтверждения регистрации"""

            registration_verify_url = url_builder.auth("verify-registration")

            @pytest.mark.asyncio
            async def test_complete_registration_success(
                self, redis_connect, client, test_db
            ):
                """Тест на успешное подтверждение регистрации и создание пользователя"""
                from src.schemas import TokenResponse

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
                # Запрос подтверждения
                response = await client.post(
                    self.registration_verify_url,
                    json={"code": user_data["code"], "phone": user_data["phone"]},
                )
                HttpAssertions.assert_success_response(
                    response=response, response_model=TokenResponse
                )
                # Проверяем наличие пользователя в БД
                async for db_session in test_db.create_session():
                    await UserDatabaseAssertions.assert_user_exists(
                        session=db_session,
                        phone=user_data["phone"],
                        expected_username=user_data["username"],
                    )
                # Проверка, что в Redis значение удалено
                await VerificationRedisAssertions.assert_no_data(user_data["phone"])

            @pytest.mark.asyncio
            async def test_complete_registration_without_redis_data(
                self, redis_connect, client
            ):
                """Тест запроса подтверждения регистрации, без данных в Redis"""
                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.registration_verify_url,
                    json={"code": user_data["code"], "phone": user_data["phone"]},
                )
                HttpAssertions.assert_error_response(
                    response=response,
                    expected_message="Время действия кода верификации истекло",
                )

            @pytest.mark.asyncio
            async def test_complete_registration_with_too_many_attempts(
                self, redis_connect, client
            ):
                """Тест запроса подтверждения регистрации, с большим количеством попыток"""
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

                response = await client.post(
                    self.registration_verify_url,
                    json={"code": user_data["code"], "phone": user_data["phone"]},
                )
                HttpAssertions.assert_error_response(
                    response=response, expected_message="Слишком много попыток"
                )

            @pytest.mark.asyncio
            async def test_complete_registration_with_invalid_code(
                self, redis_connect, client
            ):
                """Тест запроса подтверждения регистрации с неправильным кодом"""
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
                HttpAssertions.assert_error_response(response)

                # Проверка, что попытки увеличились
                await VerificationRedisAssertions.assert_attempts_count(
                    user_data_1["phone"], 1
                )

            @pytest.mark.asyncio
            async def test_complete_registration_without_redis_user_data(
                self, redis_connect, client
            ):
                """Тест запроса подтверждения регистрации, с пустыми данными о пользователе в Redis"""
                from pydantic import ValidationError

                user_data = UserDataFactory.user_1()

                # Сохраняем данные в Redis (без данных о пользователе)
                await verification_redis.save(user_data["phone"], user_data["code"], {})
                with pytest.raises(ValidationError):
                    response = await client.post(
                        self.registration_verify_url,
                        json={
                            "code": user_data["code"],
                            "phone": user_data["phone"],
                        },
                    )
                    HttpAssertions.assert_validation_error(response)

            @pytest.mark.asyncio
            async def test_complete_registration_without_phone(self, client):
                """Тест запроса подтверждения регистрации без указания телефона"""
                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.registration_verify_url,
                    json={"code": user_data["code"]},
                )
                HttpAssertions.assert_validation_error(response)

            @pytest.mark.asyncio
            async def test_complete_registration_without_code(self, client):
                """Тест запроса подтверждения регистрации без указания кода"""
                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.registration_verify_url,
                    json={"phone": user_data["phone"]},
                )
                HttpAssertions.assert_validation_error(response)

            @pytest.mark.asyncio
            async def test_complete_registration_with_incorrect_code(self, client):
                """Тест запроса подтверждения регистрации с некорректным кодом"""
                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.registration_verify_url,
                    json={"code": "", "phone": user_data["phone"]},
                )
                data = HttpAssertions.assert_validation_error(response)
                assert "Код должен состоять из 6 символов" in data["detail"]

        @pytest.mark.asyncio
        async def test_full_registration_success(self, redis_connect, client, test_db):
            """Тест на полную успешную регистрацию"""
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

            async for db_session in test_db.create_session():
                await UserDatabaseAssertions.assert_user_exists(
                    session=db_session,
                    phone=user_data["phone"],
                    expected_username=user_data["username"],
                )

    class TestLogin:
        """Тесты входа (авторизации)"""

        class TestRequest:
            """Тесты запроса на вход"""

            login_request_url = url_builder.auth("login")

            @pytest.mark.asyncio
            async def test_request_login_success(
                self, redis_connect, created_user_1, client
            ):
                """Тест на успешный запрос входа"""
                from src.schemas import VerificationCodeResponse

                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.login_request_url,
                    json={"phone": user_data["phone"]},
                )
                HttpAssertions.assert_success_response(
                    response=response, response_model=VerificationCodeResponse
                )
                await VerificationRedisAssertions.assert_has_code(
                    user_data["phone"], user_data["code"]
                )

            @pytest.mark.asyncio
            async def test_request_login_with_not_existing_user(self, client):
                """Тест запроса входа для несуществующего пользователя"""
                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.login_request_url,
                    json={"phone": user_data["phone"]},
                )
                HttpAssertions.assert_not_found_error(
                    response=response, expected_message="Пользователь не найден"
                )

            @pytest.mark.asyncio
            async def test_request_login_without_phone(self, client):
                """Тест запроса входа без указания телефона"""
                response = await client.post(self.login_request_url, json={})
                HttpAssertions.assert_validation_error(response)

        class TestComplete:
            """Тесты подтверждения входа"""

            login_verify_url = url_builder.auth("verify-login")

            @pytest.mark.asyncio
            async def test_complete_login_success(
                self, redis_connect, created_user_1, client
            ):
                """Тест на успешное подтверждение входа"""
                from src.schemas import TokenResponse

                user_data = UserDataFactory.user_1()

                # Сохраняем данные в Redis
                await verification_redis.save(
                    user_data["phone"],
                    user_data["code"],
                    {"username": user_data["username"], "phone": user_data["phone"]},
                )

                response = await client.post(
                    self.login_verify_url,
                    json={"code": user_data["code"], "phone": user_data["phone"]},
                )
                HttpAssertions.assert_success_response(
                    response=response, response_model=TokenResponse
                )

                # Проверка, что в Redis значение удалено
                await VerificationRedisAssertions.assert_no_data(user_data["phone"])

            @pytest.mark.asyncio
            async def test_complete_login_without_redis_data(
                self, redis_connect, created_user_1, client
            ):
                """Тест запроса подтверждения входа, без данных в Redis"""
                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.login_verify_url,
                    json={"code": user_data["code"], "phone": user_data["phone"]},
                )
                HttpAssertions.assert_error_response(
                    response=response,
                    expected_message="Время действия кода верификации истекло",
                )

            @pytest.mark.asyncio
            async def test_complete_login_with_too_many_attempts(
                self, redis_connect, created_user_1, client
            ):
                """Тест запроса подтверждения входа, с большим количеством попыток"""
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

                response = await client.post(
                    self.login_verify_url,
                    json={"code": user_data["code"], "phone": user_data["phone"]},
                )
                HttpAssertions.assert_error_response(
                    response=response, expected_message="Слишком много попыток"
                )

            @pytest.mark.asyncio
            async def test_complete_login_with_invalid_code(
                self, redis_connect, created_user_1, client
            ):
                """Тест запроса подтверждения входа с неправильным кодом"""
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
                HttpAssertions.assert_error_response(response)

                # Проверка, что попытки увеличились
                await VerificationRedisAssertions.assert_attempts_count(
                    user_data_1["phone"], 1
                )

            @pytest.mark.asyncio
            async def test_complete_login_with_empty_redis_user_data(
                self, redis_connect, created_user_1, client
            ):
                """Тест запроса подтверждения входа, с пустыми данными о пользователе в Redis"""
                user_data = UserDataFactory.user_1()
                # Сохраняем данные в Redis (без данных о пользователе)
                await verification_redis.save(user_data["phone"], user_data["code"], {})

                response = await client.post(
                    self.login_verify_url,
                    json={"code": user_data["code"], "phone": user_data["phone"]},
                )
                HttpAssertions.assert_not_found_error(
                    response=response, expected_message="Пользователь не найден"
                )

            @pytest.mark.asyncio
            async def test_complete_login_without_phone(self, client):
                """Тест запроса подтверждения входа без указания телефона"""
                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.login_verify_url,
                    json={"code": user_data["code"]},
                )
                HttpAssertions.assert_validation_error(response)

            @pytest.mark.asyncio
            async def test_complete_login_without_code(self, client):
                """Тест запроса подтверждения входа без указания кода"""
                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.login_verify_url,
                    json={"phone": user_data["phone"]},
                )
                HttpAssertions.assert_validation_error(response)

            @pytest.mark.asyncio
            async def test_complete_login_with_incorrect_code(self, client):
                """Тест запроса подтверждения входа с некорректным кодом"""
                user_data = UserDataFactory.user_1()

                response = await client.post(
                    self.login_verify_url,
                    json={"code": "", "phone": user_data["phone"]},
                )
                data = HttpAssertions.assert_validation_error(response)
                assert "Код должен состоять из 6 символов" in data["detail"]

        @pytest.mark.asyncio
        async def test_full_login_success(self, redis_connect, created_user_1, client):
            """Тест на полную успешную авторизацию"""
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

        refresh_token_url = url_builder.auth("refresh")

        @pytest.mark.asyncio
        async def test_get_new_token_success(self, auth_tokens_user_1, client):
            """Тест на успешное получение нового access токена по refresh"""
            from src.schemas import TokenResponse

            response = await client.post(
                self.refresh_token_url, json={"token": auth_tokens_user_1.refresh_token}
            )
            data = HttpAssertions.assert_success_response(
                response=response, response_model=TokenResponse
            )
            assert data.token_type == "Bearer"

        @pytest.mark.asyncio
        async def test_get_new_token_by_access_token(self, auth_tokens_user_1, client):
            """Тест запроса на получение нового access токена по access. Неверный тип токена"""
            response = await client.post(
                self.refresh_token_url, json={"token": auth_tokens_user_1.access_token}
            )
            HttpAssertions.assert_unauthorized_error(
                response=response,
                expected_message="Неверный тип токена. Ожидался: refresh",
            )

        @pytest.mark.asyncio
        async def test_get_new_token_by_refresh_token_not_existing_user(self, client):
            """Тест запроса на получение нового access токена по refresh, не существующего пользователя"""
            user_data = UserDataFactory.user_1()

            TokenFactory.create_refresh_token(username=user_data["username"])
            refresh_token = TokenFactory.create_refresh_token(
                username=user_data["username"]
            )
            response = await client.post(
                self.refresh_token_url, json={"token": refresh_token}
            )
            HttpAssertions.assert_not_found_error(
                response=response, expected_message="Пользователь не найден"
            )

        @pytest.mark.asyncio
        async def test_get_new_token_by_expired_refresh_token(
            self, created_user_1, client
        ):
            """Тест запроса на получение нового access токена по refresh, истекшему по времени"""
            user_data = UserDataFactory.user_1()

            refresh_token = TokenFactory.create_expired_refresh_token(
                username=user_data["username"]
            )
            response = await client.post(
                self.refresh_token_url, json={"token": refresh_token}
            )
            HttpAssertions.assert_unauthorized_error(response)

        @pytest.mark.asyncio
        async def test_get_new_token_without_refresh_token(self, client):
            """Тест запроса на получение нового access токена, без refresh токена"""
            response = await client.post(self.refresh_token_url, json={})
            HttpAssertions.assert_validation_error(response)

    class TestVerifyToken:
        verify_token_url = url_builder.auth("verify")

        @pytest.mark.asyncio
        async def test_verify_token_success(self, auth_tokens_user_1, client):
            """Тест на успешную проверку валидности access токена"""
            from src.schemas import TokenVerifyResponse

            response = await client.post(
                self.verify_token_url, json={"token": auth_tokens_user_1.access_token}
            )
            data = HttpAssertions.assert_success_response(
                response=response, response_model=TokenVerifyResponse
            )
            assert data.is_verify_token is True

        @pytest.mark.asyncio
        async def test_verify_token_by_refresh_token(self, auth_tokens_user_1, client):
            """Тест запроса на проверку валидности access токена по refresh токену (Неверный тип токена)"""
            response = await client.post(
                self.verify_token_url, json={"token": auth_tokens_user_1.refresh_token}
            )
            HttpAssertions.assert_unauthorized_error(
                response=response,
                expected_message="Неверный тип токена. Ожидался: access",
            )

        @pytest.mark.asyncio
        async def test_verify_token_by_expired_access_token(self, client):
            """Тест запроса на проверку валидности access токена истекшему по времени"""
            from src.schemas import TokenVerifyResponse

            user_data = UserDataFactory.user_1()

            access_token = TokenFactory.create_expired_access_token(
                username=user_data["username"]
            )
            response = await client.post(
                self.verify_token_url, json={"token": access_token}
            )
            data = HttpAssertions.assert_success_response(
                response=response, response_model=TokenVerifyResponse
            )
            assert data.is_verify_token is False

        @pytest.mark.asyncio
        async def test_verify_token_without_access_token(self, client):
            """Тест запроса на проверку валидности access токена, без access токена"""
            response = await client.post(self.verify_token_url, json={})
            HttpAssertions.assert_validation_error(response)
