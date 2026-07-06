from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.app.db.session import async_session_maker
from src.app.modules.ledgers.models import AccountModel, TransactionModel
from src.app.modules.ledgers.types import CurrencyType, TransactionType
from src.app.modules.ledgers.utils import transaction_effect


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


async def create_account_for_user(user_id: int, account_name: str) -> AccountModel:
    async with async_session_maker() as session:
        account = AccountModel(user_id=user_id, name=account_name)
        session.add(account)
        await session.commit()
        await session.refresh(account)
        return account


async def update_active_account_name(
    account_id: int, user_id: int, account_name: str
) -> AccountModel | None:
    async with async_session_maker() as session:
        result = await session.execute(
            select(AccountModel).where(
                AccountModel.id == account_id,
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
        )
        account = result.scalar_one_or_none()

        if not account:
            return None

        account.name = account_name
        await session.commit()
        await session.refresh(account)
        return account


#
#
# Accounts transactions services
#
#
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


async def get_transaction_by_id(transaction_id: int) -> TransactionModel | None:
    async with async_session_maker() as session:
        result = await session.execute(
            select(TransactionModel)
            .options(selectinload(TransactionModel.account))
            .where(TransactionModel.id == transaction_id)
        )
        return result.scalar_one_or_none()


async def create_transaction_for_account(
    account_id: int,
    user_id: int,
    amount: Decimal,
    currency: CurrencyType,
    transaction_type: TransactionType,
    transaction_date: datetime,
    description: str,
    transaction_category_id: int | None,
) -> TransactionModel | None:
    async with async_session_maker() as session:
        result = await session.execute(
            select(AccountModel).where(
                AccountModel.id == account_id,
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
        )
        account = result.scalar_one_or_none()

        if not account:
            return None

        transaction = TransactionModel(
            account_id=account_id,
            amount=amount,
            currency=currency.value,
            transaction_type=transaction_type.value,
            transaction_date=transaction_date,
            transaction_category_id=transaction_category_id,
            description=description,
        )
        account.balance = account.balance + transaction_effect(amount, transaction_type)
        session.add(transaction)
        await session.commit()
        await session.refresh(transaction)
        return transaction


async def update_transaction_for_user(
    transaction_id: int,
    user_id: int,
    amount: Decimal | None = None,
    currency: CurrencyType | None = None,
    transaction_type: TransactionType | None = None,
    transaction_date: datetime | None = None,
    description: str | None = None,
    transaction_category_id: int | None | object = None,
) -> TransactionModel | None:
    async with async_session_maker() as session:
        result = await session.execute(
            select(TransactionModel)
            .options(selectinload(TransactionModel.account))
            .join(AccountModel, AccountModel.id == TransactionModel.account_id)
            .where(
                TransactionModel.id == transaction_id,
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
        )
        transaction = result.scalar_one_or_none()

        if not transaction:
            return None

        account = transaction.account
        previous_amount = Decimal(transaction.amount)
        previous_type = TransactionType(transaction.transaction_type)
        previous_effect = transaction_effect(previous_amount, previous_type)

        new_amount = amount if amount is not None else previous_amount
        new_type = transaction_type if transaction_type is not None else previous_type
        new_effect = transaction_effect(new_amount, new_type)

        transaction.amount = new_amount
        transaction.currency = (
            currency.value if currency is not None else transaction.currency
        )
        transaction.transaction_type = new_type.value
        if transaction_date is not None:
            transaction.transaction_date = transaction_date
        if description is not None:
            transaction.description = description
        if transaction_category_id is not None:
            transaction.transaction_category_id = transaction_category_id

        account.balance = account.balance - previous_effect + new_effect
        await session.commit()
        await session.refresh(transaction)
        return transaction


async def delete_transaction_for_user(transaction_id: int, user_id: int) -> bool:
    async with async_session_maker() as session:
        result = await session.execute(
            select(TransactionModel)
            .options(selectinload(TransactionModel.account))
            .join(AccountModel, AccountModel.id == TransactionModel.account_id)
            .where(
                TransactionModel.id == transaction_id,
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
        )
        transaction = result.scalar_one_or_none()

        if not transaction:
            return False

        account = transaction.account
        effect = transaction_effect(
            Decimal(transaction.amount),
            TransactionType(transaction.transaction_type),
        )
        account.balance = account.balance - effect
        await session.delete(transaction)
        await session.commit()
        return True
