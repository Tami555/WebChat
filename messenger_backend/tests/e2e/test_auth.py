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
            async def test_complete_registration_without_user_data(
                self, redis_connect, client
            ):
                """Тест запроса подтверждения регистрации, с пустыми данными о пользователе"""
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
        async def test_full_registration_success(self, client):
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
