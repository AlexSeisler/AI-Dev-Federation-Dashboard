import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: number;
  email: string;
  role: 'guest' | 'member' | 'admin';
  status: 'pending' | 'approved';
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  signup: (email: string, password: string) => Promise<{ success: boolean; message: string }>;
  login: (email: string, password: string) => Promise<{ success: boolean; message: string }>;
  logout: () => void;
  approveUser: (userId: number) => Promise<{ success: boolean; message: string }>;
  checkAuth: () => Promise<void>;
  checkEmailInDatabase: (email: string) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

// ✅ Pull API base URL from Vite environment
const API_URL = import.meta.env.VITE_API_URL;

if (!API_URL) {
  throw new Error("❌ VITE_API_URL is not set. Please configure it in your Netlify environment.");
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const getToken = () => localStorage.getItem('access_token');
  const setToken = (token: string) => localStorage.setItem('access_token', token);
  const removeToken = () => localStorage.removeItem('access_token');

  const checkAuth = async () => {
    const token = getToken();
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        removeToken();
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      removeToken();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  // New method to check if email exists in the database
  const checkEmailInDatabase = async (email: string) => {
    try {
      const response = await fetch(`${API_URL}/check-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();
      return data.exists;  // Assuming the API returns { exists: true/false }
    } catch (error) {
      console.error("Error checking email:", error);
      return false;
    }
  };

  const signup = async (email: string, password: string) => {
    try {
      const response = await fetch(`${API_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        setUser({
          ...data,
          role: 'member',
          status: 'pending'
        });

        // Check if email exists in the database to allow DevBot demo
        const emailExists = await checkEmailInDatabase(email);
        if (emailExists) {
          return { success: true, message: 'Account created! Waiting for admin approval. You can access DevBot demo.' };
        } else {
          return { success: true, message: 'Account created! Waiting for admin approval.' };
        }
      } else {
        return { success: false, message: data.detail || 'Signup failed' };
      }
    } catch (error) {
      return { success: false, message: 'Network error. Please try again.' };
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        setToken(data.access_token);
        await checkAuth();
        return { success: true, message: 'Login successful!' };
      } else {
        return { success: false, message: data.detail || 'Login failed' };
      }
    } catch (error) {
      return { success: false, message: 'Network error. Please try again.' };
    }
  };

  const logout = () => {
    removeToken();
    setUser(null);
  };

  const approveUser = async (userId: number) => {
    const token = getToken();
    if (!token) {
      return { success: false, message: 'Not authenticated' };
    }

    try {
      const response = await fetch(`${API_URL}/auth/approve/${userId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        return { success: true, message: data.message };
      } else {
        return { success: false, message: data.detail || 'Approval failed' };
      }
    } catch (error) {
      return { success: false, message: 'Network error. Please try again.' };
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const value = {
    user,
    isLoading,
    signup,
    login,
    logout,
    approveUser,
    checkAuth,
    checkEmailInDatabase,  // Expose the email check method
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
