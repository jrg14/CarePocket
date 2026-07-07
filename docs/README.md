# Documentación

Este directorio agrupa la documentación base del proyecto.

## Índice

- [Arquitectura general](./architecture.md)
- [Dominio de negocio](./domain.md)
- [Modelos de datos](./data-models.md)
- [Guía de desarrollo](./development.md)
- [Roadmap](./roadmap.md)
- [Features](./features/README.md)

## Estado actual

La rama `main` contiene la base del backend:

- API en FastAPI.
- Autenticación con `fastapi-users`.
- Persistencia con SQLAlchemy async y PostgreSQL.
- Migraciones con Alembic.

La parte de análisis financiero, cuentas, transacciones, predicciones e IA todavía está en fase de definición de producto.

La documentación de cada módulo de negocio se organizará en `docs/features/<modulo>/`.
