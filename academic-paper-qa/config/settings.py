"""
学术论文问答系统 - 配置管理模块

基于 LlamaIndex 0.14+ Settings 全局配置
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager
from loguru import logger

from .llm_config import get_llm, get_embedding_model


# 加载环境变量
load_dotenv()


class SystemConfig:
    """系统配置类"""
    
    # 路径配置
    BASE_DIR = Path(__file__).parent.parent  # academic-paper-qa 目录
    DATA_DIR = BASE_DIR / "data"
    DOCUMENTS_DIR = DATA_DIR / "documents"
    PROCESSED_DIR = DATA_DIR / "processed"
    VECTOR_STORE_DIR = DATA_DIR / "vector_store"
    CACHE_DIR = DATA_DIR / "cache"
    LOGS_DIR = BASE_DIR / "logs"
    
    # 向量数据库配置
    VECTOR_STORE = os.getenv("VECTOR_STORE", "chroma")
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(VECTOR_STORE_DIR / "chroma"))
    CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "academic_papers")
    
    # RAG 配置
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))
    RETRIEVAL_SIMILARITY_THRESHOLD = float(os.getenv("RETRIEVAL_SIMILARITY_THRESHOLD", "0.7"))
    
    # Reranking 配置
    ENABLE_RERANKING = os.getenv("ENABLE_RERANKING", "false").lower() == "true"
    RERANKER_MODEL = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base")
    RERANKER_TOP_N = int(os.getenv("RERANKER_TOP_N", "3"))
    
    # Web 搜索配置
    ENABLE_WEB_SEARCH = os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"
    
    # 系统配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
    
    @classmethod
    def ensure_directories(cls):
        """确保所有必要的目录存在"""
        for directory in [
            cls.DATA_DIR,
            cls.DOCUMENTS_DIR,
            cls.PROCESSED_DIR,
            cls.VECTOR_STORE_DIR,
            cls.CACHE_DIR,
            cls.LOGS_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)
        logger.info("所有必要目录已创建")


def initialize_settings(
    embedding_provider: Optional[str] = None,
) -> None:
    """
    初始化 LlamaIndex Settings 全局配置
    
    Args:
        embedding_provider: Embedding 提供商（openai, huggingface, local）
    """
    # 确保目录存在
    SystemConfig.ensure_directories()
    
    # 配置日志
    logger.add(
        SystemConfig.LOGS_DIR / "app.log",
        rotation="500 MB",
        level=SystemConfig.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    
    # 获取 LLM
    llm = get_llm()
    Settings.llm = llm
    logger.info(f"LLM 已配置: {os.getenv('LLM_MODEL', 'N/A')}")
    
    # 获取 Embedding 模型
    embed_model = get_embedding_model(embedding_provider)
    Settings.embed_model = embed_model
    logger.info(f"Embedding 模型已配置: {embedding_provider or os.getenv('EMBEDDING_PROVIDER', 'huggingface')}")
    
    # 配置 Chunk 参数
    Settings.chunk_size = SystemConfig.CHUNK_SIZE
    Settings.chunk_overlap = SystemConfig.CHUNK_OVERLAP
    logger.info(f"Chunk 配置: size={SystemConfig.CHUNK_SIZE}, overlap={SystemConfig.CHUNK_OVERLAP}")
    
    # 配置回调管理器（可选）
    Settings.callback_manager = CallbackManager()
    
    logger.info("LlamaIndex Settings 全局配置初始化完成")


# 导出配置
__all__ = ["SystemConfig", "initialize_settings"]
