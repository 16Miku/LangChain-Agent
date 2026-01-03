#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
端到端测试脚本 - My-Chat-LangChain V9.0

测试所有微服务的集成功能:
- Auth Service: 用户注册/登录/Token刷新
- Chat Service: 会话创建/消息发送/流式响应
- RAG Service: 文档上传/向量检索

使用方法:
    1. 启动所有服务 (auth: 8001, chat: 8002, rag: 8004)
    2. 运行测试:
       python -m pytest tests/test_e2e.py -v --tb=short

前置条件:
    - 所有服务已启动
    - 数据库已初始化
    - 环境变量已配置
"""

import os
import sys
import time
import uuid
import pytest
import httpx

# 服务地址配置
# 注意: Windows 上 uvicorn 默认绑定 127.0.0.1，使用 localhost 可能导致 502 错误
AUTH_URL = os.getenv("AUTH_URL", "http://127.0.0.1:8001")
CHAT_URL = os.getenv("CHAT_URL", "http://127.0.0.1:8002")
RAG_URL = os.getenv("RAG_URL", "http://127.0.0.1:8004")

# 测试超时时间 (秒)
TIMEOUT = 30.0

# 禁用代理 (避免 Clash 等代理软件干扰本地请求)
# httpx 会读取 HTTP_PROXY/HTTPS_PROXY 环境变量，需要显式禁用
NO_PROXY_TRANSPORT = httpx.HTTPTransport(proxy=None)


class TestE2EServices:
    """端到端集成测试"""

    # 测试用户凭据 (每次测试使用唯一用户名)
    test_username = f"testuser_{uuid.uuid4().hex[:8]}"
    test_email = f"{test_username}@test.com"
    test_password = "TestPass123!"

    # Token 存储
    access_token: str = None
    refresh_token: str = None
    user_id: str = None
    conversation_id: str = None

    # ============================================================
    # 健康检查测试
    # ============================================================

    def test_01_auth_health(self):
        """测试 Auth Service 健康状态"""
        with httpx.Client(timeout=TIMEOUT, transport=NO_PROXY_TRANSPORT) as client:
            response = client.get(f"{AUTH_URL}/health")
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
            print(f"✅ Auth Service 健康: {data}")

    def test_02_chat_health(self):
        """测试 Chat Service 健康状态"""
        with httpx.Client(timeout=TIMEOUT, transport=NO_PROXY_TRANSPORT) as client:
            response = client.get(f"{CHAT_URL}/health")
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
            print(f"✅ Chat Service 健康: {data}")

    def test_03_rag_health(self):
        """测试 RAG Service 健康状态"""
        with httpx.Client(timeout=TIMEOUT, transport=NO_PROXY_TRANSPORT) as client:
            response = client.get(f"{RAG_URL}/health")
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
            print(f"✅ RAG Service 健康: {data}")

    # ============================================================
    # Auth Service 测试
    # ============================================================

    def test_10_user_register(self):
        """测试用户注册"""
        with httpx.Client(timeout=TIMEOUT, transport=NO_PROXY_TRANSPORT) as client:
            response = client.post(
                f"{AUTH_URL}/api/auth/register",
                json={
                    "username": self.test_username,
                    "email": self.test_email,
                    "password": self.test_password
                }
            )
            assert response.status_code in [200, 201], f"注册失败: {response.text}"
            data = response.json()
            assert "id" in data or "user_id" in data
            TestE2EServices.user_id = data.get("id") or data.get("user_id")
            print(f"✅ 用户注册成功: {self.test_username}")

    def test_11_user_login(self):
        """测试用户登录"""
        with httpx.Client(timeout=TIMEOUT, transport=NO_PROXY_TRANSPORT) as client:
            response = client.post(
                f"{AUTH_URL}/api/auth/login",
                json={
                    "email": self.test_email,
                    "password": self.test_password
                }
            )
            assert response.status_code == 200, f"登录失败: {response.text}"
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            TestE2EServices.access_token = data["access_token"]
            TestE2EServices.refresh_token = data["refresh_token"]
            print(f"✅ 用户登录成功，获取 Token")

    def test_12_get_current_user(self):
        """测试获取当前用户信息"""
        with httpx.Client(timeout=TIMEOUT, transport=NO_PROXY_TRANSPORT) as client:
            response = client.get(
                f"{AUTH_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            assert response.status_code == 200, f"获取用户失败: {response.text}"
            data = response.json()
            assert data.get("username") == self.test_username
            print(f"✅ 获取用户信息成功: {data.get('username')}")

    def test_13_token_refresh(self):
        """测试 Token 刷新"""
        with httpx.Client(timeout=TIMEOUT, transport=NO_PROXY_TRANSPORT) as client:
            response = client.post(
                f"{AUTH_URL}/api/auth/refresh",
                json={"refresh_token": self.refresh_token}
            )
            assert response.status_code == 200, f"Token刷新失败: {response.text}"
            data = response.json()
            assert "access_token" in data
            TestE2EServices.access_token = data["access_token"]
            if "refresh_token" in data:
                TestE2EServices.refresh_token = data["refresh_token"]
            print(f"✅ Token 刷新成功")

    # ============================================================
    # Chat Service 测试
    # ============================================================

    def test_20_create_conversation(self):
        """测试创建会话"""
        with httpx.Client(timeout=TIMEOUT, transport=NO_PROXY_TRANSPORT) as client:
            response = client.post(
                f"{CHAT_URL}/api/conversations",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={"title": "E2E Test Conversation"}
            )
            assert response.status_code in [200, 201], f"创建会话失败: {response.text}"
            data = response.json()
            assert "id" in data
            TestE2EServices.conversation_id = data["id"]
            print(f"✅ 创建会话成功: {data['id']}")

    def test_21_list_conversations(self):
        """测试获取会话列表"""
        with httpx.Client(timeout=TIMEOUT, transport=NO_PROXY_TRANSPORT) as client:
            response = client.get(
                f"{CHAT_URL}/api/conversations",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            assert response.status_code == 200, f"获取会话列表失败: {response.text}"
            data = response.json()
            assert isinstance(data, list) or "conversations" in data
            print(f"✅ 获取会话列表成功")

    def test_22_get_conversation(self):
        """测试获取单个会话"""
        with httpx.Client(timeout=TIMEOUT, transport=NO_PROXY_TRANSPORT) as client:
            response = client.get(
                f"{CHAT_URL}/api/conversations/{self.conversation_id}",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            assert response.status_code == 200, f"获取会话失败: {response.text}"
            data = response.json()
            assert data.get("id") == self.conversation_id
            print(f"✅ 获取会话详情成功")

    # ============================================================
    # RAG Service 测试
    # ============================================================

    def test_30_rag_list_documents(self):
        """测试获取文档列表"""
        with httpx.Client(timeout=TIMEOUT, transport=NO_PROXY_TRANSPORT) as client:
            response = client.get(
                f"{RAG_URL}/api/v1/documents",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            assert response.status_code == 200, f"获取文档列表失败: {response.text}"
            print(f"✅ 获取文档列表成功")

    def test_31_rag_search(self):
        """测试向量搜索 (无文档时应返回空结果)"""
        with httpx.Client(timeout=TIMEOUT, transport=NO_PROXY_TRANSPORT) as client:
            response = client.post(
                f"{RAG_URL}/api/v1/search",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={
                    "query": "测试查询",
                    "top_k": 5
                }
            )
            assert response.status_code == 200, f"搜索失败: {response.text}"
            data = response.json()
            assert "results" in data or isinstance(data, list)
            print(f"✅ 向量搜索成功 (返回 {len(data.get('results', data))} 条结果)")

    # ============================================================
    # 清理测试
    # ============================================================

    def test_90_delete_conversation(self):
        """测试删除会话"""
        if not self.conversation_id:
            pytest.skip("无会话可删除")

        with httpx.Client(timeout=TIMEOUT, transport=NO_PROXY_TRANSPORT) as client:
            response = client.delete(
                f"{CHAT_URL}/api/conversations/{self.conversation_id}",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            assert response.status_code in [200, 204], f"删除会话失败: {response.text}"
            print(f"✅ 删除会话成功")

    def test_91_user_logout(self):
        """测试用户登出"""
        with httpx.Client(timeout=TIMEOUT, transport=NO_PROXY_TRANSPORT) as client:
            response = client.post(
                f"{AUTH_URL}/api/auth/logout",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={"refresh_token": self.refresh_token}
            )
            # 登出可能返回 200 或 204
            assert response.status_code in [200, 204], f"登出失败: {response.text}"
            print(f"✅ 用户登出成功")


# ============================================================
# 独立运行支持
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("My-Chat-LangChain V9.0 端到端测试")
    print("=" * 60)
    print(f"Auth URL: {AUTH_URL}")
    print(f"Chat URL: {CHAT_URL}")
    print(f"RAG URL: {RAG_URL}")
    print("=" * 60)

    # 运行 pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
