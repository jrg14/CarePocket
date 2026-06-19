from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.users.models import User


async def get_user_db(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(session, User)
