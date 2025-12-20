"""
配置模块初始化
"""

from .settings import SystemConfig, initialize_settings
from .llm_config import get_llm, get_embedding_model

__all__ = [
    "SystemConfig",
    "initialize_settings",
    "get_llm",
    "get_embedding_model",
]
