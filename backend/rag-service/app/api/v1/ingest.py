# ============================================================
# Ingest API - 文档摄取接口
# ============================================================
# 支持两种解析模式:
# - default: 使用 PyPDF2/pdfplumber 本地解析
# - mineru: 使用 MinerU 云服务智能解析 (支持 OCR、表格、公式)
# ============================================================

from typing import Optional, List
import uuid
import io
import logging

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_new_db_session
from app.core.security import get_current_user, CurrentUser
from app.services.document_service import DocumentService
from app.services.milvus_service import MilvusService, ChunkData
from app.services.embedding_service import EmbeddingService
from app.services.chunking_service import ChunkingService, ChunkingStrategy
from app.services.mineru_service import (
    MinerUService, MinerUParseOptions, MinerULanguage,
    MinerUTaskState, MinerUServiceError, get_mineru_service
)
from app.models.document import DocumentStatus
from app.schemas.document import DocumentUploadResponse
from app.config import settings

logger = logging.getLogger(__name__)

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
    chunk_size: int = 1500,
    chunk_overlap: int = 200,
    strategy: str = "semantic",
    extract_toc: bool = True
) -> List[dict]:
    """
    智能文本分块

    Args:
        text: 输入文本
        chunk_size: 分块大小，默认 1500
        chunk_overlap: 重叠大小，默认 200
        strategy: 分块策略 (fixed, semantic, recursive, page_aware)
        extract_toc: 是否提取目录作为单独的 chunk，默认 True

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

    # 使用带目录提取的分块方法
    if extract_toc:
        results = chunking_service.chunk_with_toc(text)
    else:
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
    vector_service,  # MilvusService 或 PgvectorService
    embedding_service: EmbeddingService
):
    """
    后台处理文档

    Args:
        document_id: 文档ID
        user_id: 用户ID
        content: 文档内容
        filename: 文件名
        vector_service: 向量服务 (MilvusService 或 PgvectorService)
        embedding_service: 嵌入服务
    """
    # 后台任务需要创建新的数据库会话
    db = get_new_db_session()
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

        # 插入向量存储 (如果启用)
        if vector_service is not None:
            vector_service.insert(chunk_data_list)

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
    finally:
        db.close()


async def process_document_with_mineru(
    document_id: str,
    user_id: str,
    content_bytes: bytes,
    filename: str,
    parse_options: MinerUParseOptions,
    vector_service,
    embedding_service: EmbeddingService,
    mineru_service: MinerUService
):
    """
    使用 MinerU 后台处理文档

    Args:
        document_id: 文档ID
        user_id: 用户ID
        content_bytes: 文件内容
        filename: 文件名
        parse_options: MinerU 解析选项
        vector_service: 向量服务
        embedding_service: 嵌入服务
        mineru_service: MinerU 服务
    """
    # 后台任务需要创建新的数据库会话
    db = get_new_db_session()
    try:
        # 更新状态为处理中
        DocumentService.update_document_status(
            db=db,
            document_id=document_id,
            status=DocumentStatus.PROCESSING
        )

        logger.info(f"Starting MinerU parsing for document {document_id}: {filename}")

        # 调用 MinerU 解析
        try:
            result = await mineru_service.parse_document_bytes(
                content=content_bytes,
                filename=filename,
                options=parse_options,
                wait_for_result=True
            )
        except MinerUServiceError as e:
            logger.error(f"MinerU parsing failed: {e.message}")
            DocumentService.update_document_status(
                db=db,
                document_id=document_id,
                status=DocumentStatus.ERROR,
                error_message=f"MinerU 解析失败: {e.message}"
            )
            return

        # 检查解析结果
        if result.state == MinerUTaskState.FAILED:
            DocumentService.update_document_status(
                db=db,
                document_id=document_id,
                status=DocumentStatus.ERROR,
                error_message=result.error_message or "MinerU 解析失败"
            )
            return

        # 从结果中提取分块
        mineru_chunks = mineru_service.extract_chunks_from_result(result)

        if not mineru_chunks:
            # 如果没有分块，尝试使用 markdown 内容
            if result.markdown_content:
                chunks = chunk_text(result.markdown_content)
            else:
                DocumentService.update_document_status(
                    db=db,
                    document_id=document_id,
                    status=DocumentStatus.ERROR,
                    error_message="No content extracted from document"
                )
                return
        else:
            # 转换 MinerU 分块格式
            chunks = [
                {
                    "content": mc.content,
                    "chunk_index": mc.chunk_index,
                    "page_number": mc.page_number,
                    "section": mc.section,
                    "metadata": {
                        "chunk_type": mc.chunk_type,
                        **mc.metadata
                    }
                }
                for mc in mineru_chunks
            ]

        logger.info(f"Extracted {len(chunks)} chunks from document {document_id}")

        # 生成向量
        contents = [c["content"] for c in chunks]
        embeddings = embedding_service.embed_documents(contents)

        # 准备向量数据
        chunk_data_list = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = str(uuid.uuid4())
            metadata = {
                "filename": filename,
                "section": chunk.get("section"),
                "chunk_type": chunk.get("metadata", {}).get("chunk_type", "text"),
                "parsed_by": "mineru",
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

        # 插入向量存储
        if vector_service is not None:
            vector_service.insert(chunk_data_list)

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

        logger.info(f"Document {document_id} processed successfully with MinerU")

    except Exception as e:
        logger.error(f"Document processing error with MinerU: {e}")
        DocumentService.update_document_status(
            db=db,
            document_id=document_id,
            status=DocumentStatus.ERROR,
            error_message=str(e)
        )
    finally:
        db.close()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    http_request: Request,
    file: UploadFile = File(...),
    parse_method: str = Form(default="auto"),
    enable_ocr: bool = Form(default=False),
    enable_formula: bool = Form(default=True),
    enable_table: bool = Form(default=True),
    language: str = Form(default="ch"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传文档

    支持的文件格式:
    - .txt: 纯文本
    - .md: Markdown
    - .pdf: PDF 文档
    - .docx: Word 文档
    - .pptx: PowerPoint 文档 (仅 MinerU 模式)
    - .png/.jpg/.jpeg: 图片 (仅 MinerU 模式，需启用 OCR)

    Args:
        file: 上传的文件
        parse_method: 解析方法
            - auto: 自动选择 (PDF 优先使用 MinerU，其他使用本地解析)
            - default: 使用本地解析 (PyPDF2/pdfplumber)
            - mineru: 使用 MinerU 云服务智能解析
        enable_ocr: 是否启用 OCR (仅 MinerU 模式)
        enable_formula: 是否识别公式 (仅 MinerU 模式)
        enable_table: 是否识别表格 (仅 MinerU 模式)
        language: 文档语言 (ch/en/ja/ko 等，仅 MinerU 模式)

    Returns:
        文档上传响应
    """
    # 验证文件类型
    basic_extensions = ['.txt', '.md', '.pdf', '.docx']
    mineru_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.png', '.jpg', '.jpeg']

    filename = file.filename or "unknown"
    file_ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    # 读取文件内容
    try:
        content_bytes = await file.read()
        file_size = len(content_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {str(e)}"
        )

    # 确定解析方法
    mineru_service = get_mineru_service()
    use_mineru = False

    if parse_method == "mineru":
        if not mineru_service.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MinerU service is not configured. Please set MINERU_API_KEY."
            )
        if file_ext not in mineru_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"MinerU does not support this file type. Supported: {', '.join(mineru_extensions)}"
            )
        use_mineru = True
    elif parse_method == "auto":
        # 自动选择：PDF/图片/PPT 优先使用 MinerU（如果可用）
        if mineru_service.is_available and settings.MINERU_ENABLED:
            if file_ext in ['.pdf', '.ppt', '.pptx', '.png', '.jpg', '.jpeg']:
                use_mineru = True
            elif file_ext in ['.doc', '.docx'] and enable_ocr:
                use_mineru = True
    else:  # default
        if file_ext not in basic_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type for default parser. Allowed: {', '.join(basic_extensions)}"
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
    vector_service = getattr(http_request.app.state, 'vector_service', None) or \
                     getattr(http_request.app.state, 'milvus_service', None)
    embedding_service = http_request.app.state.embedding_service

    if use_mineru:
        # 使用 MinerU 解析
        logger.info(f"Using MinerU to parse document: {filename}")

        # 构建解析选项
        try:
            lang = MinerULanguage(language)
        except ValueError:
            lang = MinerULanguage.CHINESE

        parse_options = MinerUParseOptions(
            is_ocr=enable_ocr,
            enable_formula=enable_formula,
            enable_table=enable_table,
            language=lang
        )

        # 后台处理文档 (MinerU 模式)
        background_tasks.add_task(
            process_document_with_mineru,
            document_id=str(document.id),
            user_id=current_user.user_id,
            content_bytes=content_bytes,
            filename=filename,
            parse_options=parse_options,
            vector_service=vector_service,
            embedding_service=embedding_service,
            mineru_service=mineru_service
        )

        estimated_time = 120  # MinerU 解析通常需要更长时间
    else:
        # 使用本地解析
        logger.info(f"Using local parser for document: {filename}")

        # 解析文件内容
        try:
            if file_ext in ['.txt', '.md']:
                content = content_bytes.decode('utf-8')
            elif file_ext == '.pdf':
                content = extract_text_from_pdf(content_bytes)
                if not content.strip():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to extract text from PDF. The PDF may be image-based. Try using parse_method=mineru with enable_ocr=true."
                    )
            else:
                content = content_bytes.decode('utf-8', errors='ignore')
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse file: {str(e)}"
            )

        # 后台处理文档 (本地模式)
        background_tasks.add_task(
            process_document,
            document_id=str(document.id),
            user_id=current_user.user_id,
            content=content,
            filename=filename,
            vector_service=vector_service,
            embedding_service=embedding_service
        )

        estimated_time = 30

    return DocumentUploadResponse(
        document_id=document.id,
        filename=filename,
        status="processing",
        estimated_time=estimated_time
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

    # 获取服务实例 (优先使用 vector_service，兼容旧的 milvus_service)
    vector_service = getattr(http_request.app.state, 'vector_service', None) or \
                     getattr(http_request.app.state, 'milvus_service', None)
    embedding_service = http_request.app.state.embedding_service

    # 后台处理
    background_tasks.add_task(
        process_document,
        document_id=str(document.id),
        user_id=current_user.user_id,
        content=text,
        filename=filename,
        vector_service=vector_service,
        embedding_service=embedding_service
    )

    return DocumentUploadResponse(
        document_id=document.id,
        filename=filename,
        status="processing",
        estimated_time=15
    )
