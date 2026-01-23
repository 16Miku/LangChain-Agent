# 项目上下文记忆

## 项目概述
- **名称**: My-Chat-LangChain (Stream-Agent)
- **类型**: 全栈 AI 研究助理应用
- **当前版本**: V9.0 (开发中)
- **目标版本**: V10.0

## 技术栈
- **前端**: Next.js 14 + shadcn/ui + Tailwind CSS + Zustand
- **后端**: FastAPI 微服务架构
- **Agent**: LangGraph + LangChain + MCP Adapters
- **数据库**: PostgreSQL + pgvector / SQLite (测试)
- **LLM**: Google Gemini / OpenAI 兼容

## 微服务架构
| 服务 | 端口 | 职责 |
|------|------|------|
| frontend-next | 3000 | Next.js 前端 |
| auth-service | 8001 | 用户认证 (JWT) |
| chat-service | 8002 | 聊天核心 (LangGraph Agent) |
| whisper-service | 8003 | 语音识别 |
| rag-service | 8004 | RAG 检索 |
| presentation-service | 8005 | 演示文稿生成 |

## V9 已完成功能
1. Next.js 前端重构 (Phase 1)
2. 用户认证系统 (Phase 1)
3. 多模态交互 - 图片/语音 (Phase 2)
4. RAG 增强 - 混合检索/引用追溯 (Phase 3)
5. AI 生成 PPT (Phase 5)

## V9 待优化问题
1. PPTX 导出美学质量不达标 (2/10 评分)
2. 缺乏视觉反馈机制
3. 部署流程未完善
