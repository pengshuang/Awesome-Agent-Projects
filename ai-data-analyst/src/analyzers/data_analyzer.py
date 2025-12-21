"""
数据分析引擎
支持多数据源融合分析
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from config.llm_config import get_llm
from config.prompts import PromptTemplates, PromptBuilder
from src.datasources import (
    SQLiteDataSource,
    FileDataSource,
    KnowledgeBaseSource,
    WebSearchSource,
)
from src.tools.nl2sql import NL2SQLConverter
from src.utils.helpers import format_data_for_display


class DataAnalyzer:
    """数据分析引擎"""
    
    def __init__(self):
        """初始化分析引擎"""
        self.llm = get_llm()
        self.nl2sql = NL2SQLConverter()
        
        # 数据源管理
        self.data_sources: Dict[str, Any] = {}
        
        logger.info("✅ 数据分析引擎初始化完成")
    
    def register_data_source(self, name: str, data_source: Any):
        """
        注册数据源
        
        Args:
            name: 数据源名称
            data_source: 数据源实例
        """
        self.data_sources[name] = data_source
        logger.info(f"📊 已注册数据源: {name} ({data_source.source_type})")
    
    def analyze_single_source(
        self,
        question: str,
        source_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        分析单个数据源
        
        Args:
            question: 用户问题
            source_name: 数据源名称
            **kwargs: 额外参数
            
        Returns:
            分析结果
        """
        if source_name not in self.data_sources:
            return {
                "success": False,
                "answer": None,
                "error": f"数据源不存在: {source_name}",
            }
        
        data_source = self.data_sources[source_name]
        
        try:
            logger.info(f"🔍 正在分析数据源: {source_name}")
            
            # 根据数据源类型采用不同策略
            if isinstance(data_source, SQLiteDataSource):
                return self._analyze_database(question, data_source, **kwargs)
            elif isinstance(data_source, FileDataSource):
                return self._analyze_file(question, data_source, **kwargs)
            elif isinstance(data_source, KnowledgeBaseSource):
                return self._analyze_knowledge_base(question, data_source, **kwargs)
            elif isinstance(data_source, WebSearchSource):
                return self._analyze_web(question, data_source, **kwargs)
            else:
                return {
                    "success": False,
                    "answer": None,
                    "error": f"不支持的数据源类型: {type(data_source)}",
                }
                
        except Exception as e:
            error_msg = f"数据分析失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "answer": None,
                "error": error_msg,
            }
    
    def _analyze_database(
        self,
        question: str,
        db_source: SQLiteDataSource,
        chat_history: Optional[str] = None,
    ) -> Dict[str, Any]:
        """分析数据库数据源"""
        # 获取数据库schema
        schema = db_source.get_schema()
        
        if not schema:
            return {
                "success": False,
                "answer": None,
                "error": "无法获取数据库schema",
            }
        
        # NL2SQL转换
        nl2sql_result = self.nl2sql.convert(
            question=question,
            database_schema=schema,
            dialect="sqlite",
            chat_history=chat_history,
        )
        
        if not nl2sql_result["success"]:
            return {
                "success": False,
                "answer": None,
                "error": nl2sql_result["error"],
                "sql": None,
            }
        
        sql = nl2sql_result["sql"]
        
        # 执行SQL查询
        query_result = db_source.query(sql)
        
        if not query_result["success"]:
            # 尝试修正SQL
            logger.warning("SQL执行失败，尝试修正...")
            correction_result = self.nl2sql.correct_sql(
                sql=sql,
                error=query_result["error"],
                database_schema=schema,
            )
            
            if correction_result["success"]:
                sql = correction_result["sql"]
                query_result = db_source.query(sql)
        
        if not query_result["success"]:
            return {
                "success": False,
                "answer": None,
                "error": query_result["error"],
                "sql": sql,
            }
        
        # 使用LLM分析查询结果
        data_str = format_data_for_display(query_result["data"])
        
        analysis_prompt = PromptTemplates.DATA_ANALYSIS_TEMPLATE.format(
            data_source=f"数据库: {db_source.name}",
            data_content=data_str,
            question=question,
        )
        
        # 记录Prompt
        logger.info("=" * 70)
        logger.info("📝 [LLM调用] 数据分析")
        logger.info("=" * 70)
        logger.info(f"输入Prompt:\n{analysis_prompt}")
        logger.info("=" * 70)
        
        response = self.llm.complete(analysis_prompt)
        answer = str(response)
        
        logger.info(f"LLM响应:\n{answer}")
        logger.info("=" * 70)
        
        return {
            "success": True,
            "answer": answer,
            "error": None,
            "sql": sql,
            "data": query_result["data"],
            "metadata": query_result["metadata"],
        }
    
    def _analyze_file(
        self,
        question: str,
        file_source: FileDataSource,
        **kwargs
    ) -> Dict[str, Any]:
        """分析文件数据源"""
        # 查询文件数据
        query_result = file_source.query("", limit=100)
        
        if not query_result["success"]:
            return {
                "success": False,
                "answer": None,
                "error": query_result["error"],
            }
        
        # 格式化数据
        data_str = format_data_for_display(query_result["data"])
        
        # 使用LLM分析
        analysis_prompt = PromptTemplates.DATA_ANALYSIS_TEMPLATE.format(
            data_source=f"文件: {file_source.name}",
            data_content=data_str,
            question=question,
        )
        
        # 记录Prompt
        logger.info("=" * 70)
        logger.info("📝 [LLM调用] 文件数据分析")
        logger.info("=" * 70)
        logger.info(f"输入Prompt:\n{analysis_prompt}")
        logger.info("=" * 70)
        
        response = self.llm.complete(analysis_prompt)
        answer = str(response)
        
        logger.info(f"LLM响应:\n{answer}")
        logger.info("=" * 70)
        
        return {
            "success": True,
            "answer": answer,
            "error": None,
            "data": query_result["data"],
            "metadata": query_result["metadata"],
        }
    
    def _analyze_knowledge_base(
        self,
        question: str,
        kb_source: KnowledgeBaseSource,
        **kwargs
    ) -> Dict[str, Any]:
        """分析知识库数据源"""
        # 查询知识库
        query_result = kb_source.query(question, top_k=5)
        
        if not query_result["success"]:
            return {
                "success": False,
                "answer": None,
                "error": query_result["error"],
            }
        
        return {
            "success": True,
            "answer": query_result["data"]["answer"],
            "error": None,
            "retrieved_docs": query_result["data"]["retrieved_docs"],
            "metadata": query_result["metadata"],
        }
    
    def _analyze_web(
        self,
        question: str,
        web_source: WebSearchSource,
        **kwargs
    ) -> Dict[str, Any]:
        """分析Web搜索结果"""
        # 执行搜索
        search_result = web_source.query(question, num_results=5)
        
        if not search_result["success"]:
            return {
                "success": False,
                "answer": None,
                "error": search_result["error"],
            }
        
        # 格式化搜索结果
        results_str = "\n\n".join([
            f"标题: {r['title']}\n链接: {r['link']}\n摘要: {r['snippet']}"
            for r in search_result["data"]
        ])
        
        # 使用LLM分析
        analysis_prompt = PromptTemplates.WEB_SEARCH_ENHANCED.format(
            web_results=results_str,
            other_data="",
            question=question,
        )
        
        # 记录Prompt
        logger.info("=" * 70)
        logger.info("📝 [LLM调用] Web搜索结果分析")
        logger.info("=" * 70)
        logger.info(f"输入Prompt:\n{analysis_prompt}")
        logger.info("=" * 70)
        
        response = self.llm.complete(analysis_prompt)
        answer = str(response)
        
        logger.info(f"LLM响应:\n{answer}")
        logger.info("=" * 70)
        
        return {
            "success": True,
            "answer": answer,
            "error": None,
            "search_results": search_result["data"],
            "metadata": search_result["metadata"],
        }
    
    def analyze_multi_sources(
        self,
        question: str,
        source_names: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        融合多个数据源进行分析
        
        Args:
            question: 用户问题
            source_names: 数据源名称列表
            **kwargs: 额外参数
            
        Returns:
            融合分析结果
        """
        try:
            logger.info(f"🔗 正在融合分析多个数据源: {source_names}")
            
            # 从各个数据源获取数据
            sources_data = {}
            
            for source_name in source_names:
                if source_name not in self.data_sources:
                    logger.warning(f"⚠️  数据源不存在: {source_name}")
                    continue
                
                result = self.analyze_single_source(question, source_name, **kwargs)
                
                if result["success"]:
                    # 提取关键信息
                    if "data" in result:
                        sources_data[source_name] = format_data_for_display(result["data"])
                    elif "answer" in result:
                        sources_data[source_name] = result["answer"]
            
            if not sources_data:
                return {
                    "success": False,
                    "answer": None,
                    "error": "没有可用的数据源",
                }
            
            # 构建多数据源分析Prompt
            prompt = PromptBuilder.build_multi_source_prompt(
                question=question,
                sources=sources_data,
            )
            
            # 记录Prompt
            logger.info("=" * 70)
            logger.info("📝 [LLM调用] 多数据源融合分析")
            logger.info("=" * 70)
            logger.info(f"输入Prompt:\n{prompt}")
            logger.info("=" * 70)
            
            # 调用LLM进行综合分析
            response = self.llm.complete(prompt)
            answer = str(response)
            
            logger.info(f"LLM响应:\n{answer}")
            logger.info("=" * 70)
            
            return {
                "success": True,
                "answer": answer,
                "error": None,
                "sources_used": list(sources_data.keys()),
            }
            
        except Exception as e:
            error_msg = f"多数据源分析失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "answer": None,
                "error": error_msg,
            }
