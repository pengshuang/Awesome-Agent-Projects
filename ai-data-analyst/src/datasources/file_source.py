"""
文件数据源适配器 (使用 Pydantic 模型)
支持 CSV, Excel, JSON 等格式
"""

from pathlib import Path
from typing import Any, Dict, Optional
import time
import pandas as pd
from loguru import logger

from .base import DataSource
from src.models.datasource import QueryResponse, QueryMetadata


class FileDataSource(DataSource):
    """文件数据源"""
    
    SUPPORTED_FORMATS = {
        '.csv': 'csv',
        '.xlsx': 'excel',
        '.xls': 'excel',
        '.json': 'json',
        '.parquet': 'parquet',
        '.txt': 'text',
    }
    
    def __init__(self, name: str, file_path: str):
        """
        初始化文件数据源
        
        Args:
            name: 数据源名称
            file_path: 文件路径
        """
        super().__init__(name, "file")
        self.file_path = Path(file_path)
        self.data: Optional[pd.DataFrame] = None
        self.file_format: Optional[str] = None
        
    def connect(self) -> bool:
        """加载文件"""
        try:
            if not self.file_path.exists():
                logger.error(f"❌ 文件不存在: {self.file_path}")
                return False
            
            # 判断文件格式
            suffix = self.file_path.suffix.lower()
            self.file_format = self.SUPPORTED_FORMATS.get(suffix)
            
            if not self.file_format:
                logger.error(f"❌ 不支持的文件格式: {suffix}")
                return False
            
            # 加载文件
            logger.info(f"📁 正在加载文件: {self.file_path}")
            
            if self.file_format == 'csv':
                self.data = pd.read_csv(self.file_path)
            elif self.file_format == 'excel':
                self.data = pd.read_excel(self.file_path)
            elif self.file_format == 'json':
                self.data = pd.read_json(self.file_path)
            elif self.file_format == 'parquet':
                self.data = pd.read_parquet(self.file_path)
            elif self.file_format == 'text':
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.data = pd.DataFrame({'content': [content]})
            
            logger.info(f"✅ 文件加载成功: {len(self.data)} 行 x {len(self.data.columns)} 列")
            return True
            
        except Exception as e:
            logger.error(f"❌ 加载文件失败: {e}")
            return False
    
    def query(self, query: str, **kwargs) -> QueryResponse:
        """
        查询数据 (返回 Pydantic 验证的结果)
        
        Args:
            query: 查询描述（可以是pandas query语法或自然语言描述）
            **kwargs: 额外参数
                - limit: 限制返回行数
                - columns: 指定返回列
            
        Returns:
            QueryResponse: Pydantic 验证的查询结果
        """
        start_time = time.time()
        
        if self.data is None:
            return QueryResponse(
                success=False,
                data=None,
                error="文件未加载",
                metadata=QueryMetadata(
                    row_count=0,
                    execution_time=0.0,
                    data_source_type="file",
                    columns=[],
                )
            )
        
        try:
            result_df = self.data.copy()
            warnings = []
            
            # 尝试作为pandas query执行
            try:
                if query and query.strip():
                    result_df = self.data.query(query)
                    logger.info(f"✅ 执行pandas query: {query}")
            except Exception as e:
                # 如果不是有效的pandas query，返回全部数据
                logger.debug(f"Query不是有效的pandas表达式，返回全部数据: {e}")
                warnings.append(f"Query不是有效的pandas表达式: {str(e)}")
            
            # 应用列筛选
            if 'columns' in kwargs and kwargs['columns']:
                columns = kwargs['columns']
                if isinstance(columns, str):
                    columns = [columns]
                result_df = result_df[columns]
            
            # 应用行数限制
            limit = kwargs.get('limit', None)
            if limit:
                result_df = result_df.head(limit)
            
            # 转换为字典列表
            data = result_df.to_dict('records')
            execution_time = time.time() - start_time
            
            logger.info(f"✅ 查询成功，返回 {len(data)} 条记录")
            
            return QueryResponse(
                success=True,
                data=data,
                error=None,
                metadata=QueryMetadata(
                    row_count=len(data),
                    total_rows=len(self.data),
                    columns=list(result_df.columns),
                    execution_time=execution_time,
                    data_source_type="file",
                    file_format=self.file_format,
                    file_size=self.file_path.stat().st_size if self.file_path.exists() else None,
                ),
                warnings=warnings,
            )
            
        except Exception as e:
            error_msg = f"查询失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            execution_time = time.time() - start_time
            
            return QueryResponse(
                success=False,
                data=None,
                error=error_msg,
                metadata=QueryMetadata(
                    row_count=0,
                    columns=[],
                    execution_time=execution_time,
                    data_source_type="file",
                ),
            )
    
    def get_schema(self) -> Optional[str]:
        """
        获取文件数据的schema
        
        Returns:
            Schema描述字符串
        """
        if self.data is None:
            return None
        
        try:
            schema_parts = []
            
            schema_parts.append(f"文件: {self.file_path.name}")
            schema_parts.append(f"格式: {self.file_format}")
            schema_parts.append(f"大小: {len(self.data)} 行 x {len(self.data.columns)} 列")
            schema_parts.append("\n列信息:")
            schema_parts.append("-" * 50)
            
            # 列信息
            for col in self.data.columns:
                dtype = self.data[col].dtype
                null_count = self.data[col].isnull().sum()
                unique_count = self.data[col].nunique()
                
                schema_parts.append(
                    f"  {col}: {dtype} "
                    f"(空值: {null_count}, 唯一值: {unique_count})"
                )
            
            # 前几行样例数据
            schema_parts.append("\n样例数据 (前3行):")
            schema_parts.append("-" * 50)
            sample_data = self.data.head(3).to_string(index=False)
            schema_parts.append(sample_data)
            
            return "\n".join(schema_parts)
            
        except Exception as e:
            logger.error(f"❌ 获取schema失败: {e}")
            return None
    
    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """获取原始DataFrame"""
        return self.data
    
    def close(self):
        """清理资源"""
        self.data = None
        logger.info(f"🔒 已释放文件数据源: {self.name}")
