"""
Pydantic 配置模型

提供类型安全的配置管理和数据验证
"""

from pathlib import Path
from typing import Optional, Literal
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    """LLM 配置模型"""
    
    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    api_key: str = Field(..., description="LLM API Key")
    api_base: str = Field(
        default="https://api.openai.com/v1",
        description="LLM API Base URL"
    )
    model: str = Field(
        default="gpt-3.5-turbo",
        description="LLM 模型名称"
    )
    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="生成温度参数"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        gt=0,
        description="最大生成 token 数"
    )
    timeout: int = Field(
        default=60,
        gt=0,
        description="API 请求超时时间（秒）"
    )
    
    @field_validator("api_base")
    @classmethod
    def validate_api_base(cls, v: str) -> str:
        """验证 API Base URL"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("API Base URL 必须以 http:// 或 https:// 开头")
        return v.rstrip("/")


class EmbeddingConfig(BaseSettings):
    """Embedding 配置模型"""
    
    model_config = SettingsConfigDict(
        env_prefix="EMBEDDING_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    provider: Literal["openai", "huggingface", "fastembed"] = Field(
        default="huggingface",
        description="Embedding 提供商"
    )
    model_name: str = Field(
        default="BAAI/bge-small-zh-v1.5",
        description="Embedding 模型名称"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="Embedding API Key（OpenAI 时需要）"
    )
    batch_size: int = Field(
        default=10,
        gt=0,
        description="批处理大小"
    )
    cache_folder: Optional[str] = Field(
        default=None,
        description="模型缓存目录"
    )


class VectorStoreConfig(BaseSettings):
    """向量存储配置模型"""
    
    model_config = SettingsConfigDict(
        env_prefix="VECTOR_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    store: Literal["chroma", "faiss", "simple"] = Field(
        default="chroma",
        description="向量存储类型"
    )
    
    # Chroma 配置
    chroma_persist_dir: Optional[Path] = Field(
        default=None,
        description="Chroma 持久化目录"
    )
    chroma_collection_name: str = Field(
        default="academic_papers",
        description="Chroma 集合名称"
    )


class RAGConfig(BaseSettings):
    """RAG 配置模型"""
    
    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    chunk_size: int = Field(
        default=512,
        gt=0,
        le=4096,
        description="文本分块大小"
    )
    chunk_overlap: int = Field(
        default=50,
        ge=0,
        description="分块重叠大小"
    )
    retrieval_top_k: int = Field(
        default=5,
        gt=0,
        le=50,
        description="检索 Top-K 数量"
    )
    retrieval_similarity_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="相似度阈值"
    )
    enable_reranking: bool = Field(
        default=False,
        description="是否启用重排序"
    )
    reranker_model: str = Field(
        default="BAAI/bge-reranker-base",
        description="重排序模型"
    )
    reranker_top_n: int = Field(
        default=3,
        gt=0,
        description="重排序后保留的文档数"
    )
    
    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, v: int, info) -> int:
        """验证 chunk_overlap 必须小于 chunk_size"""
        chunk_size = info.data.get("chunk_size", 512)
        if v >= chunk_size:
            raise ValueError(f"chunk_overlap ({v}) 必须小于 chunk_size ({chunk_size})")
        return v


class WebSearchConfig(BaseSettings):
    """Web 搜索配置模型"""
    
    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    enable_web_search: bool = Field(
        default=True,
        description="是否启用 Web 搜索"
    )
    search_engine: Literal["duckduckgo", "searxng", "serpapi"] = Field(
        default="duckduckgo",
        description="搜索引擎"
    )
    max_results: int = Field(
        default=5,
        gt=0,
        le=20,
        description="最大搜索结果数"
    )
    serpapi_key: Optional[str] = Field(
        default=None,
        description="SerpAPI Key"
    )
    searxng_url: str = Field(
        default="https://searx.be",
        description="SearXNG 实例 URL"
    )


class SystemConfig(BaseSettings):
    """系统配置模型"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # 路径配置
    base_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent,
        description="项目根目录"
    )
    
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="日志级别"
    )
    enable_cache: bool = Field(
        default=True,
        description="是否启用缓存"
    )
    max_workers: int = Field(
        default=4,
        gt=0,
        le=32,
        description="最大工作线程数"
    )
    
    @property
    def data_dir(self) -> Path:
        """数据目录"""
        return self.base_dir / "data"
    
    @property
    def documents_dir(self) -> Path:
        """文档目录"""
        return self.data_dir / "documents"
    
    @property
    def processed_dir(self) -> Path:
        """处理后的文档目录"""
        return self.data_dir / "processed"
    
    @property
    def vector_store_dir(self) -> Path:
        """向量存储目录"""
        return self.data_dir / "vector_store"
    
    @property
    def cache_dir(self) -> Path:
        """缓存目录"""
        return self.data_dir / "cache"
    
    @property
    def logs_dir(self) -> Path:
        """日志目录"""
        return self.base_dir / "logs"
    
    def ensure_directories(self) -> None:
        """确保所有必要的目录存在"""
        for directory in [
            self.data_dir,
            self.documents_dir,
            self.processed_dir,
            self.vector_store_dir,
            self.cache_dir,
            self.logs_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


class AppConfig(BaseSettings):
    """应用总配置（组合所有配置）"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    system: SystemConfig = Field(default_factory=SystemConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    web_search: WebSearchConfig = Field(default_factory=WebSearchConfig)
    
    def __init__(self, **data):
        """初始化配置"""
        super().__init__(**data)
        
        # 设置 Chroma 默认路径
        if self.vector_store.chroma_persist_dir is None:
            self.vector_store.chroma_persist_dir = self.system.vector_store_dir / "chroma"
        
        # 确保目录存在
        self.system.ensure_directories()


# 全局配置实例
_config_instance: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """获取全局配置实例（单例模式）"""
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig()
    return _config_instance


def reload_config() -> AppConfig:
    """重新加载配置"""
    global _config_instance
    _config_instance = AppConfig()
    return _config_instance


__all__ = [
    "LLMConfig",
    "EmbeddingConfig",
    "VectorStoreConfig",
    "RAGConfig",
    "WebSearchConfig",
    "SystemConfig",
    "AppConfig",
    "get_config",
    "reload_config",
]
