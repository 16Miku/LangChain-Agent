-- ============================================================
-- My-Chat-LangChain V10 Supabase 初始化脚本
-- ============================================================
-- 使用方法:
--   1. 登录 Supabase 控制台: https://supabase.com/dashboard
--   2. 进入项目 -> SQL Editor
--   3. 复制并执行此脚本
--
-- 注意:
--   - 此脚本是幂等的，可以多次执行
--   - 包含 V9 基础表 + V10 新增表
--   - 启用 pgvector 扩展用于向量存储
-- ============================================================

-- ============================================================
-- 0. 启用扩展
-- ============================================================

-- 启用 pgvector 扩展 (用于向量存储)
CREATE EXTENSION IF NOT EXISTS vector;

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 启用 pg_trgm 扩展 (用于模糊搜索)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

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

-- 用户设置表
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
-- 4. Presentation Service 表
-- ============================================================

-- 演示文稿表
CREATE TABLE IF NOT EXISTS presentations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    slides JSONB NOT NULL DEFAULT '[]',
    layout_config JSONB NOT NULL DEFAULT '{}',
    theme VARCHAR(50) NOT NULL DEFAULT 'modern_business',
    custom_theme JSONB,
    target_audience VARCHAR(100),
    presentation_type VARCHAR(50),  -- informative, persuasive, instructional
    include_images BOOLEAN NOT NULL DEFAULT TRUE,
    image_style VARCHAR(50),
    slide_count INTEGER NOT NULL DEFAULT 0,
    thumbnail TEXT,                 -- Base64 编码的预览图
    status VARCHAR(20) NOT NULL DEFAULT 'draft',  -- draft, completed, archived
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_presentations_user_id ON presentations(user_id);
CREATE INDEX IF NOT EXISTS idx_presentations_status ON presentations(status);
CREATE INDEX IF NOT EXISTS idx_presentations_updated_at ON presentations(updated_at DESC);

-- 幻灯片版本表 (用于版本管理和回滚)
CREATE TABLE IF NOT EXISTS slide_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    presentation_id UUID NOT NULL REFERENCES presentations(id) ON DELETE CASCADE,
    slide_index INTEGER NOT NULL,
    content JSONB NOT NULL,
    layout VARCHAR(50),
    version_number INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_slide_versions_presentation_id ON slide_versions(presentation_id);

-- ============================================================
-- 5. V10 新增表
-- ============================================================

-- 5.1 PPTX 模板表
CREATE TABLE IF NOT EXISTS pptx_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),           -- business, academic, creative, minimal
    thumbnail TEXT,                 -- Base64 预览图
    config JSONB NOT NULL,          -- 模板配置 (颜色、字体、布局等)
    is_system BOOLEAN DEFAULT FALSE, -- 是否为系统内置模板
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,  -- NULL 表示系统模板
    usage_count INTEGER DEFAULT 0,  -- 使用次数统计
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_pptx_templates_category ON pptx_templates(category);
CREATE INDEX IF NOT EXISTS idx_pptx_templates_is_system ON pptx_templates(is_system);
CREATE INDEX IF NOT EXISTS idx_pptx_templates_user_id ON pptx_templates(user_id);

-- 5.2 工具调用缓存表
CREATE TABLE IF NOT EXISTS tool_call_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_name VARCHAR(100) NOT NULL,
    args_hash VARCHAR(64) NOT NULL,     -- 参数的 SHA256 哈希
    result JSONB NOT NULL,              -- 缓存的结果
    hit_count INTEGER DEFAULT 1,        -- 命中次数
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tool_name, args_hash)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_tool_call_cache_tool_name ON tool_call_cache(tool_name);
CREATE INDEX IF NOT EXISTS idx_tool_call_cache_expires_at ON tool_call_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_tool_call_cache_lookup ON tool_call_cache(tool_name, args_hash);

-- 5.3 查询改写历史表
CREATE TABLE IF NOT EXISTS query_rewrites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_query TEXT NOT NULL,       -- 原始查询
    rewritten_query TEXT NOT NULL,      -- 改写后的查询
    context_summary TEXT,               -- 上下文摘要
    rewrite_reason TEXT,                -- 改写原因
    retrieval_improved BOOLEAN,         -- 检索是否改善
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_query_rewrites_conversation_id ON query_rewrites(conversation_id);
CREATE INDEX IF NOT EXISTS idx_query_rewrites_user_id ON query_rewrites(user_id);
CREATE INDEX IF NOT EXISTS idx_query_rewrites_created_at ON query_rewrites(created_at DESC);

-- 5.4 上下文压缩记录表
CREATE TABLE IF NOT EXISTS context_compressions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    original_token_count INTEGER NOT NULL,
    compressed_token_count INTEGER NOT NULL,
    compression_ratio FLOAT NOT NULL,
    summary TEXT NOT NULL,              -- 压缩后的摘要
    key_points JSONB,                   -- 保留的关键点
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_context_compressions_conversation_id ON context_compressions(conversation_id);

-- ============================================================
-- 6. 向量搜索函数
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
-- 7. 工具函数
-- ============================================================

-- 清理过期的工具调用缓存
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM tool_call_cache
    WHERE expires_at < NOW();

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;

