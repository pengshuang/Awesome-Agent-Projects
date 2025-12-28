"""
数据源相关的 Pydantic 模型
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class DataSourceConfig(BaseModel):
    """数据源基础配置"""
    
    name: str = Field(..., min_length=1, description="数据源名称")
    source_type: Literal["sqlite", "file", "knowledge_base", "web"] = Field(
        ...,
        description="数据源类型"
    )
    description: Optional[str] = Field(default=None, description="数据源描述")
    enabled: bool = Field(default=True, description="是否启用")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证名称不包含特殊字符"""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("数据源名称只能包含字母、数字、下划线和连字符")
        return v


class SQLiteConfig(DataSourceConfig):
    """SQLite 数据源配置"""
    
    source_type: Literal["sqlite"] = "sqlite"
    db_path: Path = Field(..., description="数据库文件路径")
    read_only: bool = Field(default=True, description="是否只读模式")
    timeout: float = Field(default=5.0, gt=0, description="连接超时时间（秒）")
    
    @field_validator("db_path")
    @classmethod
    def validate_db_path(cls, v: Path) -> Path:
        """验证数据库文件路径"""
        if not v.exists():
            raise ValueError(f"数据库文件不存在: {v}")
        if v.suffix.lower() not in [".db", ".sqlite", ".sqlite3"]:
            raise ValueError(f"不支持的数据库文件格式: {v.suffix}")
        return v


class FileConfig(DataSourceConfig):
    """文件数据源配置"""
    
    source_type: Literal["file"] = "file"
    file_path: Path = Field(..., description="文件路径")
    file_format: Optional[Literal["csv", "excel", "json", "parquet", "text"]] = Field(
        default=None,
        description="文件格式（自动检测）"
    )
    encoding: str = Field(default="utf-8", description="文件编码")
    
    # CSV 特定配置
    delimiter: str = Field(default=",", description="CSV 分隔符")
    header_row: int = Field(default=0, ge=0, description="表头行号")
    
    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v: Path) -> Path:
        """验证文件路径"""
        if not v.exists():
            raise ValueError(f"文件不存在: {v}")
        return v
    
    @field_validator("file_format")
    @classmethod
    def validate_file_format(cls, v: Optional[str], info) -> Optional[str]:
        """自动检测文件格式"""
        if v is not None:
            return v
        
        # 从 file_path 自动检测
        file_path = info.data.get("file_path")
        if file_path:
            suffix = file_path.suffix.lower()
            format_map = {
                ".csv": "csv",
                ".xlsx": "excel",
                ".xls": "excel",
                ".json": "json",
                ".parquet": "parquet",
                ".txt": "text",
            }
            return format_map.get(suffix)
        return None


class KnowledgeBaseConfig(DataSourceConfig):
    """知识库数据源配置"""
    
    source_type: Literal["knowledge_base"] = "knowledge_base"
    kb_path: Path = Field(..., description="知识库目录路径")
    file_types: List[str] = Field(
        default=[".txt", ".md", ".pdf", ".docx"],
        description="支持的文件类型"
    )
    chunk_size: int = Field(default=512, gt=0, le=2048, description="文本分块大小")
    chunk_overlap: int = Field(default=50, ge=0, description="分块重叠大小")
    top_k: int = Field(default=5, ge=1, le=20, description="检索返回的文档数量")
    
    @field_validator("kb_path")
    @classmethod
    def validate_kb_path(cls, v: Path) -> Path:
        """验证知识库路径"""
        if not v.exists():
            raise ValueError(f"知识库目录不存在: {v}")
        if not v.is_dir():
            raise ValueError(f"知识库路径必须是目录: {v}")
        return v


class WebSourceConfig(DataSourceConfig):
    """Web 搜索数据源配置"""
    
    source_type: Literal["web"] = "web"
    api_key: str = Field(..., description="搜索 API 密钥")
    provider: Literal["serpapi", "google"] = Field(
        default="serpapi",
        description="搜索提供商"
    )
    max_results: int = Field(default=5, ge=1, le=20, description="最大搜索结果数")
    search_language: str = Field(default="zh-cn", description="搜索语言")


class QueryRequest(BaseModel):
    """查询请求模型"""
    
    query: str = Field(..., min_length=1, description="查询语句或问题")
    data_source: str = Field(..., description="数据源名称")
    
    # 可选参数
    limit: Optional[int] = Field(default=None, ge=1, description="限制返回行数")
    offset: Optional[int] = Field(default=0, ge=0, description="偏移量")
    columns: Optional[List[str]] = Field(default=None, description="指定返回列")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="过滤条件")
    
    # 查询上下文
    user_id: Optional[str] = Field(default=None, description="用户ID")
    session_id: Optional[str] = Field(default=None, description="会话ID")
    
    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """验证查询不为空"""
        if not v.strip():
            raise ValueError("查询内容不能为空")
        return v.strip()


class QueryMetadata(BaseModel):
    """查询元数据"""
    
    row_count: int = Field(ge=0, description="返回行数")
    total_rows: Optional[int] = Field(default=None, ge=0, description="总行数")
    columns: List[str] = Field(default_factory=list, description="列名列表")
    execution_time: float = Field(ge=0, description="执行时间（秒）")
    data_source_type: str = Field(..., description="数据源类型")
    
    # SQL 查询相关
    sql_query: Optional[str] = Field(default=None, description="执行的 SQL 查询")
    query_plan: Optional[str] = Field(default=None, description="查询执行计划")
    
    # 文件相关
    file_format: Optional[str] = Field(default=None, description="文件格式")
    file_size: Optional[int] = Field(default=None, ge=0, description="文件大小（字节）")
    
    # 其他元数据
    cache_hit: bool = Field(default=False, description="是否命中缓存")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="查询时间戳"
    )


class QueryResponse(BaseModel):
    """查询响应模型"""
    
    success: bool = Field(..., description="是否成功")
    data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="查询结果数据"
    )
    error: Optional[str] = Field(default=None, description="错误信息")
    metadata: QueryMetadata = Field(..., description="查询元数据")
    
    # 警告信息
    warnings: List[str] = Field(default_factory=list, description="警告信息列表")
    
    @field_validator("error")
    @classmethod
    def validate_error(cls, v: Optional[str], info) -> Optional[str]:
        """验证失败时必须有错误信息"""
        if not info.data.get("success") and not v:
            raise ValueError("查询失败时必须提供错误信息")
        return v
    
    def has_data(self) -> bool:
        """检查是否有数据"""
        return self.success and self.data is not None and len(self.data) > 0
    
    def get_column_names(self) -> List[str]:
        """获取列名"""
        return self.metadata.columns
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()
