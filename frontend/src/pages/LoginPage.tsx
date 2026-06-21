import { FormEvent, useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import { AuthLayout } from "../components/AuthLayout";
import { FormField } from "../components/FormField";
import { useAuth } from "../hooks/useAuth";

type LocationState = {
  from?: {
    pathname?: string;
  };
};

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { error, isAuthenticated, isLoading, clearError, login } = useAuth();
  const state = location.state as LocationState | null;
  const redirectTo = state?.from?.pathname ?? "/";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);

  if (isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLocalError(null);

    try {
      await login(email, password);
      navigate(redirectTo, { replace: true });
    } catch {
      setLocalError("Revisa tus credenciales e inténtalo de nuevo.");
    }
  };

  return (
    <AuthLayout
      title="Inicia sesión"
      subtitle="Entra en tu espacio personal y empieza a gestionar tu cuenta."
    >
      <form className="auth-form" onSubmit={handleSubmit}>
        <FormField
          label="Correo"
          type="email"
          autoComplete="email"
          placeholder="tu@correo.com"
          value={email}
          onChange={(event) => {
            clearError();
            setLocalError(null);
            setEmail(event.target.value);
          }}
          required
        />
        <FormField
          label="Contraseña"
          type="password"
          autoComplete="current-password"
          placeholder="••••••••"
          value={password}
          onChange={(event) => {
            clearError();
            setLocalError(null);
            setPassword(event.target.value);
          }}
          required
        />
        {(localError ?? error) && (
          <div className="alert alert-error">{localError ?? error}</div>
        )}
        <button className="primary-button" type="submit" disabled={isLoading}>
          {isLoading ? "Entrando..." : "Entrar"}
        </button>
        <p className="auth-footer">
          ¿No tienes cuenta? <Link to="/register">Crear una cuenta</Link>
        </p>
      </form>
    </AuthLayout>
  );
}
