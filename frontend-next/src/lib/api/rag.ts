// ============================================================
// RAG API for Stream-Agent V9
// ============================================================

import axios from 'axios';

// RAG service URL (默认端口 8004)
const RAG_API_URL = process.env.NEXT_PUBLIC_RAG_API_URL || 'http://localhost:8004';

// Create axios instance for RAG service
const ragClient = axios.create({
  baseURL: RAG_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
ragClient.interceptors.request.use(
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

// ============================================================
// Types
// ============================================================

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

export interface CitationDetail {
  chunkId: string;
  documentId: string;
  documentName: string;
  pageNumber?: number;
  chunkIndex: number;
  content: string;
  prevChunks?: string[];
  nextChunks?: string[];
  totalChunks: number;
  metadata?: Record<string, unknown>;
}

export interface SearchResult {
  chunkId: string;
  documentId: string;
  documentName: string;
  content: string;
  pageNumber?: number;
  score: number;
  vectorScore?: number;
  bm25Score?: number;
  rerankScore?: number;
  metadata?: Record<string, unknown>;
  citation?: Citation;
}

export interface SearchResponse {
  query: string;
  total: number;
  results: SearchResult[];
  searchTimeMs: number;
  citations?: Citation[];
}

export interface SearchRequest {
  query: string;
  topK?: number;
  alpha?: number;
  rerank?: boolean;
  documentIds?: string[];
  filters?: Record<string, unknown>;
}

export interface Document {
  id: string;
  userId: string;
  filename: string;
  fileType?: string;
  fileSize?: number;
  milvusCollection?: string;
  chunkCount: number;
  status: 'pending' | 'processing' | 'ready' | 'error';
  createdAt: string;
}

// Backend response types (snake_case)
interface BackendCitation {
  chunk_id: string;
  document_id: string;
  document_name: string;
  page_number?: number;
  section?: string;
  content: string;
  content_preview?: string;
  score: number;
  highlight_ranges?: Array<{ start: number; end: number }>;
  metadata?: Record<string, unknown>;
}

interface BackendCitationDetail {
  chunk_id: string;
  document_id: string;
  document_name: string;
  page_number?: number;
  chunk_index: number;
  content: string;
  prev_chunks?: string[];
  next_chunks?: string[];
  total_chunks: number;
  metadata?: Record<string, unknown>;
}

interface BackendSearchResult {
  chunk_id: string;
  document_id: string;
  document_name: string;
  content: string;
  page_number?: number;
  score: number;
  vector_score?: number;
  bm25_score?: number;
  rerank_score?: number;
  metadata?: Record<string, unknown>;
  citation?: BackendCitation;
}

interface BackendSearchResponse {
  query: string;
  total: number;
  results: BackendSearchResult[];
  search_time_ms: number;
  citations?: BackendCitation[];
}

interface BackendDocument {
  id: string;
  user_id: string;
  filename: string;
  file_type?: string;
  file_size?: number;
  milvus_collection?: string;
  chunk_count: number;
  status: 'pending' | 'processing' | 'ready' | 'error';
  created_at: string;
}

// ============================================================
// Converters
// ============================================================

function toCitation(backend: BackendCitation): Citation {
  return {
    chunkId: backend.chunk_id,
    documentId: backend.document_id,
    documentName: backend.document_name,
    pageNumber: backend.page_number,
    section: backend.section,
    content: backend.content,
    contentPreview: backend.content_preview,
    score: backend.score,
    highlightRanges: backend.highlight_ranges,
    metadata: backend.metadata,
  };
}

function toCitationDetail(backend: BackendCitationDetail): CitationDetail {
  return {
    chunkId: backend.chunk_id,
    documentId: backend.document_id,
    documentName: backend.document_name,
    pageNumber: backend.page_number,
    chunkIndex: backend.chunk_index,
    content: backend.content,
    prevChunks: backend.prev_chunks,
    nextChunks: backend.next_chunks,
    totalChunks: backend.total_chunks,
    metadata: backend.metadata,
  };
}

function toSearchResult(backend: BackendSearchResult): SearchResult {
  return {
    chunkId: backend.chunk_id,
    documentId: backend.document_id,
    documentName: backend.document_name,
    content: backend.content,
    pageNumber: backend.page_number,
    score: backend.score,
    vectorScore: backend.vector_score,
    bm25Score: backend.bm25_score,
    rerankScore: backend.rerank_score,
    metadata: backend.metadata,
    citation: backend.citation ? toCitation(backend.citation) : undefined,
  };
}

function toDocument(backend: BackendDocument): Document {
  return {
    id: backend.id,
    userId: backend.user_id,
    filename: backend.filename,
    fileType: backend.file_type,
    fileSize: backend.file_size,
    milvusCollection: backend.milvus_collection,
    chunkCount: backend.chunk_count,
    status: backend.status,
    createdAt: backend.created_at,
  };
}

// ============================================================
// API Methods
// ============================================================

export const ragApi = {
  /**
   * Search documents (hybrid search)
   */
  async search(request: SearchRequest): Promise<SearchResponse> {
    const backendRequest = {
      query: request.query,
      top_k: request.topK || 10,
      alpha: request.alpha || 0.5,
      rerank: request.rerank ?? true,
      document_ids: request.documentIds,
      filters: request.filters,
    };

    const response = await ragClient.post<BackendSearchResponse>(
      '/api/v1/search/hybrid',
      backendRequest
    );

    return {
      query: response.data.query,
      total: response.data.total,
      results: response.data.results.map(toSearchResult),
      searchTimeMs: response.data.search_time_ms,
      citations: response.data.citations?.map(toCitation),
    };
  },

  /**
   * BM25 keyword search
   */
  async bm25Search(query: string, topK: number = 10): Promise<SearchResponse> {
    const response = await ragClient.get<BackendSearchResponse>('/api/v1/search/bm25', {
      params: { query, top_k: topK },
    });

    return {
      query: response.data.query,
      total: response.data.total,
      results: response.data.results.map(toSearchResult),
      searchTimeMs: response.data.search_time_ms,
      citations: response.data.citations?.map(toCitation),
    };
  },

  /**
   * Get citation details for multiple chunks
   */
  async getCitations(
    chunkIds: string[],
    includeContext: boolean = true,
    contextSize: number = 1
  ): Promise<CitationDetail[]> {
    const response = await ragClient.post<BackendCitationDetail[]>('/api/v1/search/citations', {
      chunk_ids: chunkIds,
      include_context: includeContext,
      context_size: contextSize,
    });

    return response.data.map(toCitationDetail);
  },

  /**
   * Get citation detail for a single chunk
   */
  async getCitationDetail(
    chunkId: string,
    contextSize: number = 1
  ): Promise<CitationDetail> {
    const response = await ragClient.get<BackendCitationDetail>(
      `/api/v1/search/citations/${chunkId}`,
      { params: { context_size: contextSize } }
    );

    return toCitationDetail(response.data);
  },

  /**
   * Get document list
   */
  async getDocuments(skip: number = 0, limit: number = 20): Promise<Document[]> {
    const response = await ragClient.get<BackendDocument[]>('/api/v1/documents', {
      params: { skip, limit },
    });

    return response.data.map(toDocument);
  },

  /**
   * Get document by ID
   */
  async getDocument(id: string): Promise<Document> {
    const response = await ragClient.get<BackendDocument>(`/api/v1/documents/${id}`);
    return toDocument(response.data);
  },

  /**
   * Delete document
   */
  async deleteDocument(id: string): Promise<void> {
    await ragClient.delete(`/api/v1/documents/${id}`);
  },

  /**
   * Upload and ingest document
   */
  async uploadDocument(
    file: File,
    chunkSize: number = 500,
    chunkOverlap: number = 50,
    strategy: string = 'semantic'
  ): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await ragClient.post<BackendDocument>('/api/v1/ingest/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      params: {
        chunk_size: chunkSize,
        chunk_overlap: chunkOverlap,
        strategy: strategy,
      },
    });

    return toDocument(response.data);
  },
};
