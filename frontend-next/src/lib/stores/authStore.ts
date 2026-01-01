// ============================================================
// Auth Store - Zustand State Management
// ============================================================

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/lib/types';
import { authApi } from '@/lib/api';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isInitialized: boolean;  // 是否已初始化（检查过本地存储）
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<void>;
  clearError: () => void;
  setUser: (user: User | null) => void;
  initialize: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isInitialized: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.login({ email, password });
          const { tokens } = response;

          // Store tokens in localStorage for API client
          if (typeof window !== 'undefined') {
            localStorage.setItem('accessToken', tokens.accessToken);
            localStorage.setItem('refreshToken', tokens.refreshToken);
          }

          // Fetch user info after login
          const user = await authApi.getCurrentUser();

          set({
            user,
            accessToken: tokens.accessToken,
            refreshToken: tokens.refreshToken,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Login failed';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      register: async (username: string, email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          await authApi.register({ username, email, password });
          // Auto login after registration
          await get().login(email, password);
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Registration failed';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      logout: async () => {
        const { refreshToken } = get();
        try {
          if (refreshToken) {
            await authApi.logout(refreshToken);
          }
        } catch {
          // Continue with logout even if API call fails
        } finally {
          // Clear tokens from localStorage
          if (typeof window !== 'undefined') {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
          }

          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
          });
        }
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get();
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        try {
          const response = await authApi.refreshToken(refreshToken);

          if (typeof window !== 'undefined') {
            localStorage.setItem('accessToken', response.accessToken);
            localStorage.setItem('refreshToken', response.refreshToken);
          }

          set({
            accessToken: response.accessToken,
            refreshToken: response.refreshToken,
          });
        } catch (error) {
          // Token refresh failed - logout
          await get().logout();
          throw error;
        }
      },

      clearError: () => set({ error: null }),

      setUser: (user: User | null) => set({ user }),

      initialize: () => {
        // Check if there's a stored token on mount
        if (typeof window !== 'undefined') {
          const storedToken = localStorage.getItem('accessToken');
          const storedRefreshToken = localStorage.getItem('refreshToken');
          const storedUser = localStorage.getItem('auth-storage-user');

          if (storedToken && storedRefreshToken) {
            // Has tokens, mark as authenticated
            set({
              accessToken: storedToken,
              refreshToken: storedRefreshToken,
              isAuthenticated: true,
              isInitialized: true,
            });
          } else {
            // No tokens, mark as initialized but not authenticated
            set({
              isInitialized: true,
            });
          }
        } else {
          set({ isInitialized: true });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
