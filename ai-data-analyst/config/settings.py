"""
系统配置模块
"""

import os
from pathlib import Path
from typing import Optional


class SystemConfig:
    """系统配置类"""
    
    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent.parent
    
    # 数据目录
    DATA_DIR = PROJECT_ROOT / "data"
    DATABASE_DIR = DATA_DIR / "databases"
    FILES_DIR = DATA_DIR / "files"
    KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
    CACHE_DIR = DATA_DIR / "cache"
    
    # 日志目录
    LOG_DIR = PROJECT_ROOT / "logs"
    
    # 输出目录
    OUTPUT_DIR = PROJECT_ROOT / "output"
    CHAT_HISTORY_DIR = OUTPUT_DIR / "chat_history"
    
    # LLM 配置
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY")
    LLM_API_BASE: str = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    
    # Embedding 配置
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "huggingface")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-zh-v1.5")
    EMBEDDING_API_KEY: Optional[str] = os.getenv("EMBEDDING_API_KEY")
    
    # 多轮对话配置
    MAX_HISTORY_TURNS: int = int(os.getenv("MAX_HISTORY_TURNS", "10"))
    
    # Web 搜索配置
    ENABLE_WEB_SEARCH: bool = os.getenv("ENABLE_WEB_SEARCH", "false").lower() == "true"
    WEB_SEARCH_API_KEY: Optional[str] = os.getenv("WEB_SEARCH_API_KEY")
    
    # NL2SQL 配置
    SQL_DIALECT: str = os.getenv("SQL_DIALECT", "sqlite")
    
    @classmethod
    def ensure_directories(cls):
        """确保必要的目录存在"""
        for dir_path in [
            cls.DATA_DIR,
            cls.DATABASE_DIR,
            cls.FILES_DIR,
            cls.KNOWLEDGE_BASE_DIR,
            cls.CACHE_DIR,
            cls.LOG_DIR,
            cls.OUTPUT_DIR,
            cls.CHAT_HISTORY_DIR,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
