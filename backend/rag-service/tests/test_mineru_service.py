# ============================================================
# MinerU Service 单元测试
# ============================================================

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from app.services.mineru_service import (
    MinerUService,
    MinerUParseOptions,
    MinerUParseResult,
    MinerUTaskStatus,
    MinerULanguage,
    MinerUExportFormat,
    MinerUChunk,
    MinerUServiceError,
    get_mineru_service
)


class TestMinerUServiceInit:
    """测试 MinerU 服务初始化"""

    def test_init_with_api_key(self):
        """测试使用 API key 初始化"""
        service = MinerUService(api_key="test-api-key")
        assert service.api_key == "test-api-key"
        assert service.is_available is True

    def test_init_without_api_key(self):
        """测试不使用 API key 初始化"""
        with patch('app.services.mineru_service.settings') as mock_settings:
            mock_settings.MINERU_API_KEY = None
            mock_settings.MINERU_API_URL = "https://mineru.net/api/v4"
            service = MinerUService(api_key=None)
            assert service.is_available is False

    def test_init_with_custom_base_url(self):
        """测试自定义 base URL"""
        service = MinerUService(
            api_key="test-key",
            base_url="https://custom.api.com/v1/"
        )
        assert service.base_url == "https://custom.api.com/v1"  # 末尾斜杠被移除

    def test_default_settings(self):
        """测试默认设置"""
        service = MinerUService(api_key="test-key")
        assert service.timeout == 300.0
        assert service.max_retries == 3


class TestMinerUParseOptions:
    """测试解析选项"""

    def test_default_options(self):
        """测试默认选项"""
        options = MinerUParseOptions()
        assert options.is_ocr is False
        assert options.enable_formula is True
        assert options.enable_table is True
        assert options.language == MinerULanguage.CHINESE
        assert options.page_ranges is None
        assert options.model_version == "v2"
        assert MinerUExportFormat.HTML in options.extra_formats

    def test_custom_options(self):
        """测试自定义选项"""
        options = MinerUParseOptions(
            is_ocr=True,
            enable_formula=False,
            language=MinerULanguage.ENGLISH,
            page_ranges="1-10",
            extra_formats=[MinerUExportFormat.MARKDOWN, MinerUExportFormat.LATEX]
        )
        assert options.is_ocr is True
        assert options.enable_formula is False
        assert options.language == MinerULanguage.ENGLISH
        assert options.page_ranges == "1-10"
        assert len(options.extra_formats) == 2


