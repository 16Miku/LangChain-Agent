// ============================================================
// Type Definitions for Stream-Agent V9
// ============================================================

// User Types
export interface User {
  id: string;
  username: string;
  email: string;
  createdAt: string;
  isActive: boolean;
}

export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  language: string;
  voiceEnabled: boolean;
  defaultModel: string;
}

// Auth Types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

// Chat Types
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  toolCalls?: ToolCall[];
  images?: string[];
  citations?: Citation[];
  isStreaming?: boolean;
}

export interface ToolCall {
  id: string;
  name: string;
  args: Record<string, unknown>;
  status: 'running' | 'success' | 'error';
  output?: string;
  duration?: number;
}

export interface Citation {
  chunkId: string;
  documentId: string;
  documentName: string;
  pageNumber?: number;
  section?: string;
  content: string;
  contentPreview?: string;
  score: number;
  highlightRanges?: Array<{ start: number; end: number }>;
  metadata?: Record<string, unknown>;
}

export interface Conversation {
  id: string;
  title: string;
  model?: string;
  createdAt: string;
  updatedAt: string;
  messageCount?: number;
}

// API Types
export interface ChatRequest {
  conversationId?: string;
  content: string;
  images?: string[];
  apiKeys?: Record<string, string>;
}

export interface ChatStreamEvent {
  type: 'text' | 'tool_start' | 'tool_end' | 'citation' | 'done' | 'error';
  data: unknown;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
}

// Document Types
export interface Document {
  id: string;
  filename: string;
  fileType: string;
  fileSize: number;
  status: 'pending' | 'processing' | 'ready' | 'error';
  chunkCount: number;
  createdAt: string;
}
