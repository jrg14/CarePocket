from datetime import datetime
from decimal import Decimal

from sqlalchemy import select

from app.db.session import async_session_maker
from app.modules.ledgers.models import AccountModel, TransferModel
from app.modules.ledgers.types import CurrencyType
from app.modules.ledgers.utils import to_decimal


async def create_transfer_for_user(
    user_id: int,
    from_account_id: int,
    to_account_id: int,
    amount: Decimal,
    currency: CurrencyType,
    transfer_date: datetime,
    description: str,
) -> TransferModel | None:
    if from_account_id == to_account_id:
        return None

    async with async_session_maker() as session:
        result = await session.execute(
            select(AccountModel)
            .where(
                AccountModel.id.in_([from_account_id, to_account_id]),
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
            .order_by(AccountModel.id.asc())
            .with_for_update()
        )
        accounts = {account.id: account for account in result.scalars().all()}

        from_account = accounts.get(from_account_id)
        to_account = accounts.get(to_account_id)
        if not from_account or not to_account:
            return None

        transfer = TransferModel(
            user_id=user_id,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            currency=currency.value,
            transfer_date=transfer_date,
            description=description,
        )

        from_account.balance = to_decimal(from_account.balance) - amount
        to_account.balance = to_decimal(to_account.balance) + amount
        session.add(transfer)
        await session.commit()
        await session.refresh(transfer)
        return transfer
