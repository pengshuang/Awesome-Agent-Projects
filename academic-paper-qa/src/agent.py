"""
学术论文问答 Agent 核心模块

提供基于 LlamaIndex 的向量索引管理和智能问答功能
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.core.schema import Document
from loguru import logger

from config import SystemConfig
from src.loaders.document_loader import DocumentLoader
from src.constants import (
    LOG_SEPARATOR_FULL,
    LOG_SEPARATOR_HALF,
    DEFAULT_WEB_SEARCH_RESULTS,
    INDEX_FILE_NAMES,
    ERROR_NO_DOCUMENTS,
    ERROR_INDEX_NOT_INITIALIZED,
    SUCCESS_INDEX_LOADED,
    SUCCESS_INDEX_BUILT,
    SUCCESS_DOCUMENTS_LOADED,
    SUCCESS_QUERY_COMPLETED,
    WARNING_NO_DOCUMENTS_FOUND,
    WARNING_FORCE_REBUILD,
    INFO_LOADING_FROM_DISK,
    INFO_BUILDING_NEW_INDEX,
    INFO_WEB_SEARCH_ENABLED,
    INFO_WEB_SEARCH_RESULTS,
)


class AcademicAgent:
    """
    学术论文问答 Agent
    
    核心功能：
    1. 向量索引管理（构建、加载、持久化）
    2. 智能问答（基于检索增强生成）
    3. 论文管理（列出、统计）
    
    Attributes:
        documents_dir: 文档目录路径
        index_dir: 索引存储目录路径
        index: 向量索引实例
        query_engine: 查询引擎实例
        documents: 已加载的文档列表
    """
    
    def __init__(
        self,
        documents_dir: Optional[str] = None,
        index_dir: Optional[str] = None,
        auto_load: bool = True,
    ):
        """
        初始化学术论文问答 Agent
        
        Args:
            documents_dir: 文档目录路径，默认使用配置中的路径
            index_dir: 索引存储目录路径，默认使用配置中的路径
            auto_load: 是否自动加载或构建索引
        """
        logger.info(LOG_SEPARATOR_FULL)
        logger.info("初始化学术论文问答 Agent")
        logger.info(LOG_SEPARATOR_FULL)
        
        # 设置路径
        self.documents_dir = Path(documents_dir or SystemConfig.DOCUMENTS_DIR)
        self.index_dir = Path(index_dir or SystemConfig.VECTOR_STORE_DIR)
        
        logger.info(f"文档目录: {self.documents_dir}")
        logger.info(f"索引目录: {self.index_dir}")
        
        # 初始化属性
        self.index: Optional[VectorStoreIndex] = None
        self.query_engine = None
        self.documents: List[Document] = []
        
        # 对话历史管理
        self.chat_history: List[Dict[str, str]] = []  # 存储对话历史 [{"role": "user/assistant", "content": "..."}]
        self.max_history_turns: int = 10  # 最大保留历史轮数
        
        # 确保目录存在
        self._ensure_directories()
        
        # 自动加载索引
        if auto_load:
            self.load_or_build_index()
        
        logger.info("Agent 初始化完成")
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"✓ 目录检查完成")
    
    def _index_exists(self) -> bool:
        """
        检查索引是否存在
        
        Returns:
            索引是否存在
        """
        # 检查索引目录下是否有必要的文件（LlamaIndex 索引需要这三个 JSON 文件）
        required_files = INDEX_FILE_NAMES
        
        for file_name in required_files:
            file_path = self.index_dir / file_name
            if not file_path.exists():
                logger.debug(f"索引文件不存在: {file_name}")
                return False
        
        logger.debug("✓ 索引文件完整")
        return True
    
    def load_or_build_index(self, force_rebuild: bool = False) -> VectorStoreIndex:
        """
        加载或构建向量索引
        
        如果索引已存在且不强制重建，则从磁盘加载；否则重新构建索引。
        
        Args:
            force_rebuild: 是否强制重建索引
            
        Returns:
            向量索引实例
        """
        logger.info(LOG_SEPARATOR_HALF)
        logger.info("开始加载或构建索引...")
        logger.info(LOG_SEPARATOR_HALF)
        
        if force_rebuild:
            logger.info(WARNING_FORCE_REBUILD)
            return self.rebuild_index()
        
        # 尝试加载现有索引
        if self._index_exists():
            try:
                logger.info("检测到现有索引，尝试加载...")
                return self._load_index()
            except Exception as e:
                logger.warning(f"加载索引失败: {e}")
                logger.info("将重新构建索引...")
                return self.rebuild_index()
        else:
            logger.info(INFO_BUILDING_NEW_INDEX)
            return self.rebuild_index()
    
    def _load_index(self) -> VectorStoreIndex:
        """
        从磁盘加载索引
        
        Returns:
            向量索引实例
        """
        start_time = datetime.now()
        
        logger.info(INFO_LOADING_FROM_DISK.format(self.index_dir))
        
        try:
            # 加载存储上下文
            storage_context = StorageContext.from_defaults(
                persist_dir=str(self.index_dir)
            )
            
            # 加载索引
            self.index = load_index_from_storage(storage_context)
            
            # 创建查询引擎
            self._create_query_engine()
            
            # 计算加载时间
            elapsed = (datetime.now() - start_time).total_seconds()
            
            logger.success(SUCCESS_INDEX_LOADED.format(elapsed))
            
            # 尝试获取文档统计信息
            try:
                # 尝试获取索引中的文档块数量（部分索引类型可能不支持）
                doc_count = len(self.index.docstore.docs)
                logger.info(f"索引包含 {doc_count} 个文档块")
            except Exception:
                # 某些向量存储（如 Qdrant）可能没有 docstore 属性，忽略错误
                logger.debug("无法获取文档统计信息")
            
            return self.index
            
        except Exception as e:
            logger.error(f"✗ 索引加载失败: {e}")
            raise
    
    def rebuild_index(self) -> VectorStoreIndex:
        """
        重新构建向量索引
        
        完整流程：
        1. 加载文档
        2. 构建向量索引
        3. 持久化到磁盘
        
        Returns:
            向量索引实例
        """
        logger.info(LOG_SEPARATOR_FULL)
        logger.info("开始构建向量索引")
        logger.info(LOG_SEPARATOR_FULL)
        
        start_time = datetime.now()
        
        try:
            # 1. 加载文档
            logger.info("步骤 1/3: 加载文档")
            self._load_documents()
            
            if not self.documents:
                raise ValueError(ERROR_NO_DOCUMENTS.format(self.documents_dir))
            
            # 2. 构建索引
            logger.info("步骤 2/3: 构建向量索引")
            self._build_index()
            
            # 3. 持久化索引
            logger.info("步骤 3/3: 持久化索引到磁盘")
            self._persist_index()
            
            # 创建查询引擎
            self._create_query_engine()
            
            # 计算总耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            
            logger.success(LOG_SEPARATOR_FULL)
            logger.success(SUCCESS_INDEX_BUILT.format(elapsed))
            logger.success(LOG_SEPARATOR_FULL)
            
            return self.index
            
        except Exception as e:
            logger.error(f"✗ 索引构建失败: {e}")
            raise
    
    def _load_documents(self):
        """加载文档"""
        logger.info(f"从目录加载文档: {self.documents_dir}")
        
        # 使用 DocumentLoader 加载文档
        loader = DocumentLoader(
            input_dir=self.documents_dir,
            recursive=True,
            clean_text=True,
            preserve_formatting=True,
        )
        
        # 加载所有支持的文档格式
        self.documents = loader.load_documents()
        
        if not self.documents:
            logger.warning(WARNING_NO_DOCUMENTS_FOUND.format(self.documents_dir))
            return
        
        # 打印统计信息
        stats = loader.get_document_stats(self.documents)
        
        logger.success(SUCCESS_DOCUMENTS_LOADED + ":")
        logger.info(f"  - 总文档数: {stats['total_documents']}")
        logger.info(f"  - 总文件数: {stats['total_files']}")
        logger.info(f"  - 文件类型: {stats['file_types']}")
        logger.info(f"  - 总大小: {stats['total_size_mb']:.2f} MB")
        logger.info(f"  - 总字符数: {stats['total_chars']:,}")
        logger.info(f"  - 总单词数: {stats['total_words']:,}")
    
    def _build_index(self):
        """构建向量索引"""
        import os
        logger.info(f"使用 Embedding 提供商: {os.getenv('EMBEDDING_PROVIDER', 'huggingface')}")
        logger.info(f"Chunk 大小: {SystemConfig.CHUNK_SIZE}, 重叠: {SystemConfig.CHUNK_OVERLAP}")
        
        # 使用 LlamaIndex Settings 中配置的 Embedding 模型
        # Settings 已在系统初始化时配置
        
        # 构建索引
        self.index = VectorStoreIndex.from_documents(
            self.documents,
            show_progress=True,
        )
        
        logger.success(f"✓ 向量索引构建完成")
        
        # 显示索引统计
        try:
            doc_count = len(self.index.docstore.docs)
            logger.info(f"索引包含 {doc_count} 个文档块")
        except Exception:
            logger.debug("无法获取索引统计信息")
    
    def _persist_index(self):
        """持久化索引到磁盘"""
        logger.info(f"保存索引到: {self.index_dir}")
        
        # 持久化
        self.index.storage_context.persist(persist_dir=str(self.index_dir))
        
        logger.success(f"✓ 索引已保存到磁盘")
        
        # 显示保存的文件
        saved_files = list(self.index_dir.glob('*.json'))
        logger.debug(f"保存的文件: {[f.name for f in saved_files]}")
    
    def _create_query_engine(self):
        """创建查询引擎"""
        if not self.index:
            raise ValueError(ERROR_INDEX_NOT_INITIALIZED)
        
        # 创建查询引擎，使用配置的参数
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=SystemConfig.RETRIEVAL_TOP_K,
            streaming=False,
        )
        
        logger.debug(f"✓ 查询引擎已创建 (top_k={SystemConfig.RETRIEVAL_TOP_K})")
    
    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        verbose: bool = False,
        enable_web_search: bool = None,
        use_history: bool = False,
    ) -> Dict[str, Any]:
        """
        执行查询
        
        Args:
            question: 用户问题
            top_k: 检索的相关文档数量，默认使用配置值
            verbose: 是否显示详细信息
            enable_web_search: 是否启用联网搜索，None时使用配置值
            use_history: 是否使用对话历史
            
        Returns:
            包含查询结果的字典:
            - answer: 生成的答案
            - source_nodes: 参考的源文档节点（包含文本片段）
            - web_sources: 联网搜索结果（如果启用）
            - metadata: 元数据信息
        """
        if not self.query_engine:
            raise ValueError("查询引擎未初始化，请先加载或构建索引")
        
        logger.info(LOG_SEPARATOR_HALF)
        logger.info(f"问题: {question}")
        logger.info(LOG_SEPARATOR_HALF)
        
        # 处理多轮对话上下文
        enhanced_question = question
        if use_history and self.chat_history:
            # 构建带历史的提示词
            context_prompt = self._build_context_prompt(question)
            enhanced_question = context_prompt
            logger.debug(f"使用对话历史，历史轮数: {len(self.chat_history) // 2}")
        
        start_time = datetime.now()
        web_sources = []
        
        try:
            # 检查是否启用联网搜索
            if enable_web_search is None:
                enable_web_search = SystemConfig.ENABLE_WEB_SEARCH
            
            # 执行联网搜索（如果启用）
            if enable_web_search:
                try:
                    from src.tools.web_search import WebSearchTool
                    logger.info("🌐 正在进行联网搜索...")
                    web_tool = WebSearchTool(max_results=3)
                    web_sources = web_tool.search(question)
                    
                    if web_sources:
                        logger.info(f"✓ 找到 {len(web_sources)} 个网络资源:")
                        for i, source in enumerate(web_sources, 1):
                            logger.info(f"  [{i}] {source['url']}")
                    else:
                        logger.warning("⚠ 未找到相关网络资源")
                except Exception as e:
                    logger.warning(f"联网搜索失败: {e}")
            
            # 如果指定了 top_k，重新创建查询引擎
            if top_k and top_k != SystemConfig.RETRIEVAL_TOP_K:
                logger.debug(f"使用自定义 top_k: {top_k}")
                query_engine = self.index.as_query_engine(
                    similarity_top_k=top_k,
                    streaming=False,
                )
            else:
                query_engine = self.query_engine
            
            # 执行RAG查询
            logger.info("正在检索相关文档并生成回答...")
            response = query_engine.query(enhanced_question)
            
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            
            # 提取答案
            answer = str(response)
            
            # 提取源节点（包含文本片段）
            source_nodes = []
            if hasattr(response, 'source_nodes'):
                source_nodes = response.source_nodes
            
            logger.success(f"✓ 查询完成！耗时: {elapsed:.2f} 秒")
            
            if verbose:
                logger.info(f"\n回答:\n{answer}\n")
                
                if source_nodes:
                    logger.info(f"参考了 {len(source_nodes)} 个文档片段:")
                    for i, node in enumerate(source_nodes, 1):
                        score = node.score if hasattr(node, 'score') else 'N/A'
                        file_name = node.metadata.get('file_name', 'Unknown')
                        text_preview = node.text[:100].replace('\n', ' ') if hasattr(node, 'text') else 'N/A'
                        logger.info(f"  [{i}] {file_name} (相似度: {score})")
                        logger.info(f"      片段: {text_preview}...")
            
            # 更新对话历史
            if use_history:
                self._update_chat_history(question, answer)
            
            # 构建结果
            result = {
                'answer': answer,
                'source_nodes': source_nodes,
                'web_sources': web_sources,
                'metadata': {
                    'question': question,
                    'elapsed_time': elapsed,
                    'num_sources': len(source_nodes),
                    'num_web_sources': len(web_sources),
                    'top_k': top_k or SystemConfig.RETRIEVAL_TOP_K,
                    'web_search_enabled': enable_web_search,
                    'use_history': use_history,
                    'history_turns': len(self.chat_history) // 2,
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"✗ 查询失败: {e}")
            raise
    
    def query_direct(
        self,
        question: str,
        context: Optional[str] = None,
        enable_web_search: bool = None,
    ) -> Dict[str, Any]:
        """
        直接查询LLM（不使用向量库）
        
        Args:
            question: 用户问题
            context: 可选的上下文信息（用户提供的文本）
            enable_web_search: 是否启用联网搜索
            
        Returns:
            包含查询结果的字典:
            - answer: LLM生成的答案
            - web_sources: 联网搜索结果（如果启用）
            - metadata: 元数据信息
        """
        logger.info(LOG_SEPARATOR_HALF)
        logger.info(f"问题 (直接LLM模式): {question}")
        logger.info(LOG_SEPARATOR_HALF)
        
        start_time = datetime.now()
        web_sources = []
        
        try:
            # 检查是否需要联网搜索（None 时使用配置的默认值）
            if enable_web_search is None:
                enable_web_search = SystemConfig.ENABLE_WEB_SEARCH
            
            # 执行联网搜索以补充LLM知识
            if enable_web_search:
                try:
                    # 动态导入避免启动时依赖
                    from src.tools.web_search import WebSearchTool
                    logger.info(INFO_WEB_SEARCH_ENABLED)
                    # 限制返回结果数避免上下文过长
                    web_tool = WebSearchTool(max_results=DEFAULT_WEB_SEARCH_RESULTS)
                    web_sources = web_tool.search(question)
                    
                    if web_sources:
                        logger.info(INFO_WEB_SEARCH_RESULTS.format(len(web_sources)) + ":")
                        for i, source in enumerate(web_sources, 1):
                            logger.info(f"  [{i}] {source['url']}")
                except Exception as e:
                    logger.warning(f"联网搜索失败: {e}")
            
            # 构建提示词
            prompt = question
            if context:
                prompt = f"根据以下上下文回答问题:\n\n上下文:\n{context}\n\n问题: {question}"
            elif web_sources:
                # 如果有网络搜索结果，添加到提示词
                web_context = "\n\n".join([
                    f"来源 [{i+1}]: {s['title']}\n{s['snippet']}\n网址: {s['url']}"
                    for i, s in enumerate(web_sources)
                ])
                prompt = f"根据以下网络搜索结果回答问题:\n\n{web_context}\n\n问题: {question}"
            
            # 直接调用LLM
            logger.info("正在调用LLM生成回答...")
            from llama_index.core import Settings
            llm = Settings.llm
            
            response = llm.complete(prompt)
            answer = str(response)
            
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            
            logger.success(SUCCESS_QUERY_COMPLETED.format(elapsed))
            
            # 构建结果
            result = {
                'answer': answer,
                'source_nodes': [],  # 直接模式没有源节点
                'web_sources': web_sources,
                'metadata': {
                    'question': question,
                    'elapsed_time': elapsed,
                    'num_sources': 0,
                    'num_web_sources': len(web_sources),
                    'mode': 'direct_llm',
                    'has_context': bool(context),
                    'web_search_enabled': enable_web_search,
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"✗ 直接查询失败: {e}")
            raise
    
    def list_papers(self, detailed: bool = False) -> List[Dict[str, Any]]:
        """
        列出所有已加载的论文
        
        Args:
            detailed: 是否显示详细信息
            
        Returns:
            论文列表，每个论文包含元数据信息
        """
        logger.info("-" * 70)
        logger.info("已加载的论文列表")
        logger.info("-" * 70)
        
        if not self.documents:
            logger.warning("⚠ 未加载任何文档")
            return []
        
        # 按文件名分组文档
        papers_dict: Dict[str, Dict[str, Any]] = {}
        
        for doc in self.documents:
            file_name = doc.metadata.get('file_name', 'Unknown')
            
            if file_name not in papers_dict:
                papers_dict[file_name] = {
                    'file_name': file_name,
                    'file_path': doc.metadata.get('file_path', 'Unknown'),
                    'file_type': doc.metadata.get('file_type', 'Unknown'),
                    'file_size_mb': doc.metadata.get('file_size_mb', 0),
                    'page_count': 1,
                    'total_chars': len(doc.text),
                    'created_time': doc.metadata.get('created_time', 'Unknown'),
                    'modified_time': doc.metadata.get('modified_time', 'Unknown'),
                }
            else:
                # 如果是 PDF 的多页，累加信息
                papers_dict[file_name]['page_count'] += 1
                papers_dict[file_name]['total_chars'] += len(doc.text)
        
        # 转换为列表
        papers = list(papers_dict.values())
        
        # 排序
        papers.sort(key=lambda x: x['file_name'])
        
        # 显示列表
        logger.info(f"总计: {len(papers)} 个论文文件\n")
        
        for i, paper in enumerate(papers, 1):
            logger.info(f"[{i}] {paper['file_name']}")
            if detailed:
                logger.info(f"    类型: {paper['file_type']}")
                logger.info(f"    大小: {paper['file_size_mb']:.2f} MB")
                if paper['file_type'] == 'pdf':
                    logger.info(f"    页数: {paper['page_count']}")
                logger.info(f"    字符数: {paper['total_chars']:,}")
                logger.info(f"    路径: {paper['file_path']}")
                logger.info("")
        
        return papers
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取 Agent 统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            'documents_dir': str(self.documents_dir),
            'index_dir': str(self.index_dir),
            'index_exists': self._index_exists(),
            'documents_loaded': len(self.documents),
            'query_engine_ready': self.query_engine is not None,
        }
        
        # 如果有索引，添加索引统计
        if self.index:
            try:
                stats['index_doc_count'] = len(self.index.docstore.docs)
            except Exception:
                stats['index_doc_count'] = 'N/A'
        
        return stats
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"AcademicAgent(\n"
            f"  documents_dir='{self.documents_dir}',\n"
            f"  index_dir='{self.index_dir}',\n"
            f"  documents_loaded={len(self.documents)},\n"
            f"  index_ready={self.index is not None},\n"
            f"  query_engine_ready={self.query_engine is not None}\n"
            f")"
        )
    
    def _build_context_prompt(self, question: str) -> str:
        """
        构建带历史上下文的提示词
        
        Args:
            question: 当前问题
            
        Returns:
            包含历史对话的增强提示词
        """
        # 获取最近的历史（按配置的最大轮数）
        recent_history = self.chat_history[-(self.max_history_turns * 2):]
        
        # 构建对话历史字符串
        history_text = ""
        for msg in recent_history:
            role_name = "用户" if msg["role"] == "user" else "助手"
            history_text += f"\n{role_name}: {msg['content']}"
        
        # 构建最终提示词
        prompt = f"""根据以下对话历史和当前问题，提供准确的回答。

