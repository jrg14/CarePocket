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

## Migración inicial

La migración `0002_create_ledgers_tables_and_seed_categories.py` crea las tablas
del módulo `ledgers` y además carga las categorías iniciales de gasto, ahorro e
inversión.
