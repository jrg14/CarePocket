# Dominio de negocio

## Visión

CarePocket quiere convertirse en un analista financiero personal. La idea no es solo mostrar movimientos o gráficos, sino ayudar a entender comportamientos, detectar patrones y anticipar escenarios.

## Estado del dominio en `main`

En la rama `main` el dominio implementado es el mínimo necesario para arrancar la plataforma:

- usuarios.
- autenticación.
- acceso al perfil del usuario autenticado.
- cuentas financieras.
- transacciones de ingreso y gasto.
- transferencias internas entre cuentas.
- resumen financiero básico.

El dominio financiero completo aún no está implementado, pero sí está definido a nivel conceptual en `docs/ideas.md`.

## Glosario base

### Usuario

Persona que se registra y accede a la aplicación.

### Usuario activo

Usuario autenticado y habilitado para usar la API.

### Autenticación

Mecanismo por el que un usuario obtiene un token JWT para acceder a endpoints protegidos.

### Perfil

Datos básicos del usuario visibles desde la API, como nombre, email y estado de cuenta.

### Cuenta financiera

Contenedor de saldo perteneciente a un usuario, como una cuenta corriente o una
cuenta de ahorro.

### Transacción

Movimiento económico real registrado en una cuenta. Puede ser ingreso o gasto.

### Transferencia interna

Movimiento de dinero entre dos cuentas del mismo usuario. Cambia el saldo de las
cuentas implicadas, pero no se considera ingreso ni gasto real.

## Dominio futuro previsto

Los conceptos que guían la evolución del producto son:

- ingresos.
- gastos.
- transferencias internas.
- categorías.
- gastos fijos.
- patrones.
- anomalías.
- concentraciones.
- suscripciones.
- saldo futuro.
- ahorro futuro.
- tendencias.
- explicaciones.
- recomendaciones.
- simulaciones.
- salud financiera.

## Lectura de negocio

La aplicación busca responder preguntas como:

- por qué se está gastando más.
- qué patrones se repiten.
- qué categorías afectan más al ahorro.
- cómo evolucionarán las finanzas en el tiempo.
- qué pasaría si se cambian ciertos hábitos.

## Regla de diseño importante

El producto parece orientado a una evolución por etapas:

1. base de datos de usuario y autenticación.
2. registro y análisis de movimientos.
3. inteligencia sobre el comportamiento financiero.
4. predicción y simulación.
5. recomendaciones asistidas por IA.

Eso conviene mantenerlo como referencia al diseñar nuevos módulos, para no saltar demasiado pronto a la capa de analítica sin tener una base de datos de negocio sólida.
