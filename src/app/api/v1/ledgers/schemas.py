from datetime import datetime
from decimal import Decimal
from typing import Literal

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


class LedgerSummaryBalanceChangeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    percentage: Decimal = Field(
        ..., description="Absolute percentage change versus the previous month"
    )
    direction: Literal["improvement", "worsening", "neutral"] = Field(
        ..., description="Direction of the balance change"
    )


class LedgerSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance: Decimal = Field(
        ..., description="Combined balance across all active accounts"
    )
    balance_change: LedgerSummaryBalanceChangeSchema
    monthly_health: Decimal = Field(
        ..., description="Remaining percentage of the monthly income after expenses"
    )
    top_expense_categories: list[LedgerSummaryCategorySchema]
    latest_transactions: list[TransactionSchema]
