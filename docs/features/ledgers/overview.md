# Ledgers

## Cometido del módulo

El módulo `ledgers` centraliza la base funcional del análisis financiero personal.

En esta etapa cubre:

- cuentas.
- transacciones.
- categorías de transacción.
- resumen financiero mensual.

## Responsabilidades

- Persistir cuentas y transacciones del usuario.
- Mantener el saldo de cada cuenta.
- Exponer endpoints de consulta y edición para la capa HTTP.
- Preparar el terreno para analítica financiera posterior.

## Piezas principales

- `src/app/modules/ledgers/models.py`: modelos ORM del dominio financiero.
- `src/app/modules/ledgers/accounts.py`: consultas y lógica de cuentas.
- `src/app/modules/ledgers/transactions.py`: consultas y lógica de transacciones.
- `src/app/modules/ledgers/summary.py`: cálculo del resumen financiero mensual.
- `src/app/api/v1/ledgers/router.py`: endpoints HTTP del módulo.
- `src/app/api/v1/ledgers/schemas.py`: esquemas Pydantic de entrada y salida.

## Datos relevantes

- Las cuentas pertenecen a un usuario.
- Las transacciones pertenecen a una cuenta concreta.
- El resumen financiero agrega datos por periodo y por categoría.
- Los errores de recurso inexistente y acceso denegado se expresan con
  excepciones de aplicación y se serializan mediante los handlers globales.

## Alcance actual

Lo que existe en `main` es suficiente para:

- crear y consultar cuentas.
- crear, consultar, actualizar y borrar transacciones.
- consultar un resumen financiero mensual con balance, salud y últimas
  transacciones.

Lo que todavía no existe:

- presupuestos.
- reglas automáticas.
- predicciones.
- recomendaciones.
