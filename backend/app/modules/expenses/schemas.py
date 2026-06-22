from datetime import date, datetime

from pydantic import BaseModel, Field


class ExpenseCategoryRead(BaseModel):
    id: int
    name: str
    slug: str
    icon: str
    color: str


class ExpenseBase(BaseModel):
    category_id: int
    amount: float = Field(gt=0)
    description: str = Field(min_length=2, max_length=180)
    payment_method: str = Field(default="Tarjeta", min_length=2, max_length=60)
    spent_on: date
    note: str | None = Field(default=None, max_length=1000)


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    category_id: int | None = None
    amount: float | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, min_length=2, max_length=180)
    payment_method: str | None = Field(default=None, min_length=2, max_length=60)
    spent_on: date | None = None
    note: str | None = Field(default=None, max_length=1000)


class ExpenseRead(ExpenseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    category: ExpenseCategoryRead


class ExpenseListResponse(BaseModel):
    items: list[ExpenseRead]
    total: int


class CategoryBreakdownItem(BaseModel):
    category: ExpenseCategoryRead
    amount: float
    percentage: float


class ExpenseSummary(BaseModel):
    period_start: date
    period_end: date
    today_total: float
    week_total: float
    month_total: float
    average_daily: float
    total_expenses: int
    top_category: CategoryBreakdownItem | None
    category_breakdown: list[CategoryBreakdownItem]
    recent_expenses: list[ExpenseRead]
