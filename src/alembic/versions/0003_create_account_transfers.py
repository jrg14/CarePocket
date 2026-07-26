"""Create account transfers

Revision ID: 0003_account_transfers
Revises: 0002_ledgers
Create Date: 2026-07-26 00:00:00.000000

This migration adds explicit internal transfers between two active accounts
owned by the same user. Transfers move balance between accounts without being
classified as income or expense transactions.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_account_transfers"
down_revision: str | None = "0002_ledgers"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "account_transfer",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("from_account_id", sa.Integer(), nullable=False),
        sa.Column("to_account_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("transfer_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("description", sa.String(length=180), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["from_account_id"],
            ["account.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["to_account_id"],
            ["account.id"],
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "amount > 0",
            name="ck_account_transfer_amount_positive",
        ),
        sa.CheckConstraint(
            "from_account_id <> to_account_id",
            name="ck_account_transfer_distinct_accounts",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_account_transfer_user_id"),
        "account_transfer",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_account_transfer_from_account_id"),
        "account_transfer",
        ["from_account_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_account_transfer_to_account_id"),
        "account_transfer",
        ["to_account_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_account_transfer_to_account_id"),
        table_name="account_transfer",
    )
    op.drop_index(
        op.f("ix_account_transfer_from_account_id"),
        table_name="account_transfer",
    )
    op.drop_index(
        op.f("ix_account_transfer_user_id"),
        table_name="account_transfer",
    )
    op.drop_table("account_transfer")
