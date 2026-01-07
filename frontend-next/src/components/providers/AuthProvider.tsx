'use client';

// ============================================================
// Auth Provider - Authentication Context
// ============================================================

import { createContext, useContext, useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/lib/stores';

interface AuthProviderProps {
  children: React.ReactNode;
}

interface AuthContextType {
  isInitialized: boolean;
}

const AuthContext = createContext<AuthContextType>({ isInitialized: false });

// Public routes that don't require authentication
const publicRoutes = ['/login', '/register', '/'];

export function AuthProvider({ children }: AuthProviderProps) {
  const [isInitialized, setIsInitialized] = useState(false);
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Check if there's a stored token on mount
    const storedToken = localStorage.getItem('accessToken');

    if (storedToken && !isAuthenticated) {
      // Token exists but state says not authenticated - restore state
      useAuthStore.setState({
        accessToken: storedToken,
        refreshToken: localStorage.getItem('refreshToken'),
        isAuthenticated: true,
      });
    }

    // 设置初始化完成状态
    setIsInitialized(true);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!isInitialized) return;

    const isPublicRoute = publicRoutes.some((route) => pathname === route);

    if (!isAuthenticated && !isPublicRoute) {
      // Not authenticated and trying to access protected route
      router.push('/login');
    } else if (isAuthenticated && (pathname === '/login' || pathname === '/register')) {
      // Authenticated but on login/register page
      router.push('/chat');
    }
  }, [isAuthenticated, pathname, router, isInitialized]);

  // Show loading state while initializing
  if (!isInitialized) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return <AuthContext.Provider value={{ isInitialized }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
