"""
数据源基类 (使用 Pydantic 模型)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from src.models.datasource import QueryResponse


class DataSource(ABC):
    """数据源抽象基类"""
    
    def __init__(self, name: str, source_type: str):
        """
        初始化数据源
        
        Args:
            name: 数据源名称
            source_type: 数据源类型（sqlite, file, knowledge_base, web）
        """
        self.name = name
        self.source_type = source_type
    
    @abstractmethod
    def connect(self) -> bool:
        """
        连接数据源
        
        Returns:
            是否连接成功
        """
        pass
    
    @abstractmethod
    def query(self, query: str, **kwargs) -> QueryResponse:
        """
        查询数据 (返回 Pydantic 模型)
        
        Args:
            query: 查询语句或问题
            **kwargs: 额外参数
            
        Returns:
            QueryResponse: Pydantic 验证的查询结果
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Optional[str]:
        """
        获取数据源的schema信息
        
        Returns:
            Schema描述字符串
        """
        pass
    
    @abstractmethod
    def close(self):
        """关闭数据源连接"""
        pass
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
