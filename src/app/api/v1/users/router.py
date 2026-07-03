from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.users.mapper import map_user_to_v1
from app.api.v1.users.schemas import UserRead
from app.modules.users.auth import current_active_user
from app.modules.users.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def read_current_user(
    user: Annotated[User, Depends(current_active_user)],
) -> UserRead:
    return map_user_to_v1(user)
