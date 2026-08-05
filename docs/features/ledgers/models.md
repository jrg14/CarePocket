# Modelos del módulo `ledgers`

## Resumen financiero

La respuesta del resumen financiero mensual está formada por:

- `balance`
- `balance_change`
  - `percentage`
  - `direction`
- `monthly_health`
- `top_expense_categories`
- `latest_transactions`

### `balance`

Suma del balance de todas las cuentas activas del usuario.

### `balance_change`

Compara el balance total actual con el balance total que había al cierre del mes anterior.

- `percentage` devuelve el cambio absoluto en porcentaje.
- `direction` indica si el balance ha mejorado, empeorado o se ha mantenido.

### `monthly_health`

Porcentaje de los ingresos del mes que todavía no se ha gastado.

Si el gasto supera a los ingresos, el valor puede bajar hasta cero o por debajo
de cero según el comportamiento del mes.

### `top_expense_categories`

Las tres categorías con más gasto del mes actual.

Las categorías se agrupan por `category_id` y `category_name`, y se ordenan por
importe descendente.

### `latest_transactions`

Las últimas cinco transacciones del usuario, ordenadas de la más reciente a la
más antigua.

## Migración inicial

La migración `0002_create_ledgers_tables_and_seed_categories.py` crea las tablas
del módulo `ledgers` y además carga las categorías iniciales de gasto, ahorro e
inversión.
