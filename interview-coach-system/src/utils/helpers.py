"""
辅助函数模块
"""

import re
from pathlib import Path
from datetime import datetime


def format_time(seconds: float) -> str:
    """
    格式化时间
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.2f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}小时"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_filename(file_path: str) -> str:
    """
    提取文件名（不含扩展名）
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件名
    """
    return Path(file_path).stem


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    # 移除非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 移除多余的空格
    filename = re.sub(r'\s+', ' ', filename)
    # 移除首尾空格
    filename = filename.strip()
    return filename


def get_timestamp() -> str:
    """
    获取当前时间戳字符串
    
    Returns:
        时间戳字符串
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")
