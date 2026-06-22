# CarePocket

CarePocket es una aplicación web de análisis financiero personal centrada en ayudar a los usuarios a comprender sus hábitos financieros, detectar patrones de gasto, anticipar escenarios futuros y tomar mejores decisiones económicas.

A diferencia de las aplicaciones tradicionales de presupuestos, CarePocket no se limita a mostrar gráficos o clasificar movimientos bancarios. Su objetivo es actuar como un analista financiero personal, transformando datos financieros en información útil, predicciones y recomendaciones accionables.

## Visión

La mayoría de aplicaciones financieras responden preguntas como:

¿Cuánto he gastado?
¿Dónde he gastado?
¿Cuánto he ahorrado?

CarePocket busca responder preguntas más valiosas:

¿Por qué estoy gastando más?
¿Qué patrones financieros estoy repitiendo?
¿Qué gastos están afectando más a mi capacidad de ahorro?
¿Qué ocurrirá con mis finanzas dentro de unos meses?
¿Cómo cambiarían mis resultados financieros si modificara determinados hábitos?

## Objetivos
Automatizar el análisis financiero personal.
Detectar patrones y tendencias que pasan desapercibidos.
Ayudar a prevenir problemas financieros antes de que ocurran.
Facilitar la toma de decisiones mediante simulaciones y predicciones.
Generar recomendaciones personalizadas basadas en datos reales.

## Frontend
El proyecto incluye una base React en `frontend/` para autenticación con JWT y un panel financiero diario con gastos e ingresos.

### Arranque local
1. Entra en `frontend/`
2. Copia `.env.example` a `.env`
3. Instala dependencias con `npm install`
4. Ejecuta `npm run dev`

### Arranque con Docker
1. Levanta todo con `docker compose up --build`
2. Abre el frontend en `http://localhost:5173`
3. Abre el backend en `http://localhost:8000`
4. Abre `pgAdmin` en `http://localhost:5050`

### Variables
- `VITE_API_URL=http://localhost:8000/api/v1`

### Rutas incluidas
- `/login`
- `/register`
- `/`

### Panel financiero
Una vez autenticado, el dashboard permite:
- Registrar gastos diarios con categoría, importe, fecha, método de pago y nota opcional.
- Registrar ingresos diarios con categoría, importe, fecha, origen y nota opcional.
- Ver totales de hoy, semana y mes.
- Consultar distribución por categorías.
- Revisar movimientos recientes y eliminar registros de gastos e ingresos.

### API principal
- `GET /api/v1/expenses/summary`
- `GET /api/v1/expenses`
- `POST /api/v1/expenses`
- `PATCH /api/v1/expenses/{expense_id}`
- `DELETE /api/v1/expenses/{expense_id}`
- `GET /api/v1/expenses/categories`
- `GET /api/v1/incomes/summary`
- `GET /api/v1/incomes`
- `POST /api/v1/incomes`
- `PATCH /api/v1/incomes/{income_id}`
- `DELETE /api/v1/incomes/{income_id}`
- `GET /api/v1/incomes/categories`

El backend ya permite por defecto los orígenes `http://localhost:3000` y `http://localhost:5173`.
