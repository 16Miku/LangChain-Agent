# ============================================================
# RAG Search Tool - 调用 rag-service 混合检索 API
# ============================================================

import os
import httpx
from typing import Optional, List
from langchain_core.tools import tool
from pydantic import BaseModel, Field


def get_rag_service_url() -> str:
    """获取 RAG Service URL，优先从 chat-service 配置获取"""
    # 首先尝试环境变量
    url = os.getenv("RAG_SERVICE_URL")
    if url:
        return url

    # 尝试从 chat-service 配置获取
    try:
        from app.config import settings
        return settings.RAG_SERVICE_URL
    except ImportError:
        pass

    # 默认值
    return "http://localhost:8004"


def get_internal_service_key() -> str:
    """获取内部服务密钥"""
    # 首先尝试环境变量
    key = os.getenv("INTERNAL_SERVICE_KEY")
    if key:
        return key

    # 尝试从 chat-service 配置获取
    try:
        from app.config import settings
        return settings.INTERNAL_SERVICE_KEY
    except ImportError:
        pass

    # 默认值
    return "internal-service-key-change-in-production"


def get_auth_headers() -> dict:
    """获取认证请求头"""
    return {
        "Authorization": f"Bearer {get_internal_service_key()}"
    }


def get_http_client(timeout: float = 15.0) -> httpx.AsyncClient:
    """
    获取 HTTP 客户端，禁用代理以访问本地服务

    Args:
        timeout: 请求超时时间

    Returns:
        配置好的 AsyncClient
    """
    # 禁用代理，避免本地服务请求走代理导致 502 错误
    return httpx.AsyncClient(
        timeout=timeout,
        proxy=None,  # 显式禁用代理
        trust_env=False  # 不读取环境变量中的代理设置
    )


class Citation(BaseModel):
    """引用信息"""
    chunk_id: str
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    content: str
    content_preview: Optional[str] = None
    score: float


class SearchResult(BaseModel):
    """搜索结果"""
    chunk_id: str
    document_id: str
    document_name: str
    content: str
    page_number: Optional[int] = None
    score: float
    vector_score: Optional[float] = None
    bm25_score: Optional[float] = None
    rerank_score: Optional[float] = None


@tool
async def rag_search(
    query: str,
    top_k: int = 10,
    rerank: bool = True,
) -> str:
    """
    从知识库中检索相关文档内容。使用混合检索（向量+BM25+重排序）获取最相关的结果。

    当用户询问与已上传文档相关的问题时，使用此工具检索相关内容。

    Args:
        query: 用户的问题或搜索查询
        top_k: 返回的结果数量，默认10条
        rerank: 是否使用重排序提升结果质量，默认True

    Returns:
        检索到的相关文档内容，包含引用来源信息
    """
    print(f"\n🔍 [RAG Search] 正在检索知识库: {query}")
    print(f"   参数: top_k={top_k}, rerank={rerank}")

    try:
        rag_url = get_rag_service_url()
        headers = get_auth_headers()
        async with get_http_client(timeout=30.0) as client:
            # 调用 rag-service 混合检索 API
            response = await client.post(
                f"{rag_url}/api/v1/search",
                headers=headers,
                json={
                    "query": query,
                    "top_k": top_k,
                    "alpha": 0.5,  # 向量和BM25权重各50%
                    "rerank": rerank,
                }
            )

            if response.status_code != 200:
                error_detail = response.text
                print(f"❌ [RAG Search] API错误: {response.status_code} - {error_detail}")
                return f"检索失败: {error_detail}"

            data = response.json()

            results = data.get("results", [])
            citations = data.get("citations", [])
            search_time = data.get("search_time_ms", 0)
            total = data.get("total", 0)

            print(f"✅ [RAG Search] 找到 {total} 条结果 (耗时 {search_time}ms)")

            if not results:
                return "未在知识库中找到相关内容。请确认已上传相关文档，或尝试用不同的关键词搜索。"

            # 格式化输出
            output_parts = [f"从知识库中检索到 {len(results)} 条相关内容:\n"]

            for i, result in enumerate(results, 1):
                doc_name = result.get("document_name", "未知文档")
                content = result.get("content", "")
                page_num = result.get("page_number")
                score = result.get("score", 0)

                # 构建引用标识
                page_info = f" (第{page_num}页)" if page_num else ""

                output_parts.append(f"---\n**[{i}] {doc_name}{page_info}** (相关度: {score:.2f})\n")
                output_parts.append(f"{content}\n")

            # 添加引用追溯信息
            if citations:
                output_parts.append("\n---\n**引用来源:**\n")
                for cit in citations[:5]:  # 最多显示5条引用
                    cit_doc = cit.get("document_name", "未知")
                    cit_page = cit.get("page_number")
                    cit_section = cit.get("section", "")
                    page_str = f"第{cit_page}页" if cit_page else ""
                    section_str = f" - {cit_section}" if cit_section else ""
                    output_parts.append(f"- {cit_doc} {page_str}{section_str}\n")

            return "".join(output_parts)

    except httpx.TimeoutException:
        print("❌ [RAG Search] 请求超时")
        return "检索请求超时，请稍后重试。"
    except httpx.ConnectError:
        print("❌ [RAG Search] 无法连接到 RAG 服务")
        return "无法连接到知识库服务，请确认服务已启动。"
    except Exception as e:
        print(f"❌ [RAG Search] 错误: {e}")
        return f"检索时发生错误: {str(e)}"


