"""
AI 数据分析助手 Agent
核心多轮对话代理
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from loguru import logger

from config.settings import SystemConfig
from config.llm_config import get_llm
from config.prompts import PromptTemplates, PromptBuilder
from src.analyzers import DataAnalyzer
from src.datasources import (
    SQLiteDataSource,
    FileDataSource,
    KnowledgeBaseSource,
    WebSearchSource,
)
from src.utils.helpers import format_sql_for_display


class DataAnalystAgent:
    """
    AI 数据分析助手 Agent
    
    功能：
    1. 多轮对话
    2. 多数据源管理（SQLite、文件、知识库、Web搜索）
    3. NL2SQL 查询
    4. 数据融合分析
    5. 报告生成
    6. 决策支持
    """
    
    def __init__(self, max_history_turns: int = 10):
        """
        初始化 Agent
        
        Args:
            max_history_turns: 最大保留历史轮数（默认10轮）
        """
        logger.info("=" * 70)
        logger.info("🤖 初始化 AI 数据分析助手 Agent")
        logger.info("=" * 70)
        
        # 初始化LLM
        self.llm = get_llm()
        
        # 初始化分析引擎
        self.analyzer = DataAnalyzer()
        
        # 对话历史管理
        self.chat_history: List[Dict[str, str]] = []
        self.max_history_turns = max_history_turns
        
        # 确保必要目录存在
        SystemConfig.ensure_directories()
        
        logger.info(f"✅ Agent 初始化完成（历史轮数: {max_history_turns}）")
    
    def register_sqlite_database(self, name: str, db_path: str) -> bool:
        """
        注册 SQLite 数据库
        
        Args:
            name: 数据库名称
            db_path: 数据库文件路径
            
        Returns:
            是否注册成功
        """
        try:
            db_source = SQLiteDataSource(name, db_path)
            if db_source.connect():
                self.analyzer.register_data_source(name, db_source)
                return True
            return False
        except Exception as e:
            logger.error(f"注册数据库失败: {e}")
            return False
    
    def register_file(self, name: str, file_path: str) -> bool:
        """
        注册文件数据源
        
        Args:
            name: 文件名称
            file_path: 文件路径
            
        Returns:
            是否注册成功
        """
        try:
            file_source = FileDataSource(name, file_path)
            if file_source.connect():
                self.analyzer.register_data_source(name, file_source)
                return True
            return False
        except Exception as e:
            logger.error(f"注册文件失败: {e}")
            return False
    
    def register_knowledge_base(self, name: str, kb_dir: Optional[str] = None) -> bool:
        """
        注册知识库
        
        Args:
            name: 知识库名称
            kb_dir: 知识库目录（可选）
            
        Returns:
            是否注册成功
        """
        try:
            kb_source = KnowledgeBaseSource(name, kb_dir)
            if kb_source.connect():
                self.analyzer.register_data_source(name, kb_source)
                return True
            return False
        except Exception as e:
            logger.error(f"注册知识库失败: {e}")
            return False
    
    def register_web_search(self) -> bool:
        """
        注册 Web 搜索数据源
        
        Returns:
            是否注册成功
        """
        try:
            web_source = WebSearchSource()
            if web_source.connect():
                self.analyzer.register_data_source("web_search", web_source)
                return True
            return False
        except Exception as e:
            logger.error(f"注册Web搜索失败: {e}")
            return False
    
    def chat(
        self,
        message: str,
        source_name: Optional[str] = None,
        multi_sources: Optional[List[str]] = None,
    ) -> str:
        """
        多轮对话主入口
        
        Args:
            message: 用户消息
            source_name: 单个数据源名称（可选）
            multi_sources: 多个数据源名称列表（可选）
            
        Returns:
            助手回复
        """
        try:
            logger.info("=" * 70)
            logger.info(f"👤 用户: {message}")
            logger.info("=" * 70)
            
            # 添加用户消息到历史
            self._add_to_history("user", message)
            
            # 判断处理策略
            if multi_sources:
                # 多数据源融合分析
                result = self.analyzer.analyze_multi_sources(
                    question=message,
                    source_names=multi_sources,
                    chat_history=self._format_chat_history(),
                )
            elif source_name:
                # 单数据源分析
                result = self.analyzer.analyze_single_source(
                    question=message,
                    source_name=source_name,
                    chat_history=self._format_chat_history(),
                )
            else:
                # 直接对话（无数据源）
                result = self._direct_chat(message)
            
            # 构建回复
            if result["success"]:
                reply = result["answer"]
                
                # 如果有SQL，添加SQL展示
                if "sql" in result and result["sql"]:
                    sql_display = format_sql_for_display(result["sql"])
                    reply = f"### 生成的SQL查询\n\n{sql_display}\n\n### 分析结果\n\n{reply}"
            else:
                reply = f"❌ 抱歉，处理您的请求时遇到了问题：\n\n{result['error']}"
            
            # 添加助手回复到历史
            self._add_to_history("assistant", reply)
            
            logger.info(f"🤖 助手: {reply[:200]}...")
            logger.info("=" * 70)
            
            return reply
            
        except Exception as e:
            error_msg = f"❌ 对话处理失败: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _direct_chat(self, message: str) -> Dict[str, Any]:
        """直接对话（无数据源）"""
        try:
            chat_history_str = self._format_chat_history()
            
            if chat_history_str:
                prompt = PromptTemplates.CHAT_WITH_HISTORY.format(
                    chat_history=chat_history_str,
                    context="",
                    question=message,
                )
            else:
                prompt = message
            
            # 记录Prompt
            logger.info("=" * 70)
            logger.info("📝 [LLM调用] 直接对话")
            logger.info("=" * 70)
            logger.info(f"输入Prompt:\n{prompt}")
            logger.info("=" * 70)
            
            response = self.llm.complete(prompt)
            answer = str(response)
            
            logger.info(f"LLM响应:\n{answer}")
            logger.info("=" * 70)
            
            return {
                "success": True,
                "answer": answer,
                "error": None,
            }
            
        except Exception as e:
            return {
                "success": False,
                "answer": None,
                "error": str(e),
            }
    
    def _add_to_history(self, role: str, content: str):
        """添加消息到历史"""
        self.chat_history.append({
            "role": role,
            "content": content,
        })
        
        # 限制历史长度（保留最近的 N 轮对话）
        max_messages = self.max_history_turns * 2  # 每轮包含用户和助手两条消息
        if len(self.chat_history) > max_messages:
            self.chat_history = self.chat_history[-max_messages:]
            logger.debug(f"对话历史已截断到最近 {self.max_history_turns} 轮")
    
    def _format_chat_history(self) -> str:
        """格式化对话历史"""
        return PromptBuilder.format_chat_history(self.chat_history[:-1])  # 不包括当前消息
    
    def clear_history(self):
        """清空对话历史"""
        self.chat_history = []
        logger.info("🗑️  对话历史已清空")
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.chat_history.copy()
    
    def list_data_sources(self) -> Dict[str, Any]:
        """列出所有已注册的数据源"""
        sources_info = {}
        
        for name, source in self.analyzer.data_sources.items():
            sources_info[name] = {
                "type": source.source_type,
                "name": source.name,
            }
        
        return sources_info
    
    def get_data_source_schema(self, source_name: str) -> Optional[str]:
        """获取数据源的schema信息"""
        if source_name not in self.analyzer.data_sources:
            return None
        
        source = self.analyzer.data_sources[source_name]
        return source.get_schema()
