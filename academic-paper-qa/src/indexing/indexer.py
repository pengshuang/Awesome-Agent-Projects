"""
索引构建器模块
"""

from pathlib import Path
from typing import List, Optional

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from loguru import logger

from config import SystemConfig
from ..loaders.document_loader import DocumentLoader
from .vector_store import VectorStoreManager


class DocumentIndexer:
    """文档索引构建器"""
    
    def __init__(
        self,
        vector_store_type: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ):
        """
        初始化索引构建器
        
        Args:
            vector_store_type: 向量库类型
            chunk_size: 分块大小
            chunk_overlap: 分块重叠大小
        """
        # 使用配置中的值或传入的参数
        vector_store_type = vector_store_type or SystemConfig.VECTOR_STORE
        self.vector_store_manager = VectorStoreManager(store_type=vector_store_type)
        
        # 文档加载器
        self.document_loader = DocumentLoader(
            recursive=True,
            clean_text=True,
            preserve_formatting=True,
        )
        
        # 分块器
        self.chunk_size = chunk_size or SystemConfig.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or SystemConfig.CHUNK_OVERLAP
        
        self.text_splitter = SentenceSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        
        logger.info(f"索引构建器已初始化: chunk_size={self.chunk_size}, overlap={self.chunk_overlap}")
    
    def load_documents_from_directory(self, directory: str | Path) -> List[Document]:
        """
        从目录加载所有支持的文档
        
        Args:
            directory: 文档目录路径
            
        Returns:
            Document 列表
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        # 使用新的 DocumentLoader 加载
        documents = self.document_loader.load_documents(input_dir=directory)
        
        # 打印统计信息
        if documents:
            self.document_loader.print_stats(documents)
        
        return documents
    
    def build_index(
        self,
        documents: Optional[List[Document]] = None,
        document_dir: Optional[str | Path] = None,
    ) -> VectorStoreIndex:
        """
        构建向量索引
        
        Args:
            documents: 文档列表（优先）
            document_dir: 文档目录路径（备选）
            
        Returns:
            VectorStoreIndex 实例
        """
        # 加载文档
        if documents is None:
            if document_dir is None:
                document_dir = SystemConfig.DOCUMENTS_DIR
            documents = self.load_documents_from_directory(document_dir)
        
        if not documents:
            raise ValueError("没有找到任何文档，无法构建索引")
        
        # 文本分块
        logger.info("开始文本分块...")
        nodes = self.text_splitter.get_nodes_from_documents(documents)
        logger.info(f"文本分块完成，共 {len(nodes)} 个节点")
        
        # 创建索引
        storage_context = self.vector_store_manager.get_storage_context()
        index = self.vector_store_manager.create_index(
            documents=documents,
            storage_context=storage_context,
        )
        
        return index
    
    def load_index(self) -> VectorStoreIndex:
        """
        从持久化存储加载索引
        
        Returns:
            VectorStoreIndex 实例
        """
        logger.info("从持久化存储加载索引...")
        
        storage_context = self.vector_store_manager.get_storage_context()
        index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store_manager.vector_store,
            storage_context=storage_context,
        )
        
        logger.info("索引加载完成")
        
        return index


__all__ = ["DocumentIndexer"]
