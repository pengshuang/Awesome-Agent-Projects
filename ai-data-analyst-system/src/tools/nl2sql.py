"""
NL2SQL 转换器
将自然语言转换为SQL查询
"""

from typing import Optional, Dict, Any
from loguru import logger

from config.llm_config import get_llm
from config.prompts import PromptBuilder
from src.utils.helpers import extract_sql_from_response


class NL2SQLConverter:
    """NL2SQL 转换器"""
    
    def __init__(self):
        """初始化转换器"""
        self.llm = get_llm()
        logger.info("✅ NL2SQL 转换器初始化完成")
    
    def convert(
        self,
        question: str,
        database_schema: str,
        dialect: str = "sqlite",
        chat_history: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        将自然语言转换为SQL
        
        Args:
            question: 用户的自然语言问题
            database_schema: 数据库schema信息
            dialect: SQL方言（sqlite, mysql, postgresql等）
            chat_history: 对话历史（可选）
            
        Returns:
            转换结果字典
        """
        try:
            # 构建prompt
            prompt = PromptBuilder.build_nl2sql_prompt(
                question=question,
                database_schema=database_schema,
                dialect=dialect,
                chat_history=chat_history,
            )
            
            # 记录输入给大模型的Prompt（用于debug）
            logger.info("=" * 70)
            logger.info("📝 [LLM调用] NL2SQL转换")
            logger.info("=" * 70)
            logger.info(f"输入Prompt:\n{prompt}")
            logger.info("=" * 70)
            
            # 调用LLM
            response = self.llm.complete(prompt)
            sql_response = str(response)
            
            logger.info(f"LLM响应:\n{sql_response}")
            logger.info("=" * 70)
            
            # 提取SQL语句
            sql = extract_sql_from_response(sql_response)
            
            if not sql:
                # 如果没有提取到SQL，尝试直接使用响应
                sql = sql_response.strip()
            
            logger.info(f"✅ NL2SQL转换成功")
            logger.info(f"生成的SQL:\n{sql}")
            
            return {
                "success": True,
                "sql": sql,
                "raw_response": sql_response,
                "error": None,
            }
            
        except Exception as e:
            error_msg = f"NL2SQL转换失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "sql": None,
                "raw_response": None,
                "error": error_msg,
            }
    
    def correct_sql(
        self,
        sql: str,
        error: str,
        database_schema: str,
        dialect: str = "sqlite",
    ) -> Dict[str, Any]:
        """
        修正SQL语法错误
        
        Args:
            sql: 原始SQL
            error: 错误信息
            database_schema: 数据库schema
            dialect: SQL方言
            
        Returns:
            修正结果
        """
        try:
            from config.prompts import PromptTemplates
            
            prompt = PromptTemplates.SQL_CORRECTION.format(
                sql=sql,
                error=error,
                database_schema=database_schema,
            )
            
            # 记录Prompt
            logger.info("=" * 70)
            logger.info("📝 [LLM调用] SQL语法修正")
            logger.info("=" * 70)
            logger.info(f"输入Prompt:\n{prompt}")
            logger.info("=" * 70)
            
            # 调用LLM
            response = self.llm.complete(prompt)
            corrected_response = str(response)
            
            logger.info(f"LLM响应:\n{corrected_response}")
            logger.info("=" * 70)
            
            # 提取修正后的SQL
            corrected_sql = extract_sql_from_response(corrected_response)
            
            if not corrected_sql:
                corrected_sql = corrected_response.strip()
            
            logger.info(f"✅ SQL修正完成")
            
            return {
                "success": True,
                "sql": corrected_sql,
                "raw_response": corrected_response,
                "error": None,
            }
            
        except Exception as e:
            error_msg = f"SQL修正失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "sql": None,
                "raw_response": None,
                "error": error_msg,
            }
