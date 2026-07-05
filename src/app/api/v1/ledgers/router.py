from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.ledgers.schemas import (
    AccountDetailSchema,
    AccountSchema,
    TransactionSchema,
)
from app.modules.ledgers.services import (
    get_active_account_by_id,
    get_active_accounts_by_user_id,
    get_active_transactions_by_account_id,
)
from app.modules.users.auth import current_active_user
from app.modules.users.models import User

router = APIRouter(prefix="/ledgers", tags=["ledgers"])


@router.get("/accounts", response_model=list[AccountSchema])
async def get_accounts(
    user: Annotated[User, Depends(current_active_user)],
) -> list[AccountSchema]:
    accounts: list[AccountSchema] = [
        AccountSchema(account_id=account.id, account_name=account.name)
        for account in await get_active_accounts_by_user_id(user_id=user.id)
    ]

    return accounts


@router.get("/account/{account_id}", response_model=AccountDetailSchema)
async def account_resume(
    user: Annotated[User, Depends(current_active_user)],
    account_id: int,
) -> AccountDetailSchema:
    account = await get_active_account_by_id(account_id=account_id)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return AccountDetailSchema(
        account_id=account.id,
        account_name=account.name,
        balance=account.balance,
    )


@router.get(
    "/account/{account_id}/transactions", response_model=list[TransactionSchema]
)
async def account_transactions(
    user: Annotated[User, Depends(current_active_user)],
    account_id: int,
) -> list[TransactionSchema]:
    account = await get_active_account_by_id(account_id=account_id)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    transactions = await get_active_transactions_by_account_id(
        account_id=account_id,
        user_id=user.id,
    )

    return [
        TransactionSchema(
            transaction_id=transaction.id,
            amount=transaction.amount,
            currency=transaction.currency,
            transaction_type=transaction.transaction_type,
            transaction_date=transaction.transaction_date,
            description=transaction.description,
            transaction_category_id=transaction.transaction_category_id,
        )
        for transaction in transactions
    ]
