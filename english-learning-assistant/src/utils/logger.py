"""日志工具模块"""

import sys
from pathlib import Path
from loguru import logger
from config.settings import settings


def setup_logger():
    """配置日志系统"""
    
    # 移除默认处理器
    logger.remove()
    
    # 控制台输出 - 彩色日志
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if settings.DEBUG else "INFO",
        colorize=True,
    )
    
    # 文件输出 - 普通日志
    logger.add(
        settings.LOG_DIR / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )
    
    # 错误日志单独记录
    logger.add(
        settings.LOG_DIR / "error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="50 MB",
        retention="60 days",
        compression="zip",
        encoding="utf-8",
    )
    
    # API调用日志
    logger.add(
        settings.LOG_DIR / "api.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="INFO",
        rotation="50 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        filter=lambda record: "API" in record["message"],
    )
    
    return logger


# 初始化全局logger
app_logger = setup_logger()


def log_api_call(api_name: str, prompt: str, model: str = ""):
    """记录API调用信息
    
    Args:
        api_name: API名称
        prompt: 完整的Prompt内容
        model: 使用的模型名称
    """
    log_message = f"""
{'='*80}
API调用: {api_name}
模型: {model}
{'='*80}
Prompt内容:
{prompt}
{'='*80}
"""
    app_logger.info(log_message)
