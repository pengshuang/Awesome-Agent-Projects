"""
辅助工具函数
"""

from pathlib import Path
from typing import List


def get_supported_files(directory: Path, extensions: List[str]) -> List[Path]:
    """
    获取目录下所有支持的文件
    
    Args:
        directory: 目录路径
        extensions: 支持的扩展名列表（如 ['.pdf', '.docx']）
        
    Returns:
        文件路径列表
    """
    files = []
    
    for ext in extensions:
        files.extend(directory.glob(f"**/*{ext}"))
    
    return files


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        格式化后的字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} TB"


__all__ = ["get_supported_files", "format_file_size"]
