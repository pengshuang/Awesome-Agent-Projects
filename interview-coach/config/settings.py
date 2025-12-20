"""
模拟面试系统 - 配置管理模块
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from loguru import logger

from .llm_config import get_llm_client


# 加载环境变量
load_dotenv()


class SystemConfig:
    """系统配置类"""
    
    # 路径配置
    BASE_DIR = Path(__file__).parent.parent  # interview-coach 目录
    DATA_DIR = BASE_DIR / "data"
    RESUMES_DIR = DATA_DIR / "resumes"
    CACHE_DIR = DATA_DIR / "cache"
    LOGS_DIR = BASE_DIR / "logs"
    OUTPUT_DIR = BASE_DIR / "output"
    
    # LLM 配置
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_API_BASE = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Web 搜索配置
    ENABLE_WEB_SEARCH = os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"
    WEB_SEARCH_ENGINE = os.getenv("WEB_SEARCH_ENGINE", "duckduckgo")
    MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    
    # 面试配置
    MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "20"))  # 多轮对话历史轮数
    INTERVIEW_MODE = os.getenv("INTERVIEW_MODE", "technical")  # technical, behavioral, comprehensive
    
    # 系统配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    
    @classmethod
    def ensure_directories(cls):
        """确保所有必要的目录存在"""
        for directory in [
            cls.DATA_DIR,
            cls.RESUMES_DIR,
            cls.CACHE_DIR,
            cls.LOGS_DIR,
            cls.OUTPUT_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)
        logger.info("所有必要目录已创建")


def initialize_settings() -> None:
    """
    初始化系统配置
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
    
    # 验证 LLM 配置
    try:
        client, model, temperature = get_llm_client()
        logger.info(f"LLM 已配置: {model}")
    except Exception as e:
        logger.error(f"LLM 配置失败: {e}")
        raise
    
    logger.info("系统初始化完成")
