"""
系统初始化模块
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config import initialize_settings
from src.utils import setup_logger, logger


def initialize_system():
    """初始化系统"""
    # 配置日志
    setup_logger()
    
    # 初始化配置
    initialize_settings()
    
    logger.info("=" * 70)
    logger.info("模拟面试系统已初始化")
    logger.info("=" * 70)


if __name__ == "__main__":
    initialize_system()
