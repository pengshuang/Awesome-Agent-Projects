"""
日志配置模块
"""

import sys
from pathlib import Path
from loguru import logger

from config.settings import get_config


def setup_logger():
    """配置日志系统"""
    # 获取配置实例
    config = get_config()
    
    # 移除默认的 handler
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=config.log_level,
        colorize=True,
    )
    
    # 添加文件输出
    logger.add(
        config.logs_dir / "app.log",
        rotation="500 MB",
        retention="10 days",
        level=config.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    )
    
    logger.info("日志系统已初始化")
