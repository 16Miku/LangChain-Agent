# ============================================================
# Documents API - 文档管理接口
# ============================================================

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import get_current_user, CurrentUser
from app.services.document_service import DocumentService
from app.services.milvus_service import MilvusService
from app.models.document import DocumentStatus
from app.schemas.document import (
    DocumentResponse,
    DocumentListResponse,
    DocumentStatusResponse,
    DocumentUploadResponse
)

router = APIRouter()


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的文档列表

    Args:
        skip: 跳过数量
        limit: 返回数量
    """
    documents, total = DocumentService.list_documents(
        db=db,
        user_id=current_user.user_id,
        skip=skip,
        limit=limit
    )

    return DocumentListResponse(
        total=total,
        documents=[DocumentResponse.model_validate(doc) for doc in documents]
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个文档详情"""
    document = DocumentService.get_document(
        db=db,
        document_id=document_id,
        user_id=current_user.user_id
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return DocumentResponse.model_validate(document)


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取文档处理状态"""
    document = DocumentService.get_document(
        db=db,
        document_id=document_id,
        user_id=current_user.user_id
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # 估算剩余处理时间
    estimated_time = None
    if document.status == DocumentStatus.PROCESSING.value:
        estimated_time = 30  # 假设 30 秒

    return DocumentStatusResponse(
        id=document.id,
        filename=document.filename,
        status=document.status if isinstance(document.status, str) else document.status.value,
        chunk_count=document.chunk_count,
        error_message=document.error_message,
        estimated_time=estimated_time
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除文档

    同时删除:
    - PostgreSQL 中的文档和分块记录
    - Milvus 中的向量数据
    """
    # 检查文档是否存在
    document = DocumentService.get_document(
        db=db,
        document_id=document_id,
        user_id=current_user.user_id
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # 删除 Milvus 中的向量
    try:
        milvus_service: MilvusService = request.app.state.milvus_service
        milvus_service.delete_by_document(document_id)
    except Exception as e:
        print(f"Failed to delete vectors from Milvus: {e}")

    # 删除数据库记录
    success = DocumentService.delete_document(
        db=db,
        document_id=document_id,
        user_id=current_user.user_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )

    return None
