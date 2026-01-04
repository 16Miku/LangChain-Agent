# ============================================================
# Presentation Service - API v1 Router
# ============================================================

from fastapi import APIRouter

from app.api.v1 import presentations, editor, assistant

api_router = APIRouter(prefix="/v1")

# 注册子路由
api_router.include_router(presentations.router)
api_router.include_router(editor.router)
api_router.include_router(assistant.router)
