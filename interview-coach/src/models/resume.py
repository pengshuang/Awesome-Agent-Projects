"""
简历数据模型
使用 Pydantic 进行数据验证和序列化
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ResumeMetadata(BaseModel):
    """
    简历元数据
    
    Attributes:
        file_name: 文件名
        file_path: 文件完整路径
        file_size: 文件大小（字节）
        content_length: 内容长度（字符数）
        load_time: 加载耗时（秒）
        loaded_at: 加载时间戳
    """
    
    file_name: str = Field(..., description="文件名", min_length=1)
    file_path: str = Field(..., description="文件路径", min_length=1)
    file_size: int = Field(..., description="文件大小（字节）", ge=0)
    content_length: int = Field(..., description="内容长度（字符）", ge=0)
    load_time: float = Field(..., description="加载耗时（秒）", ge=0)
    loaded_at: datetime = Field(default_factory=datetime.now, description="加载时间")
    
    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """验证文件大小"""
        if v > 100 * 1024 * 1024:  # 100MB
            raise ValueError("文件大小不能超过 100MB")
        return v
    
    def get_file_size_mb(self) -> float:
        """文件大小（MB）"""
        return round(self.file_size / (1024 * 1024), 2)
    
    model_config = {
        "json_schema_mode": "validation",
        "json_schema_extra": {
            "example": {
                "file_name": "resume.pdf",
                "file_path": "/path/to/resume.pdf",
                "file_size": 1048576,
                "content_length": 5000,
                "load_time": 1.23,
            }
        },
    }


class ResumeData(BaseModel):
    """
    简历数据
    
    Attributes:
        content: 简历文本内容
        metadata: 简历元数据
    """
    
    content: str = Field(..., description="简历内容", min_length=1)
    metadata: ResumeMetadata = Field(..., description="简历元数据")
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """验证内容不为空"""
        if not v.strip():
            raise ValueError("简历内容不能为空")
        return v
    
    def get_preview(self) -> str:
        """获取内容预览（前200字符）"""
        length = 200
        if len(self.content) <= length:
            return self.content
        return self.content[:length] + "..."
    
    def get_word_count(self) -> int:
        """获取字数统计"""
        return len(self.content.split())
    
    model_config = {
        "json_schema_mode": "validation",
        "json_schema_extra": {
            "example": {
                "content": "个人简历内容...",
                "metadata": {
                    "file_name": "resume.pdf",
                    "file_path": "/path/to/resume.pdf",
                    "file_size": 1048576,
                    "content_length": 5000,
                    "load_time": 1.23,
                }
            }
        },
    }
