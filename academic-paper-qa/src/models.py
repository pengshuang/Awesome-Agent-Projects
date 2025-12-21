"""
数据模型 - 文档、查询和响应

提供类型安全的数据结构定义
"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field, field_validator


class DocumentMetadata(BaseModel):
    """文档元数据模型"""
    
    file_name: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件路径")
    file_type: str = Field(..., description="文件类型（pdf, docx, txt等）")
    file_size: Optional[int] = Field(None, description="文件大小（字节）")
    page_count: Optional[int] = Field(None, description="页数（PDF专用）")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    modified_at: Optional[datetime] = Field(None, description="修改时间")
    author: Optional[str] = Field(None, description="作者")
    title: Optional[str] = Field(None, description="标题")
    keywords: Optional[List[str]] = Field(default_factory=list, description="关键词")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Path: str,
        }


class DocumentChunk(BaseModel):
    """文档分块模型"""
    
    chunk_id: str = Field(..., description="分块唯一标识")
    text: str = Field(..., description="分块文本内容")
    metadata: DocumentMetadata = Field(..., description="文档元数据")
    page_num: Optional[int] = Field(None, description="页码")
    chunk_index: int = Field(..., description="分块索引")
    
    @field_validator("text")
    @classmethod
    def validate_text_not_empty(cls, v: str) -> str:
        """验证文本不为空"""
        if not v or not v.strip():
            raise ValueError("文本内容不能为空")
        return v


class QueryRequest(BaseModel):
    """查询请求模型"""
    
    question: str = Field(..., min_length=1, max_length=1000, description="用户问题")
    top_k: Optional[int] = Field(default=5, ge=1, le=50, description="检索文档数量")
    similarity_threshold: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="相似度阈值"
    )
    enable_reranking: Optional[bool] = Field(default=False, description="是否启用重排序")
    enable_web_search: Optional[bool] = Field(default=False, description="是否启用 Web 搜索")
    chat_history: Optional[List[Dict[str, str]]] = Field(
        default_factory=list,
        description="对话历史"
    )
    
    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """验证问题格式"""
        v = v.strip()
        if not v:
            raise ValueError("问题不能为空")
        return v


class SourceNode(BaseModel):
    """源节点模型（检索到的相关文档片段）"""
    
    file_name: str = Field(..., description="文档文件名")
    page_num: Optional[int] = Field(None, description="页码")
    score: float = Field(..., ge=0.0, le=1.0, description="相似度分数")
    text_snippet: str = Field(..., description="文本片段")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="其他元数据")


class QueryResponse(BaseModel):
    """查询响应模型"""
    
    answer: str = Field(..., description="生成的答案")
    sources: List[SourceNode] = Field(default_factory=list, description="源文档列表")
    web_search_results: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Web 搜索结果"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")
    query_time: Optional[float] = Field(None, description="查询耗时（秒）")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ChatMessage(BaseModel):
    """对话消息模型"""
    
    role: Literal["user", "assistant", "system"] = Field(..., description="消息角色")
    content: str = Field(..., min_length=1, description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="消息时间戳")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="消息元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ChatSession(BaseModel):
    """对话会话模型"""
    
    session_id: str = Field(..., description="会话ID")
    messages: List[ChatMessage] = Field(default_factory=list, description="消息列表")
    max_history_turns: int = Field(default=10, ge=1, le=100, description="最大历史轮数")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """添加消息到会话"""
        message = ChatMessage(role=role, content=content, metadata=metadata or {})
        self.messages.append(message)
        self.updated_at = datetime.now()
        
        # 限制历史记录长度（保留最近的消息）
        max_messages = self.max_history_turns * 2  # user + assistant = 1 turn
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]
    
    def get_history_for_llm(self) -> List[Dict[str, str]]:
        """获取适用于 LLM 的对话历史格式"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class WebSearchResult(BaseModel):
    """Web 搜索结果模型"""
    
    title: str = Field(..., description="标题")
    url: str = Field(..., description="URL")
    snippet: str = Field(..., description="摘要")
    source: Optional[str] = Field(None, description="来源（搜索引擎）")
    rank: Optional[int] = Field(None, description="排名")
    
    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """验证 URL 格式"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL 必须以 http:// 或 https:// 开头")
        return v


class IndexStats(BaseModel):
    """索引统计信息模型"""
    
    total_documents: int = Field(default=0, ge=0, description="文档总数")
    total_chunks: int = Field(default=0, ge=0, description="分块总数")
    index_size: Optional[int] = Field(None, ge=0, description="索引大小（字节）")
    last_updated: Optional[datetime] = Field(None, description="最后更新时间")
    documents_info: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="文档详情列表"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class FileUploadRequest(BaseModel):
    """文件上传请求模型"""
    
    file_path: str = Field(..., description="文件路径")
    file_name: Optional[str] = Field(None, description="文件名（可选）")
    overwrite: bool = Field(default=False, description="是否覆盖已存在的文件")
    
    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """验证文件路径"""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"文件不存在: {v}")
        if not path.is_file():
            raise ValueError(f"不是有效的文件: {v}")
        return v


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    
    success: bool = Field(..., description="是否成功")
    file_name: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件路径")
    file_size: int = Field(..., description="文件大小（字节）")
    message: Optional[str] = Field(None, description="消息")
    error: Optional[str] = Field(None, description="错误信息")


__all__ = [
    "DocumentMetadata",
    "DocumentChunk",
    "QueryRequest",
    "QueryResponse",
    "SourceNode",
    "ChatMessage",
    "ChatSession",
    "WebSearchResult",
    "IndexStats",
    "FileUploadRequest",
    "FileUploadResponse",
]
