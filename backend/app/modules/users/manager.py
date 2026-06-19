from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase

from app.core.settings import get_settings
from app.modules.users.db import get_user_db
from app.modules.users.models import User

settings = get_settings()


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.auth_secret
    verification_token_secret = settings.auth_secret

    async def on_after_register(
        self,
        user: User,
        request: Request | None = None,
    ) -> None:
        return None


async def get_user_manager(
    user_db: Annotated[SQLAlchemyUserDatabase[User, int], Depends(get_user_db)],
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)
