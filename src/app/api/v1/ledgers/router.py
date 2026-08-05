from typing import Annotated

from fastapi import APIRouter, Depends

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
from app.core.exceptions import PermissionDeniedError, ResourceNotFoundError
from app.modules.ledgers.models import AccountModel, TransactionModel
from app.modules.ledgers.services import (
    create_account_for_user,
    create_transaction_for_account,
    delete_transaction_for_user,
    get_active_account_by_id,
    get_active_accounts_by_user_id,
    get_active_transactions_by_account_id,
    get_transaction_by_id,
    get_transaction_categories as get_transaction_categories_from_db,
    get_user_ledger_summary,
    update_active_account_name,
    update_transaction_for_user,
)
from app.modules.users.auth import current_active_user
from app.modules.users.models import User

router = APIRouter(prefix="/ledgers", tags=["ledgers"])


def _ensure_account_access(
    account: AccountModel | None,
    user_id: int,
) -> AccountModel:
    if not account:
        raise ResourceNotFoundError(
            "Account not found",
            code="account_not_found",
        )

    if account.user_id != user_id:
        raise PermissionDeniedError(
            "Access denied",
            code="account_access_denied",
        )

    return account


def _ensure_transaction_access(
    transaction: TransactionModel | None,
    user_id: int,
) -> TransactionModel:
    if not transaction:
        raise ResourceNotFoundError(
            "Transaction not found",
            code="transaction_not_found",
        )

    if transaction.account.user_id != user_id:
        raise PermissionDeniedError(
            "Access denied",
            code="transaction_access_denied",
        )

    return transaction


#
#
# Summary
#
#
@router.get("/summary", response_model=LedgerSummarySchema)
async def get_summary(
    user: Annotated[User, Depends(current_active_user)],
) -> LedgerSummarySchema:
    summary = await get_user_ledger_summary(user_id=user.id)

    return LedgerSummarySchema(
        balance=summary["balance"],
        balance_change=summary["balance_change"],
        monthly_health=summary["monthly_health"],
        top_expense_categories=summary["top_expense_categories"],
        latest_transactions=[
            to_transaction_schema(transaction)
            for transaction in summary["latest_transactions"]
        ],
    )


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
    account = _ensure_account_access(account, user.id)

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
        raise ResourceNotFoundError(
            "Account not found",
            code="account_not_found",
        )

    return AccountSchema(account_id=account.id, account_name=account.name)


#
#
# Accounts transactions
#
#
@router.get("/transaction-categories", response_model=list[TransactionCategorySchema])
async def get_transaction_categories() -> list[TransactionCategorySchema]:
    categories = await get_transaction_categories_from_db()

    return [
        TransactionCategorySchema(
            transaction_category_id=category.id,
            transaction_category_name=category.name,
            transaction_category_description=category.description,
        )
        for category in categories
    ]


@router.get(
    "/accounts/{account_id}/transactions", response_model=list[TransactionSchema]
)
async def get_account_transactions(
    user: Annotated[User, Depends(current_active_user)],
    account_id: int,
    transaction_category_id: int | None = None,
) -> list[TransactionSchema]:
    account = await get_active_account_by_id(account_id=account_id)
    _ensure_account_access(account, user.id)

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
    _ensure_account_access(account, user.id)

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
        raise ResourceNotFoundError(
            "Account not found",
            code="account_not_found",
        )

    return to_transaction_schema(transaction)


@router.get("/transactions/{transaction_id}", response_model=TransactionSchema)
async def get_transaction(
    user: Annotated[User, Depends(current_active_user)],
    transaction_id: int,
) -> TransactionSchema:
    transaction = await get_transaction_by_id(transaction_id=transaction_id)
    transaction = _ensure_transaction_access(transaction, user.id)

    return to_transaction_schema(transaction)


@router.patch("/transactions/{transaction_id}", response_model=TransactionSchema)
async def update_transaction(
    user: Annotated[User, Depends(current_active_user)],
    transaction_id: int,
    payload: TransactionUpdateSchema,
) -> TransactionSchema:
    transaction = await get_transaction_by_id(transaction_id=transaction_id)
    _ensure_transaction_access(transaction, user.id)

    updated = await update_transaction_for_user(
        transaction_id=transaction_id,
        user_id=user.id,
        **payload.model_dump(exclude_unset=True),
    )

    if not updated:
        raise ResourceNotFoundError(
            "Transaction not found",
            code="transaction_not_found",
        )

    return to_transaction_schema(updated)


@router.delete("/transactions/{transaction_id}", status_code=204)
async def delete_transaction(
    user: Annotated[User, Depends(current_active_user)],
    transaction_id: int,
) -> None:
    transaction = await get_transaction_by_id(transaction_id=transaction_id)
    _ensure_transaction_access(transaction, user.id)

    deleted = await delete_transaction_for_user(
        transaction_id=transaction_id,
        user_id=user.id,
    )

    if not deleted:
        raise ResourceNotFoundError(
            "Transaction not found",
            code="transaction_not_found",
        )


#
#
# Accounts categories transactions
#
#
