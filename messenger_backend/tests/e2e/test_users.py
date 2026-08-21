import pytest
from tests.helpers import url_builder


class TestUsers:
    profile_url = url_builder.users("me")

    @pytest.mark.asyncio
    async def test_get_profile_success(self, auth_client_user_1):
        """Успешное получение профиля"""
        from src.schemas import UserResponse
        from tests.fixtures.data import UserDataFactory
        from tests.helpers.assertions import HttpAssertions

        user_data = UserDataFactory.user_1()

        response = await auth_client_user_1.get(self.profile_url)
        data = HttpAssertions.assert_success_response(
            response=response, response_model=UserResponse
        )
        assert data.username == user_data["username"]

    @pytest.mark.asyncio
    async def test_not_authenticated_user(self, client):
        """Ошибка получения профиля при неавторизованности"""
        from tests.helpers.assertions import HttpAssertions

        response = await client.get(self.profile_url)
        HttpAssertions.assert_unauthorized_error(
            response=response,
            expected_message="Вы не авторизованы! Войдите пожалуйста в аккаунт",
        )
