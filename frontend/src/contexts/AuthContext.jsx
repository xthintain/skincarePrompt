/**
 * Authentication Context
 * Provides authentication state and methods throughout the application
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authHelpers } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = () => {
      const token = authHelpers.getAccessToken();

      if (token) {
        // TODO: Verify token and fetch user profile
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
      }

      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (accessToken, refreshToken, userData) => {
    authHelpers.setTokens(accessToken, refreshToken);
    setUser(userData);
    setIsAuthenticated(true);
  };

  const logout = () => {
    authHelpers.clearTokens();
    setUser(null);
    setIsAuthenticated(false);
  };

  const updateUser = (userData) => {
    setUser(userData);
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
