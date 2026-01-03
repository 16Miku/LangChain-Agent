# ============================================================
# PgvectorService 自动化测试
# ============================================================
# 运行方式: cd backend/rag-service && python -m pytest tests/test_pgvector_service.py -v
# ============================================================

import pytest
import uuid
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pgvector_service import PgvectorService, get_vector_service
from app.services.milvus_service import ChunkData, VectorSearchResult
from app.config import settings


class TestPgvectorService:
    """PgvectorService 单元测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前初始化"""
        self.service = PgvectorService()
        self.service.connect()
        # 清理测试数据
        self.test_user_id = f"test-user-{uuid.uuid4().hex[:8]}"
        self.test_doc_id = f"test-doc-{uuid.uuid4().hex[:8]}"
        yield
        # 测试后清理
        self.service.delete_by_user(self.test_user_id)

    def test_connect(self):
        """测试数据库连接"""
        assert self.service.is_connected() is True
        print(f"✓ 数据库连接成功")

    def test_get_collection_stats(self):
        """测试获取统计信息"""
        stats = self.service.get_collection_stats()

        assert "name" in stats
        assert "num_entities" in stats
        assert "dimension" in stats
        assert "backend" in stats
        assert "database" in stats

        print(f"✓ 统计信息: {stats}")

    def test_insert_single_chunk(self):
        """测试插入单个分块"""
        chunk = ChunkData(
            id=str(uuid.uuid4()),
            document_id=self.test_doc_id,
            user_id=self.test_user_id,
            chunk_index=0,
            content="这是一个测试文本，用于验证插入功能。",
            page_number=1,
            embedding=[0.1] * settings.EMBEDDING_DIMENSION,
            metadata={"filename": "test.txt", "section": "第一章"}
        )

        inserted_ids = self.service.insert([chunk])

        assert len(inserted_ids) == 1
        assert inserted_ids[0] == chunk.id
        print(f"✓ 插入成功: {inserted_ids[0][:8]}...")

    def test_insert_multiple_chunks(self):
        """测试批量插入"""
        chunks = []
        for i in range(5):
            chunks.append(ChunkData(
                id=str(uuid.uuid4()),
                document_id=self.test_doc_id,
                user_id=self.test_user_id,
                chunk_index=i,
                content=f"这是第 {i+1} 个测试分块。",
                page_number=i + 1,
                embedding=[0.1 * (i + 1)] * settings.EMBEDDING_DIMENSION,
                metadata={"filename": "test.txt", "chunk": i}
            ))

        inserted_ids = self.service.insert(chunks)

        assert len(inserted_ids) == 5
        print(f"✓ 批量插入成功: {len(inserted_ids)} 条记录")

    def test_search_basic(self):
        """测试基本搜索"""
        # 先插入数据
        chunk = ChunkData(
            id=str(uuid.uuid4()),
            document_id=self.test_doc_id,
            user_id=self.test_user_id,
            chunk_index=0,
            content="机器学习是人工智能的一个分支。",
            page_number=1,
            embedding=[0.5] * settings.EMBEDDING_DIMENSION,
            metadata={"topic": "AI"}
        )
        self.service.insert([chunk])

        # 搜索
        query_embedding = [0.5] * settings.EMBEDDING_DIMENSION
        results = self.service.search(
            query_embedding=query_embedding,
            top_k=5,
            user_id=self.test_user_id
        )

        assert len(results) >= 1
        assert isinstance(results[0], VectorSearchResult)
        assert results[0].score > 0
        print(f"✓ 搜索成功: 返回 {len(results)} 条结果, 最高分={results[0].score:.4f}")

    def test_search_with_user_filter(self):
        """测试用户过滤"""
        # 插入数据
        chunk = ChunkData(
            id=str(uuid.uuid4()),
            document_id=self.test_doc_id,
            user_id=self.test_user_id,
            chunk_index=0,
            content="用户过滤测试。",
            page_number=1,
            embedding=[0.3] * settings.EMBEDDING_DIMENSION,
            metadata={}
        )
        self.service.insert([chunk])

        # 使用正确的用户ID搜索
        results = self.service.search(
            query_embedding=[0.3] * settings.EMBEDDING_DIMENSION,
            top_k=5,
            user_id=self.test_user_id
        )
        assert len(results) >= 1

        # 使用错误的用户ID搜索
        results_other = self.service.search(
            query_embedding=[0.3] * settings.EMBEDDING_DIMENSION,
            top_k=5,
            user_id="other-user-id"
        )
        assert len(results_other) == 0
        print(f"✓ 用户过滤正常")

    def test_search_with_document_filter(self):
        """测试文档过滤"""
        # 插入两个文档的数据
        doc1_id = f"doc1-{uuid.uuid4().hex[:8]}"
        doc2_id = f"doc2-{uuid.uuid4().hex[:8]}"

        chunks = [
            ChunkData(
                id=str(uuid.uuid4()),
                document_id=doc1_id,
                user_id=self.test_user_id,
                chunk_index=0,
                content="文档1的内容。",
                page_number=1,
                embedding=[0.4] * settings.EMBEDDING_DIMENSION,
                metadata={}
            ),
            ChunkData(
                id=str(uuid.uuid4()),
                document_id=doc2_id,
                user_id=self.test_user_id,
                chunk_index=0,
                content="文档2的内容。",
                page_number=1,
                embedding=[0.4] * settings.EMBEDDING_DIMENSION,
                metadata={}
            )
        ]
        self.service.insert(chunks)

        # 只搜索文档1
        results = self.service.search(
            query_embedding=[0.4] * settings.EMBEDDING_DIMENSION,
            top_k=5,
            user_id=self.test_user_id,
            document_ids=[doc1_id]
        )

        assert len(results) == 1
        assert results[0].document_id == doc1_id
        print(f"✓ 文档过滤正常")

    def test_delete_by_document(self):
        """测试按文档删除"""
        # 插入数据
        chunks = [
            ChunkData(
                id=str(uuid.uuid4()),
                document_id=self.test_doc_id,
                user_id=self.test_user_id,
                chunk_index=i,
                content=f"删除测试 {i}",
                page_number=1,
                embedding=[0.2] * settings.EMBEDDING_DIMENSION,
                metadata={}
            )
            for i in range(3)
        ]
        self.service.insert(chunks)

        # 删除
        deleted_count = self.service.delete_by_document(self.test_doc_id)

        assert deleted_count == 3

        # 验证已删除
        results = self.service.search(
            query_embedding=[0.2] * settings.EMBEDDING_DIMENSION,
            top_k=10,
            user_id=self.test_user_id,
            document_ids=[self.test_doc_id]
        )
        assert len(results) == 0
        print(f"✓ 按文档删除成功: {deleted_count} 条")

    def test_delete_by_user(self):
        """测试按用户删除"""
        temp_user = f"temp-user-{uuid.uuid4().hex[:8]}"

        # 插入数据
        chunks = [
            ChunkData(
                id=str(uuid.uuid4()),
                document_id=f"doc-{i}",
                user_id=temp_user,
                chunk_index=0,
                content=f"用户删除测试 {i}",
                page_number=1,
                embedding=[0.6] * settings.EMBEDDING_DIMENSION,
                metadata={}
            )
            for i in range(3)
        ]
        self.service.insert(chunks)

        # 删除
        deleted_count = self.service.delete_by_user(temp_user)

        assert deleted_count == 3
        print(f"✓ 按用户删除成功: {deleted_count} 条")

    def test_cosine_similarity_ranking(self):
        """测试余弦相似度排序"""
        # 插入不同相似度的向量
        base_embedding = [1.0] * settings.EMBEDDING_DIMENSION

        chunks = [
            ChunkData(
                id=str(uuid.uuid4()),
                document_id=self.test_doc_id,
                user_id=self.test_user_id,
                chunk_index=0,
                content="最相似的文档",
                page_number=1,
                embedding=[1.0] * settings.EMBEDDING_DIMENSION,  # 完全匹配
                metadata={"rank": 1}
            ),
            ChunkData(
                id=str(uuid.uuid4()),
                document_id=self.test_doc_id,
                user_id=self.test_user_id,
                chunk_index=1,
                content="较相似的文档",
                page_number=2,
                embedding=[0.8] * settings.EMBEDDING_DIMENSION,  # 较相似
                metadata={"rank": 2}
            ),
            ChunkData(
                id=str(uuid.uuid4()),
                document_id=self.test_doc_id,
                user_id=self.test_user_id,
                chunk_index=2,
                content="不太相似的文档",
                page_number=3,
                embedding=[0.3] * settings.EMBEDDING_DIMENSION,  # 不太相似
                metadata={"rank": 3}
            )
        ]
        self.service.insert(chunks)

        # 搜索
        results = self.service.search(
            query_embedding=base_embedding,
            top_k=3,
            user_id=self.test_user_id,
            document_ids=[self.test_doc_id]
        )

        assert len(results) == 3
        # 验证分数递减
        assert results[0].score >= results[1].score >= results[2].score
        print(f"✓ 相似度排序正确: {[r.score for r in results]}")


class TestGetVectorService:
    """测试 get_vector_service 工厂函数"""

    def test_returns_pgvector_by_default(self):
        """默认返回 PgvectorService"""
        service = get_vector_service()
        assert isinstance(service, PgvectorService)
        print(f"✓ get_vector_service 返回 PgvectorService")


if __name__ == "__main__":
    # 直接运行测试
    pytest.main([__file__, "-v", "--tb=short"])
