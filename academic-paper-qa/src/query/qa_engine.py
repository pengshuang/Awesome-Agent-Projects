"""
问答引擎模块
"""

from typing import Optional

from llama_index.core import VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from loguru import logger

from config import SystemConfig


class QAEngine:
    """问答引擎"""
    
    def __init__(
        self,
        index: VectorStoreIndex,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
    ):
        """
        初始化问答引擎
        
        Args:
            index: 向量索引
            top_k: 检索 Top-K 文档数量
            similarity_threshold: 相似度阈值
        """
        self.index = index
        self.top_k = top_k or SystemConfig.RETRIEVAL_TOP_K
        self.similarity_threshold = similarity_threshold or SystemConfig.RETRIEVAL_SIMILARITY_THRESHOLD
        
        # 创建查询引擎
        self.query_engine = self._create_query_engine()
        
        logger.info(f"问答引擎已初始化: top_k={self.top_k}")
    
    def _create_query_engine(self) -> RetrieverQueryEngine:
        """创建查询引擎"""
        
        # 创建检索器
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=self.top_k,
        )
        
        # 创建查询引擎
        query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever,
            # 可以添加更多配置
        )
        
        return query_engine
    
    def query(self, question: str) -> str:
        """
        执行问答查询
        
        Args:
            question: 用户问题
            
        Returns:
            生成的回答
        """
        logger.info(f"执行问答查询: {question[:50]}...")
        
        response = self.query_engine.query(question)
        
        return str(response)
    
    def query_with_metadata(self, question: str) -> dict:
        """
        执行问答查询并返回元数据
        
        Args:
            question: 用户问题
            
        Returns:
            包含回答和元数据的字典
        """
        response = self.query_engine.query(question)
        
        # 提取源节点信息
        sources = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                if node.score >= self.similarity_threshold:
                    source_info = {
                        "file_name": node.metadata.get("file_name", "未知"),
                        "score": node.score,
                        "text_snippet": node.text[:150] + "..." if len(node.text) > 150 else node.text,
                    }
                    sources.append(source_info)
        
        return {
            "answer": str(response),
            "sources": sources,
            "metadata": response.metadata if hasattr(response, 'metadata') else {}
        }


__all__ = ["QAEngine"]
