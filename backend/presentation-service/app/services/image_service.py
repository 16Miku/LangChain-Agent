# ============================================================
# Presentation Service - Image Service
# 图片服务 - 支持 Unsplash API 和本地图片
# ============================================================

import os
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from functools import lru_cache

from app.config import settings


class ImageSearchResult(BaseModel):
    """图片搜索结果"""
    id: str
    url: str  # 完整尺寸 URL
    thumb_url: str  # 缩略图 URL
    small_url: str  # 小图 URL
    regular_url: str  # 常规尺寸 URL (适合幻灯片)
    alt: str  # 图片描述
    author: str  # 作者
    author_url: str  # 作者页面
    source: str = "unsplash"  # 来源


class ImageSearchResponse(BaseModel):
    """图片搜索响应"""
    results: List[ImageSearchResult]
    total: int
    query: str


# 关键词中英文映射
KEYWORD_MAPPING: Dict[str, List[str]] = {
    # 技术/科技
    "科技": ["technology", "tech", "innovation", "digital"],
    "人工智能": ["artificial intelligence", "AI", "machine learning", "neural network"],
    "编程": ["programming", "coding", "software", "developer"],
    "数据": ["data", "analytics", "statistics", "chart"],
    "互联网": ["internet", "web", "network", "connection"],
    "云计算": ["cloud computing", "cloud", "server", "data center"],

    # 商业/办公
    "商业": ["business", "corporate", "enterprise", "company"],
    "办公": ["office", "workplace", "meeting", "desk"],
    "团队": ["team", "teamwork", "collaboration", "group"],
    "会议": ["meeting", "conference", "presentation", "boardroom"],
    "领导": ["leadership", "leader", "management", "executive"],
    "成功": ["success", "achievement", "growth", "celebration"],

    # 金融
    "金融": ["finance", "financial", "money", "banking"],
    "投资": ["investment", "investing", "stock", "market"],
    "增长": ["growth", "increase", "progress", "chart up"],

    # 教育
    "教育": ["education", "learning", "school", "study"],
    "培训": ["training", "workshop", "seminar", "course"],
    "学习": ["learning", "study", "books", "knowledge"],

    # 自然/环境
    "自然": ["nature", "natural", "landscape", "outdoor"],
    "环境": ["environment", "eco", "green", "sustainable"],
    "海洋": ["ocean", "sea", "water", "marine"],
    "山脉": ["mountain", "mountains", "peak", "summit"],
    "森林": ["forest", "trees", "woods", "nature"],

    # 城市/建筑
    "城市": ["city", "urban", "cityscape", "metropolis"],
    "建筑": ["architecture", "building", "structure", "design"],
    "夜景": ["night city", "night skyline", "city lights", "nightscape"],

    # 抽象/概念
    "创新": ["innovation", "creative", "idea", "breakthrough"],
    "未来": ["future", "futuristic", "modern", "advanced"],
    "连接": ["connection", "connected", "network", "link"],
    "合作": ["cooperation", "partnership", "together", "handshake"],
    "目标": ["goal", "target", "aim", "objective"],

    # 健康/医疗
    "健康": ["health", "healthy", "wellness", "fitness"],
    "医疗": ["medical", "healthcare", "medicine", "hospital"],

    # 通用
    "背景": ["background", "abstract", "texture", "pattern"],
    "简约": ["minimal", "minimalist", "simple", "clean"],
}