对话历史:{history_text}

当前问题: {question}

请基于上下文回答当前问题，如果问题与之前的对话相关，请结合历史信息回答。"""
        
        return prompt
    
    def _update_chat_history(self, user_message: str, assistant_message: str):
        """
        更新对话历史
        
        Args:
            user_message: 用户消息
            assistant_message: 助手回复
        """
        self.chat_history.append({"role": "user", "content": user_message})
        self.chat_history.append({"role": "assistant", "content": assistant_message})
        
        # 限制历史长度
        max_messages = self.max_history_turns * 2
        if len(self.chat_history) > max_messages:
            self.chat_history = self.chat_history[-max_messages:]
        
        logger.debug(f"对话历史已更新，当前轮数: {len(self.chat_history) // 2}")
    
    def clear_chat_history(self):
        """清除对话历史"""
        self.chat_history = []
        logger.info("对话历史已清除")
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        获取对话历史
        
        Returns:
            对话历史列表
        """
        return self.chat_history.copy()
    
    def set_max_history_turns(self, max_turns: int):
        """
        设置最大历史轮数
        
        Args:
            max_turns: 最大轮数
        """
        self.max_history_turns = max_turns
        logger.info(f"最大历史轮数已设置为: {max_turns}")


# 便捷函数
def create_agent(
    documents_dir: Optional[str] = None,
    index_dir: Optional[str] = None,
    force_rebuild: bool = False,
) -> AcademicAgent:
    """
    创建学术论文问答 Agent（便捷函数）
    
    Args:
        documents_dir: 文档目录路径
        index_dir: 索引存储目录路径
        force_rebuild: 是否强制重建索引
        
    Returns:
        AcademicAgent 实例
    """
    agent = AcademicAgent(
        documents_dir=documents_dir,
        index_dir=index_dir,
        auto_load=False,
    )
    
    agent.load_or_build_index(force_rebuild=force_rebuild)
    
    return agent


__all__ = ['AcademicAgent', 'create_agent']
