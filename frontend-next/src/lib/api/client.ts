// ============================================================
// API Client for Stream-Agent V9
// ============================================================

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

// API Base URLs for different services
// 支持通过环境变量配置各服务地址
// 注意: Windows 上使用 127.0.0.1 而不是 localhost，避免代理软件干扰
const CHAT_API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_CHAT_API_URL || 'http://127.0.0.1:8002';
const AUTH_API_URL = process.env.NEXT_PUBLIC_AUTH_URL || process.env.NEXT_PUBLIC_AUTH_API_URL || 'http://127.0.0.1:8001';
const RAG_API_URL = process.env.NEXT_PUBLIC_RAG_URL || process.env.NEXT_PUBLIC_RAG_API_URL || 'http://127.0.0.1:8004';
const WHISPER_API_URL = process.env.NEXT_PUBLIC_WHISPER_URL || process.env.NEXT_PUBLIC_VOICE_API_URL || 'http://127.0.0.1:8003';

// 默认 API 客户端 (使用 Chat 服务)
const apiClient: AxiosInstance = axios.create({
  baseURL: CHAT_API_URL,
  timeout: 30000,
  proxy: false, // 禁用代理，避免 Clash 等软件干扰本地请求
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth 服务专用客户端
export const authApiClient: AxiosInstance = axios.create({
  baseURL: AUTH_API_URL,
  timeout: 30000,
  proxy: false, // 禁用代理
  headers: {
    'Content-Type': 'application/json',
  },
});

// RAG 服务专用客户端
export const ragApiClient: AxiosInstance = axios.create({
  baseURL: RAG_API_URL,
  timeout: 60000, // RAG 操作可能需要更长时间
  proxy: false, // 禁用代理
  headers: {
    'Content-Type': 'application/json',
  },
});

// Whisper 服务专用客户端
export const whisperApiClient: AxiosInstance = axios.create({
  baseURL: WHISPER_API_URL,
  timeout: 60000, // 音频处理需要更长时间
  proxy: false, // 禁用代理
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

// Token 拦截器通用函数
const addAuthToken = (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
  // Get token from localStorage (client-side only)
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('accessToken');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
};

// 为所有客户端添加请求拦截器
[apiClient, authApiClient, ragApiClient].forEach(client => {
  client.interceptors.request.use(addAuthToken);
});

// whisperApiClient 使用 multipart/form-data，不需要 Authorization
// 也不需要在请求拦截器中添加 token

// Response interceptor - handle errors and token refresh
// 为主客户端添加响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Handle 401 errors - attempt token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post(`${AUTH_API_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;
          localStorage.setItem('accessToken', access_token);
          localStorage.setItem('refreshToken', refresh_token);

          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed - clear tokens and redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
export { CHAT_API_URL, AUTH_API_URL, RAG_API_URL, WHISPER_API_URL };
