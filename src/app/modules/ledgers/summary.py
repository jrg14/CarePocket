from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Literal, TypedDict

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


class SummaryBalanceChangeSummary(TypedDict):
    percentage: Decimal
    direction: Literal["improvement", "worsening", "neutral"]


class SummaryLedgerResponse(TypedDict):
    balance: Decimal
    balance_change: SummaryBalanceChangeSummary
    monthly_health: Decimal
    top_expense_categories: list[SummaryCategorySummary]
    latest_transactions: list[TransactionModel]


PERCENTAGE_QUANTIZER = Decimal("0.01")


def _quantize_percentage(value: Decimal) -> Decimal:
    return value.quantize(PERCENTAGE_QUANTIZER, rounding=ROUND_HALF_UP)


def _get_month_boundaries(
    now: datetime | None = None,
) -> tuple[datetime, datetime]:
    current = now or datetime.now(timezone.utc)
    month_start = current.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if month_start.month == 12:
        next_month_start = month_start.replace(
            year=month_start.year + 1,
            month=1,
        )
    else:
        next_month_start = month_start.replace(month=month_start.month + 1)

    return month_start, next_month_start


def _build_balance_change(
    current_balance: Decimal,
    current_month_income: Decimal,
    current_month_expense: Decimal,
) -> SummaryBalanceChangeSummary:
    previous_balance = current_balance - (current_month_income - current_month_expense)
    delta = current_balance - previous_balance

    if delta == 0:
        return {
            "percentage": Decimal("0.00"),
            "direction": "neutral",
        }

    if previous_balance == 0:
        percentage = Decimal("100.00")
    else:
        percentage = (abs(delta) / abs(previous_balance)) * Decimal("100")

    return {
        "percentage": _quantize_percentage(percentage),
        "direction": "improvement" if delta > 0 else "worsening",
    }


async def get_user_ledger_summary(user_id: int) -> SummaryLedgerResponse:
    async with async_session_maker() as session:
        month_start, next_month_start = _get_month_boundaries()

        accounts_result = await session.execute(
            select(AccountModel.balance)
            .where(
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
        )
        account_balances = accounts_result.scalars().all()

        transactions_result = await session.execute(
            select(TransactionModel, TransactionCategoryModel.name)
            .join(AccountModel, AccountModel.id == TransactionModel.account_id)
            .outerjoin(
                TransactionCategoryModel,
                TransactionCategoryModel.id == TransactionModel.transaction_category_id,
            )
            .where(
                AccountModel.user_id == user_id,
                AccountModel.is_active,
                TransactionModel.transaction_date >= month_start,
                TransactionModel.transaction_date < next_month_start,
            )
            .order_by(TransactionModel.transaction_date.asc(), TransactionModel.id.asc())
        )
        transactions = transactions_result.all()

        latest_transactions_result = await session.execute(
            select(TransactionModel)
            .join(AccountModel, AccountModel.id == TransactionModel.account_id)
            .where(
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
            .order_by(
                TransactionModel.transaction_date.desc(),
                TransactionModel.id.desc(),
            )
            .limit(5)
        )
        latest_transactions = latest_transactions_result.scalars().all()

    total_balance = sum((to_decimal(balance) for balance in account_balances), Decimal("0"))
    monthly_income = Decimal("0")
    monthly_expense = Decimal("0")
    top_expense_categories: dict[int | None, SummaryCategoryBucket] = {}

    for transaction, category_name in transactions:
        amount = to_decimal(transaction.amount)
        transaction_type = TransactionType(transaction.transaction_type)
        category_id = transaction.transaction_category_id
        category_label = category_name or "Sin categoría"

        if transaction_type == TransactionType.INCOME:
            monthly_income += amount
            continue

        monthly_expense += amount
        category_bucket = top_expense_categories.setdefault(
            category_id,
            {
                "category_id": category_id,
                "category_name": category_label,
                "amount": Decimal("0"),
            },
        )
        category_bucket["amount"] = to_decimal(category_bucket["amount"]) + amount

    top_expense_categories_summary: list[SummaryCategorySummary] = sorted(
        [
            {
                "category_id": item["category_id"],
                "category_name": item["category_name"],
                "amount": to_decimal(item["amount"]),
            }
            for item in top_expense_categories.values()
        ],
        key=lambda item: item["amount"],
        reverse=True,
    )

    return {
        "balance": total_balance,
        "balance_change": _build_balance_change(
            current_balance=total_balance,
            current_month_income=monthly_income,
            current_month_expense=monthly_expense,
        ),
        "monthly_health": _quantize_percentage(
            ((monthly_income - monthly_expense) / monthly_income) * Decimal("100")
            if monthly_income > 0
            else Decimal("0.00")
        ),
        "top_expense_categories": top_expense_categories_summary[:3],
        "latest_transactions": latest_transactions,
    }
