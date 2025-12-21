"""
学术论文问答系统 - 配置管理模块

基于 LlamaIndex 0.14+ Settings 全局配置和 Pydantic 数据验证
"""

from typing import Optional

from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager
from loguru import logger

from .models import get_config
from .llm_config import get_llm, get_embedding_model


# 加载环境变量
load_dotenv()


def initialize_settings(
    embedding_provider: Optional[str] = None,
) -> None:
    """
    初始化 LlamaIndex Settings 全局配置
    
    Args:
        embedding_provider: Embedding 提供商（openai, huggingface, fastembed）
    """
    # 获取配置
    config = get_config()
    
    # 确保目录存在
    config.system.ensure_directories()
    
    # 配置日志
    logger.add(
        config.system.logs_dir / "app.log",
        rotation="500 MB",
        level=config.system.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    
    # 获取 LLM
    llm = get_llm()
    Settings.llm = llm
    logger.info(f"LLM 已配置: {config.llm.model}")
    
    # 获取 Embedding 模型
    embed_model = get_embedding_model(embedding_provider)
    Settings.embed_model = embed_model
    logger.info(f"Embedding 模型已配置: {config.embedding.provider} - {config.embedding.model_name}")
    
    # 配置 Chunk 参数
    Settings.chunk_size = config.rag.chunk_size
    Settings.chunk_overlap = config.rag.chunk_overlap
    logger.info(f"Chunk 配置: size={config.rag.chunk_size}, overlap={config.rag.chunk_overlap}")
    
    # 配置回调管理器（可选）
    Settings.callback_manager = CallbackManager()
    
    logger.info("LlamaIndex Settings 全局配置初始化完成")


# 导出配置（保持向后兼容）
class SystemConfig:
    """系统配置类（向后兼容包装器）"""
    
    @classmethod
    def __getattribute__(cls, name):
        """动态获取配置属性"""
        if name in ['__class__', '__dict__']:
            return object.__getattribute__(cls, name)
        
        config = get_config()
        
        # 路径配置映射
        path_mapping = {
            'BASE_DIR': config.system.base_dir,
            'DATA_DIR': config.system.data_dir,
            'DOCUMENTS_DIR': config.system.documents_dir,
            'PROCESSED_DIR': config.system.processed_dir,
            'VECTOR_STORE_DIR': config.system.vector_store_dir,
            'CACHE_DIR': config.system.cache_dir,
            'LOGS_DIR': config.system.logs_dir,
        }
        
        if name in path_mapping:
            return path_mapping[name]
        
        # 向量数据库配置映射
        vector_mapping = {
            'VECTOR_STORE': config.vector_store.store,
            'CHROMA_PERSIST_DIR': str(config.vector_store.chroma_persist_dir),
            'CHROMA_COLLECTION_NAME': config.vector_store.chroma_collection_name,
        }
        
        if name in vector_mapping:
            return vector_mapping[name]
        
        # RAG 配置映射
        rag_mapping = {
            'CHUNK_SIZE': config.rag.chunk_size,
            'CHUNK_OVERLAP': config.rag.chunk_overlap,
            'RETRIEVAL_TOP_K': config.rag.retrieval_top_k,
            'RETRIEVAL_SIMILARITY_THRESHOLD': config.rag.retrieval_similarity_threshold,
            'ENABLE_RERANKING': config.rag.enable_reranking,
            'RERANKER_MODEL': config.rag.reranker_model,
            'RERANKER_TOP_N': config.rag.reranker_top_n,
        }
        
        if name in rag_mapping:
            return rag_mapping[name]
        
        # Web 搜索配置映射
        web_mapping = {
            'ENABLE_WEB_SEARCH': config.web_search.enable_web_search,
        }
        
        if name in web_mapping:
            return web_mapping[name]
        
        # 系统配置映射
        system_mapping = {
            'LOG_LEVEL': config.system.log_level,
            'ENABLE_CACHE': config.system.enable_cache,
            'MAX_WORKERS': config.system.max_workers,
        }
        
        if name in system_mapping:
            return system_mapping[name]
        
        if name == 'ensure_directories':
            return config.system.ensure_directories
        
        raise AttributeError(f"'{cls.__name__}' object has no attribute '{name}'")


# 导出
__all__ = ["SystemConfig", "initialize_settings", "get_config"]

