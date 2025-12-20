"""
Web 搜索工具模块
支持多个搜索引擎：DuckDuckGo、SearXNG
"""

from typing import List, Dict, Optional
import os

from loguru import logger

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

try:
    import requests
except ImportError:
    requests = None


class WebSearchTool:
    """
    Web 搜索工具
    
    支持多个搜索引擎，自动降级：
    1. DuckDuckGo（默认，免费无需 API Key）
    2. SearXNG（公共实例，免费）
    """
    
    def __init__(
        self, 
        max_results: int = 5,
        engine: str = "duckduckgo",
        searxng_url: Optional[str] = None
    ):
        """
        初始化 Web 搜索工具
        
        Args:
            max_results: 最大返回结果数
            engine: 搜索引擎 ("duckduckgo", "searxng")
            searxng_url: SearXNG 实例 URL（使用 searxng 时需要）
        """
        self.max_results = max_results
        self.engine = engine.lower()
        self.searxng_url = searxng_url or os.getenv("SEARXNG_URL", "https://searx.be")
        
        # 验证依赖
        if self.engine == "duckduckgo" and DDGS is None:
            raise ImportError("请安装 duckduckgo-search: pip install ddgs")
        
        if requests is None:
            raise ImportError("请安装 requests: pip install requests")
        
        logger.info(f"Web 搜索工具已初始化 (引擎: {self.engine})")
    
    def search(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
        """
        执行 Web 搜索（自动降级）
        
        Args:
            query: 搜索查询
            max_results: 最大结果数（覆盖默认值）
            
        Returns:
            搜索结果列表
        """
        max_results = max_results or self.max_results
        
        logger.info(f"执行 Web 搜索: {query}")
        
        # 按优先级尝试不同的搜索引擎
        engines_to_try = []
        
        if self.engine == "duckduckgo":
            engines_to_try = ["duckduckgo", "searxng"]
        elif self.engine == "searxng":
            engines_to_try = ["searxng", "duckduckgo"]
        else:
            engines_to_try = ["duckduckgo", "searxng"]
        
        # 逐个尝试搜索引擎
        for engine in engines_to_try:
            try:
                if engine == "duckduckgo":
                    results = self._search_duckduckgo(query, max_results)
                elif engine == "searxng":
                    results = self._search_searxng(query, max_results)
                else:
                    continue
                
                if results:
                    logger.info(f"✓ 使用 {engine} 找到 {len(results)} 个结果")
                    return results
                else:
                    logger.warning(f"⚠️ {engine} 未返回结果，尝试下一个引擎...")
                    
            except Exception as e:
                logger.warning(f"⚠️ {engine} 搜索失败: {e}，尝试下一个引擎...")
                continue
        
        logger.error("✗ 所有搜索引擎均失败")
        return []
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict]:
        """使用 DuckDuckGo 搜索"""
        if DDGS is None:
            raise ImportError("DuckDuckGo 未安装，请运行: pip install ddgs")
        
        try:
            # 使用 ddgs API
            results = DDGS().text(query, max_results=max_results)
            
            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                })
            
            return formatted_results
        
        except Exception as e:
            logger.debug(f"DuckDuckGo 搜索详细错误: {e}")
            raise
    
    def _search_searxng(self, query: str, max_results: int) -> List[Dict]:
        """使用 SearXNG 公共实例搜索"""
        try:
            # 尝试多个 SearXNG 公共实例
            instances = [
                self.searxng_url,
                "https://searx.tiekoetter.com",
                "https://search.sapti.me", 
                "https://searx.work",
            ]
            
            for instance_url in instances:
                try:
                    url = f"{instance_url}/search"
                    params = {
                        "q": query,
                        "format": "json",
                        "categories": "general",
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    results = data.get("results", [])[:max_results]
                    
                    # 格式化结果
                    formatted_results = []
                    for result in results:
                        formatted_results.append({
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "snippet": result.get("content", ""),
                        })
                    
                    if formatted_results:
                        return formatted_results
                
                except Exception as e:
                    logger.debug(f"SearXNG 实例 {instance_url} 失败: {e}")
                    continue
            
            raise Exception("所有 SearXNG 实例均失败")
        
        except Exception as e:
            logger.debug(f"SearXNG 搜索详细错误: {e}")
            raise
