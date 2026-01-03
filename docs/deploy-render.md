# Render 部署指南

## 概述

本指南说明如何将 My-Chat-LangChain V9.0 部署到 Render + Supabase 云平台。

## 架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Render (计算层)                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ frontend    │ │ auth        │ │ chat        │ │ rag         │   │
│  │ (Next.js)   │ │ service     │ │ service     │ │ service     │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
│         │               │               │               │           │
│         └───────────────┴───────────────┴───────────────┘           │
│                                 │                                    │
│                                 ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Supabase (数据层)                                │   │
│  │  PostgreSQL + pgvector │ Storage (可选)                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## 部署步骤

### 1. 准备 Supabase 数据库

1. **创建项目**
   - 访问 [Supabase](https://supabase.com)
   - 点击 "New Project"
   - 选择区域 (推荐 Southeast Asia)
   - 设置数据库密码并保存

2. **执行数据库 Schema**
   - 进入 SQL Editor
   - 复制 `database/supabase_schema.sql` 内容
   - 点击 Run 执行

3. **获取连接信息**
   - Settings → Database → Connection string
   - 复制 URI 格式连接字符串

### 2. 部署到 Render

#### 方式 A: Blueprint 自动部署 (推荐)

1. 将代码推送到 GitHub
2. 在 Render Dashboard 点击 "New Blueprint"
3. 选择仓库并授权
4. Render 自动检测 `render.yaml` 并创建服务
5. 手动填写 `sync: false` 的环境变量

#### 方式 B: 手动创建服务

对每个服务:

1. New → Web Service
2. 选择仓库
3. 配置如下:

| 服务 | Root Directory | Build Command | Start Command |
|------|----------------|---------------|---------------|
| frontend-next | `frontend-next` | `npm install && npm run build` | `npm start` |
| auth-service | `backend/auth-service` | `pip install -r requirements.txt` | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| chat-service | `backend/chat-service` | 同上 | 同上 |
| rag-service | `backend/rag-service` | 同上 | 同上 |

### 3. 配置环境变量

在 Render Dashboard 中为每个服务配置:

#### auth-service
```
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
JWT_SECRET=<自动生成或手动设置>
JWT_ALGORITHM=HS256
```

#### chat-service
```
DATABASE_URL=<同上>
JWT_SECRET=<与 auth-service 相同>
AUTH_SERVICE_URL=https://auth-service-xxx.onrender.com
RAG_SERVICE_URL=https://rag-service-xxx.onrender.com
GOOGLE_API_KEY=<你的 API Key>
E2B_API_KEY=<你的 API Key>
BRIGHT_DATA_API_KEY=<你的 API Key>
```

#### rag-service
```
DATABASE_URL=<同上>
JWT_SECRET=<与 auth-service 相同>
JWT_ENABLED=true
VECTOR_STORE_BACKEND=pgvector
PGVECTOR_ENABLED=true
```

#### frontend-next
```
NEXT_PUBLIC_API_URL=https://chat-service-xxx.onrender.com
```

### 4. 验证部署

1. 访问各服务的 `/health` 端点
2. 访问前端页面测试注册/登录
3. 测试聊天和 RAG 功能

## 成本估算

| 服务 | 计划 | 月费 |
|------|------|------|
| Supabase | Free/Pro | $0 / $25 |
| frontend-next | Starter | $7 |
| auth-service | Starter | $7 |
| chat-service | Standard | $25 |
| rag-service | Standard | $25 |
| **总计** | | **$64-89/月** |

## 常见问题

### Q: 服务启动失败

检查:
- 环境变量是否正确设置
- DATABASE_URL 格式是否正确
- 依赖是否完整安装

### Q: 数据库连接超时

使用 Pooler 连接 (端口 6543):
```
postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

### Q: 向量搜索失败

确保:
- pgvector 扩展已启用
- document_chunks 表存在
- embedding 维度正确 (384)

### Q: 前端无法连接后端

检查:
- NEXT_PUBLIC_API_URL 是否正确
- CORS 配置是否允许前端域名
- 服务是否已启动

## 监控与日志

- Render Dashboard 提供实时日志
- 使用 `/health` 端点监控服务状态
- Supabase Dashboard 可查看数据库状态

## 扩展

如需扩展:
1. 升级 Render 计划
2. 增加 Supabase 连接数
3. 考虑添加 Redis 缓存 (Render Redis)
