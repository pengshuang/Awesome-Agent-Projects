"""
日志工具模块
"""

import sys
from pathlib import Path
from loguru import logger


def setup_logger(
    log_file: str = "logs/app.log",
    level: str = "INFO",
    rotation: str = "500 MB",
    retention: str = "10 days",
):
    """
    设置日志配置
    
    Args:
        log_file: 日志文件路径
        level: 日志级别
        rotation: 日志轮转大小
        retention: 日志保留时间
    """
    # 创建日志目录
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台处理器
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    )
    
    # 添加文件处理器
    logger.add(
        log_file,
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation=rotation,
        retention=retention,
        encoding="utf-8",
    )
    
    logger.info(f"日志系统已初始化: {log_file}")


__all__ = ["setup_logger", "logger"]
