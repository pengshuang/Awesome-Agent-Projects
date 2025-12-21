"""
系统配置模块 (使用 Pydantic 进行数据验证)
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入 Pydantic 配置模型
from src.models.config import SystemSettings

# 创建全局配置实例
settings = SystemSettings()

# 向后兼容的配置类
class SystemConfig:
    """系统配置类 (向后兼容层)"""
    
    # 项目根目录
    PROJECT_ROOT = settings.project_root
    
    # 数据目录
    DATA_DIR = settings.data_dir
    DATABASE_DIR = settings.database_dir
    FILES_DIR = settings.files_dir
    KNOWLEDGE_BASE_DIR = settings.knowledge_base_dir
    CACHE_DIR = settings.cache_dir
    
    # 日志目录
    LOG_DIR = settings.log_dir
    
    # 输出目录
    OUTPUT_DIR = settings.output_dir
    CHAT_HISTORY_DIR = settings.chat_history_dir
    
    # LLM 配置
    LLM_API_KEY: Optional[str] = settings.llm_api_key
    LLM_API_BASE: str = settings.llm_api_base
    LLM_MODEL: str = settings.llm_model
    TEMPERATURE: float = settings.temperature
    
    # Embedding 配置
    EMBEDDING_PROVIDER: str = settings.embedding_provider
    EMBEDDING_MODEL_NAME: str = settings.embedding_model_name
    EMBEDDING_API_KEY: Optional[str] = settings.embedding_api_key
    
    # 多轮对话配置
    MAX_HISTORY_TURNS: int = settings.max_history_turns
    
    # Web 搜索配置
    ENABLE_WEB_SEARCH: bool = settings.enable_web_search
    WEB_SEARCH_API_KEY: Optional[str] = settings.web_search_api_key
    
    # NL2SQL 配置
    SQL_DIALECT: str = settings.sql_dialect
    
    @classmethod
    def ensure_directories(cls):
        """确保必要的目录存在"""
        settings.ensure_directories()
