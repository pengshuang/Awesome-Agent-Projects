"""LLM 配置"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class LLMConfig(BaseModel):
    """LLM 配置类"""
    
    # API 配置
    api_key: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", ""),
        description="API Key"
    )
    
    base_url: str = Field(
        default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        description="API Base URL"
    )
    
    # 模型配置
    model_name: str = Field(
        default_factory=lambda: os.getenv("LLM_MODEL_NAME", "gpt-4-vision-preview"),
        description="使用的模型名称"
    )
    
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="温度参数"
    )
    
    max_tokens: int = Field(
        default=2048,
        ge=1,
        description="最大生成 token 数"
    )
    
    timeout: int = Field(
        default=60,
        ge=1,
        description="请求超时时间（秒）"
    )
    
    max_retries: int = Field(
        default=3,
        ge=0,
        description="最大重试次数"
    )
    
    class Config:
        # 允许从环境变量读取
        env_prefix = "LLM_"


# 全局 LLM 配置实例
llm_config = LLMConfig()
