from decimal import Decimal

from app.modules.ledgers.types import TransactionType


def transaction_effect(amount: Decimal, transaction_type: TransactionType) -> Decimal:
    if transaction_type == TransactionType.INCOME:
        return amount
    return -amount
