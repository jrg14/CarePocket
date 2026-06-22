from app.modules.expenses.models import Expense, ExpenseCategory
from app.modules.expenses.schemas import (
    CategoryBreakdownItem,
    ExpenseCategoryRead,
    ExpenseRead,
)


def map_category_to_read(category: ExpenseCategory) -> ExpenseCategoryRead:
    return ExpenseCategoryRead(
        id=category.id,
        name=category.name,
        slug=category.slug,
        icon=category.icon,
        color=category.color,
    )


def map_expense_to_read(expense: Expense) -> ExpenseRead:
    return ExpenseRead(
        id=expense.id,
        user_id=expense.user_id,
        category_id=expense.category_id,
        amount=float(expense.amount),
        description=expense.description,
        payment_method=expense.payment_method,
        spent_on=expense.spent_on,
        note=expense.note,
        created_at=expense.created_at,
        updated_at=expense.updated_at,
        category=map_category_to_read(expense.category),
    )


def map_breakdown_item(item: dict[str, object]) -> CategoryBreakdownItem:
    category = item["category"]
    assert isinstance(category, dict)
    return CategoryBreakdownItem(
        category=ExpenseCategoryRead(**category),
        amount=float(item["amount"]),
        percentage=float(item["percentage"]),
    )
