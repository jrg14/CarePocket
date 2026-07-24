from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import TypedDict

from sqlalchemy import select

from app.db.session import async_session_maker
from app.modules.ledgers.models import (
    AccountModel,
    TransactionCategoryModel,
    TransactionModel,
)
from app.modules.ledgers.types import TransactionType
from app.modules.ledgers.utils import to_decimal


class SummaryCategoryBucket(TypedDict):
    category_id: int | None
    category_name: str
    amount: Decimal


class SummaryCategorySummary(TypedDict):
    category_id: int | None
    category_name: str
    amount: Decimal


class SummaryAccountBucket(TypedDict):
    account_id: int
    account_name: str
    balance: Decimal
    income: Decimal
    expense: Decimal
    expenses_by_category: dict[int | None, SummaryCategoryBucket]


class SummaryAccountSummary(TypedDict):
    account_id: int
    account_name: str
    balance: Decimal
    income: Decimal
    expense: Decimal
    expenses_by_category: list[SummaryCategorySummary]


class SummaryTotalsBucket(TypedDict):
    balance: Decimal
    income: Decimal
    expense: Decimal
    expenses_by_category: dict[int | None, SummaryCategoryBucket]


class SummaryTotalsSummary(TypedDict):
    balance: Decimal
    income: Decimal
    expense: Decimal
    expenses_by_category: list[SummaryCategorySummary]


class SummaryLedgerResponse(TypedDict):
    totals: SummaryTotalsSummary
    accounts: list[SummaryAccountSummary]


async def get_user_ledger_summary(
    user_id: int, period_days: int = 30
) -> SummaryLedgerResponse:
    async with async_session_maker() as session:
        period_end = datetime.now(timezone.utc)
        period_start = period_end - timedelta(days=period_days)

        accounts_result = await session.execute(
            select(AccountModel)
            .where(
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
            .order_by(AccountModel.id.asc())
        )
        accounts = accounts_result.scalars().all()

        transactions_result = await session.execute(
            select(TransactionModel, TransactionCategoryModel.name, AccountModel.id)
            .join(AccountModel, AccountModel.id == TransactionModel.account_id)
            .outerjoin(
                TransactionCategoryModel,
                TransactionCategoryModel.id == TransactionModel.transaction_category_id,
            )
            .where(
                AccountModel.user_id == user_id,
                AccountModel.is_active,
                TransactionModel.transaction_date >= period_start,
                TransactionModel.transaction_date < period_end,
            )
            .order_by(AccountModel.id.asc(), TransactionModel.transaction_date.asc())
        )
        transactions = transactions_result.all()

    totals: SummaryTotalsBucket = {
        "balance": sum(
            (to_decimal(account.balance) for account in accounts), Decimal("0")
        ),
        "income": Decimal("0"),
        "expense": Decimal("0"),
        "expenses_by_category": {},
    }

    account_summaries: dict[int, SummaryAccountBucket] = {
        account.id: {
            "account_id": account.id,
            "account_name": account.name,
            "balance": to_decimal(account.balance),
            "income": Decimal("0"),
            "expense": Decimal("0"),
            "expenses_by_category": {},
        }
        for account in accounts
    }

    for transaction, category_name, account_id in transactions:
        amount = to_decimal(transaction.amount)
        transaction_type = TransactionType(transaction.transaction_type)
        category_id = transaction.transaction_category_id
        category_label = category_name or "Sin categoría"

        account_summary = account_summaries[account_id]

        if transaction_type == TransactionType.INCOME:
            totals["income"] = to_decimal(totals["income"]) + amount
            account_summary["income"] = to_decimal(account_summary["income"]) + amount
            continue

        totals["expense"] = to_decimal(totals["expense"]) + amount
        account_summary["expense"] = to_decimal(account_summary["expense"]) + amount

        category_bucket = totals["expenses_by_category"].setdefault(
            category_id,
            {
                "category_id": category_id,
                "category_name": category_label,
                "amount": Decimal("0"),
            },
        )
        category_bucket["amount"] = to_decimal(category_bucket["amount"]) + amount

        account_category_bucket = account_summary["expenses_by_category"].setdefault(
            category_id,
            {
                "category_id": category_id,
                "category_name": category_label,
                "amount": Decimal("0"),
            },
        )
        account_category_bucket["amount"] = (
            to_decimal(account_category_bucket["amount"]) + amount
        )

    totals_expenses_by_category: list[SummaryCategorySummary] = sorted(
        [
            {
                "category_id": item["category_id"],
                "category_name": item["category_name"],
                "amount": to_decimal(item["amount"]),
            }
            for item in totals["expenses_by_category"].values()
        ],
        key=lambda item: item["amount"],
        reverse=True,
    )

    accounts_summary: list[SummaryAccountSummary] = [
        {
            "account_id": account_summary["account_id"],
            "account_name": account_summary["account_name"],
            "balance": account_summary["balance"],
            "income": account_summary["income"],
            "expense": account_summary["expense"],
            "expenses_by_category": sorted(
                [
                    {
                        "category_id": item["category_id"],
                        "category_name": item["category_name"],
                        "amount": to_decimal(item["amount"]),
                    }
                    for item in account_summary["expenses_by_category"].values()
                ],
                key=lambda item: item["amount"],
                reverse=True,
            ),
        }
        for account_summary in account_summaries.values()
    ]

    return {
        "totals": {
            "balance": to_decimal(totals["balance"]),
            "income": to_decimal(totals["income"]),
            "expense": to_decimal(totals["expense"]),
            "expenses_by_category": totals_expenses_by_category,
        },
        "accounts": accounts_summary,
    }
