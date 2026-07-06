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


class AccountDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int = Field(..., description="Unique identifier for the account")
    account_name: str = Field(..., description="Name of the account")
    balance: Decimal = Field(..., description="Current balance of the account")


class LedgerSummaryAccountSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int = Field(..., description="Unique identifier for the account")
    account_name: str = Field(..., description="Name of the account")
    balance: Decimal = Field(..., description="Current balance of the account")
    transaction_count: int = Field(
        ..., description="Number of transactions in the selected period"
    )


class LedgerSummaryCategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int | None = Field(
        None, description="Unique identifier for the transaction category"
    )
    category_name: str = Field(..., description="Name of the transaction category")
    amount: Decimal = Field(..., description="Total amount for the category")
    transaction_count: int = Field(
        ..., description="Number of transactions in the selected period"
    )


class LedgerSummaryOverviewSchema(BaseModel):
    total_balance: Decimal = Field(..., description="Combined balance across accounts")
    active_accounts_count: int = Field(
        ..., description="Number of active accounts for the user"
    )
    transactions_count: int = Field(
        ..., description="Number of transactions in the selected period"
    )
    income_total: Decimal = Field(..., description="Total income in the period")
    expense_total: Decimal = Field(..., description="Total expense in the period")
    net_flow: Decimal = Field(..., description="Income minus expense in the period")
    average_daily_income: Decimal = Field(
        ..., description="Average income per day in the period"
    )
    average_daily_expense: Decimal = Field(
        ..., description="Average expense per day in the period"
    )
    last_transaction_at: datetime | None = Field(
        None, description="Timestamp of the latest transaction in the period"
    )


class LedgerSummaryTrendSchema(BaseModel):
    income_change_pct: float = Field(
        ..., description="Income variation compared with the previous period"
    )
    expense_change_pct: float = Field(
        ..., description="Expense variation compared with the previous period"
    )
    projected_balance_next_period: Decimal = Field(
        ..., description="Projected balance if the current net flow repeats"
    )


class LedgerSummaryPeriodSchema(BaseModel):
    period_days: int = Field(..., description="Number of days used for the summary")
    period_start: datetime = Field(..., description="Start of the summary period")
    period_end: datetime = Field(..., description="End of the summary period")
    previous_period_start: datetime = Field(
        ..., description="Start of the comparison period"
    )
    previous_period_end: datetime = Field(
        ..., description="End of the comparison period"
    )


class LedgerSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    period: LedgerSummaryPeriodSchema
    overview: LedgerSummaryOverviewSchema
    top_accounts: list[LedgerSummaryAccountSchema]
    expenses_by_category: list[LedgerSummaryCategorySchema]
    income_by_category: list[LedgerSummaryCategorySchema]
    trends: LedgerSummaryTrendSchema
    alerts: list[str]
    recommendations: list[str]
