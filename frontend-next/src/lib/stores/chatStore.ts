// ============================================================
// Chat Store - Zustand State Management
// ============================================================

import { create } from 'zustand';
import type { Conversation, Message, ToolCall, Citation } from '@/lib/types';
import { chatApi } from '@/lib/api';

// Properly decode Base64 UTF-8 string
function decodeBase64UTF8(base64: string): string {
  try {
    // Decode base64 to binary string
    const binaryString = atob(base64);
    // Convert binary string to Uint8Array
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    // Decode UTF-8 bytes to string
    return new TextDecoder('utf-8').decode(bytes);
  } catch {
    // Fallback: return as-is if decoding fails
    return base64;
  }
}

interface ChatState {
  // State
  conversations: Conversation[];
  currentConversationId: string | null;
  messages: Message[];
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  streamController: AbortController | null;

  // Actions
  loadConversations: () => Promise<void>;
  createConversation: () => Promise<string>;
  selectConversation: (id: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  renameConversation: (id: string, title: string) => Promise<void>;

  // Message Actions
  sendMessage: (content: string, images?: string[]) => Promise<void>;
  stopStreaming: () => void;
  addMessage: (message: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;

  // Tool Call Actions
  updateToolCall: (messageId: string, toolCall: ToolCall) => void;

  // Utility
  clearError: () => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  currentConversationId: null,
  messages: [],
  isLoading: false,
  isStreaming: false,
  error: null,
  streamController: null,

  loadConversations: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await chatApi.getConversations();
      set({ conversations: response.conversations, isLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load conversations';
      set({ error: message, isLoading: false });
    }
  },

  createConversation: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await chatApi.createConversation();
      const newConversation: Conversation = {
        id: response.id,
        title: response.title,
        createdAt: response.createdAt,
        updatedAt: response.createdAt,
      };

      set((state) => ({
        conversations: [newConversation, ...state.conversations],
        currentConversationId: response.id,
        messages: [],
        isLoading: false,
      }));

      return response.id;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create conversation';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  selectConversation: async (id: string) => {
    set({ isLoading: true, error: null, currentConversationId: id });
    try {
      const response = await chatApi.getMessages(id);
      set({
        messages: response.messages.map((m) => ({
          ...m,
          timestamp: new Date(m.timestamp),
        })),
        isLoading: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load messages';
      set({ error: message, isLoading: false });
    }
  },

  deleteConversation: async (id: string) => {
    try {
      await chatApi.deleteConversation(id);
      set((state) => ({
        conversations: state.conversations.filter((c) => c.id !== id),
        currentConversationId:
          state.currentConversationId === id ? null : state.currentConversationId,
        messages: state.currentConversationId === id ? [] : state.messages,
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete conversation';
      set({ error: message });
    }
  },

  renameConversation: async (id: string, title: string) => {
    try {
      await chatApi.updateConversation(id, { title });
      set((state) => ({
        conversations: state.conversations.map((c) => (c.id === id ? { ...c, title } : c)),
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to rename conversation';
      set({ error: message });
    }
  },

  sendMessage: async (content: string, images?: string[]) => {
    const { currentConversationId, messages } = get();

    // Create user message
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
      images,
    };

    // Create placeholder assistant message
    const assistantMessage: Message = {
      id: `temp-assistant-${Date.now()}`,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
      toolCalls: [],
    };

    set({
      messages: [...messages, userMessage, assistantMessage],
      isStreaming: true,
      error: null,
    });

    // Track new conversation ID from response header
    let newConversationId: string | null = null;

    // Start streaming
    const controller = chatApi.streamChat(
      {
        conversationId: currentConversationId || undefined,
        content,
        images,
      },
      // onMessage
      (event) => {
        const { messages: currentMessages } = get();
        const lastMessage = currentMessages[currentMessages.length - 1];

        if (lastMessage?.role === 'assistant') {
          try {
            // Decode base64 UTF-8 data
            const decodedData = decodeBase64UTF8(event.data);

            switch (event.type) {
              case 'text':
                set({
                  messages: currentMessages.map((m) =>
                    m.id === lastMessage.id ? { ...m, content: m.content + decodedData } : m
                  ),
                });
                break;

              case 'tool_start': {
                const toolName = decodedData;
                const newToolCall: ToolCall = {
                  id: `tool-${Date.now()}`,
                  name: toolName,
                  args: {},
                  status: 'running',
                };
                set({
                  messages: currentMessages.map((m) =>
                    m.id === lastMessage.id
                      ? { ...m, toolCalls: [...(m.toolCalls || []), newToolCall] }
                      : m
                  ),
                });
                break;
              }

              case 'tool_end': {
                try {
                  const toolData = JSON.parse(decodedData);
                  set({
                    messages: currentMessages.map((m) => {
                      if (m.id === lastMessage.id && m.toolCalls) {
                        const updatedToolCalls = [...m.toolCalls];
                        const lastToolCall = updatedToolCalls[updatedToolCalls.length - 1];
                        if (lastToolCall) {
                          lastToolCall.status = 'success';
                          lastToolCall.output = toolData.output;
                          lastToolCall.duration = toolData.duration;
                        }
                        return { ...m, toolCalls: updatedToolCalls };
                      }
                      return m;
                    }),
                  });
                } catch {
                  // Handle parse error
                }
                break;
              }

              case 'citation': {
                // Handle citation event from RAG
                try {
                  const citationData = JSON.parse(decodedData);
                  const newCitation: Citation = {
                    chunkId: citationData.chunk_id,
                    documentId: citationData.document_id,
                    documentName: citationData.document_name,
                    pageNumber: citationData.page_number,
                    section: citationData.section,
                    content: citationData.content,
                    contentPreview: citationData.content_preview,
                    score: citationData.score,
                    highlightRanges: citationData.highlight_ranges,
                    metadata: citationData.metadata,
                  };
                  set({
                    messages: currentMessages.map((m) =>
                      m.id === lastMessage.id
                        ? { ...m, citations: [...(m.citations || []), newCitation] }
                        : m
                    ),
                  });
                } catch {
                  // Handle parse error
                }
                break;
              }

              case 'done': {
                // Parse done event data to get conversation_id
                try {
                  const doneData = JSON.parse(decodedData);
                  if (doneData.conversation_id && !currentConversationId) {
                    newConversationId = doneData.conversation_id;
                  }
                } catch {
                  // done data might be plain "complete" string
                }

                // If a new conversation was created, update state
                if (newConversationId) {
                  const { conversations: currentConversations } = get();
                  const newConversation: Conversation = {
                    id: newConversationId,
                    title: content.slice(0, 50) + (content.length > 50 ? '...' : ''),
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                  };
                  set({
                    currentConversationId: newConversationId,
                    conversations: [newConversation, ...currentConversations],
                    messages: currentMessages.map((m) =>
                      m.id === lastMessage.id ? { ...m, isStreaming: false } : m
                    ),
                    isStreaming: false,
                    streamController: null,
                  });
                } else {
                  set({
                    messages: currentMessages.map((m) =>
                      m.id === lastMessage.id ? { ...m, isStreaming: false } : m
                    ),
                    isStreaming: false,
                    streamController: null,
                  });
                }
                break;
              }
            }
          } catch {
            // Handle decode error - might be raw text
            if (event.type === 'text') {
              set({
                messages: currentMessages.map((m) =>
                  m.id === lastMessage.id ? { ...m, content: m.content + event.data } : m
                ),
              });
            }
          }
        }
      },
      // onError
      (error) => {
        set({
          error: error.message,
          isStreaming: false,
          streamController: null,
        });
      },
      // onComplete
      () => {
        const { isStreaming: stillStreaming } = get();
        if (stillStreaming) {
          set({
            isStreaming: false,
            streamController: null,
          });
        }
      }
    );

    set({ streamController: controller });
  },

  stopStreaming: () => {
    const { streamController, messages } = get();
    if (streamController) {
      streamController.abort();
      set({
        isStreaming: false,
        streamController: null,
        messages: messages.map((m) => (m.isStreaming ? { ...m, isStreaming: false } : m)),
      });
    }
  },

  addMessage: (message: Message) => {
    set((state) => ({
      messages: [...state.messages, message],
    }));
  },

  updateMessage: (id: string, updates: Partial<Message>) => {
    set((state) => ({
      messages: state.messages.map((m) => (m.id === id ? { ...m, ...updates } : m)),
    }));
  },

  updateToolCall: (messageId: string, toolCall: ToolCall) => {
    set((state) => ({
      messages: state.messages.map((m) => {
        if (m.id === messageId && m.toolCalls) {
          return {
            ...m,
            toolCalls: m.toolCalls.map((tc) => (tc.id === toolCall.id ? toolCall : tc)),
          };
        }
        return m;
      }),
    }));
  },

  clearError: () => set({ error: null }),

  clearMessages: () => set({ messages: [] }),
}));
