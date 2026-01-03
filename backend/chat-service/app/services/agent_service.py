# ============================================================
# Chat Service - Agent Service
# Integrated from backend/agent_service.py with user isolation
# ============================================================

import os
import asyncio
import aiosqlite
import base64
import json
import re
from typing import Dict, Any, List, Optional, AsyncGenerator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.config import settings

import logging

logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("root").setLevel(logging.ERROR)


# Global variables
_agent_executors: Dict[str, Any] = {}  # Per-user agent executors
_mcp_client = None
_mcp_tools = []
_sqlite_conn = None

# Persistence Config
DATA_DIR = settings.DATA_DIR
DB_PATH = os.path.join(DATA_DIR, "state.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

SYSTEM_PROMPT = """
# Stream-Agent v9.0 - AI Research Assistant

You are an AI research assistant equipped with powerful tools for web search, data scraping, academic research, social media analysis, e-commerce data extraction, code execution, and knowledge base retrieval.

## Core Capabilities

1. **Web Search & Scraping**: search_engine, scrape_as_markdown, scrape_as_html
2. **E-commerce Data**: Amazon, Walmart, eBay, Etsy product data
3. **Social Media**: LinkedIn, Instagram, Facebook, TikTok, X/Twitter, YouTube, Reddit
4. **Academic Research**: arXiv, PubMed, Google Scholar
5. **Knowledge Base (RAG)**: rag_search, list_knowledge_documents - 混合检索用户上传的文档
6. **Code Execution (E2B)**: execute_python_code, analyze_csv_data, etc.

## Guidelines

1. Always use appropriate tools based on user intent
2. For data analysis with charts, always use plt.show() at the end
3. Don't output raw base64 data in responses
4. Provide structured, well-organized responses
5. Use Chinese when the user communicates in Chinese
6. **重要**: 当用户询问关于已上传文档的问题时，优先使用 rag_search 工具检索知识库

## RAG Knowledge Base Usage (重要)

When using rag_search tool:
1. **必须使用检索结果**: 当 rag_search 返回相关内容时，你必须基于这些内容来回答问题，而不是说"无法获取"
2. **综合多条结果**: 检索会返回多条相关片段，请综合这些内容给出完整答案
3. **引用来源**: 在回答中提及内容来自哪个文档或页码
4. **忽略标记**: 检索结果末尾可能包含 [RAG_CITATIONS] 标记，这是系统内部使用的，请忽略
5. **内容相关性**: 即使检索内容不完全匹配问题，也要尽力从中提取有用信息

## E2B Code Execution Notes

When using E2B sandbox for code execution:
1. The default working directory is `/home/user`
2. Before saving files to subdirectories, create them first with `os.makedirs('path', exist_ok=True)`
3. For HTML/text content generation, prefer returning the content directly in the response rather than saving to files
4. If you must save files, use `/home/user/filename.ext` directly or create the directory first
5. Common pre-installed packages: numpy, pandas, matplotlib, requests, beautifulsoup4
6. Use `install_python_package` tool to install additional packages if needed

## Code Formatting Rules (IMPORTANT)

When writing Python code for execute_python_code tool:
1. Use regular triple quotes (''' or \"\"\") for multi-line strings - DO NOT escape them
2. For HTML content, use string concatenation or f-strings instead of triple-quoted strings if possible
3. Example for HTML generation:
   ```python
   html = "<!DOCTYPE html>\\n"
   html += "<html><head><title>Title</title></head>\\n"
   html += "<body><h1>Content</h1></body></html>"
   print(html)
   ```
4. Or use a list and join:
   ```python
   lines = [
       "<!DOCTYPE html>",
       "<html><head><title>Title</title></head>",
       "<body><h1>Content</h1></body></html>"
   ]
   html = "\\n".join(lines)
   print(html)
   ```
"""


async def get_tools(api_keys: Dict[str, str] = None) -> List:
    """Load MCP tools and custom tools."""
    global _mcp_client, _mcp_tools

    # Import tools dynamically - tools are in backend/ directory
    import sys
    # Path: chat-service/app/services/agent_service.py -> backend/
    backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)

    try:
        from tools.rag_search_tool import rag_search, list_knowledge_documents
        from tools.structure_tools import format_paper_analysis, format_linkedin_profile
        from tools.e2b_tools import (
            execute_python_code,
            execute_shell_command,
            install_python_package,
            upload_data_to_sandbox,
            download_file_from_sandbox,
            analyze_csv_data,
            generate_presentation,
        )

        custom_tools = [
            rag_search,
            list_knowledge_documents,
            format_paper_analysis,
            format_linkedin_profile,
            execute_python_code,
            execute_shell_command,
            install_python_package,
            upload_data_to_sandbox,
            download_file_from_sandbox,
            analyze_csv_data,
            generate_presentation,
        ]
    except ImportError as e:
        print(f"Warning: Could not import some tools: {e}")
        custom_tools = []

    # Configure MCP servers
    mcp_servers = {}
    bd_key = (api_keys or {}).get("BRIGHT_DATA_API_KEY") or settings.BRIGHT_DATA_API_KEY
    if bd_key:
        mcp_servers["bright_data"] = {
            "url": f"https://mcp.brightdata.com/mcp?token={bd_key}&pro=1",
            "transport": "streamable_http",
        }

    ps_key = (api_keys or {}).get("PAPER_SEARCH_API_KEY") or settings.PAPER_SEARCH_API_KEY
    if ps_key:
        mcp_servers["paper_search"] = {
            "url": f"https://server.smithery.ai/@adamamer20/paper-search-mcp-openai/mcp?api_key={ps_key}",
            "transport": "streamable_http",
        }

    if mcp_servers and _mcp_client is None:
        try:
            _mcp_client = MultiServerMCPClient(mcp_servers)
            _mcp_tools = await _mcp_client.get_tools()
            print(f"Loaded {len(_mcp_tools)} MCP tools.")
        except Exception as e:
            print(f"Warning: Failed to load MCP tools: {e}")
            _mcp_tools = []

    return _mcp_tools + custom_tools


