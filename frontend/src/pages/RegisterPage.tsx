import { FormEvent, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { AuthLayout } from "../components/AuthLayout";
import { FormField } from "../components/FormField";
import { useAuth } from "../hooks/useAuth";

export function RegisterPage() {
  const navigate = useNavigate();
  const { error, isAuthenticated, isLoading, clearError, register } = useAuth();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLocalError(null);

    if (password !== confirmPassword) {
      setLocalError("Las contraseñas no coinciden.");
      return;
    }

    try {
      await register({
        full_name: fullName,
        email,
        password,
      });
      navigate("/", { replace: true });
    } catch {
      setLocalError("No hemos podido crear la cuenta.");
    }
  };

  return (
    <AuthLayout
      title="Crea tu cuenta"
      subtitle="Registra tu usuario para empezar a usar el panel de CarePocket."
    >
      <form className="auth-form" onSubmit={handleSubmit}>
        <FormField
          label="Nombre completo"
          type="text"
          autoComplete="name"
          placeholder="Tu nombre"
          value={fullName}
          onChange={(event) => {
            clearError();
            setLocalError(null);
            setFullName(event.target.value);
          }}
          required
        />
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
          autoComplete="new-password"
          placeholder="••••••••"
          value={password}
          onChange={(event) => {
            clearError();
            setLocalError(null);
            setPassword(event.target.value);
          }}
          required
        />
        <FormField
          label="Confirmar contraseña"
          type="password"
          autoComplete="new-password"
          placeholder="••••••••"
          value={confirmPassword}
          onChange={(event) => {
            clearError();
            setLocalError(null);
            setConfirmPassword(event.target.value);
          }}
          required
        />
        {(localError ?? error) && (
          <div className="alert alert-error">{localError ?? error}</div>
        )}
        <button className="primary-button" type="submit" disabled={isLoading}>
          {isLoading ? "Creando cuenta..." : "Crear cuenta"}
        </button>
        <p className="auth-footer">
          ¿Ya tienes cuenta? <Link to="/login">Iniciar sesión</Link>
        </p>
      </form>
    </AuthLayout>
  );
}
