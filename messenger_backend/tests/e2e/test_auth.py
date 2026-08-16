import pytest


class TestAuth:
    """Тесты авторизации"""

    class TestRegistration:
        """Тесты регистрации"""

        class TestRequest:
            """Тесты запроса на регистрацию"""

            registration_request_url = "/api/v1/auth/register"

            @pytest.mark.asyncio
            async def test_registration_request_success(
                self, redis_connect, client, user_data
            ):
                """Тест на успешный запрос регистрации"""
                from src.schemas import VerificationCodeResponse
                from src.core.redis import verification_redis

                user_data = user_data[1]

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
            async def test_registration_request_with_existing_phone(
                self, created_user, redis_connect, client, user_data
            ):
                """Тест запроса регистрации с существующим телефоном"""
                response = await client.post(
                    self.registration_request_url,
                    json={
                        "username": user_data[2]["username"],
                        "phone": user_data[1]["phone"],
                    },
                )
                assert response.status_code == 409
                data = response.json()
                assert data["error"] is True
                assert (
                    data["message"] == "Пользователь с таким телефоном уже существует"
                )

            @pytest.mark.asyncio
            async def test_registration_request_with_existing_username(
                self, created_user, redis_connect, client, user_data
            ):
                """Тест запроса регистрации с существующим username"""
                response = await client.post(
                    self.registration_request_url,
                    json={
                        "username": user_data[1]["username"],
                        "phone": user_data[2]["phone"],
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
        async def test_full_registration_success(self, client, user_data):
            """Тест на полную успешную регистрацию"""
            user_data = user_data[1]

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
