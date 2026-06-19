from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from app.core.settings import get_settings
from app.modules.users.manager import get_user_manager
from app.modules.users.models import User

settings = get_settings()

bearer_transport = BearerTransport(
    tokenUrl=f"{settings.api_v1_prefix}/auth/jwt/login",
)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.auth_secret,
        lifetime_seconds=settings.auth_token_lifetime_seconds,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
