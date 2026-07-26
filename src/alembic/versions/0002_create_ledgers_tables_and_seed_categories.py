"""Create ledgers tables and seed transaction categories

Revision ID: 0002_create_ledgers_tables_and_seed_categories
Revises: 0001_initial_users
Create Date: 2026-07-15 00:00:00.000000

This migration creates the full ledgers schema:
- account
- transaction_category
- transaction
- recurring_transaction

It also seeds the default transaction categories used by the application on
first install, covering spending, saving, and investing.
"""

from collections.abc import Sequence
from datetime import datetime, timezone

import sqlalchemy as sa

from alembic import op

revision: str = "0002_ledgers"
down_revision: str | None = "0001_initial_users"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

seed_created_at = datetime(2026, 7, 15, tzinfo=timezone.utc)

categories: list[dict[str, object]] = [
    {
        "name": "Supermercado",
        "description": "Gastos en alimentos, limpieza y productos del hogar",
        "created_at": seed_created_at,
    },
    {
        "name": "Restaurantes",
        "description": "Comidas fuera de casa, bares y servicios de delivery",
        "created_at": seed_created_at,
    },
    {
        "name": "Transporte",
        "description": "Transporte publico, taxis y movilidad urbana",
        "created_at": seed_created_at,
    },
    {
        "name": "Gasolina",
        "description": "Combustible, recargas y costes de vehiculo relacionados",
        "created_at": seed_created_at,
    },
    {
        "name": "Vivienda",
        "description": "Alquiler, hipoteca y gastos fijos de la vivienda",
        "created_at": seed_created_at,
    },
    {
        "name": "Luz y agua",
        "description": "Suministros del hogar como electricidad, agua y gas",
        "created_at": seed_created_at,
    },
    {
        "name": "Telefonia e internet",
        "description": "Telefono movil, fibra, internet y servicios de conectividad",
        "created_at": seed_created_at,
    },
    {
        "name": "Suscripciones",
        "description": "Servicios digitales como streaming, software y membresias",
        "created_at": seed_created_at,
    },
    {
        "name": "Salud",
        "description": "Farmacia, consultas medicas, dental y bienestar",
        "created_at": seed_created_at,
    },
    {
        "name": "Farmacia",
        "description": "Medicamentos, productos sanitarios y parafarmacia",
        "created_at": seed_created_at,
    },
    {
        "name": "Educacion",
        "description": "Cursos, libros, matriculas y material educativo",
        "created_at": seed_created_at,
    },
    {
        "name": "Ropa y calzado",
        "description": "Prendas de vestir, zapatos y accesorios",
        "created_at": seed_created_at,
    },
    {
        "name": "Hogar",
        "description": "Muebles, decoracion, mantenimiento y reparaciones",
        "created_at": seed_created_at,
    },
    {
        "name": "Ocio",
        "description": "Cine, eventos, hobbies, juegos y entretenimiento",
        "created_at": seed_created_at,
    },
    {
        "name": "Viajes",
        "description": "Hoteles, vuelos, alojamiento y gastos de desplazamiento",
        "created_at": seed_created_at,
    },
    {
        "name": "Seguros",
        "description": "Seguro de coche, hogar, salud y otras polizas",
        "created_at": seed_created_at,
    },
    {
        "name": "Impuestos",
        "description": "Impuestos, tasas y obligaciones fiscales",
        "created_at": seed_created_at,
    },
    {
        "name": "Mascotas",
        "description": "Comida, veterinario y cuidados de mascotas",
        "created_at": seed_created_at,
    },
    {
        "name": "Cuidado personal",
        "description": "Peluqueria, estetica, higiene y bienestar personal",
        "created_at": seed_created_at,
    },
    {
        "name": "Banco y comisiones",
        "description": "Mantenimiento de cuenta, comisiones y cargos bancarios",
        "created_at": seed_created_at,
    },
    {
        "name": "Ahorro",
        "description": "Ahorro general para objetivos personales o financieros",
        "created_at": seed_created_at,
    },
    {
        "name": "Fondo de emergencia",
        "description": "Reserva destinada a imprevistos y gastos urgentes",
        "created_at": seed_created_at,
    },
    {
        "name": "Inversiones",
        "description": "Aportaciones a productos de inversion a largo plazo",
        "created_at": seed_created_at,
    },
    {
        "name": "Fondos indexados",
        "description": "Aportaciones a fondos indexados y fondos cotizados",
        "created_at": seed_created_at,
    },
    {
        "name": "Acciones",
        "description": "Compra y venta de acciones de empresas",
        "created_at": seed_created_at,
    },
    {
        "name": "Criptomonedas",
        "description": "Compra, venta y custodia de activos digitales",
        "created_at": seed_created_at,
    },
    {
        "name": "Planes de pensiones",
        "description": "Aportaciones para jubilacion o retiro",
        "created_at": seed_created_at,
    },
]


def upgrade() -> None:
    op.create_table(
        "account",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("balance", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_account_user_id"), "account", ["user_id"], unique=False)

    op.create_table(
        "transaction_category",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "transaction",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("transaction_type", sa.String(length=20), nullable=False),
        sa.Column("transaction_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("transaction_category_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(length=180), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["account.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["transaction_category_id"],
            ["transaction_category.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_transaction_account_id"),
        "transaction",
        ["account_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transaction_transaction_category_id"),
        "transaction",
        ["transaction_category_id"],
        unique=False,
    )

    op.create_table(
        "recurring_transaction",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("transaction_type", sa.String(length=20), nullable=False),
        sa.Column("transaction_category_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(length=180), nullable=False),
        sa.Column("recurring_date", sa.Date(), nullable=True),
        sa.Column("recurring_frequency", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["account.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["transaction_category_id"],
            ["transaction_category.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_recurring_transaction_account_id"),
        "recurring_transaction",
        ["account_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recurring_transaction_transaction_category_id"),
        "recurring_transaction",
        ["transaction_category_id"],
        unique=False,
    )

    transaction_category_table = sa.table(
        "transaction_category",
        sa.column("name", sa.String(length=80)),
        sa.column("description", sa.Text()),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    op.bulk_insert(transaction_category_table, categories)


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM transaction_category WHERE name IN "
            "('Supermercado', 'Restaurantes', 'Transporte', 'Gasolina', "
            "'Vivienda', 'Luz y agua', 'Telefonia e internet', 'Suscripciones', "
            "'Salud', 'Farmacia', 'Educacion', 'Ropa y calzado', 'Hogar', "
            "'Ocio', 'Viajes', 'Seguros', 'Impuestos', 'Mascotas', "
            "'Cuidado personal', 'Banco y comisiones', 'Ahorro', "
            "'Fondo de emergencia', 'Inversiones', 'Fondos indexados', "
            "'Acciones', 'Criptomonedas', 'Planes de pensiones')"
        )
    )
    op.drop_index(
        op.f("ix_recurring_transaction_transaction_category_id"),
        table_name="recurring_transaction",
    )
    op.drop_index(
        op.f("ix_recurring_transaction_account_id"),
        table_name="recurring_transaction",
    )
    op.drop_table("recurring_transaction")
    op.drop_index(
        op.f("ix_transaction_transaction_category_id"),
        table_name="transaction",
    )
    op.drop_index(op.f("ix_transaction_account_id"), table_name="transaction")
    op.drop_table("transaction")
    op.drop_table("transaction_category")
    op.drop_index(op.f("ix_account_user_id"), table_name="account")
    op.drop_table("account")
