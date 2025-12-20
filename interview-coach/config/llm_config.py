"""
LLM 配置模块
支持多种 LLM API：DeepSeek、OpenAI、Qwen 等
"""

import os
from typing import Optional, Tuple

from openai import OpenAI
from loguru import logger


def get_llm_client(
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> Tuple[OpenAI, str, float]:
    """
    获取 OpenAI 客户端实例
    
    支持的模型提供商：
    - OpenAI: api.openai.com
    - DeepSeek: api.deepseek.com
    - Qwen (通过 DashScope): dashscope.aliyuncs.com
    - 其他 OpenAI 兼容 API
    
    Args:
        api_key: API Key（可选，默认从环境变量读取）
        api_base: API Base URL（可选，默认从环境变量读取）
        model: 模型名称（可选，默认从环境变量读取）
        temperature: 温度参数（可选，默认从环境变量读取）
        
    Returns:
        (OpenAI客户端, 模型名称, 温度参数)
    """
    # 从环境变量获取配置
    api_key = api_key or os.getenv("LLM_API_KEY")
    api_base = api_base or os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
    model = model or os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    temperature = temperature if temperature is not None else float(os.getenv("TEMPERATURE", "0.7"))
    
    if not api_key:
        raise ValueError("LLM_API_KEY 未设置，请在 .env 文件中配置")
    
    # 创建 OpenAI 客户端（兼容所有 OpenAI API 格式的服务）
    client = OpenAI(
        api_key=api_key,
        base_url=api_base,
    )
    
    logger.info(f"LLM 客户端已初始化 | 模型: {model} | Base: {api_base}")
    
    return client, model, temperature
