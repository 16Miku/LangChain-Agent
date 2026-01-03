-- ============================================================
-- Supabase Database Schema for My-Chat-LangChain V9.0
-- ============================================================
-- 部署方式: 在 Supabase SQL Editor 中执行此脚本
--
-- 说明:
--   1. 启用 pgvector 扩展用于向量存储
--   2. 包含所有微服务的表结构
--   3. 支持 RLS (Row Level Security) 策略
-- ============================================================

-- ============================================================
-- 0. 启用扩展
-- ============================================================

-- 启用 pgvector 扩展 (用于向量存储)
CREATE EXTENSION IF NOT EXISTS vector;

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. Auth Service 表
-- ============================================================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建用户名和邮箱索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Refresh Token 表
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);

-- 用户设置表 (可选扩展)
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    theme VARCHAR(20) DEFAULT 'system',
    language VARCHAR(10) DEFAULT 'zh-CN',
    voice_enabled BOOLEAN DEFAULT FALSE,
    tts_voice VARCHAR(100) DEFAULT 'zh-CN-XiaoxiaoNeural',
    default_model VARCHAR(50) DEFAULT 'gemini-2.0-flash',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API Key 表 (用于存储用户自定义的 API Key)
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_name VARCHAR(100) NOT NULL,
    key_type VARCHAR(50) NOT NULL,  -- 'google', 'openai', 'e2b', etc.
    encrypted_value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, key_type)
);

CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);

-- ============================================================
-- 2. Chat Service 表
-- ============================================================

-- 会话表
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) DEFAULT 'New Chat',
    model VARCHAR(50),
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);

-- 消息表
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    images JSONB,               -- 图片 URL/Base64 数组
    tool_calls JSONB,           -- 工具调用记录
    citations JSONB,            -- 引用来源
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- ============================================================
-- 3. RAG Service 表
-- ============================================================

-- 文档状态枚举 (PostgreSQL 方式)
DO $$ BEGIN
    CREATE TYPE document_status AS ENUM ('pending', 'processing', 'ready', 'error');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 文档表
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    file_path VARCHAR(500),         -- 存储路径 (Supabase Storage 或 MinIO)
    collection_name VARCHAR(100),   -- 向量 collection 名称 (兼容字段)
    chunk_count INTEGER DEFAULT 0,
    status document_status DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);

-- 文档分块表 (带向量)
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    page_number INTEGER,
    section VARCHAR(255),           -- 章节标题
    embedding vector(384),          -- all-MiniLM-L6-v2 维度
    extra_data JSONB DEFAULT '{}',  -- 额外元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_user_id ON document_chunks(user_id);

-- 创建向量索引 (IVFFlat - 适用于中等规模数据)
-- 注意: lists 参数应根据数据量调整, 建议 lists = sqrt(row_count)
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- ============================================================
-- 4. 向量搜索函数
-- ============================================================

-- 相似度搜索函数 (按用户隔离)
CREATE OR REPLACE FUNCTION search_documents(
    query_embedding vector(384),
    match_user_id UUID,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    content TEXT,
    page_number INTEGER,
    section VARCHAR,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.document_id,
        dc.content,
        dc.page_number,
        dc.section,
        1 - (dc.embedding <=> query_embedding) AS similarity
    FROM document_chunks dc
    WHERE dc.user_id = match_user_id
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 混合搜索函数 (向量 + 全文)
CREATE OR REPLACE FUNCTION hybrid_search(
    query_embedding vector(384),
    query_text TEXT,
    match_user_id UUID,
    match_count INT DEFAULT 10,
    vector_weight FLOAT DEFAULT 0.5
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    content TEXT,
    page_number INTEGER,
    section VARCHAR,
    vector_score FLOAT,
    text_score FLOAT,
    combined_score FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.document_id,
        dc.content,
        dc.page_number,
        dc.section,
        (1 - (dc.embedding <=> query_embedding))::FLOAT AS vector_score,
        ts_rank(to_tsvector('simple', dc.content), plainto_tsquery('simple', query_text))::FLOAT AS text_score,
        (
            vector_weight * (1 - (dc.embedding <=> query_embedding)) +
            (1 - vector_weight) * ts_rank(to_tsvector('simple', dc.content), plainto_tsquery('simple', query_text))
        )::FLOAT AS combined_score
    FROM document_chunks dc
    WHERE dc.user_id = match_user_id
    ORDER BY combined_score DESC
    LIMIT match_count;
END;
$$;

-- ============================================================
-- 5. 触发器: 自动更新 updated_at
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为需要自动更新时间戳的表创建触发器
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_settings_updated_at ON user_settings;
CREATE TRIGGER update_user_settings_updated_at
    BEFORE UPDATE ON user_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 6. Row Level Security (RLS) 策略
-- ============================================================
-- 注意: 启用 RLS 后，需要配合 Supabase Auth 或自定义 JWT 验证
-- 以下策略可根据实际需求启用

-- 示例: 启用 users 表的 RLS
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 示例: 用户只能访问自己的数据
-- CREATE POLICY "Users can only access their own data" ON users
--     FOR ALL
--     USING (auth.uid() = id);

-- 示例: 会话表 RLS
-- ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Users can only access their own conversations" ON conversations
--     FOR ALL
--     USING (auth.uid() = user_id);

-- ============================================================
-- 7. 初始数据 (可选)
-- ============================================================

-- 示例: 创建测试用户 (密码: test123)
-- INSERT INTO users (username, email, password_hash, is_active, is_verified)
-- VALUES ('testuser', 'test@example.com', '$2b$12$...hashed...', true, true)
-- ON CONFLICT (username) DO NOTHING;

-- ============================================================
-- 完成
-- ============================================================
-- Schema 版本: 1.0.0
-- 创建日期: 2026-01-03
-- 兼容: Supabase PostgreSQL 15+
-- ============================================================
