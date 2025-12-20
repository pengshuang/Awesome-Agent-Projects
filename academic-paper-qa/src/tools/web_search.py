"""
Web 搜索工具模块
支持多个搜索引擎：DuckDuckGo (ddgs)、Google (通过 SerpAPI)、SearXNG
"""

from typing import List, Dict, Optional
import os
import json

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
    3. Google（需要 SerpAPI Key）
    """
    
    def __init__(
        self, 
        max_results: int = 5,
        engine: str = "duckduckgo",
        serpapi_key: Optional[str] = None,
        searxng_url: Optional[str] = None
    ):
        """
        初始化 Web 搜索工具
        
        Args:
            max_results: 最大返回结果数
            engine: 搜索引擎 ("duckduckgo", "searxng", "serpapi")
            serpapi_key: SerpAPI 的 API Key（使用 serpapi 时需要）
            searxng_url: SearXNG 实例 URL（使用 searxng 时需要）
        """
        self.max_results = max_results
        self.engine = engine.lower()
        self.serpapi_key = serpapi_key or os.getenv("SERPAPI_KEY")
        self.searxng_url = searxng_url or os.getenv("SEARXNG_URL", "https://searx.be")
        
        # 验证依赖
        if self.engine == "duckduckgo" and DDGS is None:
            raise ImportError("请安装 duckduckgo-search: pip install duckduckgo-search")
        
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
        elif self.engine == "serpapi":
            engines_to_try = ["serpapi", "searxng", "duckduckgo"]
        else:
            engines_to_try = ["duckduckgo", "searxng"]
        
        # 逐个尝试搜索引擎
        for engine in engines_to_try:
            try:
                if engine == "duckduckgo":
                    results = self._search_duckduckgo(query, max_results)
                elif engine == "searxng":
                    results = self._search_searxng(query, max_results)
                elif engine == "serpapi":
                    results = self._search_serpapi(query, max_results)
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
        """使用 DuckDuckGo 搜索 (ddgs 新包)"""
        if DDGS is None:
            raise ImportError("DuckDuckGo 未安装，请运行: pip install ddgs")
        
        try:
            # 使用新的 ddgs API
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
                    # SearXNG API 端点
                    api_url = f"{instance_url}/search"
                    
                    params = {
                        "q": query,
                        "format": "json",
                        "categories": "general",
                        "pageno": 1
                    }
                    
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                    }
                    
                    response = requests.get(api_url, params=params, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    results = data.get("results", [])[:max_results]
                    
                    if results:
                        # 格式化结果
                        formatted_results = []
                        for result in results:
                            formatted_results.append({
                                "title": result.get("title", ""),
                                "url": result.get("url", ""),
                                "snippet": result.get("content", ""),
                            })
                        
                        logger.debug(f"成功使用 SearXNG 实例: {instance_url}")
                        return formatted_results
                    
                except Exception as e:
                    logger.debug(f"SearXNG 实例 {instance_url} 失败: {e}")
                    continue
            
            # 所有实例都失败
            raise Exception("所有 SearXNG 实例均不可用")
        
        except Exception as e:
            logger.debug(f"SearXNG 搜索详细错误: {e}")
            raise
    
    def _search_serpapi(self, query: str, max_results: int) -> List[Dict]:
        """使用 SerpAPI (Google) 搜索"""
        if not self.serpapi_key:
            raise ValueError("SerpAPI Key 未配置")
        
        try:
            api_url = "https://serpapi.com/search"
            
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": max_results,
                "engine": "google"
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("organic_results", [])
            
            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                })
            
            return formatted_results
        
        except Exception as e:
            logger.debug(f"SerpAPI 搜索详细错误: {e}")
            raise
    
    def search_academic(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
        """
        执行学术搜索（添加学术关键词）
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        # 添加学术关键词
        academic_query = f"{query} site:arxiv.org OR site:scholar.google.com OR filetype:pdf"
        
        return self.search(academic_query, max_results)


def create_web_search_tool(
    max_results: int = 5,
    engine: Optional[str] = None
) -> WebSearchTool:
    """
    创建 Web 搜索工具的工厂函数
    
    Args:
        max_results: 最大返回结果数
        engine: 搜索引擎 ("duckduckgo", "searxng", "serpapi")，
                None 时从环境变量 WEB_SEARCH_ENGINE 读取
    
    Returns:
        WebSearchTool 实例
    """
    if engine is None:
        engine = os.getenv("WEB_SEARCH_ENGINE", "duckduckgo")
    
    return WebSearchTool(
        max_results=max_results,
        engine=engine
    )


__all__ = ["WebSearchTool", "create_web_search_tool"]
