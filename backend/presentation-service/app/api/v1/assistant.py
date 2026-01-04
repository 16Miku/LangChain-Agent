# ============================================================
# Presentation Service - AI Assistant API
# AI 助手对话接口
# ============================================================

import uuid
from datetime import datetime
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user_id
from app.database import get_db
from app.models import Presentation
from app.schemas import (
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantAction,
    ParsedIntent,
    Slide,
)
from app.services.intent_parser import get_intent_parser

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/{presentation_id}/chat", response_model=AssistantChatResponse)
async def assistant_chat(
    presentation_id: str,
    request: AssistantChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    AI 助手对话接口
    解析用户的自然语言指令并执行相应操作
    """
    # 验证 ID 格式
    try:
        uuid.UUID(presentation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid presentation ID"
        )

    # 获取演示文稿
    result = await db.execute(
        select(Presentation).where(
            Presentation.id == presentation_id,
            Presentation.user_id == user_id
        )
    )
    presentation = result.scalar_one_or_none()

    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found"
        )

    # 获取幻灯片标题列表
    slide_titles = [
        slide.get("title", f"幻灯片 {i+1}")
        for i, slide in enumerate(presentation.slides)
    ]

    # 解析用户意图
    intent_parser = get_intent_parser()
    intent = await intent_parser.parse_intent(
        message=request.message,
        slide_count=len(presentation.slides),
        current_slide=request.current_slide_index,
        slide_titles=slide_titles,
        conversation_history=request.conversation_history,
    )

    # 执行操作
    actions = []
    presentation_updated = False
    updated_slides = None

    # 如果需要确认，直接返回
    if intent.requires_confirmation:
        return AssistantChatResponse(
            response=intent.response_message,
            intent=intent,
            actions=[],
            presentation_updated=False,
            updated_slides=None,
        )

    # 根据意图类型执行操作
    try:
        if intent.intent_type == "edit_title":
            action, presentation_updated = await _execute_edit_title(
                db, presentation, intent
            )
            actions.append(action)

        elif intent.intent_type == "edit_content":
            action, presentation_updated = await _execute_edit_content(
                db, presentation, intent
            )
            actions.append(action)

        elif intent.intent_type == "edit_notes":
            action, presentation_updated = await _execute_edit_notes(
                db, presentation, intent
            )
            actions.append(action)

        elif intent.intent_type == "insert_slide":
            action, presentation_updated = await _execute_insert_slide(
                db, presentation, intent
            )
            actions.append(action)

        elif intent.intent_type == "delete_slide":
            action, presentation_updated = await _execute_delete_slide(
                db, presentation, intent
            )
            actions.append(action)

        elif intent.intent_type == "change_layout":
            action, presentation_updated = await _execute_change_layout(
                db, presentation, intent
            )
            actions.append(action)

        elif intent.intent_type == "change_theme":
            action, presentation_updated = await _execute_change_theme(
                db, presentation, intent
            )
            actions.append(action)

        elif intent.intent_type == "regenerate":
            # 重新生成需要调用 PresentationService
            action = AssistantAction(
                action_type="regenerate",
                target_slide=intent.target_slide,
                changes={},
                success=False,
                error_message="重新生成功能请使用专门的重新生成按钮",
            )
            actions.append(action)

        # 如果有更新，获取最新的幻灯片数据
        if presentation_updated:
            await db.refresh(presentation)
            updated_slides = presentation.slides

    except Exception as e:
        # 操作失败
        actions.append(AssistantAction(
            action_type=intent.intent_type,
            target_slide=intent.target_slide,
            changes={},
            success=False,
            error_message=str(e),
        ))

    return AssistantChatResponse(
        response=intent.response_message,
        intent=intent,
        actions=actions,
        presentation_updated=presentation_updated,
        updated_slides=updated_slides,
    )


async def _execute_edit_title(
    db: AsyncSession,
    presentation: Presentation,
    intent: ParsedIntent,
) -> tuple[AssistantAction, bool]:
    """执行修改标题操作"""
    if intent.target_slide is None or intent.new_value is None:
        return AssistantAction(
            action_type="edit_title",
            success=False,
            error_message="缺少目标幻灯片或新标题",
        ), False

    if intent.target_slide >= len(presentation.slides):
        return AssistantAction(
            action_type="edit_title",
            target_slide=intent.target_slide,
            success=False,
            error_message="幻灯片索引超出范围",
        ), False

    # 更新标题
    slides = list(presentation.slides)
    slide = dict(slides[intent.target_slide])
    old_title = slide.get("title", "")
    slide["title"] = intent.new_value
    slides[intent.target_slide] = slide
    presentation.slides = slides
    presentation.updated_at = datetime.utcnow()

    return AssistantAction(
        action_type="edit_title",
        target_slide=intent.target_slide,
        changes={"old_title": old_title, "new_title": intent.new_value},
        success=True,
    ), True


async def _execute_edit_content(
    db: AsyncSession,
    presentation: Presentation,
    intent: ParsedIntent,
) -> tuple[AssistantAction, bool]:
    """执行修改内容操作"""
    if intent.target_slide is None or intent.new_value is None:
        return AssistantAction(
            action_type="edit_content",
            success=False,
            error_message="缺少目标幻灯片或新内容",
        ), False

    if intent.target_slide >= len(presentation.slides):
        return AssistantAction(
            action_type="edit_content",
            target_slide=intent.target_slide,
            success=False,
            error_message="幻灯片索引超出范围",
        ), False

    # 更新内容
    slides = list(presentation.slides)
    slide = dict(slides[intent.target_slide])
    old_content = slide.get("content", "")
    slide["content"] = intent.new_value
    slides[intent.target_slide] = slide
    presentation.slides = slides
    presentation.updated_at = datetime.utcnow()

    return AssistantAction(
        action_type="edit_content",
        target_slide=intent.target_slide,
        changes={"old_content": old_content, "new_content": intent.new_value},
        success=True,
    ), True


async def _execute_edit_notes(
    db: AsyncSession,
    presentation: Presentation,
    intent: ParsedIntent,
) -> tuple[AssistantAction, bool]:
    """执行修改备注操作"""
    if intent.target_slide is None or intent.new_value is None:
        return AssistantAction(
            action_type="edit_notes",
            success=False,
            error_message="缺少目标幻灯片或新备注",
        ), False

    if intent.target_slide >= len(presentation.slides):
        return AssistantAction(
            action_type="edit_notes",
            target_slide=intent.target_slide,
            success=False,
            error_message="幻灯片索引超出范围",
        ), False

    # 更新备注
    slides = list(presentation.slides)
    slide = dict(slides[intent.target_slide])
    old_notes = slide.get("notes", "")
    slide["notes"] = intent.new_value
    slides[intent.target_slide] = slide
    presentation.slides = slides
    presentation.updated_at = datetime.utcnow()

    return AssistantAction(
        action_type="edit_notes",
        target_slide=intent.target_slide,
        changes={"old_notes": old_notes, "new_notes": intent.new_value},
        success=True,
    ), True


async def _execute_insert_slide(
    db: AsyncSession,
    presentation: Presentation,
    intent: ParsedIntent,
) -> tuple[AssistantAction, bool]:
    """执行插入幻灯片操作"""
    # 创建新幻灯片
    new_slide = {
        "title": "新幻灯片",
        "content": "- 点击编辑内容",
        "layout": "bullet_points",
        "notes": "",
    }

    slides = list(presentation.slides)
    position = intent.position if intent.position is not None else len(slides)

    # 确保位置有效
    if position < 0:
        position = 0
    elif position > len(slides):
        position = len(slides)

    slides.insert(position, new_slide)
    presentation.slides = slides
    presentation.slide_count = len(slides)
    presentation.updated_at = datetime.utcnow()

    return AssistantAction(
        action_type="insert_slide",
        target_slide=position,
        changes={"position": position, "slide": new_slide},
        success=True,
    ), True


async def _execute_delete_slide(
    db: AsyncSession,
    presentation: Presentation,
    intent: ParsedIntent,
) -> tuple[AssistantAction, bool]:
    """执行删除幻灯片操作"""
    if intent.target_slide is None:
        return AssistantAction(
            action_type="delete_slide",
            success=False,
            error_message="缺少目标幻灯片",
        ), False

    if len(presentation.slides) <= 1:
        return AssistantAction(
            action_type="delete_slide",
            target_slide=intent.target_slide,
            success=False,
            error_message="无法删除最后一张幻灯片",
        ), False

    if intent.target_slide >= len(presentation.slides):
        return AssistantAction(
            action_type="delete_slide",
            target_slide=intent.target_slide,
            success=False,
            error_message="幻灯片索引超出范围",
        ), False

    # 删除幻灯片
    slides = list(presentation.slides)
    deleted_slide = slides.pop(intent.target_slide)
    presentation.slides = slides
    presentation.slide_count = len(slides)
    presentation.updated_at = datetime.utcnow()

    return AssistantAction(
        action_type="delete_slide",
        target_slide=intent.target_slide,
        changes={"deleted_slide": deleted_slide},
        success=True,
    ), True


async def _execute_change_layout(
    db: AsyncSession,
    presentation: Presentation,
    intent: ParsedIntent,
) -> tuple[AssistantAction, bool]:
    """执行更改布局操作"""
    if intent.target_slide is None or intent.layout is None:
        return AssistantAction(
            action_type="change_layout",
            success=False,
            error_message="缺少目标幻灯片或布局类型",
        ), False

    if intent.target_slide >= len(presentation.slides):
        return AssistantAction(
            action_type="change_layout",
            target_slide=intent.target_slide,
            success=False,
            error_message="幻灯片索引超出范围",
        ), False

    # 更新布局
    slides = list(presentation.slides)
    slide = dict(slides[intent.target_slide])
    old_layout = slide.get("layout", "bullet_points")
    slide["layout"] = intent.layout
    slides[intent.target_slide] = slide
    presentation.slides = slides
    presentation.updated_at = datetime.utcnow()

    return AssistantAction(
        action_type="change_layout",
        target_slide=intent.target_slide,
        changes={"old_layout": old_layout, "new_layout": intent.layout},
        success=True,
    ), True


async def _execute_change_theme(
    db: AsyncSession,
    presentation: Presentation,
    intent: ParsedIntent,
) -> tuple[AssistantAction, bool]:
    """执行更换主题操作"""
    if intent.theme is None:
        return AssistantAction(
            action_type="change_theme",
            success=False,
            error_message="缺少主题名称",
        ), False

    # 更新主题
    old_theme = presentation.theme
    presentation.theme = intent.theme
    presentation.updated_at = datetime.utcnow()

    return AssistantAction(
        action_type="change_theme",
        changes={"old_theme": old_theme, "new_theme": intent.theme},
        success=True,
    ), True