@tool
async def list_knowledge_documents() -> str:
    """
    列出知识库中已上传的所有文档。

    当用户询问"知识库有哪些文档"、"我上传了什么文件"等问题时使用此工具。

    Returns:
        知识库中的文档列表，包含文件名、大小、状态等信息
    """
    rag_url = get_rag_service_url()
    print(f"\n📚 [RAG] 正在获取知识库文档列表... (URL: {rag_url})")

    try:
        headers = get_auth_headers()
        print(f"   Headers: Authorization=Bearer ***")

        async with get_http_client(timeout=15.0) as client:
            full_url = f"{rag_url}/api/v1/documents"
            print(f"   Requesting: GET {full_url}")

            response = await client.get(
                full_url,
                headers=headers,
                params={"skip": 0, "limit": 50}
            )

            print(f"   Response status: {response.status_code}")

            if response.status_code != 200:
                error_text = response.text[:500] if response.text else "No error details"
                print(f"   Error: {error_text}")
                return f"获取文档列表失败 (HTTP {response.status_code}): {error_text}"

            data = response.json()
            documents = data.get("documents", [])
            total = data.get("total", 0)

            print(f"✅ [RAG] 获取到 {total} 个文档")

            if not documents:
                return "知识库中暂无文档。您可以在设置页面的「Knowledge」标签页上传文档。"

            # 格式化输出
            output_parts = [f"知识库中共有 {total} 个文档:\n\n"]

            for doc in documents:
                filename = doc.get("filename", "未知")
                file_size = doc.get("file_size", 0)
                chunk_count = doc.get("chunk_count", 0)
                status = doc.get("status", "unknown")

                # 格式化文件大小
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"

                # 状态映射
                status_map = {
                    "ready": "✅ 就绪",
                    "processing": "⏳ 处理中",
                    "error": "❌ 错误",
                    "pending": "⏸️ 等待中"
                }
                status_str = status_map.get(status, status)

                output_parts.append(f"- **{filename}** ({size_str}, {chunk_count}个分块) {status_str}\n")

            return "".join(output_parts)

    except httpx.TimeoutException as e:
        print(f"❌ [RAG] 超时: {e}")
        return "获取文档列表超时，请稍后重试。"
    except httpx.ConnectError as e:
        print(f"❌ [RAG] 连接失败: {e}")
        return f"无法连接到知识库服务 ({rag_url})，请确认 rag-service 已启动。"
    except Exception as e:
        print(f"❌ [RAG] 错误: {type(e).__name__}: {e}")
        return f"获取文档列表时发生错误: {str(e)}"
