# ============================================================
# MinerU Service - 智能文档解析服务
# ============================================================
# 集成 MinerU 云服务 API，支持复杂文档解析
# - PDF/Word/PPT 等格式
# - OCR 文字识别
# - 表格/公式提取
# - 智能语义分块
# ============================================================

import asyncio
import httpx
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

from app.config import settings

logger = logging.getLogger(__name__)


class MinerUTaskStatus(str, Enum):
    """MinerU 任务状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MinerULanguage(str, Enum):
    """MinerU 支持的语言"""
    CHINESE = "ch"
    ENGLISH = "en"
    JAPANESE = "ja"
    KOREAN = "ko"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"


class MinerUExportFormat(str, Enum):
    """MinerU 导出格式"""
    MARKDOWN = "md"
    HTML = "html"
    DOCX = "docx"
    LATEX = "latex"


@dataclass
class MinerUParseOptions:
    """MinerU 解析选项"""
    is_ocr: bool = False  # 是否启用 OCR
    enable_formula: bool = True  # 是否识别公式
    enable_table: bool = True  # 是否识别表格
    language: MinerULanguage = MinerULanguage.CHINESE  # 文档语言
    page_ranges: Optional[str] = None  # 页面范围，如 "1-10,15-20"
    model_version: str = "v2"  # 模型版本
    extra_formats: List[MinerUExportFormat] = field(
        default_factory=lambda: [MinerUExportFormat.HTML]
    )


@dataclass
class MinerUParseResult:
    """MinerU 解析结果"""
    task_id: str
    status: MinerUTaskStatus
    markdown_content: Optional[str] = None
    html_content: Optional[str] = None
    pages: Optional[List[Dict[str, Any]]] = None
    tables: Optional[List[Dict[str, Any]]] = None
    formulas: Optional[List[Dict[str, Any]]] = None
    images: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None
    progress: int = 0  # 0-100


@dataclass
class MinerUChunk:
    """MinerU 分块结果"""
    content: str
    chunk_index: int
    page_number: Optional[int] = None
    section: Optional[str] = None
    chunk_type: str = "text"  # text, table, formula, image_caption
    metadata: Dict[str, Any] = field(default_factory=dict)


class MinerUServiceError(Exception):
    """MinerU 服务错误"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class MinerUService:
    """
    MinerU 智能文档解析服务

    集成 MinerU 云服务 API，提供高质量的文档解析能力：
    - 支持 PDF、Word、PPT、图片等多种格式
    - OCR 文字识别（支持扫描件）
    - 表格结构提取
    - 数学公式识别（LaTeX 格式）
    - 智能语义分块

    使用示例:
        service = MinerUService()

        # 通过 URL 解析
        result = await service.parse_document_url(
            url="https://example.com/document.pdf",
            options=MinerUParseOptions(is_ocr=True)
        )

        # 通过文件内容解析
        result = await service.parse_document_bytes(
            content=pdf_bytes,
            filename="document.pdf"
        )
    """

    # MinerU API v4 端点
    API_VERSION = "v4"
    DEFAULT_BASE_URL = "https://mineru.net/api/v4"

    # 文件限制
    MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
    MAX_PAGE_COUNT = 600

    # 支持的文件格式
    SUPPORTED_FORMATS = {
        '.pdf', '.doc', '.docx', '.ppt', '.pptx',
        '.png', '.jpg', '.jpeg'
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 300.0,
        max_retries: int = 3
    ):
        """
        初始化 MinerU 服务

        Args:
            api_key: MinerU API Bearer Token，默认从配置读取
            base_url: API 基础 URL，默认使用官方地址
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.api_key = api_key or settings.MINERU_API_KEY
        self.base_url = (base_url or settings.MINERU_API_URL or self.DEFAULT_BASE_URL).rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries

        if not self.api_key:
            logger.warning("MinerU API key not configured. Service will be unavailable.")

    @property
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return bool(self.api_key)

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        发送 API 请求

        Args:
            method: HTTP 方法
            endpoint: API 端点
            json_data: JSON 请求体
            retry_count: 当前重试次数

        Returns:
            API 响应数据
        """
        if not self.is_available:
            raise MinerUServiceError("MinerU API key not configured")

        url = f"{self.base_url}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    json=json_data
                )

                # 处理响应
                if response.status_code == 200:
                    return response.json()

                # 处理错误
                error_data = response.json() if response.content else {}
                error_code = error_data.get("code", str(response.status_code))
                error_msg = error_data.get("msg", response.text)

                # 特定错误码处理
                if error_code in ["A0202", "A0211"]:
                    raise MinerUServiceError(f"Token 错误或过期: {error_msg}", error_code)

                raise MinerUServiceError(f"API 请求失败: {error_msg}", error_code)

        except httpx.TimeoutException:
            if retry_count < self.max_retries:
                logger.warning(f"请求超时，正在重试 ({retry_count + 1}/{self.max_retries})")
                await asyncio.sleep(2 ** retry_count)  # 指数退避
                return await self._make_request(method, endpoint, json_data, retry_count + 1)
            raise MinerUServiceError("请求超时，请稍后重试")

        except httpx.RequestError as e:
            if retry_count < self.max_retries:
                logger.warning(f"网络错误，正在重试 ({retry_count + 1}/{self.max_retries}): {e}")
                await asyncio.sleep(2 ** retry_count)
                return await self._make_request(method, endpoint, json_data, retry_count + 1)
            raise MinerUServiceError(f"网络请求错误: {str(e)}")

    async def create_parsing_task(
        self,
        url: str,
        options: Optional[MinerUParseOptions] = None
    ) -> str:
        """
        创建文档解析任务（通过 URL）

        Args:
            url: 文档 URL
            options: 解析选项

        Returns:
            任务 ID
        """
        options = options or MinerUParseOptions()

        payload = {
            "url": url,
            "is_ocr": options.is_ocr,
            "enable_formula": options.enable_formula,
            "enable_table": options.enable_table,
            "language": options.language.value,
            "model_version": options.model_version,
            "extra_formats": [fmt.value for fmt in options.extra_formats]
        }

        if options.page_ranges:
            payload["page_ranges"] = options.page_ranges

        response = await self._make_request("POST", "/file-urls/batch", json_data={"files": [payload]})

        # 从批量响应中提取任务 ID
        if "batch_id" in response:
            return response["batch_id"]
        elif "task_id" in response:
            return response["task_id"]
        else:
            raise MinerUServiceError("无法获取任务 ID")

    async def get_task_status(self, task_id: str) -> MinerUParseResult:
        """
        获取任务状态和结果

        Args:
            task_id: 任务 ID

        Returns:
            解析结果
        """
        response = await self._make_request("GET", f"/extract-results/batch/{task_id}")

        # 解析状态
        status_map = {
            "pending": MinerUTaskStatus.PENDING,
            "processing": MinerUTaskStatus.PROCESSING,
            "done": MinerUTaskStatus.COMPLETED,
            "completed": MinerUTaskStatus.COMPLETED,
            "success": MinerUTaskStatus.COMPLETED,
            "failed": MinerUTaskStatus.FAILED,
            "error": MinerUTaskStatus.FAILED
        }

        raw_status = response.get("status", "pending").lower()
        status = status_map.get(raw_status, MinerUTaskStatus.PENDING)

        result = MinerUParseResult(
            task_id=task_id,
            status=status,
            progress=response.get("progress", 0)
        )

        # 如果完成，提取结果
        if status == MinerUTaskStatus.COMPLETED:
            results = response.get("extract_result", [])
            if results and len(results) > 0:
                file_result = results[0]
                result.markdown_content = file_result.get("md_content")
                result.html_content = file_result.get("html_content")
                result.pages = file_result.get("pages", [])
                result.tables = file_result.get("tables", [])
                result.formulas = file_result.get("formulas", [])
                result.images = file_result.get("images", [])

        elif status == MinerUTaskStatus.FAILED:
            result.error_message = response.get("msg", "解析失败")

        return result

    async def wait_for_completion(
        self,
        task_id: str,
        poll_interval: float = 3.0,
        max_wait_time: float = 600.0
    ) -> MinerUParseResult:
        """
        等待任务完成

        Args:
            task_id: 任务 ID
            poll_interval: 轮询间隔（秒）
            max_wait_time: 最大等待时间（秒）

        Returns:
            解析结果
        """
        elapsed = 0.0

        while elapsed < max_wait_time:
            result = await self.get_task_status(task_id)

            if result.status in [MinerUTaskStatus.COMPLETED, MinerUTaskStatus.FAILED]:
                return result

            logger.info(f"任务 {task_id} 进度: {result.progress}%")
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise MinerUServiceError(f"任务超时，已等待 {max_wait_time} 秒")

    async def parse_document_url(
        self,
        url: str,
        options: Optional[MinerUParseOptions] = None,
        wait_for_result: bool = True
    ) -> MinerUParseResult:
        """
        解析文档（通过 URL）

        Args:
            url: 文档 URL
            options: 解析选项
            wait_for_result: 是否等待结果

        Returns:
            解析结果
        """
        task_id = await self.create_parsing_task(url, options)

        if wait_for_result:
            return await self.wait_for_completion(task_id)

        return MinerUParseResult(
            task_id=task_id,
            status=MinerUTaskStatus.PENDING
        )

    async def parse_document_bytes(
        self,
        content: bytes,
        filename: str,
        options: Optional[MinerUParseOptions] = None,
        wait_for_result: bool = True
    ) -> MinerUParseResult:
        """
        解析文档（通过文件内容）

        注意: MinerU 云服务需要先上传文件获取 URL，然后再解析
        此方法会先请求上传 URL，上传文件，然后创建解析任务

        Args:
            content: 文件内容
            filename: 文件名
            options: 解析选项
            wait_for_result: 是否等待结果

        Returns:
            解析结果
        """
        options = options or MinerUParseOptions()

        # 验证文件大小
        if len(content) > self.MAX_FILE_SIZE:
            raise MinerUServiceError(f"文件大小超过限制 ({self.MAX_FILE_SIZE // 1024 // 1024}MB)")

        # 验证文件格式
        file_ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if file_ext not in self.SUPPORTED_FORMATS:
            raise MinerUServiceError(f"不支持的文件格式: {file_ext}")

        # 1. 创建批量上传任务，获取上传 URL
        payload = {
            "files": [{
                "name": filename,
                "is_ocr": options.is_ocr,
                "enable_formula": options.enable_formula,
                "enable_table": options.enable_table,
                "language": options.language.value,
                "model_version": options.model_version,
                "extra_formats": [fmt.value for fmt in options.extra_formats]
            }]
        }

        if options.page_ranges:
            payload["files"][0]["page_ranges"] = options.page_ranges

        response = await self._make_request("POST", "/file-urls/batch", json_data=payload)

        batch_id = response.get("batch_id")
        upload_urls = response.get("file_urls", [])

        if not upload_urls:
            raise MinerUServiceError("无法获取上传 URL")

        upload_url = upload_urls[0]

        # 2. 上传文件（不设置 Content-Type，让服务器自动检测）
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            upload_response = await client.put(
                upload_url,
                content=content
            )

            if upload_response.status_code not in [200, 201]:
                raise MinerUServiceError(f"文件上传失败: {upload_response.text}")

        # 3. 等待解析完成
        if wait_for_result:
            return await self.wait_for_completion(batch_id)

        return MinerUParseResult(
            task_id=batch_id,
            status=MinerUTaskStatus.PENDING
        )

    def extract_chunks_from_result(
        self,
        result: MinerUParseResult,
        chunk_size: int = 1500,
        chunk_overlap: int = 200
    ) -> List[MinerUChunk]:
        """
        从解析结果中提取分块

        Args:
            result: MinerU 解析结果
            chunk_size: 分块大小
            chunk_overlap: 重叠大小

        Returns:
            分块列表
        """
        if result.status != MinerUTaskStatus.COMPLETED:
            raise MinerUServiceError("解析未完成，无法提取分块")

        chunks: List[MinerUChunk] = []
        chunk_index = 0

        # 1. 处理 Markdown 内容（主要文本）
        if result.markdown_content:
            text_chunks = self._split_text(
                result.markdown_content,
                chunk_size,
                chunk_overlap
            )

            for i, text in enumerate(text_chunks):
                # 尝试从内容中提取页码
                page_number = self._extract_page_number(text)
                section = self._extract_section(text)

                chunks.append(MinerUChunk(
                    content=text,
                    chunk_index=chunk_index,
                    page_number=page_number,
                    section=section,
                    chunk_type="text",
                    metadata={"source": "markdown"}
                ))
                chunk_index += 1

        # 2. 处理表格（作为独立分块）
        if result.tables:
            for table in result.tables:
                table_content = table.get("content", "")
                if table_content:
                    chunks.append(MinerUChunk(
                        content=table_content,
                        chunk_index=chunk_index,
                        page_number=table.get("page_number"),
                        chunk_type="table",
                        metadata={
                            "source": "table",
                            "rows": table.get("rows"),
                            "cols": table.get("cols")
                        }
                    ))
                    chunk_index += 1

        # 3. 处理公式（作为独立分块或合并到上下文）
        if result.formulas:
            for formula in result.formulas:
                latex = formula.get("latex", "")
                if latex:
                    chunks.append(MinerUChunk(
                        content=f"$$\n{latex}\n$$",
                        chunk_index=chunk_index,
                        page_number=formula.get("page_number"),
                        chunk_type="formula",
                        metadata={"source": "formula", "latex": latex}
                    ))
                    chunk_index += 1

        return chunks

    def _split_text(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[str]:
        """
        智能文本分割

        优先按段落分割，保持语义完整性
        """
        if not text:
            return []

        # 按段落分割
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # 如果当前段落加上已有内容不超过限制，合并
            if len(current_chunk) + len(para) + 2 <= chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                # 保存当前块
                if current_chunk:
                    chunks.append(current_chunk)

                # 如果单个段落超过限制，按句子分割
                if len(para) > chunk_size:
                    sentences = self._split_into_sentences(para)
                    current_chunk = ""
                    for sent in sentences:
                        if len(current_chunk) + len(sent) + 1 <= chunk_size:
                            if current_chunk:
                                current_chunk += " " + sent
                            else:
                                current_chunk = sent
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            current_chunk = sent
                else:
                    current_chunk = para

        # 保存最后一块
        if current_chunk:
            chunks.append(current_chunk)

        # 添加重叠
        if chunk_overlap > 0 and len(chunks) > 1:
            overlapped_chunks = []
            for i, chunk in enumerate(chunks):
                if i > 0:
                    # 从前一块末尾取重叠内容
                    prev_chunk = chunks[i - 1]
                    overlap_text = prev_chunk[-chunk_overlap:] if len(prev_chunk) > chunk_overlap else prev_chunk
                    chunk = overlap_text + "\n\n" + chunk
                overlapped_chunks.append(chunk)
            return overlapped_chunks

        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """按句子分割文本"""
        import re
        # 支持中英文句子分割
        sentences = re.split(r'(?<=[。！？.!?])\s*', text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_page_number(self, text: str) -> Optional[int]:
        """从文本中提取页码"""
        import re
        match = re.search(r'\[Page\s*(\d+)\]', text)
        if match:
            return int(match.group(1))
        return None

    def _extract_section(self, text: str) -> Optional[str]:
        """从文本中提取章节标题"""
        import re
        # 匹配 Markdown 标题
        match = re.search(r'^#+\s+(.+)$', text, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None


# 单例实例
_mineru_service: Optional[MinerUService] = None


def get_mineru_service() -> MinerUService:
    """获取 MinerU 服务单例"""
    global _mineru_service
    if _mineru_service is None:
        _mineru_service = MinerUService()
    return _mineru_service
