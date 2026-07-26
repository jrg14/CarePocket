from app.api.v1.ledgers.schemas import TransactionSchema, TransferSchema
from app.modules.ledgers.models import TransactionModel, TransferModel


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


def to_transfer_schema(transfer: TransferModel) -> TransferSchema:
    return TransferSchema(
        transfer_id=transfer.id,
        from_account_id=transfer.from_account_id,
        to_account_id=transfer.to_account_id,
        amount=transfer.amount,
        currency=transfer.currency,
        transfer_date=transfer.transfer_date,
        description=transfer.description,
    )
