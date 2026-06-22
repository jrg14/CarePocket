import app.main as app_main

from app.api.v1.health import health_check
from app.core.settings import Settings
from app.main import root


def test_settings_reads_app_debug_alias(monkeypatch) -> None:
    monkeypatch.setenv("APP_DEBUG", "false")
    monkeypatch.delenv("DEBUG", raising=False)

    settings = Settings()

    assert settings.debug is False


def test_application_exposes_basic_routes() -> None:
    openapi = app_main.app.openapi()
    paths = openapi["paths"]

    assert "/api/v1/health" in paths
    assert "/api/v1/auth/jwt/login" in paths
    assert "/api/v1/auth/jwt/logout" in paths
    assert "/api/v1/users/me" in paths
    assert "/api/v1/auth/register" in paths
    assert "/api/v1/expenses" in paths
    assert "/api/v1/expenses/summary" in paths
    assert "/api/v1/expenses/categories" in paths
    assert "/api/v1/incomes" in paths
    assert "/api/v1/incomes/summary" in paths
    assert "/api/v1/incomes/categories" in paths
    assert "/" in paths

    import asyncio

    assert asyncio.run(root()) == {"message": "Bienvenido a CarePocket"}
    assert asyncio.run(health_check()) == {
        "status": "ok",
        "service": "CarePocket API",
    }


def test_alembic_tree_exists() -> None:
    from pathlib import Path

    assert Path("alembic.ini").is_file()
    assert Path("backend/alembic/env.py").is_file()
    assert Path("backend/alembic/script.py.mako").is_file()
    assert any(Path("backend/alembic/versions").glob("*.py"))
