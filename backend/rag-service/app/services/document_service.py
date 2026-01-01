# ============================================================
# Document Service - 文档管理服务
# ============================================================

from typing import List, Optional
from uuid import UUID
import os

from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.document import Document, DocumentStatus
from app.models.chunk import Chunk
from app.schemas.document import DocumentResponse


class DocumentService:
    """文档管理服务"""

    @staticmethod
    def create_document(
        db: Session,
        user_id: str,
        filename: str,
        file_type: Optional[str] = None,
        file_size: Optional[int] = None,
        file_path: Optional[str] = None
    ) -> Document:
        """
        创建文档记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            filename: 文件名
            file_type: 文件类型
            file_size: 文件大小
            file_path: 存储路径

        Returns:
            Document 对象
        """
        document = Document(
            user_id=UUID(user_id),
            filename=filename,
            file_type=file_type or os.path.splitext(filename)[1].lower(),
            file_size=file_size,
            file_path=file_path,
            status=DocumentStatus.PENDING
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def get_document(db: Session, document_id: str, user_id: str) -> Optional[Document]:
        """
        获取文档

        Args:
            db: 数据库会话
            document_id: 文档ID
            user_id: 用户ID

        Returns:
            Document 对象或 None
        """
        return db.query(Document).filter(
            Document.id == UUID(document_id),
            Document.user_id == UUID(user_id)
        ).first()

    @staticmethod
    def list_documents(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Document], int]:
        """
        获取用户的文档列表

        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过数量
            limit: 返回数量

        Returns:
            (文档列表, 总数)
        """
        query = db.query(Document).filter(Document.user_id == UUID(user_id))
        total = query.count()
        documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
        return documents, total

    @staticmethod
    def update_document_status(
        db: Session,
        document_id: str,
        status: DocumentStatus,
        chunk_count: int = 0,
        error_message: Optional[str] = None
    ) -> Optional[Document]:
        """
        更新文档状态

        Args:
            db: 数据库会话
            document_id: 文档ID
            status: 新状态
            chunk_count: 分块数量
            error_message: 错误信息

        Returns:
            更新后的 Document 对象
        """
        document = db.query(Document).filter(Document.id == UUID(document_id)).first()
        if document:
            document.status = status
            document.chunk_count = chunk_count
            if error_message:
                document.error_message = error_message
            db.commit()
            db.refresh(document)
        return document

    @staticmethod
    def delete_document(db: Session, document_id: str, user_id: str) -> bool:
        """
        删除文档

        Args:
            db: 数据库会话
            document_id: 文档ID
            user_id: 用户ID

        Returns:
            是否删除成功
        """
        document = db.query(Document).filter(
            Document.id == UUID(document_id),
            Document.user_id == UUID(user_id)
        ).first()

        if document:
            # 删除关联的 chunks
            db.query(Chunk).filter(Chunk.document_id == UUID(document_id)).delete()
            db.delete(document)
            db.commit()
            return True
        return False

    @staticmethod
    def save_chunks(
        db: Session,
        document_id: str,
        user_id: str,
        chunks: List[dict]
    ) -> List[Chunk]:
        """
        保存分块到数据库

        Args:
            db: 数据库会话
            document_id: 文档ID
            user_id: 用户ID
            chunks: 分块数据列表

        Returns:
            Chunk 对象列表
        """
        chunk_objects = []
        for i, chunk_data in enumerate(chunks):
            chunk = Chunk(
                document_id=UUID(document_id),
                user_id=UUID(user_id),
                chunk_index=i,
                content=chunk_data.get("content", ""),
                page_number=chunk_data.get("page_number"),
                metadata=chunk_data.get("metadata", {})
            )
            db.add(chunk)
            chunk_objects.append(chunk)

        db.commit()

        for chunk in chunk_objects:
            db.refresh(chunk)

        return chunk_objects

    @staticmethod
    def get_chunks(db: Session, document_id: str, user_id: str) -> List[Chunk]:
        """
        获取文档的所有分块

        Args:
            db: 数据库会话
            document_id: 文档ID
            user_id: 用户ID

        Returns:
            Chunk 对象列表
        """
        return db.query(Chunk).filter(
            Chunk.document_id == UUID(document_id),
            Chunk.user_id == UUID(user_id)
        ).order_by(Chunk.chunk_index).all()
