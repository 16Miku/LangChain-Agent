# ============================================================
# Presentation Service - AI Assistant Schemas
# AI 助手对话相关的数据模型
# ============================================================

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


# ============================
# 意图类型定义
# ============================

IntentType = Literal[
    "edit_title",       # 修改标题
    "edit_content",     # 修改内容
    "edit_notes",       # 修改备注
    "insert_slide",     # 插入幻灯片
    "delete_slide",     # 删除幻灯片
    "change_layout",    # 更改布局
    "change_theme",     # 更换主题
    "regenerate",       # 重新生成幻灯片
    "reorder_slides",   # 调整幻灯片顺序
    "chat",             # 普通对话（无操作）
    "unknown",          # 无法识别
]


# ============================
# 意图解析结果
# ============================

class ParsedIntent(BaseModel):
    """解析后的用户意图"""
    intent_type: IntentType = Field(..., description="意图类型")
    target_slide: Optional[int] = Field(None, description="目标幻灯片索引 (从0开始)")
    new_value: Optional[str] = Field(None, description="新值（标题/内容等）")
    layout: Optional[str] = Field(None, description="布局类型")
    theme: Optional[str] = Field(None, description="主题名称")
    position: Optional[int] = Field(None, description="插入位置")
    response_message: str = Field(..., description="给用户的回复消息")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="置信度")
    requires_confirmation: bool = Field(False, description="是否需要用户确认")


# ============================
# 对话消息
# ============================

class ChatMessage(BaseModel):
    """对话消息"""
    role: Literal["user", "assistant", "system"] = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


class ConversationContext(BaseModel):
    """对话上下文"""
    presentation_id: str = Field(..., description="演示文稿 ID")
    current_slide_index: int = Field(0, description="当前选中的幻灯片索引")
    history: List[ChatMessage] = Field(default_factory=list, description="对话历史")
    last_action: Optional[str] = Field(None, description="上一次执行的操作")


# ============================
# API 请求/响应
# ============================

class AssistantChatRequest(BaseModel):
    """AI 助手对话请求"""
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")
    current_slide_index: int = Field(0, ge=0, description="当前选中的幻灯片索引")
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="对话历史（最近 10 条）"
    )


class AssistantAction(BaseModel):
    """AI 助手执行的操作"""
    action_type: IntentType = Field(..., description="操作类型")
    target_slide: Optional[int] = Field(None, description="目标幻灯片")
    changes: Dict[str, Any] = Field(default_factory=dict, description="变更内容")
    success: bool = Field(True, description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")


class AssistantChatResponse(BaseModel):
    """AI 助手对话响应"""
    response: str = Field(..., description="AI 回复消息")
    intent: ParsedIntent = Field(..., description="解析的意图")
    actions: List[AssistantAction] = Field(default_factory=list, description="执行的操作")
    presentation_updated: bool = Field(False, description="演示文稿是否被更新")
    updated_slides: Optional[List[Dict[str, Any]]] = Field(None, description="更新后的幻灯片数据")


# ============================
# 确认操作
# ============================

class ConfirmActionRequest(BaseModel):
    """确认操作请求"""
    action_id: str = Field(..., description="待确认的操作 ID")
    confirmed: bool = Field(..., description="是否确认执行")


class ConfirmActionResponse(BaseModel):
    """确认操作响应"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="结果消息")
    presentation_updated: bool = Field(False, description="演示文稿是否被更新")