class ImageService:
    """图片服务"""

    def __init__(self):
        self.unsplash_access_key = getattr(settings, 'UNSPLASH_ACCESS_KEY', None) or os.getenv('UNSPLASH_ACCESS_KEY')
        self.base_url = "https://api.unsplash.com"

    def _translate_keyword(self, keyword: str) -> str:
        """
        将中文关键词翻译为英文
        如果没有映射，直接返回原关键词
        """
        keyword_lower = keyword.lower().strip()

        # 直接匹配
        if keyword_lower in KEYWORD_MAPPING:
            return KEYWORD_MAPPING[keyword_lower][0]

        # 部分匹配
        for cn_key, en_values in KEYWORD_MAPPING.items():
            if cn_key in keyword_lower or keyword_lower in cn_key:
                return en_values[0]

        # 没有映射，返回原关键词
        return keyword

    def _get_related_keywords(self, keyword: str) -> List[str]:
        """获取相关关键词列表"""
        keyword_lower = keyword.lower().strip()

        if keyword_lower in KEYWORD_MAPPING:
            return KEYWORD_MAPPING[keyword_lower]

        for cn_key, en_values in KEYWORD_MAPPING.items():
            if cn_key in keyword_lower or keyword_lower in cn_key:
                return en_values

        return [keyword]

    async def search_images(
        self,
        query: str,
        per_page: int = 10,
        page: int = 1,
        orientation: str = "landscape",  # landscape, portrait, squarish
    ) -> ImageSearchResponse:
        """
        搜索图片

        Args:
            query: 搜索关键词 (支持中英文)
            per_page: 每页数量
            page: 页码
            orientation: 图片方向

        Returns:
            ImageSearchResponse
        """
        # 翻译关键词
        translated_query = self._translate_keyword(query)

        # 如果没有 API Key，返回 Unsplash Source 链接 (免费但无法搜索)
        if not self.unsplash_access_key:
            return self._get_fallback_images(query, translated_query, per_page)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search/photos",
                    params={
                        "query": translated_query,
                        "per_page": per_page,
                        "page": page,
                        "orientation": orientation,
                    },
                    headers={
                        "Authorization": f"Client-ID {self.unsplash_access_key}",
                    },
                    timeout=10.0,
                )

                if response.status_code != 200:
                    print(f"[ImageService] Unsplash API error: {response.status_code}")
                    return self._get_fallback_images(query, translated_query, per_page)

                data = response.json()
                results = []

                for photo in data.get("results", []):
                    results.append(ImageSearchResult(
                        id=photo["id"],
                        url=photo["urls"]["full"],
                        thumb_url=photo["urls"]["thumb"],
                        small_url=photo["urls"]["small"],
                        regular_url=photo["urls"]["regular"],
                        alt=photo.get("alt_description") or photo.get("description") or query,
                        author=photo["user"]["name"],
                        author_url=photo["user"]["links"]["html"],
                        source="unsplash",
                    ))

                return ImageSearchResponse(
                    results=results,
                    total=data.get("total", 0),
                    query=query,
                )

        except Exception as e:
            print(f"[ImageService] Error searching images: {e}")
            return self._get_fallback_images(query, translated_query, per_page)

    def _get_fallback_images(
        self,
        original_query: str,
        translated_query: str,
        count: int = 10,
    ) -> ImageSearchResponse:
        """
        获取备用图片 (使用 Picsum Photos)
        无需 API Key，稳定可靠

        注意: Unsplash Source 已于 2023 年停止服务，改用 Picsum Photos
        """
        results = []
        keywords = self._get_related_keywords(original_query)

        for i in range(min(count, len(keywords) * 2)):
            keyword = keywords[i % len(keywords)]

            # 使用 Picsum Photos 作为备用图片源
            # 添加随机种子确保每次获取不同图片
            seed = hash(f"{keyword}_{i}") % 1000

            # Picsum Photos URL (免费，无需 API Key，稳定可靠)
            base_url = f"https://picsum.photos/seed/{seed}/1600/900"

            results.append(ImageSearchResult(
                id=f"picsum_{i}_{seed}",
                url=base_url,
                thumb_url=f"https://picsum.photos/seed/{seed}/200/150",
                small_url=f"https://picsum.photos/seed/{seed}/400/300",
                regular_url=f"https://picsum.photos/seed/{seed}/1080/720",
                alt=f"{original_query} - {keyword}",
                author="Picsum Photos",
                author_url="https://picsum.photos",
                source="picsum",
            ))

        return ImageSearchResponse(
            results=results,
            total=len(results),
            query=original_query,
        )

    async def get_random_image(
        self,
        query: Optional[str] = None,
        orientation: str = "landscape",
    ) -> Optional[ImageSearchResult]:
        """
        获取随机图片

        Args:
            query: 搜索关键词 (可选)
            orientation: 图片方向

        Returns:
            ImageSearchResult 或 None
        """
        if not self.unsplash_access_key:
            # 使用 Picsum Photos 获取随机图片
            import random
            seed = random.randint(1, 1000)
            keyword = self._translate_keyword(query) if query else "abstract"
            return ImageSearchResult(
                id=f"random_{seed}",
                url=f"https://picsum.photos/seed/{seed}/1600/900",
                thumb_url=f"https://picsum.photos/seed/{seed}/200/150",
                small_url=f"https://picsum.photos/seed/{seed}/400/300",
                regular_url=f"https://picsum.photos/seed/{seed}/1080/720",
                alt=query or "Random image",
                author="Picsum Photos",
                author_url="https://picsum.photos",
                source="picsum",
            )

        try:
            async with httpx.AsyncClient() as client:
                params = {"orientation": orientation}
                if query:
                    params["query"] = self._translate_keyword(query)

                response = await client.get(
                    f"{self.base_url}/photos/random",
                    params=params,
                    headers={
                        "Authorization": f"Client-ID {self.unsplash_access_key}",
                    },
                    timeout=10.0,
                )

                if response.status_code != 200:
                    return None

                photo = response.json()

                return ImageSearchResult(
                    id=photo["id"],
                    url=photo["urls"]["full"],
                    thumb_url=photo["urls"]["thumb"],
                    small_url=photo["urls"]["small"],
                    regular_url=photo["urls"]["regular"],
                    alt=photo.get("alt_description") or photo.get("description") or query or "Image",
                    author=photo["user"]["name"],
                    author_url=photo["user"]["links"]["html"],
                    source="unsplash",
                )

        except Exception as e:
            print(f"[ImageService] Error getting random image: {e}")
            return None

    def get_image_for_content(
        self,
        content_type: str,
        topic: Optional[str] = None,
    ) -> str:
        """
        根据内容类型获取合适的图片 URL

        Args:
            content_type: 内容类型 (cover, section, data, timeline, etc.)
            topic: 主题关键词

        Returns:
            图片 URL
        """
        # 内容类型到关键词的映射
        type_keywords = {
            "cover": ["presentation", "business", "professional"],
            "section": ["abstract", "minimal", "pattern"],
            "data": ["analytics", "chart", "data"],
            "timeline": ["time", "history", "evolution"],
            "process": ["workflow", "process", "steps"],
            "comparison": ["versus", "comparison", "contrast"],
            "quote": ["inspiration", "motivation", "quote"],
            "ending": ["thank you", "success", "celebration"],
            "contact": ["contact", "communication", "connection"],
        }

        # 选择关键词
        keywords = type_keywords.get(content_type, ["abstract", "background"])
        keyword = keywords[0]

        # 如果有主题，添加主题关键词
        if topic:
            translated_topic = self._translate_keyword(topic)
            keyword = f"{keyword}_{translated_topic}"

        # 使用 Picsum Photos (Unsplash Source 已停止服务)
        seed = hash(keyword) % 1000
        return f"https://picsum.photos/seed/{seed}/1600/900"

    def suggest_keywords_for_slide(
        self,
        title: str,
        content: str,
        layout: str,
    ) -> List[str]:
        """
        为幻灯片推荐图片关键词

        Args:
            title: 幻灯片标题
            content: 幻灯片内容
            layout: 布局类型

        Returns:
            推荐的关键词列表
        """
        suggestions = []

        # 从标题提取关键词
        for cn_key in KEYWORD_MAPPING.keys():
            if cn_key in title.lower():
                suggestions.extend(KEYWORD_MAPPING[cn_key][:2])

        # 从内容提取关键词
        for cn_key in KEYWORD_MAPPING.keys():
            if cn_key in content.lower():
                suggestions.extend(KEYWORD_MAPPING[cn_key][:1])

        # 根据布局添加默认关键词
        layout_defaults = {
            "title_cover": ["presentation", "professional"],
            "image_text": ["concept", "illustration"],
            "image_full": ["landscape", "abstract"],
            "gallery": ["collection", "portfolio"],
            "timeline": ["history", "time"],
            "process_flow": ["workflow", "process"],
        }

        if layout in layout_defaults:
            suggestions.extend(layout_defaults[layout])

        # 去重并限制数量
        seen = set()
        unique = []
        for kw in suggestions:
            if kw not in seen:
                seen.add(kw)
                unique.append(kw)
            if len(unique) >= 5:
                break

        return unique if unique else ["abstract", "background"]


# 全局图片服务实例
@lru_cache()
def get_image_service() -> ImageService:
    return ImageService()


image_service = get_image_service()
