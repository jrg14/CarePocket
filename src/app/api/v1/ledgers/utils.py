from app.api.v1.ledgers.schemas import TransactionSchema
from app.modules.ledgers.models import TransactionModel


def to_transaction_schema(transaction: TransactionModel) -> TransactionSchema:
    return TransactionSchema(
        transaction_id=transaction.id,
        amount=transaction.amount,
        currency=transaction.currency,
        transaction_type=transaction.transaction_type,
        transaction_date=transaction.transaction_date,
        description=transaction.description,
        transaction_category_id=transaction.transaction_category_id,
    )
