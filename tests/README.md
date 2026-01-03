# 测试指南

## 概述

本目录包含 My-Chat-LangChain V9.0 的测试脚本。

## 测试类型

| 测试 | 文件 | 说明 |
|------|------|------|
| 健康检查 | `health_check.py` | 快速检查所有服务状态 |
| 端到端测试 | `test_e2e.py` | 完整的集成测试 |
| 单元测试 | `backend/*/tests/` | 各服务的单元测试 |

## 快速开始

### 1. 健康检查

检查所有服务是否正常运行：

```bash
cd LangChain-Agent

# 使用 Python 完整路径
A:/Anaconda/envs/My-Chat-LangChain/python.exe tests/health_check.py

# 或激活 conda 环境后
conda activate My-Chat-LangChain
python tests/health_check.py
```

### 2. 端到端测试

运行完整的集成测试：

```bash
# 先启动所有服务
# 终端 1: Auth Service
cd backend/auth-service && uvicorn app.main:app --port 8001 --reload

# 终端 2: Chat Service
cd backend/chat-service && uvicorn app.main:app --port 8002 --reload

# 终端 3: RAG Service
cd backend/rag-service && uvicorn app.main:app --port 8004 --reload

# 终端 4: 运行测试
A:/Anaconda/envs/My-Chat-LangChain/python.exe -m pytest tests/test_e2e.py -v
```

### 3. RAG 单元测试

```bash
cd backend/rag-service
A:/Anaconda/envs/My-Chat-LangChain/python.exe -m pytest tests/ -v --tb=short
```

## 测试内容

### 端到端测试 (test_e2e.py)

| 测试 | 说明 |
|------|------|
| `test_01_auth_health` | Auth 服务健康检查 |
| `test_02_chat_health` | Chat 服务健康检查 |
| `test_03_rag_health` | RAG 服务健康检查 |
| `test_10_user_register` | 用户注册 |
| `test_11_user_login` | 用户登录 |
| `test_12_get_current_user` | 获取当前用户 |
| `test_13_token_refresh` | Token 刷新 |
| `test_20_create_conversation` | 创建会话 |
| `test_21_list_conversations` | 获取会话列表 |
| `test_22_get_conversation` | 获取会话详情 |
| `test_30_rag_list_documents` | 获取文档列表 |
| `test_31_rag_search` | 向量搜索 |
| `test_90_delete_conversation` | 删除会话 |
| `test_91_user_logout` | 用户登出 |

## 环境变量

测试脚本支持通过环境变量配置服务地址：

```bash
# 默认值
AUTH_URL=http://localhost:8001
CHAT_URL=http://localhost:8002
RAG_URL=http://localhost:8004
WHISPER_URL=http://localhost:8003

# 自定义
AUTH_URL=http://api.example.com:8001 python tests/test_e2e.py
```

## 依赖

测试脚本需要以下依赖：

```bash
pip install pytest httpx
```

这些依赖已包含在各服务的 `requirements.txt` 中。

## 故障排除

### 服务无法连接

1. 确认服务已启动
2. 检查端口是否被占用
3. 检查防火墙设置

### Token 验证失败

1. 确认 JWT_SECRET 在所有服务中一致
2. 检查 Token 是否过期

### 数据库错误

1. 确认 DATABASE_URL 配置正确
2. 检查数据库连接
3. 确认表结构已创建
