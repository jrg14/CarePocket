from app.modules.incomes.models import Income, IncomeCategory
from app.modules.incomes.schemas import (
    IncomeBreakdownItem,
    IncomeCategoryRead,
    IncomeRead,
)


def map_category_to_read(category: IncomeCategory) -> IncomeCategoryRead:
    return IncomeCategoryRead(
        id=category.id,
        name=category.name,
        slug=category.slug,
        icon=category.icon,
        color=category.color,
    )


def map_income_to_read(income: Income) -> IncomeRead:
    return IncomeRead(
        id=income.id,
        user_id=income.user_id,
        category_id=income.category_id,
        amount=float(income.amount),
        description=income.description,
        source=income.source,
        received_on=income.received_on,
        note=income.note,
        created_at=income.created_at,
        updated_at=income.updated_at,
        category=map_category_to_read(income.category),
    )


def map_breakdown_item(item: dict[str, object]) -> IncomeBreakdownItem:
    category = item["category"]
    assert isinstance(category, dict)
    return IncomeBreakdownItem(
        category=IncomeCategoryRead(**category),
        amount=float(item["amount"]),
        percentage=float(item["percentage"]),
    )
