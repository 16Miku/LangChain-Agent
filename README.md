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








