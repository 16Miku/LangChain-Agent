# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

My-Chat-LangChain (Stream-Agent) 是一个全栈 AI 研究助理应用，基于 LangChain + LangGraph 构建，支持多工具 Agent、网络搜索、RAG 知识库、E2B 云沙箱代码执行等功能。

## 开发命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动后端 (端口 8000)
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端 (端口 8501)
cd frontend && streamlit run app.py

# 一键启动 (同时启动前后端)
./start.sh

# Docker 构建和运行
docker build -t stream-agent .
docker run -p 8501:8501 -e GOOGLE_API_KEY=your_key stream-agent
```

## 架构设计

```
Frontend (Streamlit)          →  HTTP/SSE  →  Backend (FastAPI)
frontend/app.py                              backend/main.py
                                                    │
                                                    ▼
                                          Agent Service (LangGraph)
                                          backend/agent_service.py
                                                    │
                        ┌───────────────────────────┼───────────────────────────┐
                        ▼                           ▼                           ▼
                  MCP Tools                   Custom Tools                 E2B Tools
                  (90+ 网络/搜索工具)          (RAG 知识库)                (代码执行)
```

## 核心模块

| 文件 | 职责 |
|------|------|
| `backend/main.py` | FastAPI 路由、CORS、文件上传处理 |
| `backend/agent_service.py` | LangGraph ReAct Agent 核心、流式响应、工具加载 |
| `backend/langchain_qa_backend.py` | ChromaDB 向量存储、文档摄取、RAG 检索链 |
| `backend/tools/e2b_tools.py` | E2B 云沙箱 Python 代码执行 (V8 新增) |
| `backend/tools/rag_tools.py` | 知识摄取/查询工具 |
| `backend/tools/search_tools.py` | 搜索策略生成、Serper API |
| `backend/tools/structure_tools.py` | 论文分析、LinkedIn 格式化输出 |
| `frontend/app.py` | Streamlit UI、流式渲染、图表显示 |

## API 端点

- `GET /` - 健康检查
- `POST /chat/stream` - 流式聊天 (SSE)，主要端点
- `POST /chat_agent` - 同步聊天 (备用)
- `POST /upload_file` - 文件上传 + 自动 RAG 摄取

## 环境变量配置

在 `backend/.env` 中配置：
```
GOOGLE_API_KEY=xxx          # 必需 (Gemini)
E2B_API_KEY=xxx             # E2B 代码执行
BRIGHT_DATA_API_KEY=xxx     # BrightData MCP 工具
PAPER_SEARCH_API_KEY=xxx    # 论文搜索
SERPER_API_KEY=xxx          # 搜索 API
```

## 工具系统

项目包含 96+ 工具，分为三类：
1. **MCP 工具** (~90): 通过 langchain-mcp-adapters 加载，包括网络搜索、电商数据、社交媒体、学术论文等
2. **自定义工具** (4): RAG 摄取/查询、论文格式化、LinkedIn 格式化
3. **E2B 工具** (6): execute_python_code, analyze_csv_data, install_python_package 等

## 技术栈要点

- **后端**: FastAPI + Uvicorn + Pydantic
- **Agent**: LangGraph (create_react_agent) + AsyncSqliteSaver 持久化
- **向量数据库**: ChromaDB + HuggingFace Embedding (all-MiniLM-L6-v2)
- **LLM**: Google Gemini / OpenAI 兼容模式
- **前端**: Streamlit
- **部署**: Render (Docker) / Vercel (Serverless)

## 开发注意事项

- 前端启动时会自动加载 `backend/.env` 文件
- Agent 使用 SQLite 持久化对话历史 (`chat_history.db`)
- 流式响应使用 Server-Sent Events (SSE)
- E2B 沙箱会话默认保持 5 分钟，可通过后续调用延长