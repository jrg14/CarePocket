from datetime import date, datetime

from pydantic import BaseModel, Field


class IncomeCategoryRead(BaseModel):
    id: int
    name: str
    slug: str
    icon: str
    color: str


class IncomeBase(BaseModel):
    category_id: int
    amount: float = Field(gt=0)
    description: str = Field(min_length=2, max_length=180)
    source: str = Field(default="Transferencia", min_length=2, max_length=60)
    received_on: date
    note: str | None = Field(default=None, max_length=1000)


class IncomeCreate(IncomeBase):
    pass


class IncomeUpdate(BaseModel):
    category_id: int | None = None
    amount: float | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, min_length=2, max_length=180)
    source: str | None = Field(default=None, min_length=2, max_length=60)
    received_on: date | None = None
    note: str | None = Field(default=None, max_length=1000)


class IncomeRead(IncomeBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    category: IncomeCategoryRead


class IncomeListResponse(BaseModel):
    items: list[IncomeRead]
    total: int


class IncomeBreakdownItem(BaseModel):
    category: IncomeCategoryRead
    amount: float
    percentage: float


class IncomeSummary(BaseModel):
    period_start: date
    period_end: date
    today_total: float
    week_total: float
    month_total: float
    average_daily: float
    total_incomes: int
    top_category: IncomeBreakdownItem | None
    category_breakdown: list[IncomeBreakdownItem]
    recent_incomes: list[IncomeRead]
