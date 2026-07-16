from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import TypedDict

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import async_session_maker
from app.modules.ledgers.models import (
    AccountModel,
    TransactionCategoryModel,
    TransactionModel,
)
from app.modules.ledgers.types import CurrencyType, TransactionType
from app.modules.ledgers.utils import to_decimal, transaction_effect


class SummaryCategoryBucket(TypedDict):
    category_id: int | None
    category_name: str
    amount: Decimal


class SummaryCategorySummary(TypedDict):
    category_id: int | None
    category_name: str
    amount: Decimal


class SummaryAccountBucket(TypedDict):
    account_id: int
    account_name: str
    balance: Decimal
    income: Decimal
    expense: Decimal
    expenses_by_category: dict[int | None, SummaryCategoryBucket]


class SummaryAccountSummary(TypedDict):
    account_id: int
    account_name: str
    balance: Decimal
    income: Decimal
    expense: Decimal
    expenses_by_category: list[SummaryCategorySummary]


class SummaryTotalsBucket(TypedDict):
    balance: Decimal
    income: Decimal
    expense: Decimal
    expenses_by_category: dict[int | None, SummaryCategoryBucket]


class SummaryTotalsSummary(TypedDict):
    balance: Decimal
    income: Decimal
    expense: Decimal
    expenses_by_category: list[SummaryCategorySummary]


class SummaryLedgerResponse(TypedDict):
    totals: SummaryTotalsSummary
    accounts: list[SummaryAccountSummary]


# Servicios de cuentas: lectura y escritura sobre cuentas activas.
# Separamos esta lógica para mantener la capa HTTP delgada.
async def get_active_account_by_id(account_id: int) -> AccountModel | None:
    # Buscamos solo cuentas activas para no exponer registros inactivos.
    async with async_session_maker() as session:
        result = await session.execute(
            select(AccountModel).where(
                AccountModel.id == account_id,
                AccountModel.is_active,
            )
        )
        return result.scalar_one_or_none()


