"""
日志配置模块
"""

import sys
from pathlib import Path
from loguru import logger

from config import SystemConfig


def setup_logger():
    """配置日志系统"""
    # 移除默认的 handler
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=SystemConfig.LOG_LEVEL,
        colorize=True,
    )
    
    # 添加文件输出
    logger.add(
        SystemConfig.LOGS_DIR / "app.log",
        rotation="500 MB",
        retention="10 days",
        level=SystemConfig.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    )
    
    logger.info("日志系统已初始化")
