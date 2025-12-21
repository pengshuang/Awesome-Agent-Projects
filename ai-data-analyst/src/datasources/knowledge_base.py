"""
知识库数据源
基于向量检索的知识库
"""

from pathlib import Path
from typing import Any, Dict, Optional, List
from loguru import logger

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from .base import DataSource
from config.settings import SystemConfig


class KnowledgeBaseSource(DataSource):
    """知识库数据源（基于向量检索）"""
    
    def __init__(self, name: str, kb_dir: Optional[str] = None):
        """
        初始化知识库数据源
        
        Args:
            name: 数据源名称
            kb_dir: 知识库文档目录（可选，默认使用配置中的路径）
        """
        super().__init__(name, "knowledge_base")
        self.kb_dir = Path(kb_dir) if kb_dir else SystemConfig.KNOWLEDGE_BASE_DIR
        self.index_dir = SystemConfig.CACHE_DIR / f"kb_index_{name}"
        self.index: Optional[VectorStoreIndex] = None
        self.documents: List = []
        
    def connect(self) -> bool:
        """加载或构建知识库索引"""
        try:
            # 确保目录存在
            self.kb_dir.mkdir(parents=True, exist_ok=True)
            self.index_dir.mkdir(parents=True, exist_ok=True)
            
            # 尝试从磁盘加载索引
            if self._index_exists():
                logger.info(f"📚 正在从磁盘加载知识库索引: {self.index_dir}")
                storage_context = StorageContext.from_defaults(
                    persist_dir=str(self.index_dir)
                )
                self.index = load_index_from_storage(storage_context)
                logger.info(f"✅ 知识库索引加载成功")
                return True
            else:
                # 构建新索引
                return self._build_index()
                
        except Exception as e:
            logger.error(f"❌ 知识库连接失败: {e}")
            return False
    
    def _index_exists(self) -> bool:
        """检查索引是否存在"""
        required_files = ['docstore.json', 'index_store.json']
        return all((self.index_dir / f).exists() for f in required_files)
    
    def _build_index(self) -> bool:
        """构建知识库索引"""
        try:
            logger.info(f"📖 正在构建知识库索引...")
            
            # 检查是否有文档
            doc_files = list(self.kb_dir.glob('**/*'))
            doc_files = [f for f in doc_files if f.is_file() and not f.name.startswith('.')]
            
            if not doc_files:
                logger.warning(f"⚠️  知识库目录为空: {self.kb_dir}")
                logger.info(f"提示：请将文档放入 {self.kb_dir} 目录")
                # 创建空索引
                from llama_index.core.schema import Document
                self.documents = [Document(text="知识库为空，请添加文档")]
                self.index = VectorStoreIndex.from_documents(self.documents)
                return True
            
            # 加载文档
            logger.info(f"📄 正在加载 {len(doc_files)} 个文档...")
            reader = SimpleDirectoryReader(
                input_dir=str(self.kb_dir),
                recursive=True,
            )
            self.documents = reader.load_data()
            
            logger.info(f"✅ 已加载 {len(self.documents)} 个文档块")
            
            # 构建索引
            logger.info(f"🔨 正在构建向量索引...")
            self.index = VectorStoreIndex.from_documents(self.documents)
            
            # 持久化索引
            logger.info(f"💾 正在保存索引到磁盘...")
            self.index.storage_context.persist(persist_dir=str(self.index_dir))
            
            logger.info(f"✅ 知识库索引构建成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 构建知识库索引失败: {e}")
            return False
    
    def query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        查询知识库
        
        Args:
            query: 查询问题
            **kwargs: 额外参数
                - top_k: 返回top k个结果（默认5）
                - similarity_threshold: 相似度阈值
            
        Returns:
            查询结果
        """
        if self.index is None:
            return {
                "success": False,
                "data": None,
                "error": "知识库未初始化",
                "metadata": {}
            }
        
        try:
            top_k = kwargs.get('top_k', 5)
            
            logger.info(f"🔍 正在知识库中检索: {query}")
            
            # 创建查询引擎
            query_engine = self.index.as_query_engine(
                similarity_top_k=top_k,
            )
            
            # 执行查询
            response = query_engine.query(query)
            
            # 提取检索到的节点
            retrieved_nodes = []
            if hasattr(response, 'source_nodes'):
                for node in response.source_nodes:
                    retrieved_nodes.append({
                        'text': node.node.text,
                        'score': node.score,
                        'metadata': node.node.metadata,
                    })
            
            logger.info(f"✅ 检索成功，找到 {len(retrieved_nodes)} 个相关文档")
            
            return {
                "success": True,
                "data": {
                    "answer": str(response),
                    "retrieved_docs": retrieved_nodes,
                },
                "error": None,
                "metadata": {
                    "query": query,
                    "top_k": top_k,
                    "doc_count": len(retrieved_nodes),
                }
            }
            
        except Exception as e:
            error_msg = f"知识库查询失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "data": None,
                "error": error_msg,
                "metadata": {}
            }
    
    def get_schema(self) -> Optional[str]:
        """
        获取知识库信息
        
        Returns:
            知识库描述字符串
        """
        try:
            schema_parts = []
            
            schema_parts.append(f"知识库: {self.name}")
            schema_parts.append(f"文档目录: {self.kb_dir}")
            schema_parts.append(f"索引目录: {self.index_dir}")
            
            # 统计文档数量
            doc_files = list(self.kb_dir.glob('**/*'))
            doc_files = [f for f in doc_files if f.is_file() and not f.name.startswith('.')]
            
            schema_parts.append(f"文档数量: {len(doc_files)}")
            schema_parts.append(f"文档块数量: {len(self.documents)}")
            
            if doc_files:
                schema_parts.append("\n文档列表:")
                schema_parts.append("-" * 50)
                for doc_file in doc_files[:10]:  # 只显示前10个
                    relative_path = doc_file.relative_to(self.kb_dir)
                    schema_parts.append(f"  - {relative_path}")
                
                if len(doc_files) > 10:
                    schema_parts.append(f"  ... 还有 {len(doc_files) - 10} 个文档")
            
            return "\n".join(schema_parts)
            
        except Exception as e:
            logger.error(f"❌ 获取知识库信息失败: {e}")
            return None
    
    def rebuild_index(self) -> bool:
        """重建索引"""
        logger.info(f"🔄 正在重建知识库索引...")
        return self._build_index()
    
    def close(self):
        """清理资源"""
        self.index = None
        self.documents = []
        logger.info(f"🔒 已释放知识库资源: {self.name}")
