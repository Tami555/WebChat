from httpx import Response
from typing import Optional, TypeVar

T = TypeVar("T")


class HttpAssertions:
    """Проверки HTTP ответов"""

    @staticmethod
    def assert_error_response(
        response: Response,
        expected_message: Optional[str] = None,
        expected_status: int = 400,
    ) -> dict:
        """Проверка ответа с ошибкой"""
        assert response.status_code == expected_status
        data = response.json()

        assert "error" in data
        assert "message" in data
        assert data["error"] is True
        if expected_message is not None:
            assert data["message"] == expected_message
        return data

    @staticmethod
    def assert_success_response(
        response: Response,
        response_model: T,
        expected_status: int = 200,
    ) -> Optional[T]:
        """Проверка успешного ответа. Преобразование в модель ответа"""
        assert response.status_code == expected_status
        data = response_model(**response.json())
        return data

    @staticmethod
    def assert_validation_error(
        response: Response,
        expected_message: Optional[str] = "Невалидные данные  !!!",
    ) -> dict:
        """Проверка ошибки валидации (pydantic, 422)"""
        return HttpAssertions.assert_error_response(
            response,
            expected_message=expected_message,
            expected_status=422,
        )

    @staticmethod
    def assert_unauthorized_error(
        response: Response,
        expected_message: Optional[str] = "Невалидный токен",
    ) -> dict:
        """Проверка ошибки авторизации (401)"""
        return HttpAssertions.assert_error_response(
            response,
            expected_message=expected_message,
            expected_status=401,
        )

    @staticmethod
    def assert_not_found_error(
        response: Response, expected_message: Optional[str]
    ) -> dict:
        """Проверка ошибки "не найдено" (404)"""
        return HttpAssertions.assert_error_response(
            response,
            expected_message=expected_message,
            expected_status=404,
        )

    @staticmethod
    def assert_conflict_error(
        response: Response, expected_message: Optional[str]
    ) -> dict:
        """Проверка ошибки конфликта (409)"""
        return HttpAssertions.assert_error_response(
            response,
            expected_message=expected_message,
            expected_status=409,
        )
