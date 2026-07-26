from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.ledgers.types import (
    CurrencyType,
    TransactionRecurringType,
    TransactionType,
)


class AccountModel(Base):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(length=80), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    transactions: Mapped[list["TransactionModel"]] = relationship(
        "TransactionModel", back_populates="account"
    )
    outgoing_transfers: Mapped[list["TransferModel"]] = relationship(
        "TransferModel",
        back_populates="from_account",
        foreign_keys="TransferModel.from_account_id",
    )
    incoming_transfers: Mapped[list["TransferModel"]] = relationship(
        "TransferModel",
        back_populates="to_account",
        foreign_keys="TransferModel.to_account_id",
    )


class TransactionModel(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[CurrencyType] = mapped_column(String(3), default=CurrencyType.EUR)
    transaction_type: Mapped[TransactionType] = mapped_column(
        String(length=20), nullable=False
    )
    transaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    transaction_category_id: Mapped[int] = mapped_column(
        ForeignKey("transaction_category.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    description: Mapped[str] = mapped_column(String(length=180), nullable=False)

    account: Mapped["AccountModel"] = relationship(
        "AccountModel", back_populates="transactions"
    )


class TransferModel(Base):
    __tablename__ = "account_transfer"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_account_transfer_amount_positive"),
        CheckConstraint(
            "from_account_id <> to_account_id",
            name="ck_account_transfer_distinct_accounts",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    from_account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    to_account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[CurrencyType] = mapped_column(String(3), default=CurrencyType.EUR)
    transfer_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    description: Mapped[str] = mapped_column(String(length=180), nullable=False)

    from_account: Mapped["AccountModel"] = relationship(
        "AccountModel",
        back_populates="outgoing_transfers",
        foreign_keys=[from_account_id],
    )
    to_account: Mapped["AccountModel"] = relationship(
        "AccountModel",
        back_populates="incoming_transfers",
        foreign_keys=[to_account_id],
    )


class TransactionCategoryModel(Base):
    __tablename__ = "transaction_category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(length=80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class RecurringTransactionModel(Base):
    __tablename__ = "recurring_transaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(
        String(length=20), nullable=False
    )
    transaction_category_id: Mapped[int] = mapped_column(
        ForeignKey("transaction_category.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    description: Mapped[str] = mapped_column(String(length=180), nullable=False)
    recurring_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    recurring_frequency: Mapped[TransactionRecurringType | None] = mapped_column(
        String(length=20), nullable=True
    )
