"""
系统初始化模块

提供系统初始化功能，包括配置验证和 LlamaIndex Settings 设置
"""

import os
import sys
from pathlib import Path

from loguru import logger

# 导入新配置系统
from config import SystemConfig, initialize_settings, get_llm, get_embedding_model


def setup_logger():
    """设置日志系统"""
    # 确保日志目录存在
    SystemConfig.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台处理器
    logger.add(
        sys.stderr,
        level=SystemConfig.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    )
    
    # 添加文件处理器
    log_file = SystemConfig.LOGS_DIR / "app.log"
    logger.add(
        log_file,
        level=SystemConfig.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="500 MB",
        retention="10 days",
        encoding="utf-8",
    )
    
    logger.info(f"日志系统已初始化: {log_file}")


def print_system_info():
    """打印系统配置信息"""
    logger.info("=" * 70)
    logger.info("系统配置信息")
    logger.info("=" * 70)
    logger.info(f"文档目录: {SystemConfig.DOCUMENTS_DIR}")
    logger.info(f"向量存储目录: {SystemConfig.VECTOR_STORE_DIR}")
    logger.info(f"向量存储类型: {SystemConfig.VECTOR_STORE}")
    logger.info(f"Chunk 大小: {SystemConfig.CHUNK_SIZE}")
    logger.info(f"Chunk 重叠: {SystemConfig.CHUNK_OVERLAP}")
    logger.info(f"检索 Top-K: {SystemConfig.RETRIEVAL_TOP_K}")
    logger.info(f"LLM 模型: {os.getenv('LLM_MODEL', 'N/A')}")
    logger.info(f"Embedding 提供商: {os.getenv('EMBEDDING_PROVIDER', 'huggingface')}")
    logger.info("=" * 70)


def initialize_system():
    """
    初始化整个系统
    
    包括：
    1. 设置日志
    2. 确保必要目录存在
    3. 初始化 LlamaIndex Settings（LLM、Embedding、Chunk 参数等）
    """
    # 设置日志
    setup_logger()
    
    # 打印系统信息
    print_system_info()
    
    # 初始化 LlamaIndex Settings
    logger.info("开始初始化 LlamaIndex Settings...")
    initialize_settings()
    logger.info("系统初始化完成！")


__all__ = [
    "setup_logger",
    "print_system_info",
    "initialize_system",
]
