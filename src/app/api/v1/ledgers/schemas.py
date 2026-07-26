from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.ledgers.types import CurrencyType, TransactionType


class AccountSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int = Field(..., description="Unique identifier for the account")
    account_name: str = Field(..., description="Name of the account")


class AccountCreateSchema(BaseModel):
    account_name: str = Field(..., min_length=1, max_length=80)


class AccountUpdateSchema(BaseModel):
    account_name: str = Field(..., min_length=1, max_length=80)


class TransactionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: int = Field(
        ..., description="Unique identifier for the transaction"
    )
    amount: Decimal = Field(..., description="Transaction amount")
    currency: CurrencyType = Field(..., description="Transaction currency")
    transaction_type: TransactionType = Field(..., description="Transaction type")
    transaction_date: datetime = Field(..., description="Date of the transaction")
    description: str = Field(..., description="Transaction description")
    transaction_category_id: int | None = Field(
        None, description="Optional transaction category identifier"
    )


class TransactionCategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_category_id: int = Field(
        ..., description="Unique identifier for the transaction category"
    )
    transaction_category_name: str = Field(
        ..., description="Name of the transaction category"
    )
    transaction_category_description: str | None = Field(
        None, description="Optional category description"
    )


class TransactionCreateSchema(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Transaction amount")
    currency: CurrencyType = Field(..., description="Transaction currency")
    transaction_type: TransactionType = Field(..., description="Transaction type")
    transaction_date: datetime = Field(..., description="Date of the transaction")
    description: str = Field(..., min_length=1, max_length=180)
    transaction_category_id: int | None = Field(
        None, description="Optional transaction category identifier"
    )


class TransactionUpdateSchema(BaseModel):
    amount: Decimal | None = Field(None, gt=0, description="Transaction amount")
    currency: CurrencyType | None = Field(None, description="Transaction currency")
    transaction_type: TransactionType | None = Field(
        None, description="Transaction type"
    )
    transaction_date: datetime | None = Field(
        None, description="Date of the transaction"
    )
    description: str | None = Field(None, min_length=1, max_length=180)
    transaction_category_id: int | None = Field(
        None, description="Optional transaction category identifier"
    )


class TransferSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transfer_id: int = Field(..., description="Unique identifier for the transfer")
    from_account_id: int = Field(..., description="Source account identifier")
    to_account_id: int = Field(..., description="Destination account identifier")
    amount: Decimal = Field(..., description="Transfer amount")
    currency: CurrencyType = Field(..., description="Transfer currency")
    transfer_date: datetime = Field(..., description="Date of the transfer")
    description: str = Field(..., description="Transfer description")


class TransferCreateSchema(BaseModel):
    from_account_id: int = Field(..., gt=0, description="Source account identifier")
    to_account_id: int = Field(..., gt=0, description="Destination account identifier")
    amount: Decimal = Field(..., gt=0, description="Transfer amount")
    currency: CurrencyType = Field(..., description="Transfer currency")
    transfer_date: datetime = Field(..., description="Date of the transfer")
    description: str = Field(..., min_length=1, max_length=180)


class AccountDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int = Field(..., description="Unique identifier for the account")
    account_name: str = Field(..., description="Name of the account")
    balance: Decimal = Field(..., description="Current balance of the account")


class LedgerSummaryCategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int | None = Field(
        None, description="Unique identifier for the transaction category"
    )
    category_name: str = Field(..., description="Name of the transaction category")
    amount: Decimal = Field(..., description="Total amount for the category")


class LedgerSummaryTotalsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance: Decimal = Field(..., description="Combined balance across accounts")
    income: Decimal = Field(..., description="Total income in the period")
    expense: Decimal = Field(..., description="Total expense in the period")
    expenses_by_category: list[LedgerSummaryCategorySchema]


class LedgerSummaryAccountSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int = Field(..., description="Unique identifier for the account")
    account_name: str = Field(..., description="Name of the account")
    balance: Decimal = Field(..., description="Current balance of the account")
    income: Decimal = Field(..., description="Total income for the account")
    expense: Decimal = Field(..., description="Total expense for the account")
    expenses_by_category: list[LedgerSummaryCategorySchema]


class LedgerSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    totals: LedgerSummaryTotalsSchema
    accounts: list[LedgerSummaryAccountSchema]
