from sqlalchemy import select

from app.db.session import async_session_maker
from src.app.modules.ledgers.models import AccountModel, TransactionModel


#
#
# Accounts services
#
#
async def get_active_account_by_id(account_id: int) -> AccountModel | None:
    async with async_session_maker() as session:
        result = await session.execute(
            select(AccountModel).where(
                AccountModel.id == account_id,
                AccountModel.is_active,
            )
        )
        return result.scalar_one_or_none()


async def get_active_accounts_by_user_id(user_id: int) -> list[AccountModel]:
    async with async_session_maker() as session:
        result = await session.execute(
            select(AccountModel).where(
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
        )
        return result.scalars().all()


async def get_active_transactions_by_account_id(
    account_id: int, user_id: int
) -> list[TransactionModel]:
    async with async_session_maker() as session:
        result = await session.execute(
            select(TransactionModel)
            .join(AccountModel, AccountModel.id == TransactionModel.account_id)
            .where(
                TransactionModel.account_id == account_id,
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
            .order_by(TransactionModel.transaction_date.desc())
        )
        return result.scalars().all()
