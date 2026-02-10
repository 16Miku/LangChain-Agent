---
typora-copy-images-to: media
---


# My-Chat-LangChain



## My-Chat-LangChain 应用说明书 v1.0

[My-Chat-LangChain\Note\Note-V1.md](Note/Note-V1.md)



## My-Chat-LangChain 应用说明书 v2.0 (企业版)

[My-Chat-LangChain\Note\Note-V2.md](Note/Note-V2.md)


## My-Chat-LangChain 应用说明书 v3.0 (企业版)



[My-Chat-LangChain\Note\Note-V3.md](Note/Note-V3.md)




## My-Chat-LangChain 应用说明书 v4.0 (企业版)



[My-Chat-LangChain\Note\Note-V4.md](Note/Note-V4.md)


[CSDN文章：从0到1，构建你的专属AI知识库：My-Chat-LangChain项目深度解析](https://blog.csdn.net/m0_73479109/article/details/152751205?spm=1001.2014.3001.5501)

[稀土掘金文章：从0到1，构建你的专属AI知识库：My-Chat-LangChain项目深度解析](https://juejin.cn/post/7564230484126859303)






## My-Chat-LangChain 应用说明书 v5.0 (引入Agent)



[My-Chat-LangChain\Note\Note-V5.md](Note/Note-V5.md)







## My-Chat-LangChain 应用说明书 v6.0 (引入Agent)

[My-Chat-LangChain\Note\Plan-V6.md](Note/Plan-V6.md)

[My-Chat-LangChain\Note\Note-V6.md](Note/Note-V6.md)



## 在Render上部署

### 部署链接

*   https://my-chat-langchain.onrender.com/

[My-Chat-LangChain\Note\Deployment-Guide.md](Note/Deployment-Guide.md)



[render.yaml](../render.yaml)



[My-Chat-LangChain\Dockerfile](Dockerfile)



[My-Chat-LangChain\start.sh](start.sh)



[My-Chat-LangChain\requirements.txt](requirements.txt)







## My-Chat-LangChain 应用说明书 v7.0 (引入Agent)

[My-Chat-LangChain\Note\Note-V7.md](Note/Note-V7.md)


## Plan-V8: E2B 代码执行沙箱集成方案

[My-Chat-LangChain\Note\Plan-V8.md](Note/Plan-V8.md)



## # Stream-Agent V8.0 开发说明文档- 集成了 E2B 云沙箱


[My-Chat-LangChain\Note\Note-V8.md](Note/Note-V8.md)



## Plan-V9: 现代化前端重构与多模态增强

[Note\Plan-V9.md](Note/Plan-V9.md)

V9.0 是 My-Chat-LangChain 项目的重大升级版本，核心目标是：

1. **前端现代化**: 使用 Next.js + shadcn/ui 完全重构前端，替代 Streamlit
2. **多模态交互**: 支持图片理解/OCR 和语音交互
3. **RAG 能力增强**: 混合检索、引用追溯、重排序、MinerU 文档解析
4. **用户系统**: 传统账号认证 + JWT
5. **生产级部署**: Docker Compose 一键部署


## API 文档

### 在线文档

各服务启动后可访问 Swagger UI 和 ReDoc：

| 服务 | Swagger UI | ReDoc |
|------|------------|-------|
| Auth Service (8001) | http://localhost:8001/docs | http://localhost:8001/redoc |
| Chat Service (8002) | http://localhost:8002/docs | http://localhost:8002/redoc |
| RAG Service (8004) | http://localhost:8004/docs | http://localhost:8004/redoc |
| Presentation Service (8005) | http://localhost:8005/docs | http://localhost:8005/redoc |

### API 概览

#### Auth Service (端口 8001)
用户认证服务，提供注册、登录、令牌管理功能。

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/refresh` | POST | 刷新令牌 |
| `/api/auth/logout` | POST | 用户登出 |
| `/api/auth/me` | GET | 获取当前用户 |
| `/api/users/me` | GET/PUT | 用户资料管理 |
| `/api/users/me/password` | PUT | 修改密码 |

#### Chat Service (端口 8002)
聊天服务，提供 AI Agent 对话和会话管理。

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/chat/stream` | POST | 流式聊天 (SSE) |
| `/api/conversations` | GET/POST | 会话列表/创建 |
| `/api/conversations/{id}` | GET/PUT/DELETE | 会话详情/更新/删除 |
| `/api/conversations/{id}/messages` | GET | 获取消息列表 |

#### RAG Service (端口 8004)
检索增强生成服务，提供文档管理和混合检索。

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/documents` | GET | 文档列表 |
| `/api/v1/documents/{id}` | GET/DELETE | 文档详情/删除 |
| `/api/v1/ingest/upload` | POST | 上传文档 |
| `/api/v1/ingest/text` | POST | 摄取文本 |
| `/api/v1/search` | POST | 混合检索 |
| `/api/v1/search/vector` | POST | 向量检索 |
| `/api/v1/search/bm25` | POST | BM25 检索 |
| `/api/v1/search/citations` | POST/GET | 引用追溯 |

#### Presentation Service (端口 8005)
演示文稿服务，提供 AI 生成 PPT 和编辑功能。

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/presentations` | GET/POST | 演示文稿列表/创建 |
| `/api/v1/presentations/{id}` | GET/PUT/DELETE | 详情/更新/删除 |
| `/api/v1/presentations/{id}/export/html` | GET | 导出 HTML |
| `/api/v1/editor/generate` | POST | AI 生成 PPT |
| `/api/v1/editor/themes` | GET | 主题列表 |
| `/api/v1/editor/layouts` | GET | 布局列表 |
| `/api/v1/assistant/{id}/chat` | POST | AI 助手对话 |

### 错误码文档

详细的错误码说明请参考: [docs/API_ERROR_CODES.md](docs/API_ERROR_CODES.md)

### OpenAPI 导出

运行以下命令导出 OpenAPI 文档：

```bash
python scripts/export_openapi.py
```

导出文件位于 `docs/openapi/` 目录。


# ## Plan-V10:

[Note\Plan-V10.md](Note/Plan-V10.md)


[tNote\V10-Manual-Test-Guide.mdt](Note/V10-Manual-Test-Guide.md)







## 面试备战文档

[Interview\面试备战文档.md](Interview/面试备战文档.md)

**Agentic RAG 平台** | 个人项目 | 2025-06 ~ 2025-09

**项目描述**:
一个面向研究人员的 AI 助理平台，集成了多工具 Agent、知识库检索、代码执行、多模态交互等功能，帮助用户进行文献调研、数据分析、代码编写等研究工作。

**核心职责**:
- 设计并实现微服务架构，将系统拆分为认证、聊天、RAG、语音四个独立服务
- 基于 LangGraph 实现 ReAct Agent，支持 96+ 工具的动态调用和流式响应
- 设计 RAG 混合检索方案，融合向量检索（pgvector）、关键词检索（BM25）和 Reranker 重排序
- 实现 SSE 流式传输，支持工具调用可视化、代码高亮、图表渲染等实时反馈
- 集成 E2B 云沙箱，实现安全隔离的 Python 代码执行和数据可视化
- 开发语音交互模块，集成 faster-whisper 语音识别和 Edge TTS 语音合成

**技术亮点**:
- 采用 RRF（Reciprocal Rank Fusion）算法融合多路检索结果，提升检索准确率
- 实现智能分块策略（语义感知/页面感知/递归分块），优化长文档处理
- 设计引用追溯机制，支持 RAG 结果的来源定位和原文高亮
- 使用 MCP（Model Context Protocol）协议集成 90+ 外部工具








