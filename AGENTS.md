# AGENTS.md

Guía de contexto y trabajo para agentes de código en CarePocket.

## Objetivo del proyecto

CarePocket es un backend para análisis financiero personal. Su foco actual es sentar la base técnica y de dominio para evolucionar después hacia cuentas, transacciones, analítica, predicción e IA.

## Orden de lectura recomendado

Antes de modificar código, leer en este orden:

1. `README.md`
2. `docs/README.md`
3. `docs/architecture.md`
4. `docs/domain.md`
5. `docs/data-models.md`
6. `docs/features/<modulo>/overview.md`
7. `docs/features/<modulo>/models.md`
8. `docs/development.md`
9. `docs/roadmap.md`

Si el cambio afecta a un módulo concreto, leer también su documentación de feature completa antes de editar.

## Estructura de documentación

La documentación de modelos se organiza así:

- `docs/data-models.md` actúa como índice general.
- `docs/features/<modulo>/overview.md` explica el cometido, funcionamiento y datos relevantes del módulo.
- `docs/features/<modulo>/models.md` documenta los modelos del módulo y justifica cada campo.

Cada módulo nuevo debe seguir esa misma estructura.

## Módulos actuales

- `users`

Módulos previstos a futuro:

- `ledgers`
- otros módulos de negocio que se incorporen después

## Convenciones arquitectónicas

- `app/main.py` arranca la aplicación.
- `app/core` centraliza configuración.
- `app/api` contiene la capa HTTP.
- `app/modules` contiene la lógica de dominio y acceso a datos por módulo.
- `app/db` contiene la infraestructura de persistencia.

## Convenciones de implementación

- Mantener los routers HTTP delgados.
- Mover la lógica de negocio a servicios o utilidades del módulo.
- Usar modelos SQLAlchemy para persistencia.
- Usar esquemas Pydantic para entrada y salida de la API.
- Usar Alembic para cambios de esquema.

## Archivos habituales por módulo

Cuando exista un módulo nuevo, suele contener:

- `models.py` para modelos ORM.
- `services.py` para consultas y lógica de base de datos.
- `types.py` para enumerados o tipos compartidos del módulo.
- `utils.py` para funciones auxiliares del módulo.
- `db.py` si necesita helpers de acceso a datos específicos.
- `auth.py` o `manager.py` si el módulo toca autenticación o gestión especializada.

## Regla de documentación obligatoria

Cada cambio de código debe reflejarse en la documentación del feature correspondiente dentro de `docs/features/<modulo>/`.

Si el cambio afecta a la arquitectura, dominio o flujo general, actualizar también:

- `docs/architecture.md`
- `docs/domain.md`
- `docs/data-models.md`
- `docs/development.md`
- `docs/roadmap.md`

## Prioridades de trabajo

1. Entender el contexto antes de tocar código.
2. Respetar la estructura actual del proyecto.
3. Evitar introducir módulos o conceptos que todavía no existan.
4. Mantener documentación y código alineados.

## Estilo de trabajo esperado

- Preferir cambios pequeños y coherentes.
- No asumir modelos de negocio que no estén documentados.
- Si un cambio introduce una nueva entidad o regla, documentarla en el mismo turno.
- Si hay dudas entre implementación y documentación, tratar ambas como una sola tarea.