async def initialize_agent(
    user_id: str, api_keys: Dict[str, str] = None
) -> Any:
    """
    Initialize or get the LangGraph agent for a specific user.

    Args:
        user_id: User ID for isolation
        api_keys: Optional API keys override

    Returns:
        Agent executor
    """
    global _agent_executors, _sqlite_conn

    # Check if agent already exists for this user
    if user_id in _agent_executors:
        return _agent_executors[user_id]

    print(f"Initializing agent for user {user_id}...")

    # Load tools
    all_tools = await get_tools(api_keys)

    # Configure LLM
    llm_provider = (api_keys or {}).get("LLM_PROVIDER") or settings.LLM_PROVIDER

    if llm_provider == "openai_compatible":
        openai_base_url = (api_keys or {}).get("OPENAI_BASE_URL") or settings.OPENAI_BASE_URL
        openai_api_key = (api_keys or {}).get("OPENAI_API_KEY") or settings.OPENAI_API_KEY
        openai_model = (api_keys or {}).get("OPENAI_MODEL") or settings.OPENAI_MODEL

        if not openai_base_url or not openai_api_key:
            raise ValueError("OpenAI Compatible mode requires OPENAI_BASE_URL and OPENAI_API_KEY!")

        llm = ChatOpenAI(
            model=openai_model,
            base_url=openai_base_url,
            api_key=openai_api_key,
            temperature=0,
        )
        print(f"Using OpenAI Compatible LLM: {openai_model}")
    else:
        google_api_key = (api_keys or {}).get("GOOGLE_API_KEY") or settings.GOOGLE_API_KEY
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY is missing!")

        google_model = (api_keys or {}).get("GOOGLE_MODEL") or settings.GOOGLE_MODEL

        llm = ChatGoogleGenerativeAI(
            model=google_model,
            google_api_key=google_api_key,
            temperature=0,
        )
        print(f"Using Google Gemini LLM: {google_model}")

    # Create SQLite connection for checkpointer
    if _sqlite_conn is None:
        _sqlite_conn = await aiosqlite.connect(DB_PATH)

    checkpointer = AsyncSqliteSaver(_sqlite_conn)

    # Create agent
    agent_executor = create_react_agent(
        model=llm,
        tools=all_tools,
        checkpointer=checkpointer,
    )

    _agent_executors[user_id] = agent_executor
    print(f"Agent initialized for user {user_id}")

    return agent_executor


