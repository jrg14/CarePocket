from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.incomes.mapper import (
    map_breakdown_item,
    map_category_to_read,
    map_income_to_read,
)
from app.db.session import get_db
from app.modules.incomes.schemas import (
    IncomeCategoryRead,
    IncomeCreate,
    IncomeListResponse,
    IncomeRead,
    IncomeSummary,
    IncomeUpdate,
)
from app.modules.incomes.services import (
    create_income,
    delete_income,
    ensure_default_categories,
    get_categories,
    get_category_or_404,
    get_income_by_id,
    get_summary,
    list_incomes,
    update_income,
)
from app.modules.users.auth import current_active_user
from app.modules.users.models import User

router = APIRouter(prefix="/incomes", tags=["incomes"])


@router.get("/categories", response_model=list[IncomeCategoryRead])
async def read_income_categories(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[IncomeCategoryRead]:
    await ensure_default_categories(session)
    categories = await get_categories(session)
    return [map_category_to_read(category) for category in categories]


@router.get("/summary", response_model=IncomeSummary)
async def read_income_summary(
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> IncomeSummary:
    await ensure_default_categories(session)
    summary = await get_summary(session, user.id)
    return IncomeSummary(
        period_start=summary["period_start"],
        period_end=summary["period_end"],
        today_total=summary["today_total"],
        week_total=summary["week_total"],
        month_total=summary["month_total"],
        average_daily=summary["average_daily"],
        total_incomes=summary["total_incomes"],
        top_category=(
            map_breakdown_item(summary["top_category"])
            if summary["top_category"] is not None
            else None
        ),
        category_breakdown=[
            map_breakdown_item(item) for item in summary["category_breakdown"]
        ],
        recent_incomes=[
            map_income_to_read(income) for income in summary["recent_incomes"]
        ],
    )


@router.get("", response_model=IncomeListResponse)
async def read_incomes(
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    start_date: date | None = None,
    end_date: date | None = None,
    category_id: int | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> IncomeListResponse:
    await ensure_default_categories(session)
    incomes, total = await list_incomes(
        session,
        user.id,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        limit=limit,
        offset=offset,
    )
    return IncomeListResponse(
        items=[map_income_to_read(income) for income in incomes],
        total=total,
    )


@router.post("", response_model=IncomeRead, status_code=status.HTTP_201_CREATED)
async def create_income_item(
    payload: IncomeCreate,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> IncomeRead:
    await ensure_default_categories(session)
    try:
        await get_category_or_404(session, payload.category_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Categoría no encontrada") from exc

    income = await create_income(
        session,
        user.id,
        category_id=payload.category_id,
        amount=payload.amount,
        description=payload.description,
        source=payload.source,
        received_on=payload.received_on,
        note=payload.note,
    )
    income.category = await get_category_or_404(session, income.category_id)
    return map_income_to_read(income)


@router.get("/{income_id}", response_model=IncomeRead)
async def read_income_item(
    income_id: int,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> IncomeRead:
    income = await get_income_by_id(session, user.id, income_id)
    if income is None:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")
    income.category = await get_category_or_404(session, income.category_id)
    return map_income_to_read(income)


@router.patch("/{income_id}", response_model=IncomeRead)
async def update_income_item(
    income_id: int,
    payload: IncomeUpdate,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> IncomeRead:
    income = await get_income_by_id(session, user.id, income_id)
    if income is None:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")

    updates = payload.model_dump(exclude_unset=True)
    if "category_id" in updates:
        try:
            await get_category_or_404(session, int(updates["category_id"]))
        except LookupError as exc:
            raise HTTPException(
                status_code=404, detail="Categoría no encontrada"
            ) from exc

    income = await update_income(session, income, **updates)
    income.category = await get_category_or_404(session, income.category_id)
    return map_income_to_read(income)


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_income_item(
    income_id: int,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    income = await get_income_by_id(session, user.id, income_id)
    if income is None:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")
    await delete_income(session, income)
