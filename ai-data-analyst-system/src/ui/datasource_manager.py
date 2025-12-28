"""
Web UI 数据源管理模块
"""

from typing import Optional
from loguru import logger

from src.agent import DataAnalystAgent
from .helpers import format_datasource_info, format_error_message, format_datasource_list
from .constants import MSG_ERROR_NOT_INITIALIZED, TIPS


class DataSourceManager:
    """数据源管理器"""
    
    def __init__(self, agent: Optional[DataAnalystAgent] = None):
        self.agent = agent
    
    def set_agent(self, agent: DataAnalystAgent):
        """设置Agent实例"""
        self.agent = agent
    
    def register_sqlite(self, db_name: str, db_path: str) -> str:
        """
        注册 SQLite 数据库
        
        Args:
            db_name: 数据库名称
            db_path: 数据库路径
            
        Returns:
            注册结果消息
        """
        if not self.agent:
            return MSG_ERROR_NOT_INITIALIZED
        
        if not db_name or not db_path:
            return format_error_message("请填写数据库名称和路径")
        
        try:
            success = self.agent.register_sqlite_database(db_name, db_path)
            if success:
                schema = self.agent.get_data_source_schema(db_name)
                return format_datasource_info(
                    name=db_name,
                    path=db_path,
                    source_type="SQLite Database",
                    schema=schema,
                    tips=TIPS["database"]
                )
            else:
                return format_error_message(f"数据库注册失败: {db_name}")
        except Exception as e:
            logger.error(f"注册数据库失败: {e}")
            return format_error_message(f"注册失败: {str(e)}")
    
    def register_file(self, file_name: str, file_path: str) -> str:
        """
        注册文件数据源
        
        Args:
            file_name: 文件名称
            file_path: 文件路径
            
        Returns:
            注册结果消息
        """
        if not self.agent:
            return MSG_ERROR_NOT_INITIALIZED
        
        if not file_name or not file_path:
            return format_error_message("请填写文件名称和路径")
        
        try:
            success = self.agent.register_file(file_name, file_path)
            if success:
                schema = self.agent.get_data_source_schema(file_name)
                return format_datasource_info(
                    name=file_name,
                    path=file_path,
                    source_type="File (CSV/Excel/JSON)",
                    schema=schema,
                    tips=TIPS["file"]
                )
            else:
                return format_error_message(f"文件注册失败: {file_name}")
        except Exception as e:
            logger.error(f"注册文件失败: {e}")
            return format_error_message(f"注册失败: {str(e)}")
    
    def register_knowledge_base(self, kb_name: str, kb_dir: Optional[str] = None) -> str:
        """
        注册知识库
        
        Args:
            kb_name: 知识库名称
            kb_dir: 知识库目录
            
        Returns:
            注册结果消息
        """
        if not self.agent:
            return MSG_ERROR_NOT_INITIALIZED
        
        if not kb_name:
            return format_error_message("请填写知识库名称")
        
        try:
            success = self.agent.register_knowledge_base(kb_name, kb_dir)
            if success:
                schema = self.agent.get_data_source_schema(kb_name)
                kb_dir_display = kb_dir if kb_dir else "默认目录 (data/knowledge_base/)"
                return format_datasource_info(
                    name=kb_name,
                    path=kb_dir_display,
                    source_type="Vector Knowledge Base",
                    schema=schema,
                    tips=TIPS["knowledge_base"]
                )
            else:
                return format_error_message(f"知识库注册失败: {kb_name}")
        except Exception as e:
            logger.error(f"注册知识库失败: {e}")
            return format_error_message(f"注册失败: {str(e)}")
    
    def register_web_search(self) -> str:
        """
        注册 Web 搜索
        
        Returns:
            注册结果消息
        """
        if not self.agent:
            return MSG_ERROR_NOT_INITIALIZED
        
        try:
            success = self.agent.register_web_search()
            if success:
                result = """## ✅ Web搜索已启用

**数据源名称**: `web_search`  
**数据源类型**: Web Search Engine

---

### 🌐 Web搜索功能

Web搜索可以帮助您获取实时的互联网信息，适用于：
- 📰 获取最新资讯和动态
- 🔍 验证事实和数据
- 📊 补充分析所需的外部信息
- 🌍 了解行业趋势和市场动态

---

💡 **提示**: 现在可以在「对话分析」页面选择此数据源进行联网查询了！

""" + TIPS["web_search"]
                return result
            else:
                return """❌ Web搜索启用失败

请检查配置：
1. 确保在 `.env` 文件中设置了 `ENABLE_WEB_SEARCH=true`
2. 配置 `WEB_SEARCH_API_KEY`（如使用SerpAPI等服务）
3. 重启服务使配置生效
"""
        except Exception as e:
            logger.error(f"启用Web搜索失败: {e}")
            return format_error_message(f"启用失败: {str(e)}")
    
    def list_sources(self) -> str:
        """
        列出所有数据源
        
        Returns:
            数据源列表
        """
        if not self.agent:
            return MSG_ERROR_NOT_INITIALIZED
        
        sources = self.agent.list_data_sources()
        return format_datasource_list(sources)