async def chat_with_agent_stream(
    message: str,
    user_id: str,
    conversation_id: str,
    history: List[Dict[str, str]] = None,
    images: List[str] = None,
    api_keys: Dict[str, str] = None,
) -> AsyncGenerator[str, None]:
    """
    Stream agent responses with user isolation.

    Args:
        message: User message
        user_id: User ID for isolation
        conversation_id: Conversation ID for thread management
        history: Previous messages in the conversation
        images: Optional list of base64-encoded images
        api_keys: Optional API keys override

    Yields:
        SSE formatted events
    """

    def encode_sse_data(data: str) -> str:
        """Base64 encode data to avoid SSE newline issues."""
        return base64.b64encode(data.encode("utf-8")).decode("ascii")

    def extract_text_content(content) -> str:
        """Extract text from various content formats."""
        if content is None:
            return ""

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict):
                    if "text" in part:
                        text_parts.append(part["text"])
                    elif "content" in part:
                        text_parts.append(str(part["content"]))
            return "".join(text_parts)

        return str(content) if content else ""

    def build_multimodal_content(text: str, image_list: List[str] = None) -> list:
        """
        Build multimodal content for HumanMessage.

        Args:
            text: Text content
            image_list: Optional list of base64-encoded images

        Returns:
            List of content parts for multimodal message
        """
        content_parts = []

        # Add images first (Vision models typically expect images before text)
        if image_list:
            for img_base64 in image_list:
                # Detect image type from base64 header or default to jpeg
                if img_base64.startswith("/9j/"):
                    media_type = "image/jpeg"
                elif img_base64.startswith("iVBORw"):
                    media_type = "image/png"
                elif img_base64.startswith("R0lGOD"):
                    media_type = "image/gif"
                elif img_base64.startswith("UklGR"):
                    media_type = "image/webp"
                else:
                    media_type = "image/jpeg"  # Default

                content_parts.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{img_base64}"
                    }
                })

        # Add text content
        content_parts.append({
            "type": "text",
            "text": text
        })

        return content_parts

    # Initialize agent
    agent = await initialize_agent(user_id, api_keys)

    # Build thread_id with user isolation
    thread_id = f"{user_id}:{conversation_id}"
    config = {"configurable": {"thread_id": thread_id}}

    # Build messages with history
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    if history:
        for msg in history:
            if msg["role"] == "user":
                # Check if history message has images
                msg_images = msg.get("images")
                if msg_images:
                    content = build_multimodal_content(msg["content"], msg_images)
                    messages.append(HumanMessage(content=content))
                else:
                    messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

    # Build current message (with images if provided)
    if images:
        current_content = build_multimodal_content(message, images)
        messages.append(HumanMessage(content=current_content))
    else:
        messages.append(HumanMessage(content=message))

    # Stream events
    async for event in agent.astream_events(
        {"messages": messages}, config=config, version="v1"
    ):
        kind = event["event"]

        if kind == "on_chat_model_stream":
            raw_content = event["data"]["chunk"].content
            text_content = extract_text_content(raw_content)
            if text_content:
                encoded_data = encode_sse_data(text_content)
                yield f"event: text\ndata: {encoded_data}\n\n"

        elif kind == "on_tool_start":
            tool_name = event["name"]
            encoded_data = encode_sse_data(tool_name)
            yield f"event: tool_start\ndata: {encoded_data}\n\n"

        elif kind == "on_tool_end":
            tool_name = event["name"]
            output = str(event["data"].get("output", ""))

            # 处理 RAG 引用数据 - 解析 [RAG_CITATIONS] 标记
            citations_data = None
            display_output = output
            if "[RAG_CITATIONS]" in output and "[/RAG_CITATIONS]" in output:
                try:
                    start_marker = "[RAG_CITATIONS]"
                    end_marker = "[/RAG_CITATIONS]"
                    start_idx = output.find(start_marker) + len(start_marker)
                    end_idx = output.find(end_marker)
                    citations_json = output[start_idx:end_idx]
                    citations_data = json.loads(citations_json)
                    # 从显示输出中移除引用数据标记
                    display_output = output[:output.find(start_marker)].strip()
                except Exception as e:
                    print(f"解析 RAG 引用数据失败: {e}")

            # Handle image data - preserve full images, truncate text
            if "[IMAGE_BASE64:" in display_output:
                image_pattern = r"\[IMAGE_BASE64:[A-Za-z0-9+/=]+\]"
                image_matches = re.findall(image_pattern, display_output)
                text_parts = re.split(image_pattern, display_output)

                truncated_text_parts = [
                    (part[:500] + "..." if len(part) > 500 else part)
                    for part in text_parts
                ]

                safe_output = ""
                for i, text_part in enumerate(truncated_text_parts):
                    safe_output += text_part
                    if i < len(image_matches):
                        safe_output += image_matches[i]

            # Handle presentation data - preserve full HTML, truncate text
            elif "[PRESENTATION_HTML:" in display_output:
                pres_pattern = r"\[PRESENTATION_HTML:[A-Za-z0-9+/=]+\]"
                pres_matches = re.findall(pres_pattern, display_output)
                text_parts = re.split(pres_pattern, display_output)

                truncated_text_parts = [
                    (part[:500] + "..." if len(part) > 500 else part)
                    for part in text_parts
                ]

                safe_output = ""
                for i, text_part in enumerate(truncated_text_parts):
                    safe_output += text_part
                    if i < len(pres_matches):
                        safe_output += pres_matches[i]

            else:
                safe_output = (display_output[:1000] + "...") if len(display_output) > 1000 else display_output

            tool_data = json.dumps(
                {"name": tool_name, "output": safe_output}, ensure_ascii=False
            )
            encoded_data = encode_sse_data(tool_data)
            yield f"event: tool_end\ndata: {encoded_data}\n\n"

            # 发送 citation 事件（如果有引用数据）
            if citations_data:
                for citation in citations_data:
                    citation_event = json.dumps({
                        "chunk_id": citation.get("chunk_id", ""),
                        "document_id": citation.get("document_id", ""),
                        "document_name": citation.get("document_name", ""),
                        "page_number": citation.get("page_number"),
                        "section": citation.get("section"),
                        "content": citation.get("content", ""),
                        "content_preview": citation.get("content_preview", ""),
                        "score": citation.get("score", 0),
                    }, ensure_ascii=False)
                    encoded_citation = encode_sse_data(citation_event)
                    yield f"event: citation\ndata: {encoded_citation}\n\n"

    # Send done marker with conversation_id for new conversations
    done_data = json.dumps({"conversation_id": conversation_id}, ensure_ascii=False)
    encoded_done = encode_sse_data(done_data)
    yield f"event: done\ndata: {encoded_done}\n\n"


async def cleanup():
    """Cleanup resources."""
    global _sqlite_conn, _mcp_client, _agent_executors

    if _sqlite_conn:
        await _sqlite_conn.close()
        _sqlite_conn = None

    _mcp_client = None
    _agent_executors.clear()

    # Cleanup E2B sandbox
    try:
        import sys
        backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        from tools.e2b_tools import close_sandbox
        await close_sandbox()
    except Exception:
        pass
