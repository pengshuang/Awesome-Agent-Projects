"""
配置相关的 Pydantic 模型
"""

from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseModel):
    """LLM 配置模型"""
    
    api_key: str = Field(..., description="LLM API 密钥")
    api_base: str = Field(
        default="https://api.openai.com/v1",
        description="LLM API Base URL"
    )
    model: str = Field(default="gpt-3.5-turbo", description="模型名称")
    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="温度参数，控制随机性"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        gt=0,
        description="最大生成 token 数"
    )
    
    @field_validator("api_base")
    @classmethod
    def validate_api_base(cls, v: str) -> str:
        """验证 API Base URL"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("API Base URL 必须以 http:// 或 https:// 开头")
        return v.rstrip("/")


class EmbeddingConfig(BaseModel):
    """Embedding 配置模型"""
    
    provider: Literal["openai", "huggingface", "fastembed"] = Field(
        default="huggingface",
        description="Embedding 提供商"
    )
    model_name: str = Field(
        default="BAAI/bge-small-zh-v1.5",
        description="模型名称"
    )
    api_key: Optional[str] = Field(default=None, description="API 密钥（OpenAI需要）")
    embed_batch_size: int = Field(
        default=10,
        gt=0,
        description="批量嵌入大小"
    )
    
    @model_validator(mode="after")
    def validate_api_key_for_openai(self):
        """验证 OpenAI provider 需要 API key"""
        if self.provider == "openai" and not self.api_key:
            raise ValueError("使用 OpenAI Embedding 时必须提供 api_key")
        return self


class WebSearchConfig(BaseModel):
    """Web 搜索配置模型"""
    
    enabled: bool = Field(default=False, description="是否启用 Web 搜索")
    api_key: Optional[str] = Field(default=None, description="搜索 API 密钥")
    provider: Literal["serpapi", "google"] = Field(
        default="serpapi",
        description="搜索提供商"
    )
    max_results: int = Field(default=5, ge=1, le=20, description="最大搜索结果数")
    
    @model_validator(mode="after")
    def validate_api_key_when_enabled(self):
        """验证启用搜索时需要 API key"""
        if self.enabled and not self.api_key:
            raise ValueError("启用 Web 搜索时必须提供 api_key")
        return self


class NL2SQLConfig(BaseModel):
    """NL2SQL 配置模型"""
    
    dialect: Literal["sqlite", "mysql", "postgresql", "oracle"] = Field(
        default="sqlite",
        description="SQL 方言"
    )
    max_query_complexity: int = Field(
        default=3,
        ge=1,
        le=5,
        description="最大查询复杂度"
    )
    enable_query_validation: bool = Field(
        default=True,
        description="是否启用查询验证"
    )


class SystemSettings(BaseSettings):
    """系统配置（从环境变量加载）"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # 项目路径配置
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent,
        description="项目根目录"
    )
    
    # LLM 配置
    llm_api_key: Optional[str] = Field(default=None, alias="LLM_API_KEY")
    llm_api_base: str = Field(
        default="https://api.openai.com/v1",
        alias="LLM_API_BASE"
    )
    llm_model: str = Field(default="gpt-3.5-turbo", alias="LLM_MODEL")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, alias="TEMPERATURE")
    
    # Embedding 配置
    embedding_provider: Literal["openai", "huggingface", "fastembed"] = Field(
        default="huggingface",
        alias="EMBEDDING_PROVIDER"
    )
    embedding_model_name: str = Field(
        default="BAAI/bge-small-zh-v1.5",
        alias="EMBEDDING_MODEL_NAME"
    )
    embedding_api_key: Optional[str] = Field(
        default=None,
        alias="EMBEDDING_API_KEY"
    )
    
    # 多轮对话配置
    max_history_turns: int = Field(
        default=10,
        ge=1,
        le=200,  # 提高限制以支持更长的对话历史
        alias="MAX_HISTORY_TURNS"
    )
    
    # Web 搜索配置
    enable_web_search: bool = Field(default=False, alias="ENABLE_WEB_SEARCH")
    web_search_api_key: Optional[str] = Field(
        default=None,
        alias="WEB_SEARCH_API_KEY"
    )
    
    # NL2SQL 配置
    sql_dialect: Literal["sqlite", "mysql", "postgresql", "oracle"] = Field(
        default="sqlite",
        alias="SQL_DIALECT"
    )
    
    @property
    def data_dir(self) -> Path:
        """数据目录"""
        return self.project_root / "data"
    
    @property
    def database_dir(self) -> Path:
        """数据库目录"""
        return self.data_dir / "databases"
    
    @property
    def files_dir(self) -> Path:
        """文件目录"""
        return self.data_dir / "files"
    
    @property
    def knowledge_base_dir(self) -> Path:
        """知识库目录"""
        return self.data_dir / "knowledge_base"
    
    @property
    def cache_dir(self) -> Path:
        """缓存目录"""
        return self.data_dir / "cache"
    
    @property
    def log_dir(self) -> Path:
        """日志目录"""
        return self.project_root / "logs"
    
    @property
    def output_dir(self) -> Path:
        """输出目录"""
        return self.project_root / "output"
    
    @property
    def chat_history_dir(self) -> Path:
        """对话历史目录"""
        return self.output_dir / "chat_history"
    
    def get_llm_config(self) -> Optional[LLMConfig]:
        """获取 LLM 配置对象"""
        if not self.llm_api_key:
            return None
        return LLMConfig(
            api_key=self.llm_api_key,
            api_base=self.llm_api_base,
            model=self.llm_model,
            temperature=self.temperature,
        )
    
    def get_embedding_config(self) -> EmbeddingConfig:
        """获取 Embedding 配置对象"""
        return EmbeddingConfig(
            provider=self.embedding_provider,
            model_name=self.embedding_model_name,
            api_key=self.embedding_api_key,
        )
    
    def get_web_search_config(self) -> WebSearchConfig:
        """获取 Web 搜索配置对象"""
        return WebSearchConfig(
            enabled=self.enable_web_search,
            api_key=self.web_search_api_key,
        )
    
    def get_nl2sql_config(self) -> NL2SQLConfig:
        """获取 NL2SQL 配置对象"""
        return NL2SQLConfig(dialect=self.sql_dialect)
    
    def ensure_directories(self) -> None:
        """确保所有必要的目录存在"""
        directories = [
            self.data_dir,
            self.database_dir,
            self.files_dir,
            self.knowledge_base_dir,
            self.cache_dir,
            self.log_dir,
            self.output_dir,
            self.chat_history_dir,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
