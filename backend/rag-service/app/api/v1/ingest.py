# ============================================================
# Ingest API - 文档摄取接口
# ============================================================

from typing import Optional, List
import uuid
import io

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import get_current_user, CurrentUser
from app.services.document_service import DocumentService
from app.services.milvus_service import MilvusService, ChunkData
from app.services.embedding_service import EmbeddingService
from app.services.chunking_service import ChunkingService, ChunkingStrategy
from app.models.document import DocumentStatus
from app.schemas.document import DocumentUploadResponse

router = APIRouter()


def extract_text_from_pdf(content_bytes: bytes) -> str:
    """
    从 PDF 文件中提取文本

    Args:
        content_bytes: PDF 文件的字节内容

    Returns:
        提取的文本内容
    """
    try:
        import PyPDF2

        pdf_file = io.BytesIO(content_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        text_parts = []
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"[Page {page_num + 1}]\n{page_text}")

        return "\n\n".join(text_parts)

    except ImportError:
        print("PyPDF2 not installed, trying pdfplumber...")
        try:
            import pdfplumber

            pdf_file = io.BytesIO(content_bytes)
            text_parts = []

            with pdfplumber.open(pdf_file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"[Page {page_num + 1}]\n{page_text}")

            return "\n\n".join(text_parts)

        except ImportError:
            raise Exception("No PDF library available. Please install PyPDF2 or pdfplumber.")

    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    strategy: str = "semantic"
) -> List[dict]:
    """
    智能文本分块

    Args:
        text: 输入文本
        chunk_size: 分块大小
        chunk_overlap: 重叠大小
        strategy: 分块策略 (fixed, semantic, recursive, page_aware)

    Returns:
        分块列表
    """
    # 自动检测是否包含 PDF 页面标记
    if "[Page " in text and strategy == "semantic":
        strategy = "page_aware"

    chunking_service = ChunkingService(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        strategy=ChunkingStrategy(strategy)
    )

    results = chunking_service.chunk(text)

    return [
        {
            "content": r.content,
            "chunk_index": r.chunk_index,
            "page_number": r.page_number,
            "section": r.section,
            "metadata": r.metadata or {}
        }
        for r in results
    ]


async def process_document(
    document_id: str,
    user_id: str,
    content: str,
    filename: str,
    db: Session,
    milvus_service: MilvusService,
    embedding_service: EmbeddingService
):
    """
    后台处理文档

    Args:
        document_id: 文档ID
        user_id: 用户ID
        content: 文档内容
        filename: 文件名
        db: 数据库会话
        milvus_service: Milvus 服务
        embedding_service: 嵌入服务
    """
    try:
        # 更新状态为处理中
        DocumentService.update_document_status(
            db=db,
            document_id=document_id,
            status=DocumentStatus.PROCESSING
        )

        # 分块
        chunks = chunk_text(content)

        if not chunks:
            DocumentService.update_document_status(
                db=db,
                document_id=document_id,
                status=DocumentStatus.ERROR,
                error_message="No content to process"
            )
            return

        # 生成向量
        contents = [c["content"] for c in chunks]
        embeddings = embedding_service.embed_documents(contents)

        # 准备 Milvus 数据
        chunk_data_list = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = str(uuid.uuid4())
            # 合并元数据，包含章节信息
            metadata = {
                "filename": filename,
                "section": chunk.get("section"),  # 章节标题
                **chunk.get("metadata", {})
            }
            chunk_data_list.append(ChunkData(
                id=chunk_id,
                document_id=document_id,
                user_id=user_id,
                chunk_index=i,
                content=chunk["content"],
                page_number=chunk.get("page_number"),
                embedding=embedding,
                metadata=metadata
            ))

        # 插入 Milvus (如果启用)
        if milvus_service is not None:
            milvus_service.insert(chunk_data_list)

        # 保存分块到数据库 (用于 BM25)
        chunk_dicts = [
            {
                "content": cd.content,
                "page_number": cd.page_number,
                "metadata": cd.metadata
            }
            for cd in chunk_data_list
        ]
        DocumentService.save_chunks(db, document_id, user_id, chunk_dicts)

        # 更新状态为完成
        DocumentService.update_document_status(
            db=db,
            document_id=document_id,
            status=DocumentStatus.READY,
            chunk_count=len(chunks)
        )

    except Exception as e:
        print(f"Document processing error: {e}")
        DocumentService.update_document_status(
            db=db,
            document_id=document_id,
            status=DocumentStatus.ERROR,
            error_message=str(e)
        )


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    http_request: Request,
    file: UploadFile = File(...),
    parse_method: str = Form(default="default"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传文档

    支持的文件格式:
    - .txt: 纯文本
    - .md: Markdown
    - .pdf: PDF (需要 MinerU 或 PyPDF2)

    Args:
        file: 上传的文件
        parse_method: 解析方法 (default, mineru)

    Returns:
        文档上传响应
    """
    # 验证文件类型
    allowed_extensions = ['.txt', '.md', '.pdf', '.docx']
    filename = file.filename or "unknown"
    file_ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # 读取文件内容
    try:
        content_bytes = await file.read()
        file_size = len(content_bytes)

        # 解析文件内容
        if file_ext in ['.txt', '.md']:
            content = content_bytes.decode('utf-8')
        elif file_ext == '.pdf':
            content = extract_text_from_pdf(content_bytes)
            if not content.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to extract text from PDF. The PDF may be image-based or encrypted."
                )
        else:
            content = content_bytes.decode('utf-8', errors='ignore')

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {str(e)}"
        )

    # 创建文档记录
    document = DocumentService.create_document(
        db=db,
        user_id=current_user.user_id,
        filename=filename,
        file_type=file_ext,
        file_size=file_size
    )

    # 获取服务实例
    milvus_service = http_request.app.state.milvus_service
    embedding_service = http_request.app.state.embedding_service

    # 后台处理文档
    background_tasks.add_task(
        process_document,
        document_id=str(document.id),
        user_id=current_user.user_id,
        content=content,
        filename=filename,
        db=db,
        milvus_service=milvus_service,
        embedding_service=embedding_service
    )

    return DocumentUploadResponse(
        document_id=document.id,
        filename=filename,
        status="processing",
        estimated_time=30
    )


@router.post("/text", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_text(
    background_tasks: BackgroundTasks,
    http_request: Request,
    text: str = Form(...),
    title: str = Form(default="Untitled"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    直接摄取文本

    Args:
        text: 文本内容
        title: 文档标题

    Returns:
        文档上传响应
    """
    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text content cannot be empty"
        )

    filename = f"{title}.txt"

    # 创建文档记录
    document = DocumentService.create_document(
        db=db,
        user_id=current_user.user_id,
        filename=filename,
        file_type=".txt",
        file_size=len(text.encode('utf-8'))
    )

    # 获取服务实例
    milvus_service = http_request.app.state.milvus_service
    embedding_service = http_request.app.state.embedding_service

    # 后台处理
    background_tasks.add_task(
        process_document,
        document_id=str(document.id),
        user_id=current_user.user_id,
        content=text,
        filename=filename,
        db=db,
        milvus_service=milvus_service,
        embedding_service=embedding_service
    )

    return DocumentUploadResponse(
        document_id=document.id,
        filename=filename,
        status="processing",
        estimated_time=15
    )
