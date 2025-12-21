"""
数据源基类
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


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
    def query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        查询数据
        
        Args:
            query: 查询语句或问题
            **kwargs: 额外参数
            
        Returns:
            查询结果字典，包含：
            - success: bool, 是否成功
            - data: 查询到的数据
            - error: Optional[str], 错误信息
            - metadata: Dict, 元数据
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
