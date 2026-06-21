import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <main className="page-center">
      <section className="card compact-card">
        <p className="eyebrow">404</p>
        <h1>Página no encontrada</h1>
        <p>La ruta que buscabas no existe.</p>
        <Link className="primary-button inline-button" to="/">
          Volver al inicio
        </Link>
      </section>
    </main>
  );
}
