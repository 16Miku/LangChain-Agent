#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务健康检查脚本

快速检查所有微服务是否正常运行。

使用方法:
    python tests/health_check.py

    # 指定服务地址
    AUTH_URL=http://localhost:8001 python tests/health_check.py
"""

import os
import sys
import httpx

# 服务配置
# 注意: Windows 上 uvicorn 默认绑定 127.0.0.1，使用 localhost 可能导致连接问题
SERVICES = {
    "Auth Service": {
        "url": os.getenv("AUTH_URL", "http://127.0.0.1:8001"),
        "health_endpoint": "/health",
        "port": 8001,
    },
    "Chat Service": {
        "url": os.getenv("CHAT_URL", "http://127.0.0.1:8002"),
        "health_endpoint": "/health",
        "port": 8002,
    },
    "Whisper Service": {
        "url": os.getenv("WHISPER_URL", "http://127.0.0.1:8003"),
        "health_endpoint": "/api/v1/voice/health",
        "port": 8003,
        "optional": True,  # 可选服务
    },
    "RAG Service": {
        "url": os.getenv("RAG_URL", "http://127.0.0.1:8004"),
        "health_endpoint": "/health",
        "port": 8004,
    },
}

# 禁用代理 (避免 Clash 等代理软件干扰本地请求)
NO_PROXY_TRANSPORT = httpx.HTTPTransport(proxy=None)


def check_service(name: str, config: dict) -> bool:
    """检查单个服务健康状态"""
    url = f"{config['url']}{config['health_endpoint']}"
    optional = config.get("optional", False)

    try:
        with httpx.Client(timeout=5.0, transport=NO_PROXY_TRANSPORT) as client:
            response = client.get(url)

            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                print(f"  ✅ {name}: 正常 (status={status})")
                return True
            else:
                print(f"  ❌ {name}: 异常 (HTTP {response.status_code})")
                return False

    except httpx.ConnectError:
        if optional:
            print(f"  ⚠️  {name}: 未启动 (可选服务)")
            return True  # 可选服务未启动不算失败
        else:
            print(f"  ❌ {name}: 无法连接 (端口 {config['port']})")
            return False

    except Exception as e:
        print(f"  ❌ {name}: 错误 ({e})")
        return False


def main():
    """运行健康检查"""
    print("=" * 50)
    print("My-Chat-LangChain V9.0 服务健康检查")
    print("=" * 50)
    print()

    all_healthy = True
    required_healthy = True

    for name, config in SERVICES.items():
        healthy = check_service(name, config)
        if not healthy:
            all_healthy = False
            if not config.get("optional", False):
                required_healthy = False

    print()
    print("=" * 50)

    if all_healthy:
        print("✅ 所有服务运行正常！")
        return 0
    elif required_healthy:
        print("⚠️  必需服务正常，部分可选服务未启动")
        return 0
    else:
        print("❌ 部分必需服务异常，请检查！")
        print()
        print("启动服务命令:")
        print("  # Auth Service")
        print("  cd backend/auth-service && uvicorn app.main:app --port 8001 --reload")
        print()
        print("  # Chat Service")
        print("  cd backend/chat-service && uvicorn app.main:app --port 8002 --reload")
        print()
        print("  # RAG Service")
        print("  cd backend/rag-service && uvicorn app.main:app --port 8004 --reload")
        print()
        print("  # Whisper Service (可选)")
        print("  cd backend/whisper-service && uvicorn app.main:app --port 8003 --reload")
        return 1


if __name__ == "__main__":
    sys.exit(main())
