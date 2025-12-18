import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children, apiUrl }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  const checkAuth = async () => {
    try {
      // Get current hostname to build Laravel URLs
      const hostname = window.location.hostname;
      const host = hostname === 'localhost' || hostname === '127.0.0.1' ? 'localhost' : hostname;

      // Try Laravel 11 first
      try {
        const response = await axios.get(`http://${host}/v2/api/session/validate`, {
          withCredentials: true,
          timeout: 5000
        });

        if (response.data.authenticated) {
          setUser(response.data.user);
          setAuthError(null);
          setLoading(false);
          return;
        }
      } catch (error) {
        console.log('Laravel 11 session not found, trying Laravel 9...');
      }

      // Try Laravel 9
      try {
        const response = await axios.get(`http://${host}/api/session/validate`, {
          withCredentials: true,
          timeout: 5000
        });

        if (response.data.authenticated) {
          setUser(response.data.user);
          setAuthError(null);
          setLoading(false);
          return;
        }
      } catch (error) {
        console.log('Laravel 9 session not found');
      }

      // No valid session found
      setUser(null);
      setAuthError('Not authenticated');
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
