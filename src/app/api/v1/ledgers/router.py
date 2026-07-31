from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.v1.ledgers.schemas import (
    AccountCreateSchema,
    AccountDetailSchema,
    AccountSchema,
    AccountUpdateSchema,
    LedgerSummarySchema,
    TransactionCategorySchema,
    TransactionCreateSchema,
    TransactionSchema,
    TransactionUpdateSchema,
)
from app.api.v1.ledgers.utils import to_transaction_schema
from app.modules.ledgers.services import (
    create_account_for_user,
    create_transaction_for_account,
    delete_transaction_for_user,
    get_active_account_by_id,
    get_active_accounts_by_user_id,
    get_active_transactions_by_account_id,
    get_transaction_by_id,
    get_transaction_categories,
    get_user_ledger_summary,
    update_active_account_name,
    update_transaction_for_user,
)
from app.modules.users.auth import current_active_user
from app.modules.users.models import User

router = APIRouter(prefix="/ledgers", tags=["ledgers"])


#
#
# Summary
#
#
@router.get("/summary", response_model=LedgerSummarySchema)
async def get_summary(
    user: Annotated[User, Depends(current_active_user)],
    period_days: int = Query(30, ge=7, le=365),
) -> LedgerSummarySchema:
    return await get_user_ledger_summary(user_id=user.id, period_days=period_days)


#
#
# Accounts
#
#
@router.get("/accounts", response_model=list[AccountSchema])
async def get_accounts(
    user: Annotated[User, Depends(current_active_user)],
) -> list[AccountSchema]:
    accounts: list[AccountSchema] = [
        AccountSchema(account_id=account.id, account_name=account.name)
        for account in await get_active_accounts_by_user_id(user_id=user.id)
    ]

    return accounts


@router.post("/accounts", response_model=AccountSchema, status_code=201)
async def create_account(
    user: Annotated[User, Depends(current_active_user)],
    payload: AccountCreateSchema,
) -> AccountSchema:
    account = await create_account_for_user(
        user_id=user.id,
        account_name=payload.account_name,
    )

    return AccountSchema(account_id=account.id, account_name=account.name)


@router.get("/accounts/{account_id}", response_model=AccountDetailSchema)
async def get_account(
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


@router.patch("/accounts/{account_id}", response_model=AccountSchema)
async def update_account(
    user: Annotated[User, Depends(current_active_user)],
    account_id: int,
    payload: AccountUpdateSchema,
) -> AccountSchema:
    account = await update_active_account_name(
        account_id=account_id,
        user_id=user.id,
        account_name=payload.account_name,
    )

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return AccountSchema(account_id=account.id, account_name=account.name)


#
#
# Accounts transactions
#
#
@router.get("/transaction-categories", response_model=list[TransactionCategorySchema])
async def get_transaction_categories() -> list[TransactionCategorySchema]:
    categories = await get_transaction_categories()

    return [
        TransactionCategorySchema(
            transaction_category_id=category.id,
            transaction_category_name=category.name,
            transaction_category_description=category.description,
        )
        for category in categories
    ]


@router.get("/accounts/{account_id}/transactions", response_model=list[TransactionSchema])
async def get_account_transactions(
    user: Annotated[User, Depends(current_active_user)],
    account_id: int,
    transaction_category_id: int | None = None,
) -> list[TransactionSchema]:
    account = await get_active_account_by_id(account_id=account_id)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    transactions = await get_active_transactions_by_account_id(
        account_id=account_id,
        user_id=user.id,
        transaction_category_id=transaction_category_id,
    )

    return [to_transaction_schema(transaction) for transaction in transactions]


@router.post(
    "/accounts/{account_id}/transactions",
    response_model=TransactionSchema,
    status_code=201,
)
async def create_transaction(
    user: Annotated[User, Depends(current_active_user)],
    account_id: int,
    payload: TransactionCreateSchema,
) -> TransactionSchema:
    account = await get_active_account_by_id(account_id=account_id)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    transaction = await create_transaction_for_account(
        account_id=account_id,
        user_id=user.id,
        amount=payload.amount,
        currency=payload.currency,
        transaction_type=payload.transaction_type,
        transaction_date=payload.transaction_date,
        description=payload.description,
        transaction_category_id=payload.transaction_category_id,
    )

    if not transaction:
        raise HTTPException(status_code=404, detail="Account not found")

    return to_transaction_schema(transaction)


@router.get("/transactions/{transaction_id}", response_model=TransactionSchema)
async def get_transaction(
    user: Annotated[User, Depends(current_active_user)],
    transaction_id: int,
) -> TransactionSchema:
    transaction = await get_transaction_by_id(transaction_id=transaction_id)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.account.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return to_transaction_schema(transaction)


@router.patch("/transactions/{transaction_id}", response_model=TransactionSchema)
async def update_transaction(
    user: Annotated[User, Depends(current_active_user)],
    transaction_id: int,
    payload: TransactionUpdateSchema,
) -> TransactionSchema:
    transaction = await get_transaction_by_id(transaction_id=transaction_id)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.account.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    updated = await update_transaction_for_user(
        transaction_id=transaction_id,
        user_id=user.id,
        **payload.model_dump(exclude_unset=True),
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return to_transaction_schema(updated)


@router.delete("/transactions/{transaction_id}", status_code=204)
async def delete_transaction(
    user: Annotated[User, Depends(current_active_user)],
    transaction_id: int,
) -> None:
    transaction = await get_transaction_by_id(transaction_id=transaction_id)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.account.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    deleted = await delete_transaction_for_user(
        transaction_id=transaction_id,
        user_id=user.id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")


#
#
# Accounts categories transactions
#
#
