"""
向量存储管理模块
"""

import os
from pathlib import Path
from typing import Optional

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.vector_stores import VectorStore
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.vector_stores.qdrant import QdrantVectorStore
from loguru import logger

try:
    import chromadb
except ImportError:
    chromadb = None

try:
    from qdrant_client import QdrantClient
except ImportError:
    QdrantClient = None


class VectorStoreManager:
    """向量存储管理器"""
    
    def __init__(
        self,
        store_type: str = "chroma",
        persist_dir: Optional[str] = None,
        collection_name: str = "academic_papers",
    ):
        """
        初始化向量存储管理器
        
        Args:
            store_type: 向量库类型（chroma, qdrant）
            persist_dir: 持久化目录
            collection_name: 集合名称
        """
        self.store_type = store_type.lower()
        self.collection_name = collection_name
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./data/vector_store/chroma")
        
        # 创建持久化目录
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        
        self.vector_store = self._create_vector_store()
        logger.info(f"向量存储已初始化: {self.store_type}")
    
    def _create_vector_store(self) -> VectorStore:
        """创建向量存储实例"""
        
        if self.store_type == "chroma":
            if chromadb is None:
                raise ImportError("请安装 chromadb: pip install chromadb")
            
            # 创建 Chroma 客户端
            client = chromadb.PersistentClient(path=self.persist_dir)
            
            # 获取或创建集合
            collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "学术论文向量存储"}
            )
            
            # 创建 ChromaVectorStore
            vector_store = ChromaVectorStore(chroma_collection=collection)
            
            logger.info(f"Chroma 向量库已创建: {self.persist_dir}")
            return vector_store
        
        elif self.store_type == "qdrant":
            if QdrantClient is None:
                raise ImportError("请安装 qdrant-client: pip install qdrant-client")
            
            # Qdrant 配置
            qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
            qdrant_api_key = os.getenv("QDRANT_API_KEY")
            
            # 创建 Qdrant 客户端
            client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
                # 或使用本地持久化
                # path=self.persist_dir
            )
            
            # 创建 QdrantVectorStore
            vector_store = QdrantVectorStore(
                client=client,
                collection_name=self.collection_name,
            )
            
            logger.info(f"Qdrant 向量库已创建: {qdrant_url}")
            return vector_store
        
        else:
            raise ValueError(f"不支持的向量库类型: {self.store_type}")
    
    def get_storage_context(self) -> StorageContext:
        """
        获取存储上下文
        
        Returns:
            StorageContext 实例
        """
        return StorageContext.from_defaults(vector_store=self.vector_store)
    
    def create_index(self, documents, storage_context=None, show_progress=True):
        """
        创建向量索引
        
        Args:
            documents: 文档列表
            storage_context: 存储上下文
            show_progress: 是否显示进度
            
        Returns:
            VectorStoreIndex 实例
        """
        if storage_context is None:
            storage_context = self.get_storage_context()
        
        logger.info(f"开始创建向量索引，文档数量: {len(documents)}")
        
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=show_progress,
        )
        
        logger.info("向量索引创建完成")
        
        return index


__all__ = ["VectorStoreManager"]
