"""
LLM 和 Embedding 模型配置模块

基于 Pydantic 配置模型
"""

from typing import Optional

from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import LLM
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.dashscope import DashScopeEmbedding
from llama_index.llms.openai import OpenAI
from loguru import logger

from .models import get_config


def get_llm(
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    model: Optional[str] = None,
) -> LLM:
    """
    获取 LLM 实例
    
    Args:
        api_key: API Key（可选，默认从配置读取）
        api_base: API Base URL（可选，默认从配置读取）
        model: 模型名称（可选，默认从配置读取）
        
    Returns:
        LLM 实例
    """
    config = get_config()
    
    # 使用传入参数或配置中的值
    api_key = api_key or config.llm.api_key
    api_base = api_base or config.llm.api_base
    model = model or config.llm.model
    temperature = config.llm.temperature
    
    # 判断是否是 OpenAI 官方 API
    if "api.openai.com" in api_base:
        # 使用 OpenAI 官方类
        logger.info(f"使用 OpenAI 官方 API: {model}")
        return OpenAI(
            api_key=api_key,
            api_base=api_base,
            model=model,
            temperature=temperature,
            timeout=config.llm.timeout,
            max_tokens=config.llm.max_tokens,
        )
    else:
        # 使用 OpenAILike 适配其他 OpenAI 兼容的 API（DeepSeek, Qwen 等）
        try:
            from llama_index.llms.openai_like import OpenAILike
            
            logger.info(f"使用 OpenAI 兼容 API: {model} (Base: {api_base})")
            return OpenAILike(
                api_key=api_key,
                api_base=api_base,
                model=model,
                temperature=temperature,
                is_chat_model=True,
                timeout=config.llm.timeout,
                max_tokens=config.llm.max_tokens,
            )
        except Exception as e:
            # 如果 OpenAILike 导入失败（依赖问题），回退到 OpenAI 类
            logger.warning(f"OpenAILike 导入失败: {e}")
            logger.warning(f"回退使用 OpenAI 类（可能存在兼容性问题）")
            return OpenAI(
                api_key=api_key,
                api_base=api_base,
                model=model,
                temperature=temperature,
                timeout=config.llm.timeout,
                max_tokens=config.llm.max_tokens,
            )


def get_embedding_model(provider: Optional[str] = None) -> BaseEmbedding:
    """
    获取 Embedding 模型实例
    
    Args:
        provider: Embedding 提供商（openai, huggingface, fastembed）
        
    Returns:
        Embedding 模型实例
    """
    config = get_config()
    provider = provider or config.embedding.provider
    
    logger.info(f"Embedding 提供商: {provider}")
    
    if provider == "openai":
        # 使用 OpenAI Embedding
        api_key = config.embedding.api_key or config.llm.api_key
        model = config.embedding.model_name
        
        logger.info(f"使用 OpenAI Embedding: {model}")
        return OpenAIEmbedding(
            api_key=api_key,
            model=model,
        )
    
    elif provider in ["huggingface", "local"]:
        # 使用本地 HuggingFace Embedding 模型
        logger.info(f"准备加载本地 Embedding 模型...")
        
        model_name = config.embedding.model_name
        
        try:
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding
            
            logger.info(f"正在加载 HuggingFace Embedding 模型: {model_name}")
            logger.info("首次加载可能需要下载模型，请耐心等待...")
            
            kwargs = {
                "model_name": model_name,
                "embed_batch_size": config.embedding.batch_size,
            }
            
            if config.embedding.cache_folder:
                kwargs["cache_folder"] = config.embedding.cache_folder
            
            embedding = HuggingFaceEmbedding(**kwargs)
            
            logger.info(f"✅ Embedding 模型加载成功: {model_name}")
            return embedding
            
        except ImportError as e:
            logger.error(f"❌ 无法导入 HuggingFace Embedding 库: {e}")
            logger.error("\n请安装必要的依赖:")
            logger.error("  pip install llama-index-embeddings-huggingface")
            logger.error("  pip install sentence-transformers")
            raise RuntimeError(
                f"HuggingFace Embedding 依赖缺失\n"
                f"请运行: pip install llama-index-embeddings-huggingface sentence-transformers"
            )
            
        except Exception as e:
            logger.error(f"❌ 无法加载 HuggingFace Embedding 模型: {e}")
            logger.error(f"模型名称: {model_name}")
            logger.error("\n可能的原因:")
            logger.error("  1. 模型名称错误或不存在")
            logger.error("  2. 网络连接问题（首次使用需要下载模型）")
            logger.error("  3. 磁盘空间不足")
            logger.error("  4. transformers/torch 版本冲突")
            logger.error("\n解决方案:")
            logger.error("  方案1: 检查模型名称")
            logger.error(f"    当前设置: {model_name}")
            logger.error("    推荐模型: BAAI/bge-small-zh-v1.5")
            logger.error("  方案2: 使用 FastEmbed（轻量级，推荐）")
            logger.error("    pip install llama-index-embeddings-fastembed")
            logger.error("    在 .env 中设置: EMBEDDING_PROVIDER=fastembed")
            logger.error("  方案3: 使用 OpenAI Embedding（需要 API Key）")
            logger.error("    在 .env 中设置: EMBEDDING_PROVIDER=openai")
            raise RuntimeError(
                f"无法加载 Embedding 模型: {model_name}\n"
                f"错误: {str(e)}\n"
                f"请参考上方日志的解决方案"
            )
    
    elif provider == "qwen3":
        # 使用 Qwen3 Embedding 模型（DashScope）
        logger.info("准备加载 Qwen3 Embedding 模型...")

        try:
            import os
            api_key = config.embedding.api_key or os.getenv("DASHSCOPE_API_KEY")
            model = config.embedding.model_name or "text-embedding-v3"
            
            if not api_key:
                raise RuntimeError(
                    "DASHSCOPE_API_KEY 未设置。请在 .env 文件中设置 EMBEDDING_API_KEY 或环境变量 DASHSCOPE_API_KEY"
                )
            
            logger.info(f"使用 DashScope Embedding: {model}")
            # DashScope batch_size 最大为 10
            batch_size = min(config.embedding.batch_size, 10)
            logger.info(f"DashScope Embedding batch_size 设置为: {batch_size}")
            
            return DashScopeEmbedding(
                model_name=model,
                api_key=api_key,
                text_type="document",  # 设置文本类型
                embed_batch_size=batch_size  # 设置批处理大小
            )

        except ImportError as e:
            logger.error(f"❌ 无法导入 DashScope Embedding 库: {e}")
            logger.error("\n请安装必要的依赖:")
            logger.error("  pip install llama-index-embeddings-dashscope")
            raise RuntimeError(
                f"DashScope Embedding 依赖缺失\n"
                f"请运行: pip install llama-index-embeddings-dashscope"
            )

        except Exception as e:
            logger.error(f"❌ 无法加载 DashScope Embedding 模型: {e}")
            raise RuntimeError(f"DashScope Embedding 加载失败: {str(e)}")
    
    else:
        raise ValueError(f"不支持的 Embedding 提供商: {provider}\n"
                        f"支持的选项: openai, huggingface, fastembed")


__all__ = ["get_llm", "get_embedding_model"]
