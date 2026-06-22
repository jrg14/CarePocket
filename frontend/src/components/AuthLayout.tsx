import type { ReactNode } from "react";

type AuthLayoutProps = {
  title: string;
  subtitle: string;
  children: ReactNode;
};

export function AuthLayout({ title, subtitle, children }: AuthLayoutProps) {
  return (
    <div className="auth-shell">
      <section className="auth-copy">
        <p className="eyebrow">CarePocket</p>
        <h1>{title}</h1>
        <p>{subtitle}</p>
        <ul className="feature-list">
          <li>Autenticación con JWT</li>
          <li>Sesión persistente en el navegador</li>
          <li>Panel financiero con ingresos, gastos, categorías y resúmenes</li>
        </ul>
      </section>
      <section className="auth-card">{children}</section>
    </div>
  );
}
