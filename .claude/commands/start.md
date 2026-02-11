启动所有后端服务（生成命令供用户执行）：

请在 4 个终端窗口中分别执行：

**终端 1 - Auth 服务：**
```bash
cd A:\study\AI\LLM\LangChain-Agent
.\.venv\Scripts\Activate.ps1
cd backend/auth-service
uvicorn app.main:app --port 8001 --reload
```

**终端 2 - Chat 服务：**
```bash
cd A:\study\AI\LLM\LangChain-Agent
.\.venv\Scripts\Activate.ps1
cd backend/chat-service
uvicorn app.main:app --port 8002 --reload
```

**终端 3 - RAG 服务：**
```bash
cd A:\study\AI\LLM\LangChain-Agent
.\.venv\Scripts\Activate.ps1
cd backend/rag-service
uvicorn app.main:app --port 8004 --reload
```

**终端 4 - 前端：**
```bash
cd A:\study\AI\LLM\LangChain-Agent\frontend-next
npm run dev
```

启动后访问：
- 前端: http://localhost:3000
- API 文档: http://localhost:8001/docs (Auth)
- API 文档: http://localhost:8002/docs (Chat)
- API 文档: http://localhost:8004/docs (RAG)
