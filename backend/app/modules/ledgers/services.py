from sqlalchemy import select

from app.db.session import async_session_maker
from app.modules.ledgers.models import Account


async def get_account_by_id(account_id: int) -> Account | None:
    async with async_session_maker() as session:
        result = await session.execute(select(Account).where(Account.id == account_id))
        return result.scalar_one_or_none()
