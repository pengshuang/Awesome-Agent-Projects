"""
SQLite 数据源适配器 (使用 Pydantic 模型)
"""

import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, Optional, List
from loguru import logger

from .base import DataSource
from src.models.datasource import QueryResponse, QueryMetadata


class SQLiteDataSource(DataSource):
    """SQLite 数据源"""
    
    def __init__(self, name: str, db_path: str):
        """
        初始化 SQLite 数据源
        
        Args:
            name: 数据源名称
            db_path: 数据库文件路径
        """
        super().__init__(name, "sqlite")
        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        
    def connect(self) -> bool:
        """连接数据库"""
        try:
            # check_same_thread=False 允许在不同线程中使用连接
            # 注意：这在单线程或使用适当锁的情况下是安全的
            self.connection = sqlite3.connect(
                str(self.db_path), 
                check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row  # 返回字典格式的结果
            self.cursor = self.connection.cursor()
            logger.info(f"✅ 已连接到SQLite数据库: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 连接数据库失败: {e}")
            return False
    
    def query(self, query: str, **kwargs) -> QueryResponse:
        """
        执行SQL查询 (返回 Pydantic 验证的结果)
        
        Args:
            query: SQL查询语句
            **kwargs: 额外参数
            
        Returns:
            QueryResponse: Pydantic 验证的查询结果
        """
        start_time = time.time()
        
        if not self.connection:
            return QueryResponse(
                success=False,
                data=None,
                error="数据库未连接",
                metadata=QueryMetadata(
                    row_count=0,
                    execution_time=0.0,
                    data_source_type="sqlite",
                    columns=[],
                )
            )
        
        try:
            # 清理查询语句
            query = query.strip()
            
            # 如果包含多条语句（用分号分隔），只执行第一条 SELECT 语句
            warnings = []
            if ';' in query:
                statements = [s.strip() for s in query.split(';') if s.strip()]
                # 找到第一条 SELECT 语句
                select_statement = None
                for stmt in statements:
                    if stmt.upper().startswith('SELECT'):
                        select_statement = stmt
                        break
                
                if select_statement:
                    query = select_statement
                    warnings.append("检测到多条SQL语句，只执行第一条 SELECT 语句")
                else:
                    # 如果没有 SELECT，使用第一条语句
                    query = statements[0]
                    warnings.append("检测到多条SQL语句，只执行第一条语句")
            
            # 记录查询日志
            logger.info(f"📊 执行SQL查询:\n{query}")
            
            # 执行查询
            self.cursor.execute(query)
            execution_time = time.time() - start_time
            
            # 判断是否是查询操作
            if query.strip().upper().startswith('SELECT'):
                # 获取结果
                rows = self.cursor.fetchall()
                
                # 转换为字典列表
                data = [dict(row) for row in rows]
                columns = [desc[0] for desc in self.cursor.description] if self.cursor.description else []
                
                logger.info(f"✅ 查询成功，返回 {len(data)} 条记录")
                
                return QueryResponse(
                    success=True,
                    data=data,
                    error=None,
                    metadata=QueryMetadata(
                        row_count=len(data),
                        columns=columns,
                        execution_time=execution_time,
                        data_source_type="sqlite",
                        sql_query=query,
                    ),
                    warnings=warnings,
                )
            else:
                # 非查询操作（INSERT, UPDATE, DELETE等）
                self.connection.commit()
                affected_rows = self.cursor.rowcount
                
                logger.info(f"✅ 操作成功，影响 {affected_rows} 行")
                
                return QueryResponse(
                    success=True,
                    data=None,
                    error=None,
                    metadata=QueryMetadata(
                        row_count=affected_rows,
                        columns=[],
                        execution_time=execution_time,
                        data_source_type="sqlite",
                        sql_query=query,
                    ),
                    warnings=warnings,
                )
                
        except sqlite3.Error as e:
            error_msg = f"SQL执行错误: {str(e)}"
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
                    data_source_type="sqlite",
                    sql_query=query,
                ),
            )
    
    def get_schema(self) -> Optional[str]:
        """
        获取数据库schema
        
        Returns:
            Schema描述字符串
        """
        if not self.connection:
            return None
        
        try:
            schema_parts = []
            
            # 获取所有表名
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in self.cursor.fetchall()]
            
            logger.info(f"📋 数据库包含 {len(tables)} 个表")
            
            # 获取每个表的结构
            for table in tables:
                # 获取表结构
                self.cursor.execute(f"PRAGMA table_info({table})")
                columns = self.cursor.fetchall()
                
                schema_parts.append(f"\n表: {table}")
                schema_parts.append("-" * 50)
                
                for col in columns:
                    col_id, col_name, col_type, not_null, default_val, pk = col
                    constraints = []
                    if pk:
                        constraints.append("PRIMARY KEY")
                    if not_null:
                        constraints.append("NOT NULL")
                    
                    constraint_str = " " + ", ".join(constraints) if constraints else ""
                    schema_parts.append(f"  {col_name}: {col_type}{constraint_str}")
                
                # 获取样例数据（前3行）
                self.cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                sample_rows = self.cursor.fetchall()
                if sample_rows:
                    schema_parts.append(f"\n  样例数据 ({len(sample_rows)} 条):")
                    for row in sample_rows:
                        schema_parts.append(f"    {dict(row)}")
            
            schema = "\n".join(schema_parts)
            return schema
            
        except Exception as e:
            logger.error(f"❌ 获取schema失败: {e}")
            return None
    
    def get_table_names(self) -> List[str]:
        """获取所有表名"""
        if not self.connection:
            return []
        
        try:
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"获取表名失败: {e}")
            return []
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info(f"🔒 已关闭数据库连接: {self.name}")