async def get_active_accounts_by_user_id(user_id: int) -> list[AccountModel]:
    # Recuperamos solo las cuentas activas del usuario porque son las únicas válidas
    # para el flujo normal de la aplicación.
    async with async_session_maker() as session:
        result = await session.execute(
            select(AccountModel).where(
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
        )
        return result.scalars().all()


async def create_account_for_user(user_id: int, account_name: str) -> AccountModel:
    # Creamos y persistimos la cuenta para devolver el estado real guardado.
    async with async_session_maker() as session:
        account = AccountModel(user_id=user_id, name=account_name)
        session.add(account)
        await session.commit()
        await session.refresh(account)
        return account


async def update_active_account_name(
    account_id: int, user_id: int, account_name: str
) -> AccountModel | None:
    # Validamos propiedad y estado antes de editar, así evitamos modificar una cuenta
    # ajena o desactivada.
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


# Servicios de transacciones:
# concentran la lectura, creación, actualización y borrado de movimientos
# manteniendo la consistencia del balance de la cuenta asociada.
async def get_active_transactions_by_account_id(
    account_id: int, user_id: int, transaction_category_id: int | None = None
) -> list[TransactionModel]:
    # Filtramos por cuenta, usuario y estado para evitar fugas de datos.
    # El filtro opcional por categoría permite reutilizar el servicio.
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
    # Ordenamos alfabéticamente para que la UI muestre un selector estable.
    async with async_session_maker() as session:
        result = await session.execute(
            select(TransactionCategoryModel).order_by(
                TransactionCategoryModel.name.asc()
            )
        )
        return result.scalars().all()


async def get_transaction_by_id(transaction_id: int) -> TransactionModel | None:
    # Cargamos la transacción junto con su cuenta para evitar consultas adicionales
    # cuando la API necesite mostrar contexto del movimiento.
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
    # Antes de crear el movimiento comprobamos que la cuenta pertenezca al usuario
    # y siga activa; así evitamos escribir sobre una cuenta inválida.
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
    # Primero recuperamos la transacción con su cuenta para poder:
    # 1) validar que pertenece al usuario,
    # 2) recalcular el balance correctamente si cambian importe o tipo.
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
        # Guardamos el efecto anterior para revertirlo antes de aplicar el nuevo valor.
        previous_amount = Decimal(transaction.amount)
        previous_type = TransactionType(transaction.transaction_type)
        previous_effect = transaction_effect(previous_amount, previous_type)

        # Calculamos el nuevo efecto a partir de los cambios recibidos.
        new_amount = amount if amount is not None else previous_amount
        new_type = transaction_type if transaction_type is not None else previous_type
        new_effect = transaction_effect(new_amount, new_type)

        # Actualizamos solo los campos enviados para respetar el comportamiento parcial.
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
    # Borramos solo si pertenece al usuario y la cuenta sigue activa.
    # Antes de eliminarla, revertimos su efecto en el balance.
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
) -> SummaryLedgerResponse:
    # Devolvemos un resumen global y otro por cuenta para el periodo seleccionado.
    async with async_session_maker() as session:
        period_end = datetime.now(timezone.utc)
        period_start = period_end - timedelta(days=period_days)

        accounts_result = await session.execute(
            select(AccountModel)
            .where(
                AccountModel.user_id == user_id,
                AccountModel.is_active,
            )
            .order_by(AccountModel.id.asc())
        )
        accounts = accounts_result.scalars().all()

        transactions_result = await session.execute(
            select(TransactionModel, TransactionCategoryModel.name, AccountModel.id)
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
            .order_by(AccountModel.id.asc(), TransactionModel.transaction_date.asc())
        )
        transactions = transactions_result.all()

    totals: SummaryTotalsBucket = {
        "balance": sum(
            (to_decimal(account.balance) for account in accounts), Decimal("0")
        ),
        "income": Decimal("0"),
        "expense": Decimal("0"),
        "expenses_by_category": {},
    }

    account_summaries: dict[int, SummaryAccountBucket] = {
        account.id: {
            "account_id": account.id,
            "account_name": account.name,
            "balance": to_decimal(account.balance),
            "income": Decimal("0"),
            "expense": Decimal("0"),
            "expenses_by_category": {},
        }
        for account in accounts
    }

    for transaction, category_name, account_id in transactions:
        amount = to_decimal(transaction.amount)
        transaction_type = TransactionType(transaction.transaction_type)
        category_id = transaction.transaction_category_id
        category_label = category_name or "Sin categoría"

        account_summary = account_summaries[account_id]

        if transaction_type == TransactionType.INCOME:
            totals["income"] = to_decimal(totals["income"]) + amount
            account_summary["income"] = to_decimal(account_summary["income"]) + amount
            continue

        totals["expense"] = to_decimal(totals["expense"]) + amount
        account_summary["expense"] = to_decimal(account_summary["expense"]) + amount

        totals_categories = totals["expenses_by_category"]
        category_bucket = totals_categories.setdefault(
            category_id,
            {
                "category_id": category_id,
                "category_name": category_label,
                "amount": Decimal("0"),
            },
        )
        category_bucket["amount"] = to_decimal(category_bucket["amount"]) + amount

        account_categories = account_summary["expenses_by_category"]
        account_category_bucket = account_categories.setdefault(
            category_id,
            {
                "category_id": category_id,
                "category_name": category_label,
                "amount": Decimal("0"),
            },
        )
        account_category_bucket["amount"] = (
            to_decimal(account_category_bucket["amount"]) + amount
        )

    totals_expenses_by_category: list[SummaryCategorySummary] = sorted(
        [
            {
                "category_id": item["category_id"],
                "category_name": item["category_name"],
                "amount": to_decimal(item["amount"]),
            }
            for item in totals["expenses_by_category"].values()
        ],
        key=lambda item: item["amount"],
        reverse=True,
    )

    accounts_summary: list[SummaryAccountSummary] = [
        {
            "account_id": account_summary["account_id"],
            "account_name": account_summary["account_name"],
            "balance": account_summary["balance"],
            "income": account_summary["income"],
            "expense": account_summary["expense"],
            "expenses_by_category": sorted(
                [
                    {
                        "category_id": item["category_id"],
                        "category_name": item["category_name"],
                        "amount": to_decimal(item["amount"]),
                    }
                    for item in account_summary["expenses_by_category"].values()
                ],
                key=lambda item: item["amount"],
                reverse=True,
            ),
        }
        for account_summary in account_summaries.values()
    ]

    return {
        "totals": {
            "balance": to_decimal(totals["balance"]),
            "income": to_decimal(totals["income"]),
            "expense": to_decimal(totals["expense"]),
            "expenses_by_category": totals_expenses_by_category,
        },
        "accounts": accounts_summary,
    }
