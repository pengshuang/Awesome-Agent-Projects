"""工具函数"""

import os
import json
import base64
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime


def setup_logger(name: str, log_dir: Path, level: str = "INFO") -> logging.Logger:
    """设置日志器"""
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # 文件处理器
    log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(getattr(logging, level))
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def encode_image_to_base64(image_path: str) -> str:
    """将图片编码为 base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_image_data_url(image_path: str) -> str:
    """获取图片的 data URL"""
    # 获取图片扩展名
    ext = Path(image_path).suffix.lower()
    mime_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    mime_type = mime_type_map.get(ext, 'image/jpeg')
    
    base64_image = encode_image_to_base64(image_path)
    return f"data:{mime_type};base64,{base64_image}"


def save_json(data: dict, file_path: Path):
    """保存 JSON 数据"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_json(file_path: Path) -> dict:
    """加载 JSON 数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_json_from_text(text: str) -> dict:
    """从文本中提取 JSON"""
    import re
    import json
    
    if not text:
        raise ValueError("输入文本为空")
    
    # 尝试直接解析整个文本
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 尝试提取 JSON 代码块（带 json 标记）
    json_pattern = r'```json\s*(\{[\s\S]*?\})\s*```'
    matches = re.findall(json_pattern, text, re.DOTALL)
    if matches:
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    # 尝试提取 JSON 代码块（不带语言标记）
    json_pattern = r'```\s*(\{[\s\S]*?\})\s*```'
    matches = re.findall(json_pattern, text, re.DOTALL)
    if matches:
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    # 尝试提取花括号内容（最后的手段）
    brace_pattern = r'\{[\s\S]*\}'
    matches = re.findall(brace_pattern, text, re.DOTALL)
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    raise ValueError(f"无法从文本中提取有效的 JSON。原始文本:\n{text[:200]}")


def format_qa_for_display(qa_pair: dict, iteration: int) -> str:
    """格式化问答对用于显示"""
    return f"""
### 迭代 {iteration} - 难度 {qa_pair.get('difficulty', 0):.2f}

**问题：**
{qa_pair['question']}

**答案：**
{qa_pair['answer']}
"""


def generate_task_id() -> str:
    """生成任务 ID"""
    return f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
