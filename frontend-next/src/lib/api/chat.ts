// ============================================================
// Chat API for Stream-Agent V9
// ============================================================

import axios from 'axios';
import { CHAT_API_URL } from './client';
import type { Conversation, Message, ChatRequest } from '@/lib/types';

// Create a separate axios instance for chat service
const chatClient = axios.create({
  baseURL: CHAT_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
chatClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('accessToken');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Backend response format (snake_case)
interface BackendConversation {
  id: string;
  title: string;
  model?: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

interface BackendMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  images?: string[];
  tool_calls?: Array<{
    id: string;
    name: string;
    args: Record<string, unknown>;
    status: 'running' | 'success' | 'error';
    output?: string;
    duration?: number;
  }>;
  citations?: Array<{
    sourceId: string;
    sourceName: string;
    pageNumber?: number;
    content: string;
    confidence: number;
  }>;
}

interface BackendConversationListResponse {
  conversations: BackendConversation[];
  total: number;
}

interface BackendMessageListResponse {
  messages: BackendMessage[];
  total: number;
}

// Convert backend conversation to frontend format
function toConversation(backend: BackendConversation): Conversation {
  return {
    id: backend.id,
    title: backend.title,
    model: backend.model,
    createdAt: backend.created_at,
    updatedAt: backend.updated_at,
    messageCount: backend.message_count,
  };
}

// Convert backend message to frontend format
function toMessage(backend: BackendMessage): Message {
  return {
    id: backend.id,
    role: backend.role,
    content: backend.content,
    timestamp: new Date(backend.created_at),
    images: backend.images,
    toolCalls: backend.tool_calls,
    citations: backend.citations,
  };
}

export interface CreateConversationResponse {
  id: string;
  title: string;
  createdAt: string;
}

export interface ConversationListResponse {
  conversations: Conversation[];
  total: number;
}

export interface MessageListResponse {
  messages: Message[];
  total: number;
}

export const chatApi = {
  /**
   * Get conversation list
   */
  async getConversations(skip = 0, limit = 20): Promise<ConversationListResponse> {
    const response = await chatClient.get<BackendConversationListResponse>('/api/conversations', {
      params: { skip, limit },
    });
    return {
      conversations: response.data.conversations.map(toConversation),
      total: response.data.total,
    };
  },

  /**
   * Create new conversation
   */
  async createConversation(title?: string): Promise<CreateConversationResponse> {
    const response = await chatClient.post<BackendConversation>('/api/conversations', {
      title: title || 'New Chat',
    });
    return {
      id: response.data.id,
      title: response.data.title,
      createdAt: response.data.created_at,
    };
  },

  /**
   * Get conversation details
   */
  async getConversation(id: string): Promise<Conversation> {
    const response = await chatClient.get<BackendConversation>(`/api/conversations/${id}`);
    return toConversation(response.data);
  },

  /**
   * Update conversation
   */
  async updateConversation(id: string, data: Partial<Conversation>): Promise<Conversation> {
    const response = await chatClient.put<BackendConversation>(`/api/conversations/${id}`, {
      title: data.title,
      model: data.model,
    });
    return toConversation(response.data);
  },

  /**
   * Delete conversation
   */
  async deleteConversation(id: string): Promise<void> {
    await chatClient.delete(`/api/conversations/${id}`);
  },

  /**
   * Get messages for a conversation
   */
  async getMessages(conversationId: string, skip = 0, limit = 50): Promise<MessageListResponse> {
    const response = await chatClient.get<BackendMessageListResponse>(
      `/api/conversations/${conversationId}/messages`,
      { params: { skip, limit } }
    );
    return {
      messages: response.data.messages.map(toMessage),
      total: response.data.total,
    };
  },

  /**
   * Stream chat response using SSE
   *
   * SSE Event format from backend:
   * - event: text\ndata: <base64 encoded text>
   * - event: tool_start\ndata: <base64 encoded tool name>
   * - event: tool_end\ndata: <base64 encoded JSON {output, duration}>
   * - event: done\ndata: <base64 encoded JSON {message_id, conversation_id}>
   * - event: error\ndata: <base64 encoded error message>
   */
  streamChat(
    request: ChatRequest,
    onMessage: (event: { type: string; data: string }) => void,
    onError: (error: Error) => void,
    onComplete: () => void
  ): AbortController {
    const controller = new AbortController();
    const token = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;

    // Convert request to snake_case for backend
    const backendRequest = {
      conversation_id: request.conversationId,
      content: request.content,
      images: request.images,
      api_keys: request.apiKeys,
    };

    fetch(`${CHAT_API_URL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(backendRequest),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        const decoder = new TextDecoder();
        let buffer = '';
        let currentEventType = 'text';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmedLine = line.trim();

            if (trimmedLine.startsWith('event:')) {
              // Store the event type for the next data line
              currentEventType = trimmedLine.slice(6).trim();
            } else if (trimmedLine.startsWith('data:')) {
              const data = trimmedLine.slice(5).trim();
              if (data) {
                onMessage({ type: currentEventType, data });
              }
              // Reset to default after processing
              currentEventType = 'text';
            }
          }
        }

        onComplete();
      })
      .catch((error) => {
        if (error.name !== 'AbortError') {
          onError(error);
        }
      });

    return controller;
  },

  /**
   * Stop streaming
   */
  stopStreaming(controller: AbortController): void {
    controller.abort();
  },
};
