// ============================================================
// Chat API for Stream-Agent V9
// ============================================================

import apiClient, { API_BASE_URL } from './client';
import type { Conversation, Message, ChatRequest } from '@/lib/types';

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
    const response = await apiClient.get<ConversationListResponse>('/api/conversations', {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Create new conversation
   */
  async createConversation(title?: string): Promise<CreateConversationResponse> {
    const response = await apiClient.post<CreateConversationResponse>('/api/conversations', {
      title: title || 'New Chat',
    });
    return response.data;
  },

  /**
   * Get conversation details
   */
  async getConversation(id: string): Promise<Conversation> {
    const response = await apiClient.get<Conversation>(`/api/conversations/${id}`);
    return response.data;
  },

  /**
   * Update conversation
   */
  async updateConversation(id: string, data: Partial<Conversation>): Promise<Conversation> {
    const response = await apiClient.put<Conversation>(`/api/conversations/${id}`, data);
    return response.data;
  },

  /**
   * Delete conversation
   */
  async deleteConversation(id: string): Promise<void> {
    await apiClient.delete(`/api/conversations/${id}`);
  },

  /**
   * Get messages for a conversation
   */
  async getMessages(conversationId: string, skip = 0, limit = 50): Promise<MessageListResponse> {
    const response = await apiClient.get<MessageListResponse>(
      `/api/conversations/${conversationId}/messages`,
      { params: { skip, limit } }
    );
    return response.data;
  },

  /**
   * Stream chat response using SSE
   */
  streamChat(
    request: ChatRequest,
    onMessage: (event: { type: string; data: string }) => void,
    onError: (error: Error) => void,
    onComplete: () => void
  ): AbortController {
    const controller = new AbortController();
    const token = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;

    fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(request),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('event:')) {
              const eventType = line.slice(6).trim();
              const dataLine = lines[lines.indexOf(line) + 1];
              if (dataLine?.startsWith('data:')) {
                const data = dataLine.slice(5).trim();
                onMessage({ type: eventType, data });
              }
            } else if (line.startsWith('data:')) {
              const data = line.slice(5).trim();
              onMessage({ type: 'text', data });
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
