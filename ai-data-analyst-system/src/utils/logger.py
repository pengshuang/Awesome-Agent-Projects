"""
日志配置模块
"""

import sys
from pathlib import Path
from loguru import logger
from config.settings import SystemConfig


def setup_logger(log_level: str = "INFO"):
    """
    配置日志系统
    
    Args:
        log_level: 日志级别（DEBUG, INFO, WARNING, ERROR）
    """
    # 移除默认的 handler
    logger.remove()
    
    # 确保日志目录存在
    SystemConfig.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # 添加控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )
    
    # 添加文件输出（按日期轮转）
    logger.add(
        SystemConfig.LOG_DIR / "ai_data_analyst_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation="00:00",  # 每天零点轮转
        retention="30 days",  # 保留30天
        compression="zip",  # 压缩旧日志
        encoding="utf-8",
    )
    
    # 添加错误日志文件
    logger.add(
        SystemConfig.LOG_DIR / "error_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )
    
    logger.info("✅ 日志系统初始化完成")


# 导出 logger 实例
__all__ = ['logger', 'setup_logger']
