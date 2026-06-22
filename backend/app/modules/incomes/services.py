from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import Select, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.incomes.models import Income, IncomeCategory

DEFAULT_INCOME_CATEGORIES: list[dict[str, object]] = [
    {"name": "Salario", "slug": "salario", "icon": "💼", "color": "#0f766e", "sort_order": 1},
    {"name": "Freelance", "slug": "freelance", "icon": "🧑‍💻", "color": "#2563eb", "sort_order": 2},
    {"name": "Negocio", "slug": "negocio", "icon": "🏢", "color": "#8b5cf6", "sort_order": 3},
    {"name": "Becas", "slug": "becas", "icon": "🎓", "color": "#0ea5e9", "sort_order": 4},
    {"name": "Reembolsos", "slug": "reembolsos", "icon": "↩", "color": "#10b981", "sort_order": 5},
    {"name": "Otros", "slug": "otros", "icon": "💡", "color": "#64748b", "sort_order": 6},
]


def _start_of_today() -> date:
    return datetime.now(timezone.utc).astimezone().date()


async def ensure_default_categories(session: AsyncSession) -> None:
    result = await session.execute(select(IncomeCategory.id).limit(1))
    if result.scalar_one_or_none() is not None:
        return

    session.add_all(
        [IncomeCategory(is_active=True, **payload) for payload in DEFAULT_INCOME_CATEGORIES]
    )
    await session.commit()


async def get_categories(session: AsyncSession) -> list[IncomeCategory]:
    result = await session.execute(
        select(IncomeCategory)
        .where(IncomeCategory.is_active.is_(True))
        .order_by(IncomeCategory.sort_order, IncomeCategory.name)
    )
    return list(result.scalars().all())


async def get_category_or_404(session: AsyncSession, category_id: int) -> IncomeCategory:
    result = await session.execute(
        select(IncomeCategory).where(
            IncomeCategory.id == category_id,
            IncomeCategory.is_active.is_(True),
        )
    )
    category = result.scalar_one_or_none()
    if category is None:
        raise LookupError("category-not-found")
    return category


async def list_incomes(
    session: AsyncSession,
    user_id: int,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    category_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Income], int]:
    clauses = [Income.user_id == user_id]
    if start_date is not None:
        clauses.append(Income.received_on >= start_date)
    if end_date is not None:
        clauses.append(Income.received_on <= end_date)
    if category_id is not None:
        clauses.append(Income.category_id == category_id)

    count_stmt = select(func.count()).select_from(Income).where(*clauses)
    total = await session.scalar(count_stmt)

    stmt: Select[tuple[Income]] = (
        select(Income)
        .options(selectinload(Income.category))
        .where(*clauses)
        .order_by(desc(Income.received_on), desc(Income.created_at), desc(Income.id))
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all()), int(total or 0)


async def get_income_by_id(
    session: AsyncSession,
    user_id: int,
    income_id: int,
) -> Income | None:
    result = await session.execute(
        select(Income)
        .options(selectinload(Income.category))
        .where(
            Income.id == income_id,
            Income.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def create_income(
    session: AsyncSession,
    user_id: int,
    *,
    category_id: int,
    amount: float,
    description: str,
    source: str,
    received_on: date,
    note: str | None,
) -> Income:
    income = Income(
        user_id=user_id,
        category_id=category_id,
        amount=Decimal(str(amount)),
        description=description,
        source=source,
        received_on=received_on,
        note=note,
    )
    session.add(income)
    await session.commit()
    await session.refresh(income)
    return income


async def update_income(
    session: AsyncSession,
    income: Income,
    **updates: object,
) -> Income:
    for key, value in updates.items():
        if value is not None or key == "note":
            if key == "amount":
                setattr(income, key, Decimal(str(value)))
            else:
                setattr(income, key, value)

    await session.commit()
    await session.refresh(income)
    return income


async def delete_income(session: AsyncSession, income: Income) -> None:
    await session.delete(income)
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
            select(func.coalesce(func.sum(Income.amount), 0)).where(
                Income.user_id == user_id,
                Income.received_on >= start,
                Income.received_on < end,
            )
        )
        return float(total or 0)

    today_total = await _sum_for_range(today, tomorrow)
    week_total = await _sum_for_range(week_start, next_week)
    month_total = await _sum_for_range(month_start, next_month)

    total_incomes = int(
        await session.scalar(
            select(func.count()).select_from(Income).where(Income.user_id == user_id)
        )
        or 0
    )

    breakdown_result = await session.execute(
        select(
            Income.category_id,
            func.sum(Income.amount).label("amount"),
            IncomeCategory.id,
            IncomeCategory.name,
            IncomeCategory.slug,
            IncomeCategory.icon,
            IncomeCategory.color,
        )
        .join(IncomeCategory, IncomeCategory.id == Income.category_id)
        .where(
            Income.user_id == user_id,
            Income.received_on >= month_start,
            Income.received_on < next_month,
        )
        .group_by(
            Income.category_id,
            IncomeCategory.id,
            IncomeCategory.name,
            IncomeCategory.slug,
            IncomeCategory.icon,
            IncomeCategory.color,
        )
        .order_by(desc(func.sum(Income.amount)))
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
        select(Income)
        .options(selectinload(Income.category))
        .where(Income.user_id == user_id)
        .order_by(desc(Income.received_on), desc(Income.created_at), desc(Income.id))
        .limit(8)
    )
    recent_incomes = list(recent_result.scalars().all())

    top_category = category_breakdown[0] if category_breakdown else None

    elapsed_days = max((today - month_start).days + 1, 1)

    return {
        "period_start": month_start,
        "period_end": next_month - timedelta(days=1),
        "today_total": today_total,
        "week_total": week_total,
        "month_total": month_total,
        "average_daily": round(month_total / elapsed_days, 2),
        "total_incomes": total_incomes,
        "top_category": top_category,
        "category_breakdown": category_breakdown,
        "recent_incomes": recent_incomes,
    }
