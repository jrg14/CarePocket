# Modelos del módulo `ledgers`

## Resumen financiero

La respuesta del resumen financiero está formada por:

- `totals`
  - `balance`
  - `income`
  - `expense`
  - `expenses_by_category`
- `accounts`
  - `account_id`
  - `account_name`
  - `balance`
  - `income`
  - `expense`
  - `expenses_by_category`

Las categorías de gasto se agrupan por `category_id` y `category_name`, y se ordenan por importe descendente.

## `AccountModel`

Representa una cuenta financiera del usuario.

- `id`: identificador interno de la cuenta.
- `created_at`: fecha de creación.
- `user_id`: usuario propietario.
- `name`: nombre visible de la cuenta.
- `balance`: balance actual de la cuenta.
- `is_active`: permite desactivar cuentas sin borrar su historial.

## `TransactionModel`

Representa un ingreso o gasto real dentro de una cuenta.

- `id`: identificador interno de la transacción.
- `created_at`: fecha de creación del registro.
- `account_id`: cuenta a la que pertenece la transacción.
- `amount`: importe positivo de la operación.
- `currency`: moneda de la operación.
- `transaction_type`: tipo de operación, `income` o `expense`.
- `transaction_date`: fecha económica de la operación.
- `transaction_category_id`: categoría opcional.
- `description`: descripción visible para el usuario.

Las transacciones actualizan el balance de su cuenta. Los ingresos suman y los
gastos restan.

## `TransferModel`

Representa una transferencia interna entre dos cuentas activas del mismo usuario.

- `id`: identificador interno de la transferencia.
- `created_at`: fecha de creación del registro.
- `user_id`: usuario propietario de la transferencia.
- `from_account_id`: cuenta origen.
- `to_account_id`: cuenta destino.
- `amount`: importe positivo transferido.
- `currency`: moneda de la transferencia.
- `transfer_date`: fecha económica del movimiento.
- `description`: descripción visible para el usuario.

Una transferencia resta el importe a la cuenta origen y lo suma a la cuenta
destino dentro de una misma operación de base de datos. No se clasifica como
ingreso ni como gasto para evitar duplicar métricas financieras.

La base de datos exige que el importe sea mayor que cero y que la cuenta origen
sea distinta de la cuenta destino.

## Migración inicial

La migración `0002_create_ledgers_tables_and_seed_categories.py` crea las tablas
del módulo `ledgers` y además carga las categorías iniciales de gasto, ahorro e
inversión.

La migración `0003_create_account_transfers.py` añade la tabla
`account_transfer` para persistir transferencias internas entre cuentas.
