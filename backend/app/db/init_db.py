from sqlalchemy import select

import app.modules.expenses.models  # noqa: F401
import app.modules.incomes.models  # noqa: F401
import app.modules.users.models  # noqa: F401

from app.db.base import Base
from app.db.session import engine
from app.modules.expenses.models import ExpenseCategory
from app.modules.expenses.services import DEFAULT_EXPENSE_CATEGORIES
from app.modules.incomes.models import IncomeCategory
from app.modules.incomes.services import DEFAULT_INCOME_CATEGORIES


async def init_db() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        expense_categories = await connection.execute(
            select(ExpenseCategory.id).limit(1)
        )
        if expense_categories.scalar_one_or_none() is None:
            await connection.execute(
                ExpenseCategory.__table__.insert(),
                [
                    {**payload, "is_active": True}
                    for payload in DEFAULT_EXPENSE_CATEGORIES
                ],
            )

        income_categories = await connection.execute(select(IncomeCategory.id).limit(1))
        if income_categories.scalar_one_or_none() is None:
            await connection.execute(
                IncomeCategory.__table__.insert(),
                [
                    {**payload, "is_active": True}
                    for payload in DEFAULT_INCOME_CATEGORIES
                ],
            )
