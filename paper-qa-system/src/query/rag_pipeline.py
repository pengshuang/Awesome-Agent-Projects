"""
RAG 流水线模块

基于 LlamaIndex 0.14+ RAG Pipeline 特性
"""

from typing import List, Optional

from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.response_synthesizers import ResponseMode, get_response_synthesizer
from loguru import logger

from config import SystemConfig


class RAGPipeline:
    """RAG 流水线"""
    
    def __init__(
        self,
        index: VectorStoreIndex,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        response_mode: str = "compact",
    ):
        """
        初始化 RAG 流水线
        
        Args:
            index: 向量索引
            top_k: 检索 Top-K 文档数量
            similarity_threshold: 相似度阈值
            response_mode: 响应模式（compact, tree_summarize, refine）
        """
        self.index = index
        self.top_k = top_k or SystemConfig.RETRIEVAL_TOP_K
        self.similarity_threshold = similarity_threshold or SystemConfig.RETRIEVAL_SIMILARITY_THRESHOLD
        
        # 创建检索器
        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=self.top_k,
        )
        
        # 创建响应合成器
        self.response_synthesizer = get_response_synthesizer(
            response_mode=ResponseMode(response_mode),
        )
        
        logger.info(f"RAG 流水线已初始化: top_k={self.top_k}, threshold={self.similarity_threshold}")
    
    def query(self, query_text: str) -> str:
        """
        执行 RAG 查询
        
        Args:
            query_text: 查询文本
            
        Returns:
            生成的回答
        """
        logger.info(f"执行 RAG 查询: {query_text[:50]}...")
        
        # 检索相关文档
        retrieved_nodes = self.retriever.retrieve(query_text)
        
        # 过滤低相似度节点
        filtered_nodes = [
            node for node in retrieved_nodes
            if node.score >= self.similarity_threshold
        ]
        
        logger.info(f"检索到 {len(retrieved_nodes)} 个节点，过滤后 {len(filtered_nodes)} 个")
        
        if not filtered_nodes:
            return "抱歉，没有找到相关的文档内容。"
        
        # 合成响应
        response = self.response_synthesizer.synthesize(
            query=query_text,
            nodes=filtered_nodes,
        )
        
        return str(response)
    
    def query_with_sources(self, query_text: str) -> dict:
        """
        执行 RAG 查询并返回来源信息
        
        Args:
            query_text: 查询文本
            
        Returns:
            包含回答和来源的字典
        """
        # 检索相关文档
        retrieved_nodes = self.retriever.retrieve(query_text)
        
        # 过滤低相似度节点
        filtered_nodes = [
            node for node in retrieved_nodes
            if node.score >= self.similarity_threshold
        ]
        
        if not filtered_nodes:
            return {
                "answer": "抱歉，没有找到相关的文档内容。",
                "sources": []
            }
        
        # 合成响应
        response = self.response_synthesizer.synthesize(
            query=query_text,
            nodes=filtered_nodes,
        )
        
        # 提取来源信息
        sources = []
        for node in filtered_nodes:
            source_info = {
                "file_name": node.metadata.get("file_name", "未知"),
                "score": node.score,
                "text": node.text[:200] + "..." if len(node.text) > 200 else node.text,
            }
            sources.append(source_info)
        
        return {
            "answer": str(response),
            "sources": sources
        }


__all__ = ["RAGPipeline"]
