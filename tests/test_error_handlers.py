import asyncio
import json

from fastapi.exceptions import RequestValidationError
from starlette.requests import Request

from app.core.error_handlers import app_error_handler, validation_error_handler
from app.core.exceptions import ResourceNotFoundError


def _request(path: str) -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": path,
            "headers": [],
            "scheme": "http",
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
        }
    )


def test_app_errors_return_structured_payload() -> None:
    exc = ResourceNotFoundError(
        "Account not found",
        code="account_not_found",
        details={"account_id": 42},
    )

    response = asyncio.run(app_error_handler(_request("/accounts/42"), exc))

    assert response.status_code == 404
    assert json.loads(response.body) == {
        "error": {
            "code": "account_not_found",
            "message": "Account not found",
            "details": {"account_id": 42},
        }
    }


def test_validation_errors_return_structured_payload() -> None:
    exc = RequestValidationError(
        [
            {
                "type": "int_parsing",
                "loc": ("path", "account_id"),
                "msg": "Input should be a valid integer",
                "input": "not-a-number",
            }
        ]
    )
    response = asyncio.run(
        validation_error_handler(_request("/accounts/not-a-number"), exc)
    )
    payload = json.loads(response.body)

    assert response.status_code == 422
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["message"] == "Request validation failed"
    assert payload["error"]["details"][0]["loc"] == ["path", "account_id"]
