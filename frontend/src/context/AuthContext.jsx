import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { api } from "../lib/api";

const AuthContext = createContext(null);

const TOKEN_KEY = "iafs_token";
const USER_KEY = "iafs_user";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    // A saved user is only valid alongside its token.
    if (!localStorage.getItem(TOKEN_KEY)) return null;
    try {
      return JSON.parse(localStorage.getItem(USER_KEY) || "null");
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [loading, setLoading] = useState(Boolean(localStorage.getItem(TOKEN_KEY)));

  // Verify the saved token when the app loads.
  useEffect(() => {
    if (!token) {
      localStorage.removeItem(USER_KEY);
      setUser(null);
      setLoading(false);
      return;
    }

    let cancelled = false;
    api
      .get("/auth/me")
      .then(({ user: freshUser }) => {
        if (cancelled) return;
        setUser(freshUser);
        localStorage.setItem(USER_KEY, JSON.stringify(freshUser));
      })
      .catch(() => {
        if (cancelled) return;
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        setUser(null);
        setToken(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
    // Only run when the token changes (login/logout).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const saveSession = useCallback((data) => {
    localStorage.setItem(TOKEN_KEY, data.token);
    localStorage.setItem(USER_KEY, JSON.stringify(data.user));
    setToken(data.token);
    setUser(data.user);
  }, []);

  const login = useCallback(
    async (email, password) => {
      const data = await api.post("/auth/login", { email, password });
      saveSession(data);
      return data.user;
    },
    [saveSession]
  );

  const register = useCallback(
    async (payload) => {
      const data = await api.post("/auth/register", payload);
      saveSession(data);
      return data.user;
    },
    [saveSession]
  );

  const updateUser = useCallback((freshUser) => {
    setUser(freshUser);
    localStorage.setItem(USER_KEY, JSON.stringify(freshUser));
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.post("/auth/logout");
    } catch {
      // The local session is cleared even if the network request fails.
    }
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setUser(null);
    setToken(null);
  }, []);

  const value = useMemo(
    () => ({ user, token, loading, login, register, logout, updateUser }),
    [user, token, loading, login, register, logout, updateUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside an AuthProvider");
  }
  return context;
}

export function homeForRole(role) {
  if (role === "admin") return "/admin";
  if (role === "teacher") return "/teacher";
  return "/student";
}
