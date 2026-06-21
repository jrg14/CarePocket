import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  getCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
} from "../lib/api";
import type { RegisterInput, User } from "../types/auth";

const tokenStorageKey = "carepocket.auth.token";

type AuthContextValue = {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: RegisterInput) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  clearError: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function getStoredToken() {
  return localStorage.getItem(tokenStorageKey);
}

function storeToken(token: string) {
  localStorage.setItem(tokenStorageKey, token);
}

function clearStoredToken() {
  localStorage.removeItem(tokenStorageKey);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadUser = useCallback(async (storedToken: string) => {
    const currentUser = await getCurrentUser(storedToken);
    setToken(storedToken);
    setUser(currentUser);
  }, []);

  useEffect(() => {
    const storedToken = getStoredToken();

    if (!storedToken) {
      setIsLoading(false);
      return;
    }

    let isMounted = true;

    void (async () => {
      try {
        await loadUser(storedToken);
      } catch {
        if (!isMounted) {
          return;
        }
        clearStoredToken();
        setToken(null);
        setUser(null);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    })();

    return () => {
      isMounted = false;
    };
  }, [loadUser]);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await loginUser(email, password);
      storeToken(response.access_token);
      await loadUser(response.access_token);
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo iniciar sesión";
      setError(message);
      throw caughtError;
    } finally {
      setIsLoading(false);
    }
  }, [loadUser]);

  const register = useCallback(
    async (payload: RegisterInput) => {
      setIsLoading(true);
      setError(null);

      try {
        await registerUser(payload);
        await login(payload.email, payload.password);
      } catch (caughtError) {
        const message =
          caughtError instanceof Error
            ? caughtError.message
            : "No se pudo registrar el usuario";
        setError(message);
        throw caughtError;
      } finally {
        setIsLoading(false);
      }
    },
    [login],
  );

  const logout = useCallback(async () => {
    const storedToken = getStoredToken();

    try {
      if (storedToken) {
        await logoutUser(storedToken);
      }
    } finally {
      clearStoredToken();
      setToken(null);
      setUser(null);
      setError(null);
    }
  }, []);

  const refreshUser = useCallback(async () => {
    const storedToken = token ?? getStoredToken();
    if (!storedToken) {
      return;
    }

    const currentUser = await getCurrentUser(storedToken);
    setToken(storedToken);
    setUser(currentUser);
  }, [token]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isLoading,
      error,
      isAuthenticated: Boolean(user),
      login,
      register,
      logout,
      refreshUser,
      clearError,
    }),
    [clearError, error, isLoading, login, logout, register, refreshUser, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuthContext must be used within AuthProvider");
  }

  return context;
}
