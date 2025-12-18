import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children, apiUrl }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  const checkAuth = async () => {
    try {
      const response = await axios.get(`${apiUrl}/auth/user`, {
        withCredentials: true
      });

      if (response.data.authenticated) {
        setUser(response.data.user);
        setAuthError(null);
      } else {
        setUser(null);
        setAuthError('Not authenticated');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
      setAuthError('Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
    // Re-check authentication every 5 minutes
    const interval = setInterval(checkAuth, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [apiUrl]);

  return (
    <AuthContext.Provider value={{ user, loading, authError, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
