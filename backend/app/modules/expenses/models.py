from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ExpenseCategory(Base):
    __tablename__ = "expense_category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=80), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(length=80), unique=True, nullable=False)
    icon: Mapped[str] = mapped_column(String(length=24), nullable=False)
    color: Mapped[str] = mapped_column(String(length=32), nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )


class Expense(Base):
    __tablename__ = "expense"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("expense_category.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(length=180), nullable=False)
    payment_method: Mapped[str] = mapped_column(
        String(length=60),
        nullable=False,
        default="Tarjeta",
    )
    spent_on: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    category: Mapped["ExpenseCategory"] = relationship(back_populates="expenses")
