# Users - Modelos de datos

## `User`

Modelo definido en `src/app/modules/users/models.py` y respaldado por la migración inicial en `src/alembic/versions/0001_initial_users.py`.

### Campos

#### `id`

Identificador primario entero autoincremental.

Motivo:

- permite identificar de forma simple y eficiente a cada usuario.
- encaja con `fastapi-users`, que está configurado con IDs enteros.

#### `email`

Correo electrónico del usuario.

Motivo:

- actúa como identificador natural para autenticación y contacto.
- debe ser único para evitar duplicidades de cuenta.

#### `hashed_password`

Contraseña almacenada en formato cifrado.

Motivo:

- nunca se guarda la contraseña en texto plano.
- se necesita para validar credenciales en el login.

#### `is_active`

Indica si la cuenta puede usarse.

Motivo:

- permite desactivar cuentas sin borrarlas.
- útil para bloquear accesos o cuentas suspendidas.

#### `is_superuser`

Indica permisos administrativos.

Motivo:

- habilita diferenciación de privilegios.
- deja preparada la base para paneles o tareas administrativas.

#### `is_verified`

Indica si la cuenta ha sido verificada.

Motivo:

- permite controlar el estado de confianza de una cuenta.
- prepara el terreno para flujos de verificación de email.

#### `full_name`

Nombre completo del usuario.

Motivo:

- mejora la experiencia de la interfaz y la identificación humana del perfil.
- ofrece un dato de presentación distinto al email.

## Tabla `user`

La tabla creada por Alembic contiene los mismos campos de base que el modelo.

### Restricciones

- `email` es único.
- `full_name` es obligatorio.
- `hashed_password` es obligatorio.
- `is_active` no admite nulos.
- `is_superuser` no admite nulos.
- `is_verified` no admite nulos.

## Esquemas relacionados

### `UserRead`

Esquema de salida para leer un usuario desde la API.

Incluye:

- `id`
- `email`
- `is_active`
- `is_superuser`
- `is_verified`
- `full_name`

### `UserCreate`

Esquema de entrada para crear un usuario.

Añade `full_name` al esquema base de `fastapi-users`.

### `UserUpdate`

Esquema de actualización parcial.

Permite cambiar `full_name` de forma opcional.

## Nota de diseño

Este modelo debe seguir siendo pequeño y estable.

La información financiera del usuario no debería mezclarse aquí; esa parte irá a módulos específicos como `ledgers` en el futuro.
