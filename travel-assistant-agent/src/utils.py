"""
工具函数模块
提供各种辅助功能
"""

import json
import base64
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Union
from PIL import Image

logger = logging.getLogger(__name__)


def encode_image_to_base64(image_path: Union[str, Path]) -> Optional[str]:
    """
    将图片编码为 Base64 字符串
    
    Args:
        image_path: 图片路径
    
    Returns:
        Base64 编码字符串，失败返回 None
    """
    try:
        image_path = Path(image_path)
        
        if not image_path.exists():
            logger.error(f"❌ 图片文件不存在: {image_path}")
            return None
        
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        
        logger.debug(f"✅ 图片编码成功: {image_path.name}")
        return encoded
        
    except Exception as e:
        logger.error(f"❌ 图片编码失败: {e}")
        return None


def get_image_info(image_path: Union[str, Path]) -> dict:
    """
    获取图片信息
    
    Args:
        image_path: 图片路径
    
    Returns:
        包含图片信息的字典
    """
    try:
        image_path = Path(image_path)
        
        if not image_path.exists():
            return {"error": "文件不存在"}
        
        with Image.open(image_path) as img:
            info = {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height,
                "file_size": image_path.stat().st_size
            }
        
        return info
        
    except Exception as e:
        logger.error(f"❌ 获取图片信息失败: {e}")
        return {"error": str(e)}


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
    
    Returns:
        格式化的字符串（如 "1.5 MB"）
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def save_json_file(data: dict, file_path: Union[str, Path], indent: int = 2) -> bool:
    """
    保存 JSON 文件
    
    Args:
        data: 要保存的数据
        file_path: 文件路径
        indent: 缩进空格数
    
    Returns:
        是否保存成功
    """
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        
        logger.info(f"✅ JSON 文件已保存: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 保存 JSON 文件失败: {e}")
        return False


def load_json_file(file_path: Union[str, Path]) -> Optional[dict]:
    """
    加载 JSON 文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        加载的数据，失败返回 None
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"❌ 文件不存在: {file_path}")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.debug(f"✅ JSON 文件已加载: {file_path}")
        return data
        
    except Exception as e:
        logger.error(f"❌ 加载 JSON 文件失败: {e}")
        return None


def generate_timestamp_filename(prefix: str = "", suffix: str = "", extension: str = "txt") -> str:
    """
    生成带时间戳的文件名
    
    Args:
        prefix: 前缀
        suffix: 后缀
        extension: 扩展名（不含点）
    
    Returns:
        文件名字符串
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    parts = []
    if prefix:
        parts.append(prefix)
    parts.append(timestamp)
    if suffix:
        parts.append(suffix)
    
    filename = "_".join(parts)
    return f"{filename}.{extension}"


def clean_text(text: str) -> str:
    """
    清理文本内容
    
    Args:
        text: 原始文本
    
    Returns:
        清理后的文本
    """
    if not text:
        return ""
    
    # 去除首尾空白
    text = text.strip()
    
    # 规范化换行
    text = text.replace('\r\n', '\n')
    
    # 去除多余空行
    lines = [line for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)
    
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
    
    Returns:
        截断后的文本
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_conversation_history(history: list) -> str:
    """
    格式化对话历史为文本
    
    Args:
        history: Gradio 对话历史列表
    
    Returns:
        格式化的文本
    """
    lines = []
    lines.append("=" * 80)
    lines.append("对话记录")
    lines.append("=" * 80)
    lines.append("")
    
    for i, (user_msg, bot_msg) in enumerate(history, 1):
        lines.append(f"【对话 {i}】")
        lines.append(f"用户: {user_msg}")
        lines.append(f"助手: {bot_msg}")
        lines.append("-" * 80)
    
    return "\n".join(lines)


def extract_keywords(text: str, keywords: list) -> list:
    """
    从文本中提取关键词
    
    Args:
        text: 原始文本
        keywords: 关键词列表
    
    Returns:
        匹配到的关键词列表
    """
    text_lower = text.lower()
    matched = [kw for kw in keywords if kw.lower() in text_lower]
    return matched


def validate_api_key(api_key: str) -> bool:
    """
    验证 API 密钥格式
    
    Args:
        api_key: API 密钥
    
    Returns:
        是否有效
    """
    if not api_key:
        return False
    
    # 基本长度检查
    if len(api_key) < 20:
        return False
    
    # 检查是否只包含合法字符
    valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    if not all(c in valid_chars for c in api_key):
        return False
    
    return True


class Timer:
    """简单的计时器"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """开始计时"""
        self.start_time = datetime.now()
        return self
    
    def stop(self):
        """停止计时"""
        self.end_time = datetime.now()
        return self
    
    def elapsed(self) -> float:
        """获取耗时（秒）"""
        if not self.start_time:
            return 0.0
        
        end = self.end_time or datetime.now()
        delta = end - self.start_time
        return delta.total_seconds()
    
    def elapsed_str(self) -> str:
        """获取格式化的耗时字符串"""
        seconds = self.elapsed()
        
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"
    
    def __enter__(self):
        """上下文管理器入口"""
        return self.start()
    
    def __exit__(self, *args):
        """上下文管理器出口"""
        self.stop()
