from app.api.v1.users.schemas import UserRead
from app.modules.users.models import User


def map_user_to_v1(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        is_verified=user.is_verified,
    )
