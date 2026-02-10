# ============================================================
# Chat Service - Chat Request/Response Schemas
# ============================================================

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Schema for chat request."""

    conversation_id: Optional[str] = Field(
        default=None,
        alias="conversationId",
        description="会话 ID，如果不提供则自动创建新会话",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"}
    )
    content: str = Field(
        ...,
        description="用户消息内容",
        json_schema_extra={"example": "请帮我搜索最新的 AI 研究论文"}
    )
    images: Optional[List[str]] = Field(
        default=None,
        description="图片列表 (Base64 编码或 URL)，用于多模态对话",
        json_schema_extra={"example": ["data:image/png;base64,iVBORw0KGgo..."]}
    )
    api_keys: Optional[Dict[str, str]] = Field(
        default=None,
        alias="apiKeys",
        description="自定义 API 密钥 (可选)",
        json_schema_extra={"example": {"SERPER_API_KEY": "xxx"}}
    )

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "content": "请帮我搜索最新的 AI 研究论文"
                },
                {
                    "conversationId": "550e8400-e29b-41d4-a716-446655440000",
                    "content": "继续上一个话题",
                    "images": ["data:image/png;base64,iVBORw0KGgo..."]
                }
            ]
        }
    }


class ChatStreamEvent(BaseModel):
    """Schema for SSE stream event."""

    type: Literal["text", "tool_start", "tool_end", "citation", "done", "error"] = Field(
        ...,
        description="事件类型: text(文本), tool_start(工具开始), tool_end(工具结束), citation(引用), done(完成), error(错误)"
    )
    data: Any = Field(
        ...,
        description="事件数据 (Base64 编码)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"type": "text", "data": "SGVsbG8gV29ybGQ="},
                {"type": "tool_start", "data": "c2VhcmNoX3dlYg=="},
                {"type": "tool_end", "data": "eyJuYW1lIjogInNlYXJjaF93ZWIiLCAib3V0cHV0IjogIi4uLiJ9"},
                {"type": "done", "data": ""},
            ]
        }
    }
