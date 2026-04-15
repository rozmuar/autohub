"""Иерархия исключений приложения и обработчики FastAPI."""

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse


# ─── Базовые исключения ───────────────────────────────────────────

class AppError(Exception):
    """Корневое исключение приложения."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"
    message: str = "Внутренняя ошибка сервера"

    def __init__(self, message: str | None = None, **details) -> None:
        self.message = message or self.__class__.message
        self.details = details
        super().__init__(self.message)


# ─── 400 Bad Request ─────────────────────────────────────────────

class ValidationError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "validation_error"
    message = "Неверные данные запроса"


class BadRequestError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "bad_request"
    message = "Некорректный запрос"


# ─── 401 Unauthorized ────────────────────────────────────────────

class AuthError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "unauthorized"
    message = "Требуется авторизация"


class TokenExpiredError(AuthError):
    error_code = "token_expired"
    message = "Токен истёк"


class InvalidTokenError(AuthError):
    error_code = "invalid_token"
    message = "Недействительный токен"


# ─── 403 Forbidden ───────────────────────────────────────────────

class PermissionDeniedError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "permission_denied"
    message = "Недостаточно прав"


# ─── 404 Not Found ───────────────────────────────────────────────

class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"
    message = "Ресурс не найден"


# ─── 409 Conflict ────────────────────────────────────────────────

class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "conflict"
    message = "Конфликт данных"


class AlreadyExistsError(ConflictError):
    error_code = "already_exists"
    message = "Объект уже существует"


# ─── 422 Unprocessable ───────────────────────────────────────────

class BusinessLogicError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "business_logic_error"
    message = "Нарушение бизнес-логики"


# Короткий алиас для удобства импорта
BusinessError = BusinessLogicError


class SlotNotAvailableError(BusinessLogicError):
    error_code = "slot_not_available"
    message = "Выбранное время недоступно"


class PaymentError(BusinessLogicError):
    error_code = "payment_error"
    message = "Ошибка платежа"


class AmountExceedsLimitError(BusinessLogicError):
    error_code = "amount_exceeds_limit"
    message = "Сумма превышает допустимый лимит (+15%)"


# ─── 429 Too Many Requests ───────────────────────────────────────

class RateLimitError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "rate_limit_exceeded"
    message = "Слишком много запросов. Попробуйте позже."


# ─── Регистрация обработчиков ─────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                **({"details": exc.details} if exc.details else {}),
            },
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "not_found", "message": "Маршрут не найден"},
        )

    @app.exception_handler(405)
    async def method_not_allowed_handler(request: Request, exc) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            content={"error": "method_not_allowed", "message": "Метод не разрешён"},
        )
