import logging

from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppError

logger = logging.getLogger(__name__)


def _http_error_code(status_code: int) -> str:
    try:
        http_status = HTTPStatus(status_code)
    except ValueError:
        return "http_error"

    codes = {
        HTTPStatus.BAD_REQUEST: "bad_request",
        HTTPStatus.UNAUTHORIZED: "unauthorized",
        HTTPStatus.FORBIDDEN: "forbidden",
        HTTPStatus.NOT_FOUND: "not_found",
        HTTPStatus.CONFLICT: "conflict",
        HTTPStatus.UNPROCESSABLE_ENTITY: "validation_error",
    }
    return codes.get(http_status, "http_error")


def _error_payload(
    *,
    code: str,
    message: str,
    details: dict[str, Any] | list[Any] | None = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    if exc.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
        logger.exception(
            "Application error",
            extra={"path": request.url.path, "error_code": exc.code},
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            _error_payload(
                code=exc.code,
                message=exc.message,
                details=exc.details,
            )
        ),
    )


async def http_error_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            _error_payload(
                code=_http_error_code(exc.status_code),
                message=exc.detail,
                details={},
            )
        ),
        headers=exc.headers,
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            _error_payload(
                code="validation_error",
                message="Request validation failed",
                details=exc.errors(),
            )
        ),
    )


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unexpected error", extra={"path": request.url.path})

    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            _error_payload(
                code="internal_server_error",
                message="Internal server error",
            )
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
