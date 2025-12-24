"""Utility functions for the system."""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List
from loguru import logger

from src.models import QAPair
from config import settings


def ensure_directories():
    """Ensure all required directories exist."""
    dirs = [
        settings.upload_dir,
        settings.output_dir,
        settings.log_dir,
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.debug("Ensured directory exists: {}", dir_path)


def save_qa_pairs(qa_pairs: List[dict], task_type: str) -> str:
    """
    Save QA pairs to a JSON file.
    
    Args:
        qa_pairs: List of QA pair dictionaries
        task_type: Type of task
    
    Returns:
        Path to saved file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"qa_pairs_{task_type}_{timestamp}.json"
    filepath = Path(settings.output_dir) / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2, default=str)
    
    logger.info("Saved {} QA pairs to: {}", len(qa_pairs), filepath)
    return str(filepath)


def format_qa_for_display(qa_dict: dict, index: int) -> str:
    """
    Format a QA pair for markdown display.
    
    Args:
        qa_dict: QA pair dictionary
        index: Index number
    
    Returns:
        Formatted markdown string
    """
    md = f"""
### 问答对 {index}

**问题：**
{qa_dict['question']}

**答案：**
{qa_dict['answer']}

**推理：**
{qa_dict.get('reasoning', 'N/A')}

**迭代次数：** {qa_dict.get('iteration', 'N/A')}

---
"""
    return md


def format_iteration_status(
    iteration: int,
    max_iterations: int,
    valid_count: int,
    failed_count: int
) -> str:
    """Format iteration status for display."""
    progress = (iteration / max_iterations) * 100
    
    status = f"""
### 进度状态

- **当前迭代：** {iteration} / {max_iterations} ({progress:.1f}%)
- **有效问答对：** {valid_count}
- **验证失败：** {failed_count}
"""
    return status


def read_document_file(file_path: str) -> str:
    """
    Read document content from file.
    
    Args:
        file_path: Path to document file
    
    Returns:
        Document content as string
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read based on file type
    if file_path.suffix == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    elif file_path.suffix == ".md":
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        # For other types, try reading as text
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    
    logger.info("Read document from {}: {} chars", file_path, len(content))
    return content
