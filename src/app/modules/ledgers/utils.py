from datetime import datetime
from decimal import Decimal

from app.modules.ledgers.models import TransactionModel
from app.modules.ledgers.types import TransactionType


def transaction_effect(amount: Decimal, transaction_type: TransactionType) -> Decimal:
    if transaction_type == TransactionType.INCOME:
        return amount
    return -amount


def to_decimal(value: Decimal | int | float) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def percent_change(current: Decimal, previous: Decimal) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return float(((current - previous) / previous) * Decimal("100"))


def aggregate_transactions(
    transactions: list[tuple[TransactionModel, str | None]],
) -> dict[str, object]:
    income_total = Decimal("0")
    expense_total = Decimal("0")
    transactions_count = 0
    last_transaction_at: datetime | None = None
    expenses_by_category: dict[int | None, dict[str, object]] = {}
    income_by_category: dict[int | None, dict[str, object]] = {}

    for transaction, category_name in transactions:
        amount = to_decimal(transaction.amount)
        transaction_type = TransactionType(transaction.transaction_type)
        category_id = transaction.transaction_category_id
        name = category_name or "Sin categoría"

        transactions_count += 1
        if (
            last_transaction_at is None
            or transaction.transaction_date > last_transaction_at
        ):
            last_transaction_at = transaction.transaction_date

        target = (
            income_by_category
            if transaction_type == TransactionType.INCOME
            else expenses_by_category
        )
        bucket = target.setdefault(
            category_id,
            {
                "category_id": category_id,
                "category_name": name,
                "amount": Decimal("0"),
                "transaction_count": 0,
            },
        )
        bucket["amount"] = to_decimal(bucket["amount"]) + amount
        bucket["transaction_count"] = int(bucket["transaction_count"]) + 1

        if transaction_type == TransactionType.INCOME:
            income_total += amount
        else:
            expense_total += amount

    return {
        "income_total": income_total,
        "expense_total": expense_total,
        "transactions_count": transactions_count,
        "last_transaction_at": last_transaction_at,
        "expenses_by_category": list(expenses_by_category.values()),
        "income_by_category": list(income_by_category.values()),
    }
