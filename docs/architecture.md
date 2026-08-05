# Arquitectura general

## Resumen

CarePocket está planteado como un backend modular en Python con FastAPI. La estructura actual separa la aplicación en capas para mantener clara la responsabilidad de cada parte:

- `app/main.py` arranca la aplicación.
- `app/core` centraliza configuración.
- `app/api` expone los endpoints HTTP.
- `app/modules` contiene la lógica de dominio y acceso a datos por área funcional.
- `app/db` encapsula la conexión a base de datos y la base declarativa de SQLAlchemy.

## Flujo de una petición

1. FastAPI recibe la request.
2. El router de `app/api` resuelve el endpoint.
3. Las dependencias inyectadas proporcionan usuario actual, sesión de base de datos o configuración.
4. El endpoint delega en servicios o utilidades del módulo correspondiente.
5. Los modelos SQLAlchemy representan los datos persistidos.
6. La respuesta se serializa con esquemas Pydantic.
7. Los errores de aplicación se traducen en respuestas HTTP mediante handlers
   globales.

## Componentes principales

### `app/main.py`

Punto de entrada de la aplicación. Aquí se crea `FastAPI`, se añade CORS, se incluye el router versionado y se ejecuta la inicialización de base de datos durante el `lifespan`.

### `app/core/settings.py`

Define la configuración del proyecto con `pydantic-settings`.

Responsabilidades:

- leer variables de entorno.
- construir la URL de base de datos.
- normalizar valores como `DEBUG` y `CORS_ORIGINS`.

### `app/core/exceptions.py` y `app/core/error_handlers.py`

Definen el contrato común de errores de la aplicación.

Responsabilidades:

- declarar excepciones propias como `ResourceNotFoundError` y
  `PermissionDeniedError`.
- registrar handlers globales en FastAPI.
- devolver errores con un formato estable para clientes HTTP.
- registrar errores inesperados antes de responder con un `500` genérico.

### `app/api`

Capa HTTP.

En la rama `main` existen:

- `health` para comprobación de estado.
- `auth` para login y registro.
- `users` para consultar el usuario actual.

### `app/modules/users`

Módulo de dominio de usuarios.

Incluye:

- modelo `User`.
- gestor de usuarios para `fastapi-users`.
- acceso a datos del usuario.
- utilidades de autenticación.

### `app/db`

Capa de infraestructura de base de datos.

Incluye:

- base declarativa de SQLAlchemy.
- motor async.
- fábrica de sesiones.
- inicialización de tablas.

## Decisiones técnicas actuales

- Se usa FastAPI por su soporte nativo para dependencias, OpenAPI y asincronía.
- Se usa `fastapi-users` para no reinventar autenticación, registro y usuario actual.
- Se usa SQLAlchemy async para separar modelo de persistencia y lógica HTTP.
- Se usa Alembic para migraciones explícitas y evolutivas.
- La creación automática de tablas en `init_db()` es útil en desarrollo, pero las migraciones deben ser la referencia real para cambios de esquema.
- Los routers deben lanzar excepciones de aplicación cuando expresan errores de
  negocio o acceso, y dejar que los handlers globales construyan la respuesta
  HTTP final.
