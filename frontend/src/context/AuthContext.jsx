import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [viewLimitModalOpen, setViewLimitModalOpen] = useState(false);
  const [viewLimitInfo, setViewLimitInfo] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('eh_token');
    if (token) {
      authService.getMe()
        .then((res) => setUser(res.data))
        .catch(() => {
          localStorage.removeItem('eh_token');
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }

    // Listen for 5-view limit event
    const handleViewLimit = (e) => {
      setViewLimitInfo(e.detail);
      setViewLimitModalOpen(true);
    };

    window.addEventListener('eh:view-limit-reached', handleViewLimit);
    return () => window.removeEventListener('eh:view-limit-reached', handleViewLimit);
  }, []);

  const login = async (email, password) => {
    const res = await authService.login({ email, password });
    localStorage.setItem('eh_token', res.data.access_token);
    setUser(res.data.user);
    setViewLimitModalOpen(false);
    return res.data;
  };

  const register = async (email, password, fullName) => {
    const res = await authService.register({ email, password, full_name: fullName });
    localStorage.setItem('eh_token', res.data.access_token);
    setUser(res.data.user);
    setViewLimitModalOpen(false);
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('eh_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
        isAdmin: user?.role === 'admin' || user?.role === 'super_admin',
        isSuperAdmin: user?.role === 'super_admin',
        viewLimitModalOpen,
        setViewLimitModalOpen,
        viewLimitInfo
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
