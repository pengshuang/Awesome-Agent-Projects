"""
模拟面试系统 - 配置管理模块
使用 Pydantic Settings 进行配置管理和验证
"""

import os
from pathlib import Path
from typing import Optional, Literal

from pydantic import Field, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger

from .llm_config import get_llm_client


class SystemConfig(BaseSettings):
    """
    系统配置类
    
    使用 Pydantic Settings 自动从环境变量读取配置
    支持 .env 文件
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # LLM 配置
    llm_api_key: str = Field(..., description="LLM API Key", alias="LLM_API_KEY")
    llm_api_base: str = Field(
        default="https://api.openai.com/v1",
        description="LLM API Base URL",
        alias="LLM_API_BASE",
    )
    llm_model: str = Field(
        default="gpt-3.5-turbo", description="LLM 模型名称", alias="LLM_MODEL"
    )
    temperature: float = Field(
        default=0.7,
        description="温度参数",
        ge=0.0,
        le=2.0,
        alias="TEMPERATURE",
    )
    
    # Web 搜索配置
    enable_web_search: bool = Field(
        default=True, description="是否启用联网搜索", alias="ENABLE_WEB_SEARCH"
    )
    web_search_engine: Literal["duckduckgo", "searxng"] = Field(
        default="duckduckgo", description="搜索引擎", alias="WEB_SEARCH_ENGINE"
    )
    max_search_results: int = Field(
        default=5, description="最大搜索结果数", ge=1, le=20, alias="MAX_SEARCH_RESULTS"
    )
    searxng_url: Optional[str] = Field(
        default="https://searx.be", description="SearXNG 实例 URL", alias="SEARXNG_URL"
    )
    
    # 面试配置
    max_history_turns: int = Field(
        default=20,
        description="多轮对话历史轮数",
        ge=1,
        le=100,
        alias="MAX_HISTORY_TURNS",
    )
    interview_mode: Literal["technical", "behavioral", "comprehensive"] = Field(
        default="technical", description="面试模式", alias="INTERVIEW_MODE"
    )
    
    # 系统配置
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="日志级别", alias="LOG_LEVEL"
    )
    enable_cache: bool = Field(
        default=True, description="是否启用缓存", alias="ENABLE_CACHE"
    )
    
    # 路径配置（计算属性）
    @computed_field
    @property
    def base_dir(self) -> Path:
        """项目根目录"""
        return Path(__file__).parent.parent
    
    @computed_field
    @property
    def data_dir(self) -> Path:
        """数据目录"""
        return self.base_dir / "data"
    
    @computed_field
    @property
    def resumes_dir(self) -> Path:
        """简历目录"""
        return self.data_dir / "resumes"
    
    @computed_field
    @property
    def cache_dir(self) -> Path:
        """缓存目录"""
        return self.data_dir / "cache"
    
    @computed_field
    @property
    def logs_dir(self) -> Path:
        """日志目录"""
        return self.base_dir / "logs"
    
    @computed_field
    @property
    def output_dir(self) -> Path:
        """输出目录"""
        return self.base_dir / "output"
    
    @field_validator("llm_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """验证 API Key"""
        if not v or v.strip() == "":
            raise ValueError("LLM_API_KEY 不能为空，请在 .env 文件中配置")
        return v.strip()
    
    @field_validator("llm_api_base")
    @classmethod
    def validate_api_base(cls, v: str) -> str:
        """验证 API Base URL"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("LLM_API_BASE 必须是有效的 HTTP(S) URL")
        return v.rstrip("/")
    
    def ensure_directories(self) -> None:
        """确保所有必要的目录存在"""
        for directory in [
            self.data_dir,
            self.resumes_dir,
            self.cache_dir,
            self.logs_dir,
            self.output_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)
        logger.info("所有必要目录已创建")
    
    def get_summary(self) -> str:
        """获取配置摘要"""
        return f"""
系统配置摘要:
- LLM 模型: {self.llm_model}
- LLM Base: {self.llm_api_base}
- 温度参数: {self.temperature}
- 联网搜索: {'启用' if self.enable_web_search else '禁用'}
- 搜索引擎: {self.web_search_engine}
- 最大历史轮数: {self.max_history_turns}
- 日志级别: {self.log_level}
        """.strip()


# 全局配置实例（单例）
_config: Optional[SystemConfig] = None


def get_config() -> SystemConfig:
    """
    获取系统配置实例（单例模式）
    
    Returns:
        SystemConfig: 系统配置对象
    """
    global _config
    if _config is None:
        _config = SystemConfig()
    return _config


def initialize_settings() -> SystemConfig:
    """
    初始化系统配置
    
    Returns:
        SystemConfig: 初始化后的配置对象
    """
    # 获取配置实例
    config = get_config()
    
    # 确保目录存在
    config.ensure_directories()
    
    # 配置日志
    logger.add(
        config.logs_dir / "app.log",
        rotation="500 MB",
        level=config.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )
    
    # 验证 LLM 配置
    try:
        client, model, temperature = get_llm_client(
            api_key=config.llm_api_key,
            api_base=config.llm_api_base,
            model=config.llm_model,
            temperature=config.temperature,
        )
        logger.info(f"LLM 已配置: {model}")
    except Exception as e:
        logger.error(f"LLM 配置失败: {e}")
        raise
    
    # 打印配置摘要
    logger.info(f"\\n{config.get_summary()}")
    
    logger.info("系统初始化完成")
    
    return config
