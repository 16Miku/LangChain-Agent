# Supabase 数据库配置

## 概述

本目录包含 My-Chat-LangChain V9.0 的 Supabase 数据库 Schema 和迁移脚本。

## 文件说明

| 文件 | 说明 |
|------|------|
| `supabase_schema.sql` | 完整的数据库 Schema (包含 pgvector) |

## 部署步骤

### 1. 创建 Supabase 项目

1. 访问 [Supabase](https://supabase.com) 并登录
2. 点击 "New Project" 创建新项目
3. 选择区域 (推荐: Southeast Asia 或 US East)
4. 设置数据库密码并保存

### 2. 执行 Schema

1. 进入 Supabase Dashboard
2. 点击左侧 "SQL Editor"
3. 新建 Query
4. 复制 `supabase_schema.sql` 的全部内容
5. 点击 "Run" 执行

### 3. 获取连接信息

在 Supabase Dashboard 中:

1. 点击 "Settings" → "Database"
2. 找到 "Connection string" 部分
3. 复制 "URI" 格式的连接字符串

```bash
# 连接字符串格式
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

### 4. 配置环境变量

在各微服务的 `.env` 文件中设置:

```bash
# 数据库连接
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres

# Supabase 配置 (可选, 用于 Supabase Auth 集成)
SUPABASE_URL=https://[project-ref].supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key

# pgvector 配置
VECTOR_STORE_BACKEND=pgvector
PGVECTOR_ENABLED=true
```

## 表结构

### Auth Service

| 表名 | 说明 |
|------|------|
| `users` | 用户账户 |
| `refresh_tokens` | JWT 刷新令牌 |
| `user_settings` | 用户设置 |
| `api_keys` | 用户自定义 API Key |

### Chat Service

| 表名 | 说明 |
|------|------|
| `conversations` | 会话记录 |
| `messages` | 消息内容 |

### RAG Service

| 表名 | 说明 |
|------|------|
| `documents` | 文档元数据 |
| `document_chunks` | 文档分块 (含向量) |

## 向量搜索

Schema 包含两个向量搜索函数:

### `search_documents`

纯向量相似度搜索:

```sql
SELECT * FROM search_documents(
    '[0.1, 0.2, ...]'::vector(384),  -- 查询向量
    'user-uuid',                       -- 用户 ID
    10                                 -- 返回数量
);
```

### `hybrid_search`

混合搜索 (向量 + 全文):

```sql
SELECT * FROM hybrid_search(
    '[0.1, 0.2, ...]'::vector(384),  -- 查询向量
    '搜索关键词',                      -- 文本查询
    'user-uuid',                       -- 用户 ID
    10,                                -- 返回数量
    0.5                                -- 向量权重 (0-1)
);
```

## 索引说明

### 向量索引

使用 IVFFlat 索引加速向量搜索:

```sql
CREATE INDEX idx_chunks_embedding ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**调优建议**:
- `lists` 参数建议设为 `sqrt(row_count)`
- 数据量 < 10万: `lists = 100`
- 数据量 10-100万: `lists = 300-1000`
- 查询时可设置 `probes` 参数提升召回率

### B-tree 索引

所有外键和常用查询字段都已创建 B-tree 索引。

## 安全配置

### Row Level Security (RLS)

Schema 中包含 RLS 策略示例 (已注释)。如需启用:

1. 取消注释相关 RLS 语句
2. 确保应用使用 Supabase Auth 或正确传递 JWT

### 密码存储

用户密码使用 bcrypt 加密存储，由应用层 (auth-service) 处理。

## 迁移注意事项

### 从 SQLite 迁移

1. SQLite 使用的 `String(36)` 需改为 `UUID`
2. SQLite 的 `JSON` 类型改为 PostgreSQL 的 `JSONB`
3. 日期时间使用 `TIMESTAMP WITH TIME ZONE`

### 从 Milvus 迁移

1. Milvus Collection 数据需要重新导入
2. 使用 `document_chunks` 表替代 Milvus
3. 向量维度保持 384 (all-MiniLM-L6-v2)

## 备份与恢复

### 备份

```bash
# 使用 pg_dump (需要 PostgreSQL 客户端)
pg_dump -h aws-0-[region].pooler.supabase.com \
        -p 6543 \
        -U postgres.[project-ref] \
        -d postgres \
        -F c -f backup.dump
```

### 恢复

```bash
pg_restore -h aws-0-[region].pooler.supabase.com \
           -p 6543 \
           -U postgres.[project-ref] \
           -d postgres \
           backup.dump
```

## 故障排除

### pgvector 扩展不存在

```sql
-- 检查扩展是否安装
SELECT * FROM pg_extension WHERE extname = 'vector';

-- 手动安装
CREATE EXTENSION vector;
```

### 向量维度不匹配

确保 embedding 模型输出维度与表定义一致 (384)。

### 连接超时

- 使用 Pooler 连接 (端口 6543)
- 检查 IP 白名单设置