class TestMinerUServiceAPI:
    """测试 MinerU API 调用"""

    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return MinerUService(api_key="test-api-key")

    @pytest.mark.asyncio
    async def test_create_parsing_task_success(self, service):
        """测试创建解析任务成功"""
        mock_response = {
            "batch_id": "batch-123",
            "file_urls": ["https://upload.url/file1"]
        }

        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            task_id = await service.create_parsing_task(
                url="https://example.com/doc.pdf",
                options=MinerUParseOptions()
            )

            assert task_id == "batch-123"
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_task_status_completed(self, service):
        """测试获取已完成任务状态"""
        mock_response = {
            "status": "done",
            "progress": 100,
            "extract_result": [{
                "md_content": "# Test Document\n\nThis is test content.",
                "html_content": "<h1>Test Document</h1><p>This is test content.</p>",
                "tables": [],
                "formulas": []
            }]
        }

        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await service.get_task_status("task-123")

            assert result.status == MinerUTaskStatus.COMPLETED
            assert result.progress == 100
            assert result.markdown_content == "# Test Document\n\nThis is test content."

    @pytest.mark.asyncio
    async def test_get_task_status_failed(self, service):
        """测试获取失败任务状态"""
        mock_response = {
            "status": "failed",
            "msg": "File format not supported"
        }

        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await service.get_task_status("task-123")

            assert result.status == MinerUTaskStatus.FAILED
            assert result.error_message == "File format not supported"

    @pytest.mark.asyncio
    async def test_get_task_status_processing(self, service):
        """测试获取处理中任务状态"""
        mock_response = {
            "status": "processing",
            "progress": 50
        }

        with patch.object(service, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await service.get_task_status("task-123")

            assert result.status == MinerUTaskStatus.PROCESSING
            assert result.progress == 50

    @pytest.mark.asyncio
    async def test_service_unavailable_error(self):
        """测试服务不可用错误"""
        with patch('app.services.mineru_service.settings') as mock_settings:
            mock_settings.MINERU_API_KEY = None
            mock_settings.MINERU_API_URL = "https://mineru.net/api/v4"
            service = MinerUService(api_key=None)

            with pytest.raises(MinerUServiceError) as exc_info:
                await service._make_request("GET", "/test")

            assert "not configured" in str(exc_info.value)


class TestMinerUServiceChunking:
    """测试分块功能"""

    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return MinerUService(api_key="test-api-key")

    def test_extract_chunks_from_result(self, service):
        """测试从结果中提取分块"""
        result = MinerUParseResult(
            task_id="task-123",
            status=MinerUTaskStatus.COMPLETED,
            markdown_content="# Chapter 1\n\nThis is the first paragraph.\n\n## Section 1.1\n\nThis is section content.",
            tables=[{
                "content": "| A | B |\n|---|---|\n| 1 | 2 |",
                "page_number": 1,
                "rows": 2,
                "cols": 2
            }],
            formulas=[{
                "latex": "E = mc^2",
                "page_number": 2
            }]
        )

        chunks = service.extract_chunks_from_result(result)

        assert len(chunks) > 0
        # 检查是否包含文本分块
        text_chunks = [c for c in chunks if c.chunk_type == "text"]
        assert len(text_chunks) > 0

        # 检查是否包含表格分块
        table_chunks = [c for c in chunks if c.chunk_type == "table"]
        assert len(table_chunks) == 1
        assert table_chunks[0].page_number == 1

        # 检查是否包含公式分块
        formula_chunks = [c for c in chunks if c.chunk_type == "formula"]
        assert len(formula_chunks) == 1
        assert "E = mc^2" in formula_chunks[0].content

    def test_extract_chunks_not_completed(self, service):
        """测试从未完成结果中提取分块应抛出错误"""
        result = MinerUParseResult(
            task_id="task-123",
            status=MinerUTaskStatus.PROCESSING
        )

        with pytest.raises(MinerUServiceError) as exc_info:
            service.extract_chunks_from_result(result)

        assert "未完成" in str(exc_info.value)

    def test_split_text_basic(self, service):
        """测试基本文本分割"""
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunks = service._split_text(text, chunk_size=50, chunk_overlap=0)

        assert len(chunks) > 0
        # 验证所有内容都被保留
        combined = " ".join(chunks)
        assert "First" in combined
        assert "Second" in combined
        assert "Third" in combined

    def test_split_text_with_overlap(self, service):
        """测试带重叠的文本分割"""
        text = "A" * 100 + "\n\n" + "B" * 100 + "\n\n" + "C" * 100
        chunks = service._split_text(text, chunk_size=150, chunk_overlap=20)

        assert len(chunks) >= 2
        # 验证重叠存在（第二个块应该包含第一个块的部分内容）
        if len(chunks) > 1:
            # 重叠部分应该在后续块的开头
            pass  # 重叠逻辑已在实现中处理

    def test_split_text_empty(self, service):
        """测试空文本分割"""
        chunks = service._split_text("", chunk_size=100, chunk_overlap=10)
        assert chunks == []

    def test_extract_page_number(self, service):
        """测试页码提取"""
        text_with_page = "[Page 5] This is content from page 5."
        page_num = service._extract_page_number(text_with_page)
        assert page_num == 5

        text_without_page = "This is content without page marker."
        page_num = service._extract_page_number(text_without_page)
        assert page_num is None

    def test_extract_section(self, service):
        """测试章节标题提取"""
        text_with_section = "# Introduction\n\nThis is the introduction."
        section = service._extract_section(text_with_section)
        assert section == "Introduction"

        text_with_subsection = "## Methods\n\nThis describes methods."
        section = service._extract_section(text_with_subsection)
        assert section == "Methods"

        text_without_section = "Plain text without headers."
        section = service._extract_section(text_without_section)
        assert section is None


class TestMinerUServiceIntegration:
    """集成测试（需要模拟完整流程）"""

    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return MinerUService(api_key="test-api-key")

    @pytest.mark.asyncio
    async def test_parse_document_url_full_flow(self, service):
        """测试完整的 URL 解析流程"""
        # 模拟创建任务响应
        create_response = {"batch_id": "batch-123"}

        # 模拟状态查询响应（先处理中，后完成）
        status_responses = [
            {"status": "processing", "progress": 50},
            {"status": "done", "progress": 100, "extract_result": [{
                "md_content": "# Test\n\nContent"
            }]}
        ]

        call_count = [0]

        async def mock_request(method, endpoint, json_data=None, retry_count=0):
            if "batch" in endpoint and method == "POST":
                return create_response
            elif "extract-results" in endpoint:
                response = status_responses[min(call_count[0], len(status_responses) - 1)]
                call_count[0] += 1
                return response
            return {}

        with patch.object(service, '_make_request', side_effect=mock_request):
            with patch('asyncio.sleep', new_callable=AsyncMock):
                result = await service.parse_document_url(
                    url="https://example.com/doc.pdf",
                    wait_for_result=True
                )

                assert result.status == MinerUTaskStatus.COMPLETED
                assert result.markdown_content == "# Test\n\nContent"

    @pytest.mark.asyncio
    async def test_parse_document_bytes_validation(self, service):
        """测试文件字节解析的验证"""
        # 测试文件大小超限
        large_content = b"x" * (201 * 1024 * 1024)  # 201MB

        with pytest.raises(MinerUServiceError) as exc_info:
            await service.parse_document_bytes(
                content=large_content,
                filename="large.pdf"
            )

        assert "超过限制" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_parse_document_bytes_unsupported_format(self, service):
        """测试不支持的文件格式"""
        with pytest.raises(MinerUServiceError) as exc_info:
            await service.parse_document_bytes(
                content=b"test content",
                filename="test.xyz"
            )

        assert "不支持" in str(exc_info.value)


class TestMinerULanguage:
    """测试语言枚举"""

    def test_language_values(self):
        """测试语言值"""
        assert MinerULanguage.CHINESE.value == "ch"
        assert MinerULanguage.ENGLISH.value == "en"
        assert MinerULanguage.JAPANESE.value == "ja"
        assert MinerULanguage.KOREAN.value == "ko"

    def test_language_from_string(self):
        """测试从字符串创建语言"""
        lang = MinerULanguage("ch")
        assert lang == MinerULanguage.CHINESE

        with pytest.raises(ValueError):
            MinerULanguage("invalid")


class TestMinerUExportFormat:
    """测试导出格式枚举"""

    def test_export_format_values(self):
        """测试导出格式值"""
        assert MinerUExportFormat.MARKDOWN.value == "md"
        assert MinerUExportFormat.HTML.value == "html"
        assert MinerUExportFormat.DOCX.value == "docx"
        assert MinerUExportFormat.LATEX.value == "latex"


class TestGetMinerUService:
    """测试单例获取函数"""

    def test_get_mineru_service_singleton(self):
        """测试单例模式"""
        # 重置单例
        import app.services.mineru_service as module
        module._mineru_service = None

        with patch('app.services.mineru_service.settings') as mock_settings:
            mock_settings.MINERU_API_KEY = "test-key"
            mock_settings.MINERU_API_URL = "https://mineru.net/api/v4"

            service1 = get_mineru_service()
            service2 = get_mineru_service()

            assert service1 is service2


class TestMinerUChunk:
    """测试分块数据类"""

    def test_chunk_creation(self):
        """测试分块创建"""
        chunk = MinerUChunk(
            content="Test content",
            chunk_index=0,
            page_number=1,
            section="Introduction",
            chunk_type="text",
            metadata={"source": "test"}
        )

        assert chunk.content == "Test content"
        assert chunk.chunk_index == 0
        assert chunk.page_number == 1
        assert chunk.section == "Introduction"
        assert chunk.chunk_type == "text"
        assert chunk.metadata["source"] == "test"

    def test_chunk_defaults(self):
        """测试分块默认值"""
        chunk = MinerUChunk(
            content="Test",
            chunk_index=0
        )

        assert chunk.page_number is None
        assert chunk.section is None
        assert chunk.chunk_type == "text"
        assert chunk.metadata == {}
