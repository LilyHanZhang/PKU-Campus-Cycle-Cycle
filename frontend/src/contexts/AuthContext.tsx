"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      fetchUser(token);
    } else {
      setLoading(false);
    }
  }, []);

  // 生产环境 API 地址
  const API_URL = "https://pku-campus-cycle-cycle.onrender.com";

  const fetchUser = async (token: string) => {
    try {
      const { data } = await axios.get(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUser({
        id: data.id,
        email: data.email,
        name: data.name,
        role: data.role,
      });
    } catch (error) {
      console.error('获取用户信息失败:', error);
      localStorage.removeItem("access_token");
      setUser(null);  // 明确设置 user 为 null
    } finally {
      setLoading(false);
    }
  };

  const login = async (token: string) => {
    localStorage.setItem("access_token", token);
    await fetchUser(token);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
