# Guía de desarrollo

## Requisitos

- Python 3.10 o superior.
- PostgreSQL.
- `uvicorn` para ejecutar la API.

## Instalación

El proyecto usa dependencias declaradas en `pyproject.toml`.

Entorno de desarrollo recomendado:

```bash
pip install -e ".[dev]"
```

## Variables de entorno

Las variables principales están en `.env.example`:

- `APP_NAME`
- `APP_ENV`
- `APP_DEBUG`
- `API_V1_PREFIX`
- `CORS_ORIGINS`
- `AUTH_SECRET`
- `AUTH_TOKEN_LIFETIME_SECONDS`
- `DATABASE_URL`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

## Arranque local

Con base de datos disponible:

```bash
uvicorn app.main:app --reload
```

## Base de datos

La sesión async está en `app/db/session.py`.

La inicialización de tablas se realiza en el `lifespan` de `app/main.py` mediante `init_db()`.

Para cambios de esquema, la referencia debe ser Alembic, no la creación automática de tablas.

## Migraciones

La migración inicial está en `src/alembic/versions/0001_initial_users.py`.

Flujo recomendado para nuevas modificaciones:

1. cambiar el modelo SQLAlchemy.
2. generar o escribir la migración.
3. aplicar la migración en base de datos.
4. comprobar que los esquemas de API siguen alineados.

## Convenciones del código

- Routers HTTP en `app/api/v1`.
- Lógica de dominio y acceso a datos en `app/modules`.
- Configuración en `app/core`.
- Infraestructura de persistencia en `app/db`.

## Archivos que suele contener un módulo
1. El archivo `models.py` encargado de contener los modelos del ORM
2. El archivo `types.py` encargadp de contener los enumerados que use el módulo
3. El archivo `utils.py` encargado de contener las funciones auxiliares correspondientes al módulo que puedan usarse en todo el proyecto.
5. El archivo `services.py` encargado de contener las consultas a la base de datos haciendo uso del ORM


## Cómo añadir un nuevo módulo

1. Crear el modelo SQLAlchemy.
2. Añadir la migración correspondiente.
3. Implementar serviciosm aquellos que se encargan de hacer las peticiones a la db.
4. Exponer schemas Pydantic para la API.
5. Registrar el router en `app/api/v1/router.py`.

## Calidad de código

El proyecto ya contempla `ruff` para lint y formato.

Recomendación práctica:

- mantener imports ordenados.
- usar tipos explícitos.
- separar la lógica de negocio del router HTTP.
- evitar lógica compleja dentro de los endpoints.

## Docker

El repo incluye `Dockerfile` y `docker-compose.yml`.

Eso permite levantar:

- PostgreSQL.
- backend FastAPI.
- pgAdmin.

## Qué revisar antes de tocar código

- Cada cambio realizado en codigo deberá reflejarse en su respectiva documentación de feature en docs/features/{feature_correspondiente}
