import React, { createContext, useContext, useEffect, useState } from "react";
import { User } from "@/types";
import { api, apiClient } from "@/api/client";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (email: string, pass: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const token = apiClient.getToken();
    if (token) {
      api.auth
        .getMe()
        .then((userData) => {
          setUser(userData);
        })
        .catch(() => {
          apiClient.setToken(null);
          setUser(null);
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, pass: string) => {
    const res = await api.auth.login({ email, password: pass });
    apiClient.setToken(res.access_token);
    const userData = await api.auth.getMe();
    setUser(userData);
  };

  const register = async (email: string, pass: string, fullName: string) => {
    const res = await api.auth.register({ email, password: pass, full_name: fullName });
    apiClient.setToken(res.access_token);
    const userData = await api.auth.getMe();
    setUser(userData);
  };

  const logout = async () => {
    try {
      await api.auth.logout();
    } catch {
      // ignore
    } finally {
      apiClient.setToken(null);
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
