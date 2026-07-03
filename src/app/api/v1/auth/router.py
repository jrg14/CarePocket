from fastapi import APIRouter

from app.api.v1.users.schemas import UserCreate, UserRead
from app.modules.users.auth import (
    auth_backend,
    fastapi_users,
)

router = APIRouter(prefix="/auth", tags=["auth"])

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)
