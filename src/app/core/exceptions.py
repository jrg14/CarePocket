from http import HTTPStatus
from typing import Any


class AppError(Exception):
    status_code = HTTPStatus.BAD_REQUEST
    code = "application_error"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.code
        self.details = details or {}


class ResourceNotFoundError(AppError):
    status_code = HTTPStatus.NOT_FOUND
    code = "resource_not_found"


class PermissionDeniedError(AppError):
    status_code = HTTPStatus.FORBIDDEN
    code = "permission_denied"


class ConflictError(AppError):
    status_code = HTTPStatus.CONFLICT
    code = "conflict"
