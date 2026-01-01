# ============================================================
# Chunking Service - 智能分块服务
# ============================================================
# 支持多种分块策略：
# 1. 固定大小分块 (带重叠)
# 2. 语义分块 (基于段落/章节)
# 3. 递归分块 (按层级分割)
# 4. PDF 页面感知分块

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ChunkingStrategy(str, Enum):
    """分块策略"""
    FIXED = "fixed"           # 固定大小
    SEMANTIC = "semantic"     # 语义分块
    RECURSIVE = "recursive"   # 递归分块
    PAGE_AWARE = "page_aware" # 页面感知


@dataclass
class ChunkResult:
    """分块结果"""
    content: str
    chunk_index: int
    page_number: Optional[int] = None
    section: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ChunkingService:
    """
    智能分块服务

    支持多种分块策略，针对中文文本优化
    """

    # 中文句子结束符
    CHINESE_SENTENCE_ENDS = ['。', '！', '？', '；', '…']
    # 英文句子结束符
    ENGLISH_SENTENCE_ENDS = ['.', '!', '?']
    # 段落分隔符
    PARAGRAPH_SEPARATORS = ['\n\n', '\r\n\r\n']
    # 章节标题模式
    SECTION_PATTERNS = [
        r'^第[一二三四五六七八九十百千]+[章节篇部]',  # 中文章节
        r'^[一二三四五六七八九十]+[、．.]',           # 中文序号
        r'^\d+[\.、]\s*\S+',                          # 数字序号
        r'^#{1,6}\s+',                                # Markdown 标题
        r'^\[Page \d+\]',                             # PDF 页面标记
    ]

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        strategy: ChunkingStrategy = ChunkingStrategy.SEMANTIC
    ):
        """
        初始化分块服务

        Args:
            chunk_size: 目标分块大小（字符数）
            chunk_overlap: 分块重叠大小
            strategy: 分块策略
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy

        # 编译正则表达式
        self._section_patterns = [re.compile(p, re.MULTILINE) for p in self.SECTION_PATTERNS]

    def chunk(
        self,
        text: str,
        strategy: Optional[ChunkingStrategy] = None,
        **kwargs
    ) -> List[ChunkResult]:
        """
        对文本进行分块

        Args:
            text: 输入文本
            strategy: 分块策略（可覆盖默认策略）
            **kwargs: 额外参数

        Returns:
            分块结果列表
        """
        if not text or not text.strip():
            return []

        strategy = strategy or self.strategy

        if strategy == ChunkingStrategy.FIXED:
            return self._fixed_chunk(text, **kwargs)
        elif strategy == ChunkingStrategy.SEMANTIC:
            return self._semantic_chunk(text, **kwargs)
        elif strategy == ChunkingStrategy.RECURSIVE:
            return self._recursive_chunk(text, **kwargs)
        elif strategy == ChunkingStrategy.PAGE_AWARE:
            return self._page_aware_chunk(text, **kwargs)
        else:
            return self._semantic_chunk(text, **kwargs)

    def _fixed_chunk(self, text: str, **kwargs) -> List[ChunkResult]:
        """
        固定大小分块（带句子边界优化）

        尝试在句子结束处分割，避免截断句子
        """
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))

            # 如果不是最后一块，尝试在句子边界分割
            if end < len(text):
                best_end = self._find_sentence_boundary(text, start, end)
                if best_end > start:
                    end = best_end

            chunk_content = text[start:end].strip()
            if chunk_content:
                chunks.append(ChunkResult(
                    content=chunk_content,
                    chunk_index=chunk_index,
                    metadata={
                        "start_char": start,
                        "end_char": end,
                        "strategy": "fixed"
                    }
                ))
                chunk_index += 1

            # 计算下一个起始位置（带重叠）
            start = max(start + 1, end - self.chunk_overlap)

        return chunks

    def _semantic_chunk(self, text: str, **kwargs) -> List[ChunkResult]:
        """
        语义分块

        基于段落和章节边界进行分块，保持语义完整性
        """
        # 1. 先按段落分割
        paragraphs = self._split_paragraphs(text)

        chunks = []
        current_chunk = []
        current_length = 0
        current_section = None
        chunk_index = 0

        for para in paragraphs:
            para_text = para.strip()
            if not para_text:
                continue

            # 检查是否是章节标题
            section = self._extract_section(para_text)
            if section:
                # 如果当前有内容，先保存
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk, chunk_index, current_section
                    ))
                    chunk_index += 1
                    current_chunk = []
                    current_length = 0
                current_section = section

            para_length = len(para_text)

            # 如果单个段落超过 chunk_size，需要进一步分割
            if para_length > self.chunk_size:
                # 先保存当前积累的内容
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk, chunk_index, current_section
                    ))
                    chunk_index += 1
                    current_chunk = []
                    current_length = 0

                # 对长段落进行句子级分割
                sub_chunks = self._split_long_paragraph(para_text)
                for sub in sub_chunks:
                    chunks.append(ChunkResult(
                        content=sub,
                        chunk_index=chunk_index,
                        section=current_section,
                        metadata={"strategy": "semantic", "sub_split": True}
                    ))
                    chunk_index += 1

            # 如果添加这个段落会超过限制
            elif current_length + para_length + 1 > self.chunk_size:
                # 保存当前块
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk, chunk_index, current_section
                    ))
                    chunk_index += 1

                # 开始新块
                current_chunk = [para_text]
                current_length = para_length
            else:
                # 添加到当前块
                current_chunk.append(para_text)
                current_length += para_length + 1  # +1 for newline

        # 保存最后一块
        if current_chunk:
            chunks.append(self._create_chunk(
                current_chunk, chunk_index, current_section
            ))

        return chunks

    def _recursive_chunk(self, text: str, **kwargs) -> List[ChunkResult]:
        """
        递归分块

        按层级分隔符递归分割：
        1. 先按章节分割
        2. 再按段落分割
        3. 最后按句子分割
        """
        # 分隔符层级（从大到小）
        separators = [
            '\n\n\n',    # 章节
            '\n\n',      # 段落
            '\n',        # 行
            '。',        # 中文句号
            '.',         # 英文句号
            '；',        # 中文分号
            ';',         # 英文分号
            ' ',         # 空格
        ]

        chunks = self._recursive_split(text, separators, 0)

        # 转换为 ChunkResult
        results = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                results.append(ChunkResult(
                    content=chunk.strip(),
                    chunk_index=i,
                    metadata={"strategy": "recursive"}
                ))

        return results

    def _recursive_split(
        self,
        text: str,
        separators: List[str],
        level: int
    ) -> List[str]:
        """递归分割辅助函数"""
        if level >= len(separators):
            # 没有更多分隔符，直接按固定大小分割
            return self._force_split(text)

        separator = separators[level]
        parts = text.split(separator)

        chunks = []
        current = ""

        for part in parts:
            test_chunk = current + separator + part if current else part

            if len(test_chunk) <= self.chunk_size:
                current = test_chunk
            else:
                if current:
                    chunks.append(current)

                # 如果单个部分太大，递归处理
                if len(part) > self.chunk_size:
                    sub_chunks = self._recursive_split(part, separators, level + 1)
                    chunks.extend(sub_chunks)
                    current = ""
                else:
                    current = part

        if current:
            chunks.append(current)

        return chunks

    def _page_aware_chunk(self, text: str, **kwargs) -> List[ChunkResult]:
        """
        PDF 页面感知分块

        识别 [Page N] 标记，保留页面信息
        """
        # 按页面标记分割
        page_pattern = re.compile(r'\[Page (\d+)\]')

        chunks = []
        chunk_index = 0
        current_page = None

        # 找到所有页面标记的位置
        matches = list(page_pattern.finditer(text))

        if not matches:
            # 没有页面标记，使用语义分块
            return self._semantic_chunk(text, **kwargs)

        # 按页面处理
        for i, match in enumerate(matches):
            page_num = int(match.group(1))
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

            page_content = text[start:end].strip()
            if not page_content:
                continue

            # 对每页内容进行分块
            if len(page_content) <= self.chunk_size:
                chunks.append(ChunkResult(
                    content=page_content,
                    chunk_index=chunk_index,
                    page_number=page_num,
                    metadata={"strategy": "page_aware"}
                ))
                chunk_index += 1
            else:
                # 页面内容太长，进行子分块
                sub_chunks = self._semantic_chunk(page_content)
                for sub in sub_chunks:
                    sub.chunk_index = chunk_index
                    sub.page_number = page_num
                    sub.metadata["strategy"] = "page_aware"
                    chunks.append(sub)
                    chunk_index += 1

        return chunks

    def _split_paragraphs(self, text: str) -> List[str]:
        """按段落分割文本"""
        # 首先尝试双换行分割
        paragraphs = re.split(r'\n\s*\n', text)

        result = []
        for para in paragraphs:
            # 进一步处理单换行的情况
            if '\n' in para and len(para) > self.chunk_size:
                result.extend(para.split('\n'))
            else:
                result.append(para)

        return result

    def _split_long_paragraph(self, text: str) -> List[str]:
        """
        分割长段落为多个句子组
        """
        # 中英文句子分割
        sentence_pattern = re.compile(
            r'([^。！？.!?；;]+[。！？.!?；;]?)'
        )
        sentences = sentence_pattern.findall(text)

        chunks = []
        current = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current) + len(sentence) + 1 <= self.chunk_size:
                current = current + sentence if not current else current + sentence
            else:
                if current:
                    chunks.append(current)

                # 如果单个句子太长，强制分割
                if len(sentence) > self.chunk_size:
                    chunks.extend(self._force_split(sentence))
                    current = ""
                else:
                    current = sentence

        if current:
            chunks.append(current)

        return chunks if chunks else [text]

    def _force_split(self, text: str) -> List[str]:
        """强制按固定大小分割"""
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk.strip():
                chunks.append(chunk.strip())
        return chunks if chunks else [text]

    def _find_sentence_boundary(self, text: str, start: int, end: int) -> int:
        """
        在指定范围内找到最佳句子边界
        """
        search_range = min(100, end - start)  # 向后搜索的范围

        # 所有句子结束符
        all_ends = self.CHINESE_SENTENCE_ENDS + self.ENGLISH_SENTENCE_ENDS

        best_pos = end
        for sep in all_ends:
            pos = text.rfind(sep, start, end + search_range)
            if pos > start and pos < best_pos:
                best_pos = pos + len(sep)

        return best_pos if best_pos != end else end

    def _extract_section(self, text: str) -> Optional[str]:
        """
        提取章节标题
        """
        for pattern in self._section_patterns:
            match = pattern.match(text)
            if match:
                # 返回整行作为章节标题
                end_pos = text.find('\n')
                return text[:end_pos] if end_pos > 0 else text[:50]
        return None

    def _create_chunk(
        self,
        paragraphs: List[str],
        index: int,
        section: Optional[str]
    ) -> ChunkResult:
        """
        从段落列表创建分块
        """
        content = '\n'.join(paragraphs)
        return ChunkResult(
            content=content,
            chunk_index=index,
            section=section,
            metadata={"strategy": "semantic", "paragraph_count": len(paragraphs)}
        )


# 便捷函数
def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    strategy: str = "semantic"
) -> List[dict]:
    """
    对文本进行分块（便捷函数）

    Args:
        text: 输入文本
        chunk_size: 分块大小
        chunk_overlap: 重叠大小
        strategy: 分块策略 (fixed, semantic, recursive, page_aware)

    Returns:
        分块字典列表
    """
    service = ChunkingService(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        strategy=ChunkingStrategy(strategy)
    )

    results = service.chunk(text)

    return [
        {
            "content": r.content,
            "chunk_index": r.chunk_index,
            "page_number": r.page_number,
            "section": r.section,
            "metadata": r.metadata
        }
        for r in results
    ]
