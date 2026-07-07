# Users

## Cometido del módulo

El módulo `users` gestiona la identidad básica de las personas que usan la aplicación.

En esta primera etapa cubre:

- registro de usuarios.
- autenticación con JWT.
- consulta del usuario autenticado.

## Responsabilidades

- Persistir la información básica de usuario.
- Integrarse con `fastapi-users` para no reimplementar autenticación.
- Exponer el perfil del usuario actual en la API v1.

## Piezas principales

- `src/app/modules/users/models.py`: modelo SQLAlchemy de usuario.
- `src/app/modules/users/db.py`: acceso a datos del usuario.
- `src/app/modules/users/manager.py`: gestor de usuarios para `fastapi-users`.
- `src/app/modules/users/auth.py`: configuración de autenticación JWT.
- `src/app/api/v1/auth/router.py`: endpoints de login y registro.
- `src/app/api/v1/users/router.py`: endpoint para leer el usuario actual.

## Datos relevantes

- El módulo está diseñado para ser la base de la identidad de todo el proyecto.
- El resto de módulos de negocio dependerá de `User` como entidad raíz.
- El usuario actual se obtiene a través de la dependencia `current_active_user`.

## Alcance actual

Lo que existe en `main` es suficiente para:

- crear una cuenta.
- iniciar sesión.
- obtener el perfil autenticado.

Lo que todavía no existe:

- gestión avanzada de perfil.
- recuperación de contraseña.
- verificación de email con flujo propio.
- relación con módulos financieros.
