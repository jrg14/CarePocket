from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import Select, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.expenses.models import Expense, ExpenseCategory

DEFAULT_EXPENSE_CATEGORIES: list[dict[str, object]] = [
    {"name": "Comida", "slug": "comida", "icon": "🍽", "color": "#f97316", "sort_order": 1},
    {"name": "Transporte", "slug": "transporte", "icon": "🚇", "color": "#0ea5e9", "sort_order": 2},
    {"name": "Casa", "slug": "casa", "icon": "🏠", "color": "#8b5cf6", "sort_order": 3},
    {"name": "Salud", "slug": "salud", "icon": "🩺", "color": "#ef4444", "sort_order": 4},
    {"name": "Ocio", "slug": "ocio", "icon": "🎮", "color": "#10b981", "sort_order": 5},
    {"name": "Compras", "slug": "compras", "icon": "🛍", "color": "#ec4899", "sort_order": 6},
    {"name": "Suscripciones", "slug": "suscripciones", "icon": "💳", "color": "#6366f1", "sort_order": 7},
    {"name": "Imprevistos", "slug": "imprevistos", "icon": "⚡", "color": "#64748b", "sort_order": 8},
]


def _start_of_today() -> date:
    return datetime.now(timezone.utc).astimezone().date()


async def ensure_default_categories(session: AsyncSession) -> None:
    result = await session.execute(select(ExpenseCategory.id).limit(1))
    if result.scalar_one_or_none() is not None:
        return

    session.add_all(
        [ExpenseCategory(is_active=True, **payload) for payload in DEFAULT_EXPENSE_CATEGORIES]
    )
    await session.commit()


async def get_categories(session: AsyncSession) -> list[ExpenseCategory]:
    result = await session.execute(
        select(ExpenseCategory)
        .where(ExpenseCategory.is_active.is_(True))
        .order_by(ExpenseCategory.sort_order, ExpenseCategory.name)
    )
    return list(result.scalars().all())


async def get_category_or_404(session: AsyncSession, category_id: int) -> ExpenseCategory:
    result = await session.execute(
        select(ExpenseCategory).where(
            ExpenseCategory.id == category_id,
            ExpenseCategory.is_active.is_(True),
        )
    )
    category = result.scalar_one_or_none()
    if category is None:
        raise LookupError("category-not-found")
    return category


async def list_expenses(
    session: AsyncSession,
    user_id: int,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    category_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Expense], int]:
    clauses = [Expense.user_id == user_id]
    if start_date is not None:
        clauses.append(Expense.spent_on >= start_date)
    if end_date is not None:
        clauses.append(Expense.spent_on <= end_date)
    if category_id is not None:
        clauses.append(Expense.category_id == category_id)

    count_stmt = select(func.count()).select_from(Expense).where(*clauses)
    total = await session.scalar(count_stmt)

    stmt: Select[tuple[Expense]] = (
        select(Expense)
        .options(selectinload(Expense.category))
        .where(*clauses)
        .order_by(desc(Expense.spent_on), desc(Expense.created_at), desc(Expense.id))
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all()), int(total or 0)


async def get_expense_by_id(
    session: AsyncSession,
    user_id: int,
    expense_id: int,
) -> Expense | None:
    result = await session.execute(
        select(Expense)
        .options(selectinload(Expense.category))
        .where(
            Expense.id == expense_id,
            Expense.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def create_expense(
    session: AsyncSession,
    user_id: int,
    *,
    category_id: int,
    amount: float,
    description: str,
    payment_method: str,
    spent_on: date,
    note: str | None,
) -> Expense:
    expense = Expense(
        user_id=user_id,
        category_id=category_id,
        amount=Decimal(str(amount)),
        description=description,
        payment_method=payment_method,
        spent_on=spent_on,
        note=note,
    )
    session.add(expense)
    await session.commit()
    await session.refresh(expense)
    return expense


async def update_expense(
    session: AsyncSession,
    expense: Expense,
    **updates: object,
) -> Expense:
    for key, value in updates.items():
        if value is not None or key == "note":
            if key == "amount":
                setattr(expense, key, Decimal(str(value)))
            else:
                setattr(expense, key, value)

    await session.commit()
    await session.refresh(expense)
    return expense


async def delete_expense(session: AsyncSession, expense: Expense) -> None:
    await session.delete(expense)
    await session.commit()


async def get_summary(
    session: AsyncSession,
    user_id: int,
    *,
    today: date | None = None,
) -> dict[str, object]:
    today = today or _start_of_today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    tomorrow = today + timedelta(days=1)
    next_week = week_start + timedelta(days=7)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)

    async def _sum_for_range(start: date, end: date) -> float:
        total = await session.scalar(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                Expense.user_id == user_id,
                Expense.spent_on >= start,
                Expense.spent_on < end,
            )
        )
        return float(total or 0)

    today_total = await _sum_for_range(today, tomorrow)
    week_total = await _sum_for_range(week_start, next_week)
    month_total = await _sum_for_range(month_start, next_month)

    total_expenses = int(
        await session.scalar(
            select(func.count()).select_from(Expense).where(Expense.user_id == user_id)
        )
        or 0
    )

    breakdown_result = await session.execute(
        select(
            Expense.category_id,
            func.sum(Expense.amount).label("amount"),
            ExpenseCategory.id,
            ExpenseCategory.name,
            ExpenseCategory.slug,
            ExpenseCategory.icon,
            ExpenseCategory.color,
        )
        .join(ExpenseCategory, ExpenseCategory.id == Expense.category_id)
        .where(
            Expense.user_id == user_id,
            Expense.spent_on >= month_start,
            Expense.spent_on < next_month,
        )
        .group_by(
            Expense.category_id,
            ExpenseCategory.id,
            ExpenseCategory.name,
            ExpenseCategory.slug,
            ExpenseCategory.icon,
            ExpenseCategory.color,
        )
        .order_by(desc(func.sum(Expense.amount)))
    )
    breakdown_rows: Sequence[tuple] = breakdown_result.all()

    category_breakdown: list[dict[str, object]] = []
    for row in breakdown_rows:
        amount = float(row.amount or 0)
        category_breakdown.append(
            {
                "category": {
                    "id": row.id,
                    "name": row.name,
                    "slug": row.slug,
                    "icon": row.icon,
                    "color": row.color,
                },
                "amount": amount,
                "percentage": round((amount / month_total * 100) if month_total else 0, 1),
            }
        )

    recent_result = await session.execute(
        select(Expense)
        .options(selectinload(Expense.category))
        .where(Expense.user_id == user_id)
        .order_by(desc(Expense.spent_on), desc(Expense.created_at), desc(Expense.id))
        .limit(8)
    )
    recent_expenses = list(recent_result.scalars().all())

    top_category = category_breakdown[0] if category_breakdown else None

    elapsed_days = max((today - month_start).days + 1, 1)

    return {
        "period_start": month_start,
        "period_end": next_month - timedelta(days=1),
        "today_total": today_total,
        "week_total": week_total,
        "month_total": month_total,
        "average_daily": round(month_total / elapsed_days, 2),
        "total_expenses": total_expenses,
        "top_category": top_category,
        "category_breakdown": category_breakdown,
        "recent_expenses": recent_expenses,
    }
