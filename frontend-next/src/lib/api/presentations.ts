// ============================================================
// Presentation API for Stream-Agent V9
// ============================================================

import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

const PRESENTATION_API_URL = process.env.NEXT_PUBLIC_PRESENTATION_URL || 'http://127.0.0.1:8005';

// 创建演示文稿服务专用客户端
const presentationClient: AxiosInstance = axios.create({
  baseURL: PRESENTATION_API_URL,
  timeout: 120000, // AI 生成可能需要更长时间
  proxy: false, // 禁用代理，避免 Clash 等软件干扰本地请求
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
presentationClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== 'undefined') {
      // 优先从 zustand persist 读取
      const authStorage = localStorage.getItem('auth-storage');
      if (authStorage) {
        try {
          const parsed = JSON.parse(authStorage);
          if (parsed.state?.accessToken && config.headers) {
            config.headers.Authorization = `Bearer ${parsed.state.accessToken}`;
            return config;
          }
        } catch (e) {
          console.error('Failed to parse auth-storage:', e);
        }
      }
      // 回退到直接读取 accessToken
      const token = localStorage.getItem('accessToken');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 导入类型
import type {
  Presentation,
  PresentationGenerateRequest,
  PresentationListResponse,
  RegenerateSlideRequest,
  ChangeThemeRequest,
  UpdateSlideRequest,
  AddSlideRequest,
} from '@/lib/types/presentations';

// Backend response format
interface BackendPresentation {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  slides: unknown[];
  layout_config?: Record<string, unknown>;
  theme: string;
  custom_theme?: Record<string, unknown>;
  target_audience?: string;
  presentation_type?: string;
  include_images: boolean;
  image_style?: string;
  slide_count: number;
  thumbnail?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

interface BackendPresentationListResponse {
  presentations: BackendPresentation[];
  total: number;
}

// Convert backend presentation to frontend format
function convertPresentation(backend: BackendPresentation): Presentation {
  return {
    id: backend.id,
    userId: backend.user_id,
    title: backend.title,
    description: backend.description,
    slides: backend.slides as Presentation['slides'],
    layoutConfig: backend.layout_config,
    theme: backend.theme as Presentation['theme'],
    customTheme: backend.custom_theme,
    targetAudience: backend.target_audience,
    presentationType: backend.presentation_type as Presentation['presentationType'],
    includeImages: backend.include_images,
    imageStyle: backend.image_style,
    slideCount: backend.slide_count,
    thumbnail: backend.thumbnail,
    status: backend.status as Presentation['status'],
    createdAt: backend.created_at,
    updatedAt: backend.updated_at,
  };
}

// ============================================================
// AI Assistant Types
// ============================================================

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface ParsedIntent {
  intent_type: string;
  target_slide?: number | null;
  new_value?: string | null;
  layout?: string | null;
  theme?: string | null;
  position?: number | null;
  response_message: string;
  confidence: number;
  requires_confirmation: boolean;
}

export interface AssistantAction {
  action_type: string;
  target_slide?: number | null;
  changes: Record<string, unknown>;
  success: boolean;
  error_message?: string | null;
}

export interface AssistantChatRequest {
  message: string;
  current_slide_index: number;
  conversation_history?: ChatMessage[];
}

export interface AssistantChatResponse {
  response: string;
  intent: ParsedIntent;
  actions: AssistantAction[];
  presentation_updated: boolean;
  updated_slides?: unknown[] | null;
}

export const presentationApi = {
  /**
   * 获取演示文稿列表
   */
  async getPresentations(skip = 0, limit = 20): Promise<PresentationListResponse> {
    const response = await presentationClient.get<BackendPresentationListResponse>('/api/v1/presentations', {
      params: { skip, limit },
    });
    return {
      presentations: response.data.presentations.map(convertPresentation),
      total: response.data.total,
    };
  },

  /**
   * 创建新演示文稿 (空白)
   */
  async createPresentation(data: { title: string; description?: string }): Promise<Presentation> {
    const response = await presentationClient.post<BackendPresentation>('/api/v1/presentations', data);
    return convertPresentation(response.data);
  },

  /**
   * 获取演示文稿详情
   */
  async getPresentation(id: string): Promise<Presentation> {
    const response = await presentationClient.get<BackendPresentation>(`/api/v1/presentations/${id}`);
    return convertPresentation(response.data);
  },

  /**
   * 更新演示文稿基本信息
   */
  async updatePresentation(id: string, data: { title?: string; description?: string }): Promise<Presentation> {
    const response = await presentationClient.put<BackendPresentation>(`/api/v1/presentations/${id}`, data);
    return convertPresentation(response.data);
  },

  /**
   * 删除演示文稿
   */
  async deletePresentation(id: string): Promise<void> {
    await presentationClient.delete(`/api/v1/presentations/${id}`);
  },

  /**
   * AI 生成演示文稿
   */
  async generatePresentation(data: PresentationGenerateRequest): Promise<Presentation> {
    const response = await presentationClient.post<BackendPresentation>(
      '/api/v1/editor/generate',
      {
        topic: data.topic,
        title: data.title,
        slide_count: data.slideCount,
        target_audience: data.targetAudience,
        presentation_type: data.presentationType,
        theme: data.theme,
        include_images: data.includeImages,
        image_style: data.imageStyle,
        language: data.language,
      }
    );
    return convertPresentation(response.data);
  },

  /**
   * 重新生成指定幻灯片
   */
  async regenerateSlide(
    presentationId: string,
    slideIndex: number,
    data: RegenerateSlideRequest
  ): Promise<Presentation> {
    const response = await presentationClient.post<BackendPresentation>(
      `/api/v1/editor/${presentationId}/regenerate/${slideIndex}`,
      { feedback: data.feedback }
    );
    return convertPresentation(response.data);
  },

  /**
   * 更换演示文稿主题
   */
  async changeTheme(presentationId: string, data: ChangeThemeRequest): Promise<Presentation> {
    const response = await presentationClient.post<BackendPresentation>(
      `/api/v1/editor/${presentationId}/theme`,
      { theme: data.theme }
    );
    return convertPresentation(response.data);
  },

  /**
   * 更新指定幻灯片内容
   */
  async updateSlide(
    presentationId: string,
    slideIndex: number,
    data: UpdateSlideRequest
  ): Promise<Presentation> {
    const response = await presentationClient.put<BackendPresentation>(
      `/api/v1/editor/${presentationId}/slides/${slideIndex}`,
      data
    );
    return convertPresentation(response.data);
  },

  /**
   * 添加新幻灯片
   */
  async addSlide(presentationId: string, data: AddSlideRequest): Promise<Presentation> {
    const response = await presentationClient.post<BackendPresentation>(
      `/api/v1/editor/${presentationId}/slides`,
      {
        slide: data.slide,
        position: data.position,
      }
    );
    return convertPresentation(response.data);
  },

  /**
   * 删除指定幻灯片
   */
  async deleteSlide(presentationId: string, slideIndex: number): Promise<Presentation> {
    const response = await presentationClient.delete<BackendPresentation>(
      `/api/v1/editor/${presentationId}/slides/${slideIndex}`
    );
    return convertPresentation(response.data);
  },

  // ============================================================
  // AI Assistant API
  // ============================================================

  /**
   * AI 助手对话
   * 解析用户的自然语言指令并执行相应操作
   */
  async assistantChat(
    presentationId: string,
    data: AssistantChatRequest
  ): Promise<AssistantChatResponse> {
    const response = await presentationClient.post<AssistantChatResponse>(
      `/api/v1/assistant/${presentationId}/chat`,
      data
    );
    return response.data;
  },
};

export default presentationApi;
