import { useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export function DashboardPage() {
  const navigate = useNavigate();
  const { logout, user } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <main className="dashboard-shell">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">CarePocket</p>
          <h1>Panel de autenticación</h1>
          <p>Tu base React ya está conectada al backend.</p>
        </div>
        <button className="secondary-button" type="button" onClick={handleLogout}>
          Cerrar sesión
        </button>
      </header>

      <section className="grid">
        <article className="card">
          <h2>Usuario conectado</h2>
          <dl className="info-list">
            <div>
              <dt>Nombre</dt>
              <dd>{user?.full_name}</dd>
            </div>
            <div>
              <dt>Correo</dt>
              <dd>{user?.email}</dd>
            </div>
            <div>
              <dt>Estado</dt>
              <dd>{user?.is_active ? "Activo" : "Inactivo"}</dd>
            </div>
          </dl>
        </article>

        <article className="card">
          <h2>Siguiente paso</h2>
          <p>
            Aquí podemos montar el resto del sistema: perfil, movimientos,
            dashboard financiero y permisos.
          </p>
        </article>
      </section>
    </main>
  );
}
