# Ledgers

## Cometido del módulo

El módulo `ledgers` gestiona la base financiera operativa del usuario.

En esta etapa cubre:

- cuentas financieras del usuario.
- transacciones de ingreso y gasto.
- categorías de transacción.
- transferencias internas entre cuentas propias.
- resumen financiero básico por periodo.

## Responsabilidades

- Persistir cuentas, movimientos y transferencias internas.
- Mantener el balance de cada cuenta actualizado.
- Separar ingresos y gastos reales de movimientos internos de dinero.
- Exponer endpoints protegidos por el usuario autenticado.
- Preparar datos fiables para futuras capas de analítica y predicción.

## Piezas principales

- `src/app/modules/ledgers/models.py`: modelos SQLAlchemy del módulo.
- `src/app/modules/ledgers/accounts.py`: operaciones de cuentas.
- `src/app/modules/ledgers/transactions.py`: operaciones de transacciones.
- `src/app/modules/ledgers/transfers.py`: operaciones de transferencias internas.
- `src/app/modules/ledgers/summary.py`: cálculo del resumen financiero.
- `src/app/api/v1/ledgers/router.py`: endpoints HTTP del módulo.
- `src/app/api/v1/ledgers/schemas.py`: esquemas Pydantic de entrada y salida.

## Transferencias internas

Una transferencia interna mueve dinero entre dos cuentas activas del mismo usuario.

Ejemplo:

- cuenta corriente: recibe una nómina de 1000 EUR como `income`.
- cuenta ahorro: recibe 500 EUR desde la cuenta corriente mediante una transferencia.

La transferencia reduce el balance de la cuenta origen y aumenta el balance de la
cuenta destino en una única operación de base de datos. No se registra como
`income` ni como `expense`, porque no representa dinero nuevo ni consumo.

## Datos relevantes

- Las cuentas pertenecen siempre a un usuario.
- Las transacciones pertenecen a una cuenta.
- Las transferencias pertenecen a un usuario y enlazan una cuenta origen con una
  cuenta destino.
- El resumen financiero suma balances de cuentas y calcula ingresos/gastos solo
  desde transacciones reales.

## Alcance actual

Lo que existe ahora permite:

- crear y consultar cuentas.
- crear, consultar, actualizar y eliminar transacciones.
- consultar categorías de transacción.
- crear transferencias internas entre cuentas propias.
- consultar un resumen financiero básico.

Lo que todavía no existe:

- listado o detalle histórico de transferencias.
- conciliación bancaria.
- transacciones recurrentes ejecutables.
- presupuestos, objetivos de ahorro o reglas automáticas.
