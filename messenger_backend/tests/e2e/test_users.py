import pytest


class TestUsers:
    profile_url = "/api/v1/users/me"

    @pytest.mark.asyncio
    async def test_get_profile_success(self, auth_client_user_1):
        """Успешное получение профиля"""
        from tests.fixtures.data import UserDataFactory

        user_data = UserDataFactory.user_1()

        response = await auth_client_user_1.get(self.profile_url)
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert data["username"] == user_data["username"]

    @pytest.mark.asyncio
    async def test_not_authenticated_user(self, client):
        """Ошибка получения профиля при неавторизованности"""
        response = await client.get(self.profile_url)
        assert response.status_code == 401
        assert response.json()["error"] is True
