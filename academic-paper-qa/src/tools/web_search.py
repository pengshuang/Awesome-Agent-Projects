"""
Web 搜索工具模块
"""

from typing import List, Dict, Optional
import os

from loguru import logger

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None


class WebSearchTool:
    """Web 搜索工具（使用 DuckDuckGo）"""
    
    def __init__(self, max_results: int = 5):
        """
        初始化 Web 搜索工具
        
        Args:
            max_results: 最大返回结果数
        """
        if DDGS is None:
            raise ImportError("请安装 duckduckgo-search: pip install duckduckgo-search")
        
        self.max_results = max_results
        logger.info("Web 搜索工具已初始化")
    
    def search(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
        """
        执行 Web 搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数（覆盖默认值）
            
        Returns:
            搜索结果列表
        """
        max_results = max_results or self.max_results
        
        logger.info(f"执行 Web 搜索: {query}")
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            
            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                })
            
            logger.info(f"找到 {len(formatted_results)} 个结果")
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Web 搜索失败: {e}")
            return []
    
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


__all__ = ["WebSearchTool"]
