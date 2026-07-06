from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import async_session_maker
from app.modules.ledgers.models import (
    AccountModel,
    TransactionCategoryModel,
    TransactionModel,
)
from app.modules.ledgers.types import CurrencyType, TransactionType
from app.modules.ledgers.utils import (
    aggregate_transactions,
    percent_change,
    to_decimal,
    transaction_effect,
)


#
#
# Accounts services
#
#
async def get_active_account_by_id(account_id: int) -> AccountModel | None:
    async with async_session_maker() as session:
        result = await session.execute(
            select(AccountModel).where(
                AccountModel.id == account_id,
                AccountModel.is_active,
            )
        )
        return result.scalar_one_or_none()


async def get_active_accounts_by_user_id(user_id: int) -> list[AccountModel]:
    async with async_session_maker() as session:
        result = await session.execute(
            select(AccountModel).where(
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
        )
        return result.scalars().all()


async def create_account_for_user(user_id: int, account_name: str) -> AccountModel:
    async with async_session_maker() as session:
        account = AccountModel(user_id=user_id, name=account_name)
        session.add(account)
        await session.commit()
        await session.refresh(account)
        return account


async def update_active_account_name(
    account_id: int, user_id: int, account_name: str
) -> AccountModel | None:
    async with async_session_maker() as session:
        result = await session.execute(
            select(AccountModel).where(
                AccountModel.id == account_id,
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
        )
        account = result.scalar_one_or_none()

        if not account:
            return None

        account.name = account_name
        await session.commit()
        await session.refresh(account)
        return account


#
#
# Accounts transactions services
#
#
async def get_active_transactions_by_account_id(
    account_id: int, user_id: int, transaction_category_id: int | None = None
) -> list[TransactionModel]:
    async with async_session_maker() as session:
        query = (
            select(TransactionModel)
            .join(AccountModel, AccountModel.id == TransactionModel.account_id)
            .where(
                TransactionModel.account_id == account_id,
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
            .order_by(TransactionModel.transaction_date.desc())
        )

        if transaction_category_id is not None:
            query = query.where(
                TransactionModel.transaction_category_id == transaction_category_id
            )

        result = await session.execute(query)
        return result.scalars().all()


async def get_transaction_categories() -> list[TransactionCategoryModel]:
    async with async_session_maker() as session:
        result = await session.execute(
            select(TransactionCategoryModel).order_by(
                TransactionCategoryModel.name.asc()
            )
        )
        return result.scalars().all()


async def get_transaction_by_id(transaction_id: int) -> TransactionModel | None:
    async with async_session_maker() as session:
        result = await session.execute(
            select(TransactionModel)
            .options(selectinload(TransactionModel.account))
            .where(TransactionModel.id == transaction_id)
        )
        return result.scalar_one_or_none()


async def create_transaction_for_account(
    account_id: int,
    user_id: int,
    amount: Decimal,
    currency: CurrencyType,
    transaction_type: TransactionType,
    transaction_date: datetime,
    description: str,
    transaction_category_id: int | None,
) -> TransactionModel | None:
    async with async_session_maker() as session:
        result = await session.execute(
            select(AccountModel).where(
                AccountModel.id == account_id,
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
        )
        account = result.scalar_one_or_none()

        if not account:
            return None

        transaction = TransactionModel(
            account_id=account_id,
            amount=amount,
            currency=currency.value,
            transaction_type=transaction_type.value,
            transaction_date=transaction_date,
            transaction_category_id=transaction_category_id,
            description=description,
        )
        account.balance = account.balance + transaction_effect(amount, transaction_type)
        session.add(transaction)
        await session.commit()
        await session.refresh(transaction)
        return transaction


async def update_transaction_for_user(
    transaction_id: int,
    user_id: int,
    amount: Decimal | None = None,
    currency: CurrencyType | None = None,
    transaction_type: TransactionType | None = None,
    transaction_date: datetime | None = None,
    description: str | None = None,
    transaction_category_id: int | None | object = None,
) -> TransactionModel | None:
    async with async_session_maker() as session:
        result = await session.execute(
            select(TransactionModel)
            .options(selectinload(TransactionModel.account))
            .join(AccountModel, AccountModel.id == TransactionModel.account_id)
            .where(
                TransactionModel.id == transaction_id,
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
        )
        transaction = result.scalar_one_or_none()

        if not transaction:
            return None

        account = transaction.account
        previous_amount = Decimal(transaction.amount)
        previous_type = TransactionType(transaction.transaction_type)
        previous_effect = transaction_effect(previous_amount, previous_type)

        new_amount = amount if amount is not None else previous_amount
        new_type = transaction_type if transaction_type is not None else previous_type
        new_effect = transaction_effect(new_amount, new_type)

        transaction.amount = new_amount
        transaction.currency = (
            currency.value if currency is not None else transaction.currency
        )
        transaction.transaction_type = new_type.value
        if transaction_date is not None:
            transaction.transaction_date = transaction_date
        if description is not None:
            transaction.description = description
        if transaction_category_id is not None:
            transaction.transaction_category_id = transaction_category_id

        account.balance = account.balance - previous_effect + new_effect
        await session.commit()
        await session.refresh(transaction)
        return transaction


async def delete_transaction_for_user(transaction_id: int, user_id: int) -> bool:
    async with async_session_maker() as session:
        result = await session.execute(
            select(TransactionModel)
            .options(selectinload(TransactionModel.account))
            .join(AccountModel, AccountModel.id == TransactionModel.account_id)
            .where(
                TransactionModel.id == transaction_id,
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
        )
        transaction = result.scalar_one_or_none()

        if not transaction:
            return False

        account = transaction.account
        effect = transaction_effect(
            Decimal(transaction.amount),
            TransactionType(transaction.transaction_type),
        )
        account.balance = account.balance - effect
        await session.delete(transaction)
        await session.commit()
        return True


async def get_user_ledger_summary(
    user_id: int, period_days: int = 30
) -> dict[str, object]:
    async with async_session_maker() as session:
        now = datetime.now(timezone.utc)
        period_end = now
        period_start = period_end - timedelta(days=period_days)
        previous_period_end = period_start
        previous_period_start = previous_period_end - timedelta(days=period_days)

        accounts_result = await session.execute(
            select(AccountModel).where(
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
        )
        accounts = accounts_result.scalars().all()

        current_transactions_result = await session.execute(
            select(TransactionModel, TransactionCategoryModel.name)
            .join(AccountModel, AccountModel.id == TransactionModel.account_id)
            .outerjoin(
                TransactionCategoryModel,
                TransactionCategoryModel.id == TransactionModel.transaction_category_id,
            )
            .where(
                AccountModel.user_id == user_id,
                AccountModel.is_active,
                TransactionModel.transaction_date >= period_start,
                TransactionModel.transaction_date < period_end,
            )
            .order_by(TransactionModel.transaction_date.asc())
        )
        current_transactions = current_transactions_result.all()

        previous_transactions_result = await session.execute(
            select(TransactionModel, TransactionCategoryModel.name)
            .join(AccountModel, AccountModel.id == TransactionModel.account_id)
            .outerjoin(
                TransactionCategoryModel,
                TransactionCategoryModel.id == TransactionModel.transaction_category_id,
            )
            .where(
                AccountModel.user_id == user_id,
                AccountModel.is_active,
                TransactionModel.transaction_date >= previous_period_start,
                TransactionModel.transaction_date < previous_period_end,
            )
        )
        previous_transactions = previous_transactions_result.all()

    current_data = aggregate_transactions(current_transactions)
    previous_data = aggregate_transactions(previous_transactions)

    total_balance = sum(
        (to_decimal(account.balance) for account in accounts), Decimal("0")
    )
    net_flow = to_decimal(current_data["income_total"]) - to_decimal(
        current_data["expense_total"]
    )

    account_transaction_counts: dict[int, int] = defaultdict(int)
    for transaction, _ in current_transactions:
        account_transaction_counts[transaction.account_id] += 1

    top_accounts = sorted(
        accounts,
        key=lambda account: (to_decimal(account.balance), account.id),
        reverse=True,
    )

    expense_categories = sorted(
        (
            {
                "category_id": item["category_id"],
                "category_name": item["category_name"],
                "amount": to_decimal(item["amount"]),
                "transaction_count": int(item["transaction_count"]),
            }
            for item in current_data["expenses_by_category"]
        ),
        key=lambda item: item["amount"],
        reverse=True,
    )
    income_categories = sorted(
        (
            {
                "category_id": item["category_id"],
                "category_name": item["category_name"],
                "amount": to_decimal(item["amount"]),
                "transaction_count": int(item["transaction_count"]),
            }
            for item in current_data["income_by_category"]
        ),
        key=lambda item: item["amount"],
        reverse=True,
    )

    overview = {
        "total_balance": total_balance,
        "active_accounts_count": len(accounts),
        "transactions_count": int(current_data["transactions_count"]),
        "income_total": to_decimal(current_data["income_total"]),
        "expense_total": to_decimal(current_data["expense_total"]),
        "net_flow": net_flow,
        "average_daily_income": to_decimal(current_data["income_total"]) / period_days,
        "average_daily_expense": to_decimal(current_data["expense_total"])
        / period_days,
        "last_transaction_at": current_data["last_transaction_at"],
    }

    trends = {
        "income_change_pct": percent_change(
            to_decimal(current_data["income_total"]),
            to_decimal(previous_data["income_total"]),
        ),
        "expense_change_pct": percent_change(
            to_decimal(current_data["expense_total"]),
            to_decimal(previous_data["expense_total"]),
        ),
        "projected_balance_next_period": total_balance + net_flow,
    }

    alerts: list[str] = []
    recommendations: list[str] = []

    if overview["transactions_count"] == 0:
        alerts.append("No hay movimientos en el periodo seleccionado.")
        recommendations.append(
            "Registra algunas transacciones para empezar a ver patrones."
        )
    else:
        if to_decimal(current_data["expense_total"]) > to_decimal(
            current_data["income_total"]
        ):
            alerts.append("Estás gastando más de lo que ingresas en este periodo.")

        if (
            to_decimal(previous_data["expense_total"]) > 0
            and trends["expense_change_pct"] > 10
        ):
            alerts.append(
                "Tus gastos han subido con fuerza respecto al periodo anterior."
            )

        if expense_categories:
            top_expense = expense_categories[0]
            expense_total = to_decimal(current_data["expense_total"])
            if expense_total > 0:
                share = (top_expense["amount"] / expense_total) * Decimal("100")
                if share >= 35:
                    alerts.append(
                        f"La categoría {top_expense['category_name']} concentra "
                        f"{share:.0f}% de tu gasto."
                    )
                    recommendations.append(
                        f"Revisar {top_expense['category_name']} puede darte el mayor "
                        "ahorro."
                    )

        if to_decimal(trends["projected_balance_next_period"]) < 0:
            alerts.append("La proyección del próximo periodo es negativa.")
            recommendations.append(
                "Conviene recortar gasto variable o reforzar ingresos."
            )

        if not recommendations and expense_categories:
            top_expense = expense_categories[0]
            recommendations.append(
                f"El gasto más alto está en {top_expense['category_name']}; controlar "
                "esa categoría mejoraría tu cierre."
            )

    if not alerts:
        alerts.append("Tus cuentas están estables en el periodo seleccionado.")
    if not recommendations:
        recommendations.append(
            "Sigue monitorizando ingresos y gastos para detectar desviaciones a tiempo."
        )

    return {
        "period": {
            "period_days": period_days,
            "period_start": period_start,
            "period_end": period_end,
            "previous_period_start": previous_period_start,
            "previous_period_end": previous_period_end,
        },
        "overview": overview,
        "top_accounts": [
            {
                "account_id": account.id,
                "account_name": account.name,
                "balance": to_decimal(account.balance),
                "transaction_count": account_transaction_counts.get(account.id, 0),
            }
            for account in top_accounts
        ],
        "expenses_by_category": expense_categories,
        "income_by_category": income_categories,
        "trends": trends,
        "alerts": alerts,
        "recommendations": recommendations,
    }
