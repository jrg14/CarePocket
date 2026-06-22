from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.expenses.mapper import (
    map_breakdown_item,
    map_category_to_read,
    map_expense_to_read,
)
from app.db.session import get_db
from app.modules.expenses.schemas import (
    ExpenseCategoryRead,
    ExpenseCreate,
    ExpenseListResponse,
    ExpenseRead,
    ExpenseSummary,
    ExpenseUpdate,
)
from app.modules.expenses.services import (
    create_expense,
    delete_expense,
    ensure_default_categories,
    get_categories,
    get_category_or_404,
    get_expense_by_id,
    get_summary,
    list_expenses,
    update_expense,
)
from app.modules.users.auth import current_active_user
from app.modules.users.models import User

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/categories", response_model=list[ExpenseCategoryRead])
async def read_expense_categories(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[ExpenseCategoryRead]:
    await ensure_default_categories(session)
    categories = await get_categories(session)
    return [map_category_to_read(category) for category in categories]


@router.get("/summary", response_model=ExpenseSummary)
async def read_expense_summary(
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ExpenseSummary:
    await ensure_default_categories(session)
    summary = await get_summary(session, user.id)
    return ExpenseSummary(
        period_start=summary["period_start"],
        period_end=summary["period_end"],
        today_total=summary["today_total"],
        week_total=summary["week_total"],
        month_total=summary["month_total"],
        average_daily=summary["average_daily"],
        total_expenses=summary["total_expenses"],
        top_category=(
            map_breakdown_item(summary["top_category"])
            if summary["top_category"] is not None
            else None
        ),
        category_breakdown=[
            map_breakdown_item(item) for item in summary["category_breakdown"]
        ],
        recent_expenses=[
            map_expense_to_read(expense) for expense in summary["recent_expenses"]
        ],
    )


@router.get("", response_model=ExpenseListResponse)
async def read_expenses(
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    start_date: date | None = None,
    end_date: date | None = None,
    category_id: int | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ExpenseListResponse:
    await ensure_default_categories(session)
    expenses, total = await list_expenses(
        session,
        user.id,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        limit=limit,
        offset=offset,
    )
    return ExpenseListResponse(
        items=[map_expense_to_read(expense) for expense in expenses],
        total=total,
    )


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
async def create_expense_item(
    payload: ExpenseCreate,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ExpenseRead:
    await ensure_default_categories(session)
    try:
        await get_category_or_404(session, payload.category_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Categoría no encontrada") from exc

    expense = await create_expense(
        session,
        user.id,
        category_id=payload.category_id,
        amount=payload.amount,
        description=payload.description,
        payment_method=payload.payment_method,
        spent_on=payload.spent_on,
        note=payload.note,
    )
    expense.category = await get_category_or_404(session, expense.category_id)
    return map_expense_to_read(expense)


@router.get("/{expense_id}", response_model=ExpenseRead)
async def read_expense_item(
    expense_id: int,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ExpenseRead:
    expense = await get_expense_by_id(session, user.id, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    expense.category = await get_category_or_404(session, expense.category_id)
    return map_expense_to_read(expense)


@router.patch("/{expense_id}", response_model=ExpenseRead)
async def update_expense_item(
    expense_id: int,
    payload: ExpenseUpdate,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ExpenseRead:
    expense = await get_expense_by_id(session, user.id, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")

    updates = payload.model_dump(exclude_unset=True)
    if "category_id" in updates:
        try:
            await get_category_or_404(session, int(updates["category_id"]))
        except LookupError as exc:
            raise HTTPException(
                status_code=404, detail="Categoría no encontrada"
            ) from exc

    if "amount" in updates and updates["amount"] is not None:
        updates["amount"] = updates["amount"]

    expense = await update_expense(session, expense, **updates)
    expense.category = await get_category_or_404(session, expense.category_id)
    return map_expense_to_read(expense)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_item(
    expense_id: int,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    expense = await get_expense_by_id(session, user.id, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    await delete_expense(session, expense)
