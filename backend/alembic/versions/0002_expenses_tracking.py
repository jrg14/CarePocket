"""Create expense tracking tables

Revision ID: 0002_expenses_tracking
Revises: 0001_initial_users
Create Date: 2026-06-21 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_expenses_tracking"
down_revision: str | None = "0001_initial_users"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "expense_category",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("icon", sa.String(length=24), nullable=False),
        sa.Column("color", sa.String(length=32), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "expense",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("description", sa.String(length=180), nullable=False),
        sa.Column("payment_method", sa.String(length=60), nullable=False),
        sa.Column("spent_on", sa.Date(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["expense_category.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_expense_category_id"), "expense", ["category_id"], unique=False)
    op.create_index(op.f("ix_expense_spent_on"), "expense", ["spent_on"], unique=False)
    op.create_index(op.f("ix_expense_user_id"), "expense", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_expense_user_id"), table_name="expense")
    op.drop_index(op.f("ix_expense_spent_on"), table_name="expense")
    op.drop_index(op.f("ix_expense_category_id"), table_name="expense")
    op.drop_table("expense")
    op.drop_table("expense_category")
