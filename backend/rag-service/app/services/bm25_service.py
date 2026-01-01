# ============================================================
# BM25 Service - 关键词检索服务
# ============================================================

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import math
import jieba
from collections import defaultdict
from sqlalchemy.orm import Session

from app.models.chunk import Chunk


@dataclass
class BM25Result:
    """BM25 检索结果"""
    chunk_id: str
    document_id: str
    content: str
    page_number: Optional[int]
    score: float
    metadata: Dict[str, Any]


class BM25Service:
    """
    BM25 关键词检索服务

    使用 Okapi BM25 算法实现关键词检索
    支持中英文分词
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        初始化 BM25 参数

        Args:
            k1: 词频饱和参数 (默认 1.5)
            b: 文档长度归一化参数 (默认 0.75)
        """
        self.k1 = k1
        self.b = b

        # 索引数据结构
        self.doc_count = 0
        self.avg_doc_len = 0
        self.doc_lengths: Dict[str, int] = {}  # chunk_id -> doc_length
        self.term_doc_freq: Dict[str, int] = defaultdict(int)  # term -> df
        self.inverted_index: Dict[str, Dict[str, int]] = defaultdict(dict)  # term -> {chunk_id: tf}

        # 文档元数据
        self.doc_metadata: Dict[str, Dict[str, Any]] = {}

    def tokenize(self, text: str) -> List[str]:
        """
        中英文分词

        Args:
            text: 输入文本

        Returns:
            词语列表
        """
        # 使用 jieba 分词
        tokens = list(jieba.cut(text.lower()))
        # 过滤空白和单字符
        tokens = [t.strip() for t in tokens if len(t.strip()) > 1]
        return tokens

    def build_index(self, chunks: List[Dict[str, Any]]) -> None:
        """
        构建 BM25 索引

        Args:
            chunks: 分块列表，每个分块包含 id, content, document_id, page_number, metadata
        """
        self.doc_count = len(chunks)
        total_length = 0

        for chunk in chunks:
            chunk_id = str(chunk["id"])
            content = chunk["content"]
            tokens = self.tokenize(content)
            doc_len = len(tokens)

            self.doc_lengths[chunk_id] = doc_len
            total_length += doc_len

            # 存储元数据
            self.doc_metadata[chunk_id] = {
                "document_id": str(chunk.get("document_id", "")),
                "content": content,
                "page_number": chunk.get("page_number"),
                "metadata": chunk.get("metadata", {})
            }

            # 统计词频
            term_freq: Dict[str, int] = defaultdict(int)
            for token in tokens:
                term_freq[token] += 1

            # 更新倒排索引
            for term, tf in term_freq.items():
                if chunk_id not in self.inverted_index[term]:
                    self.term_doc_freq[term] += 1
                self.inverted_index[term][chunk_id] = tf

        self.avg_doc_len = total_length / self.doc_count if self.doc_count > 0 else 0

    def build_index_from_db(self, db: Session, user_id: str, document_ids: Optional[List[str]] = None) -> None:
        """
        从数据库构建索引

        Args:
            db: 数据库会话
            user_id: 用户ID
            document_ids: 可选的文档ID列表过滤
        """
        query = db.query(Chunk).filter(Chunk.user_id == user_id)
        if document_ids:
            query = query.filter(Chunk.document_id.in_(document_ids))

        chunks = query.all()

        chunk_dicts = [
            {
                "id": str(chunk.id),
                "content": chunk.content,
                "document_id": str(chunk.document_id),
                "page_number": chunk.page_number,
                "metadata": chunk.extra_data or {}
            }
            for chunk in chunks
        ]

        self.build_index(chunk_dicts)

    def _compute_idf(self, term: str) -> float:
        """计算 IDF 值"""
        df = self.term_doc_freq.get(term, 0)
        if df == 0:
            return 0
        return math.log((self.doc_count - df + 0.5) / (df + 0.5) + 1)

    def _compute_bm25_score(self, query_terms: List[str], chunk_id: str) -> float:
        """计算单个文档的 BM25 分数"""
        score = 0
        doc_len = self.doc_lengths.get(chunk_id, 0)

        for term in query_terms:
            if term not in self.inverted_index:
                continue

            tf = self.inverted_index[term].get(chunk_id, 0)
            if tf == 0:
                continue

            idf = self._compute_idf(term)

            # BM25 公式
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len)

            score += idf * (numerator / denominator)

        return score

    def search(
        self,
        query: str,
        top_k: int = 10,
        document_ids: Optional[List[str]] = None
    ) -> List[BM25Result]:
        """
        BM25 检索

        Args:
            query: 查询文本
            top_k: 返回数量
            document_ids: 限定文档ID列表

        Returns:
            检索结果列表
        """
        query_terms = self.tokenize(query)
        if not query_terms:
            return []

        # 获取候选文档 (包含至少一个查询词的文档)
        candidate_docs = set()
        for term in query_terms:
            if term in self.inverted_index:
                candidate_docs.update(self.inverted_index[term].keys())

        # 按文档ID过滤
        if document_ids:
            document_ids_set = set(document_ids)
            candidate_docs = {
                doc_id for doc_id in candidate_docs
                if self.doc_metadata.get(doc_id, {}).get("document_id") in document_ids_set
            }

        # 计算分数并排序
        scores: List[tuple] = []
        for chunk_id in candidate_docs:
            score = self._compute_bm25_score(query_terms, chunk_id)
            if score > 0:
                scores.append((chunk_id, score))

        scores.sort(key=lambda x: x[1], reverse=True)

        # 构建结果
        results = []
        for chunk_id, score in scores[:top_k]:
            meta = self.doc_metadata.get(chunk_id, {})
            results.append(BM25Result(
                chunk_id=chunk_id,
                document_id=meta.get("document_id", ""),
                content=meta.get("content", ""),
                page_number=meta.get("page_number"),
                score=score,
                metadata=meta.get("metadata", {})
            ))

        return results

    def add_document(self, chunk: Dict[str, Any]) -> None:
        """
        增量添加单个文档到索引

        Args:
            chunk: 分块数据
        """
        chunk_id = str(chunk["id"])
        content = chunk["content"]
        tokens = self.tokenize(content)
        doc_len = len(tokens)

        # 更新统计
        old_total = self.avg_doc_len * self.doc_count
        self.doc_count += 1
        self.doc_lengths[chunk_id] = doc_len
        self.avg_doc_len = (old_total + doc_len) / self.doc_count

        # 存储元数据
        self.doc_metadata[chunk_id] = {
            "document_id": str(chunk.get("document_id", "")),
            "content": content,
            "page_number": chunk.get("page_number"),
            "metadata": chunk.get("metadata", {})
        }

        # 统计词频并更新索引
        term_freq: Dict[str, int] = defaultdict(int)
        for token in tokens:
            term_freq[token] += 1

        for term, tf in term_freq.items():
            if chunk_id not in self.inverted_index[term]:
                self.term_doc_freq[term] += 1
            self.inverted_index[term][chunk_id] = tf

    def remove_document(self, chunk_id: str) -> None:
        """
        从索引中移除文档

        Args:
            chunk_id: 分块ID
        """
        if chunk_id not in self.doc_lengths:
            return

        doc_len = self.doc_lengths[chunk_id]

        # 更新统计
        old_total = self.avg_doc_len * self.doc_count
        self.doc_count -= 1
        del self.doc_lengths[chunk_id]

        if self.doc_count > 0:
            self.avg_doc_len = (old_total - doc_len) / self.doc_count
        else:
            self.avg_doc_len = 0

        # 从倒排索引中移除
        terms_to_remove = []
        for term, doc_dict in self.inverted_index.items():
            if chunk_id in doc_dict:
                del doc_dict[chunk_id]
                self.term_doc_freq[term] -= 1
                if self.term_doc_freq[term] == 0:
                    terms_to_remove.append(term)

        for term in terms_to_remove:
            del self.inverted_index[term]
            del self.term_doc_freq[term]

        # 移除元数据
        if chunk_id in self.doc_metadata:
            del self.doc_metadata[chunk_id]

    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        return {
            "doc_count": self.doc_count,
            "avg_doc_len": self.avg_doc_len,
            "vocab_size": len(self.term_doc_freq)
        }