-- 获取或创建缓存
CREATE OR REPLACE FUNCTION get_or_create_cache(
    p_tool_name VARCHAR(100),
    p_args_hash VARCHAR(64),
    p_result JSONB,
    p_ttl_seconds INTEGER DEFAULT 3600
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    cached_result JSONB;
BEGIN
    -- 尝试获取缓存
    SELECT result INTO cached_result
    FROM tool_call_cache
    WHERE tool_name = p_tool_name
      AND args_hash = p_args_hash
      AND expires_at > NOW();

    IF cached_result IS NOT NULL THEN
        -- 更新命中次数
        UPDATE tool_call_cache
        SET hit_count = hit_count + 1,
            updated_at = NOW()
        WHERE tool_name = p_tool_name
          AND args_hash = p_args_hash;

        RETURN cached_result;
    END IF;

    -- 插入新缓存
    INSERT INTO tool_call_cache (tool_name, args_hash, result, expires_at)
    VALUES (p_tool_name, p_args_hash, p_result, NOW() + (p_ttl_seconds || ' seconds')::INTERVAL)
    ON CONFLICT (tool_name, args_hash)
    DO UPDATE SET
        result = EXCLUDED.result,
        expires_at = NOW() + (p_ttl_seconds || ' seconds')::INTERVAL,
        hit_count = tool_call_cache.hit_count + 1,
        updated_at = NOW();

    RETURN p_result;
END;
$$;

-- ============================================================
-- 8. 触发器: 自动更新 updated_at
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

DROP TRIGGER IF EXISTS update_presentations_updated_at ON presentations;
CREATE TRIGGER update_presentations_updated_at
    BEFORE UPDATE ON presentations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_pptx_templates_updated_at ON pptx_templates;
CREATE TRIGGER update_pptx_templates_updated_at
    BEFORE UPDATE ON pptx_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_tool_call_cache_updated_at ON tool_call_cache;
CREATE TRIGGER update_tool_call_cache_updated_at
    BEFORE UPDATE ON tool_call_cache
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 9. 初始数据: 系统内置 PPTX 模板
-- ============================================================

-- 插入系统内置模板
INSERT INTO pptx_templates (name, description, category, is_system, config)
VALUES
    ('现代商务', '简洁专业的商务演示模板', 'business', TRUE, '{
        "colors": {
            "primary": "#2563eb",
            "secondary": "#64748b",
            "accent": "#0ea5e9",
            "background": "#ffffff",
            "text": "#1e293b"
        },
        "fonts": {
            "heading": "Inter",
            "body": "Inter"
        },
        "spacing": "comfortable"
    }'),
    ('学术报告', '适合学术演讲和研究报告', 'academic', TRUE, '{
        "colors": {
            "primary": "#1e40af",
            "secondary": "#475569",
            "accent": "#3b82f6",
            "background": "#f8fafc",
            "text": "#0f172a"
        },
        "fonts": {
            "heading": "Georgia",
            "body": "Times New Roman"
        },
        "spacing": "normal"
    }'),
    ('创意设计', '大胆配色的创意演示模板', 'creative', TRUE, '{
        "colors": {
            "primary": "#7c3aed",
            "secondary": "#ec4899",
            "accent": "#f59e0b",
            "background": "#faf5ff",
            "text": "#1f2937"
        },
        "fonts": {
            "heading": "Poppins",
            "body": "Open Sans"
        },
        "spacing": "relaxed"
    }'),
    ('极简风格', '简约大方的极简主义模板', 'minimal', TRUE, '{
        "colors": {
            "primary": "#18181b",
            "secondary": "#71717a",
            "accent": "#a1a1aa",
            "background": "#ffffff",
            "text": "#27272a"
        },
        "fonts": {
            "heading": "Helvetica",
            "body": "Helvetica"
        },
        "spacing": "spacious"
    }'),
    ('科技未来', '科技感十足的演示模板', 'business', TRUE, '{
        "colors": {
            "primary": "#06b6d4",
            "secondary": "#8b5cf6",
            "accent": "#22d3ee",
            "background": "#0f172a",
            "text": "#f1f5f9"
        },
        "fonts": {
            "heading": "Roboto",
            "body": "Roboto"
        },
        "spacing": "comfortable"
    }')
ON CONFLICT DO NOTHING;

-- ============================================================
-- 10. Row Level Security (RLS) 策略 (可选)
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
-- 11. 定时任务 (使用 pg_cron 扩展，需要在 Supabase 中启用)
-- ============================================================

-- 每小时清理过期缓存
-- SELECT cron.schedule('cleanup-cache', '0 * * * *', 'SELECT cleanup_expired_cache()');

-- ============================================================
-- 完成
-- ============================================================
-- Schema 版本: 2.0.0 (V10)
-- 创建日期: 2026-01-24
-- 兼容: Supabase PostgreSQL 15+
--
-- 新增表 (V10):
--   - pptx_templates: PPTX 模板管理
--   - tool_call_cache: 工具调用缓存
--   - query_rewrites: 查询改写历史
--   - context_compressions: 上下文压缩记录
--
-- 新增函数 (V10):
--   - cleanup_expired_cache(): 清理过期缓存
--   - get_or_create_cache(): 获取或创建缓存
-- ============================================================
