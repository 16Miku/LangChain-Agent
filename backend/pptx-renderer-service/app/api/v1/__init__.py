# ============================================================
# API v1 Package
# ============================================================
"""
API v1 路由模块
"""

from fastapi import APIRouter

from app.api.v1.render import router as render_router

api_v1_router = APIRouter()
api_v1_router.include_router(render_router, prefix="/render", tags=["render"])
