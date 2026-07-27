from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .base import BaseAppException


def exception_handler(app: FastAPI):

    @app.exception_handler(BaseAppException)
    def app_exception_handler(request: Request, exc: BaseAppException):
        """Обработчик кастомных ошибок"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
            },
        )

    @app.exception_handler(RequestValidationError)
    def pydantic_validation_error_handler(
        request: Request, exc: RequestValidationError
    ):
        """Обработчик Pydantic при невалидных данных"""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "error": True,
                "message": "Невалидные данные  !!!",
                "detail": exc.errors()[0].get("msg"),
            },
        )

    @app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
    def server_error_handler(request: Request, exc: Exception):
        """Обработчик ошибок сервера"""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "message": "Сервер упал !!! Мы его уже поднимаем!! Извините за неудобства :(",
            },
        )

    @app.exception_handler(status.HTTP_404_NOT_FOUND)
    def not_found_error_handler(request: Request, exc: Exception):
        """Обработчик не найденных ресурсов"""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": True,
                "message": "НЕТ здесь ничего такого !!! Фигню какую-то не ищи пж",
            },
        )

    @app.exception_handler(status.HTTP_401_UNAUTHORIZED)
    def no_authenticated_error_handler(request: Request, exc: Exception):
        """Обработчик ошибок авторизации"""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": True,
                "message": "Вы не авторизованы! Войдите пожалуйста в аккаунт",
            },
        )
