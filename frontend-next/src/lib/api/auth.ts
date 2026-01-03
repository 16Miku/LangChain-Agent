// ============================================================
// Auth API for Stream-Agent V9
// ============================================================

import { authApiClient } from './client';
import type { User, LoginCredentials, RegisterData, AuthTokens } from '@/lib/types';

// Backend response format (snake_case)
interface BackendTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface BackendUserResponse {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginResponse {
  tokens: AuthTokens;
}

export interface RegisterResponse {
  user: User;
}

// Convert backend user to frontend format
function toUser(backend: BackendUserResponse): User {
  return {
    id: backend.id,
    username: backend.username,
    email: backend.email,
    isActive: backend.is_active,
    createdAt: backend.created_at,
  };
}

// Convert backend tokens to frontend format
function toTokens(backend: BackendTokenResponse): AuthTokens {
  return {
    accessToken: backend.access_token,
    refreshToken: backend.refresh_token,
    tokenType: backend.token_type,
    expiresIn: backend.expires_in,
  };
}

export const authApi = {
  /**
   * User registration
   */
  async register(data: RegisterData): Promise<RegisterResponse> {
    const response = await authApiClient.post<BackendUserResponse>('/api/auth/register', data);
    return {
      user: toUser(response.data),
    };
  },

  /**
   * User login
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await authApiClient.post<BackendTokenResponse>('/api/auth/login', credentials);
    return {
      tokens: toTokens(response.data),
    };
  },

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    const response = await authApiClient.post<BackendTokenResponse>('/api/auth/refresh', {
      refresh_token: refreshToken,
    });
    return toTokens(response.data);
  },

  /**
   * Logout
   */
  async logout(refreshToken: string): Promise<void> {
    await authApiClient.post('/api/auth/logout', {
      refresh_token: refreshToken,
    });
  },

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<User> {
    const response = await authApiClient.get<BackendUserResponse>('/api/auth/me');
    return toUser(response.data);
  },

  /**
   * Update password
   */
  async updatePassword(currentPassword: string, newPassword: string): Promise<void> {
    await authApiClient.put('/api/auth/password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },
};
