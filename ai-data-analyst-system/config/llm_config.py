"""
LLM 和 Embedding 模型配置模块
支持多种三方 LLM API（DeepSeek、OpenAI、Qwen 等）及本地模型
使用 Pydantic 进行配置验证
"""

import os
from typing import Optional
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import LLM
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from loguru import logger

from src.models.config import LLMConfig, EmbeddingConfig


def get_llm(
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> LLM:
    """
    获取 LLM 实例（使用 Pydantic 验证配置）
    支持 OpenAI、DeepSeek、Qwen 等兼容 OpenAI API 的服务
    
    Args:
        api_key: API Key（可选，默认从环境变量读取）
        api_base: API Base URL（可选，默认从环境变量读取）
        model: 模型名称（可选，默认从环境变量读取）
        temperature: 温度参数（可选，默认从环境变量读取）
        
    Returns:
        LLM 实例
    """
    # 从环境变量获取配置
    api_key = api_key or os.getenv("LLM_API_KEY")
    api_base = api_base or os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
    model = model or os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    temperature = temperature if temperature is not None else float(os.getenv("TEMPERATURE", "0.1"))
    
    if not api_key:
        raise ValueError(
            "LLM_API_KEY 未设置，请在 .env 文件中配置\n"
            "示例配置：\n"
            "  # OpenAI\n"
            "  LLM_API_KEY=sk-...\n"
            "  LLM_API_BASE=https://api.openai.com/v1\n"
            "  LLM_MODEL=gpt-3.5-turbo\n\n"
            "  # DeepSeek\n"
            "  LLM_API_KEY=sk-...\n"
            "  LLM_API_BASE=https://api.deepseek.com/v1\n"
            "  LLM_MODEL=deepseek-chat\n\n"
            "  # Qwen\n"
            "  LLM_API_KEY=sk-...\n"
            "  LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1\n"
            "  LLM_MODEL=qwen-turbo\n"
        )
    
    # 使用 Pydantic 验证配置
    try:
        llm_config = LLMConfig(
            api_key=api_key,
            api_base=api_base,
            model=model,
            temperature=temperature,
        )
    except Exception as e:
        raise ValueError(f"LLM 配置验证失败: {e}")
    
    # 判断是否是 OpenAI 官方 API
    if "api.openai.com" in llm_config.api_base:
        logger.info(f"🤖 使用 OpenAI 官方 API: {llm_config.model}")
        return OpenAI(
            api_key=llm_config.api_key,
            api_base=llm_config.api_base,
            model=llm_config.model,
            temperature=llm_config.temperature,
        )
    else:
        # 使用 OpenAILike 适配其他 OpenAI 兼容的 API
        try:
            from llama_index.llms.openai_like import OpenAILike
            
            logger.info(f"🤖 使用 OpenAI 兼容 API: {llm_config.model} (Base: {llm_config.api_base})")
            return OpenAILike(
                api_key=llm_config.api_key,
                api_base=llm_config.api_base,
                model=llm_config.model,
                temperature=llm_config.temperature,
                is_chat_model=True,
            )
        except Exception as e:
            # 如果 OpenAILike 导入失败，回退到 OpenAI 类
            logger.warning(f"OpenAILike 导入失败: {e}")
            logger.warning(f"回退使用 OpenAI 类（可能存在兼容性问题）")
            return OpenAI(
                api_key=llm_config.api_key,
                api_base=llm_config.api_base,
                model=llm_config.model,
                temperature=llm_config.temperature,
            )


def get_embedding_model(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
) -> BaseEmbedding:
    """
    获取 Embedding 模型实例（使用 Pydantic 验证配置）
    
    Args:
        provider: Embedding 提供商（openai, huggingface）
        model_name: 模型名称
        api_key: API 密钥（OpenAI 需要）
        
    Returns:
        Embedding 模型实例
    """
    # 从环境变量获取配置
    provider = provider or os.getenv("EMBEDDING_PROVIDER", "huggingface")
    model_name = model_name or os.getenv("EMBEDDING_MODEL") or os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-zh-v1.5")
    api_key = api_key or os.getenv("EMBEDDING_API_KEY") or os.getenv("LLM_API_KEY")
    
    # 使用 Pydantic 验证配置
    try:
        embedding_config = EmbeddingConfig(
            provider=provider,
            model_name=model_name,
            api_key=api_key,
        )
    except Exception as e:
        raise ValueError(f"Embedding 配置验证失败: {e}")
    
    logger.info(f"📚 Embedding 提供商: {embedding_config.provider}")
    
    if embedding_config.provider == "openai":
        # 使用 OpenAI Embedding
        if not embedding_config.api_key:
            raise ValueError("使用 OpenAI Embedding 时必须提供 API Key")
        
        logger.info(f"  模型: {embedding_config.model_name}")
        return OpenAIEmbedding(
            api_key=embedding_config.api_key,
            model=embedding_config.model_name
        )
    
    elif embedding_config.provider == "huggingface":
        # 使用 HuggingFace Embedding
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        
        logger.info(f"  模型: {embedding_config.model_name}")
        return HuggingFaceEmbedding(
            model_name=embedding_config.model_name,
            embed_batch_size=embedding_config.embed_batch_size,
        )
    
    else:
        raise ValueError(f"不支持的 Embedding 提供商: {embedding_config.provider}")
