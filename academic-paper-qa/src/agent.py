"""
学术论文问答 Agent 核心模块

提供基于 LlamaIndex 的向量索引管理和智能问答功能
"""

import os
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
from openai import OpenAI

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
        max_history_turns: int = 10,
    ):
        """
        初始化学术论文问答 Agent
        
        Args:
            documents_dir: 文档目录路径，默认使用配置中的路径
            index_dir: 索引存储目录路径，默认使用配置中的路径
            auto_load: 是否自动加载或构建索引
            max_history_turns: 多轮对话最大保留历史轮数（默认10轮，即20条消息）
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
        self.max_history_turns: int = max_history_turns  # 最大保留历史轮数
        
        # 文件上传缓存（用于多轮对话）
        self._uploaded_files_cache: Dict[str, Dict[str, Any]] = {}  # {file_path: {"id": file_id, "content": file_content}}
        
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
            logger.debug(f"使用对话历史，当前轮数: {len(self.chat_history) // 2}，最大限制: {self.max_history_turns} 轮")
        
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
                        
                        # 将搜索结果添加到查询中
                        web_context = "\n\n".join([
                            f"来源 [{i+1}]: {s['title']}\n{s['snippet']}\n网址: {s['url']}"
                            for i, s in enumerate(web_sources)
                        ])
                        enhanced_question = f"{enhanced_question}\n\n参考以下网络搜索结果:\n{web_context}"
                        logger.debug(f"已将 {len(web_sources)} 个搜索结果添加到查询上下文")
                        
                        # 打印加上网络搜索结果后输入给模型的完整内容
                        logger.info("\n" + "="*70)
                        logger.info("【RAG模式】输入给模型的完整查询内容:")
                        logger.info("="*70)
                        logger.info(enhanced_question)
                        logger.info("="*70 + "\n")
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
    
    def _upload_files_to_moonshot(self, file_paths: List[str], use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        上传文件到 Moonshot API
        
        Args:
            file_paths: 文件路径列表
            use_cache: 是否使用缓存（多轮对话时避免重复上传）
            
        Returns:
            上传的文件对象列表
        """
        api_key = os.getenv("LLM_API_KEY")
        api_base = os.getenv("LLM_API_BASE", "https://api.moonshot.cn/v1")
        
        # 检查是否是 Moonshot API
        if "moonshot" not in api_base.lower():
            logger.warning("当前 API 不是 Moonshot，无法使用文件上传功能")
            return []
        
        client = OpenAI(api_key=api_key, base_url=api_base)
        uploaded_files = []
        
        for file_path in file_paths:
            try:
                # 处理路径
                path = Path(file_path)
                if not path.is_absolute():
                    path = self.documents_dir / path
                
                path_str = str(path)
                
                if not path.exists():
                    logger.warning(f"⚠️ 文件不存在: {path}")
                    continue
                
                # 检查缓存
                if use_cache and path_str in self._uploaded_files_cache:
                    cached_file = self._uploaded_files_cache[path_str]
                    uploaded_files.append(cached_file)
                    logger.info(f"♻️ 使用缓存的文件: {path.name} (ID: {cached_file['id']})")
                    continue
                
                logger.info(f"📤 正在上传文件到 Moonshot: {path.name}")
                
                # 上传文件
                file_object = client.files.create(
                    file=path,
                    purpose="file-extract"
                )
                
                file_data = {
                    'id': file_object.id,
                    'filename': file_object.filename,
                    'path': path_str
                }
                
                uploaded_files.append(file_data)
                
                # 缓存文件信息
                if use_cache:
                    self._uploaded_files_cache[path_str] = file_data
                
                logger.info(f"✅ 文件上传成功: {path.name} (ID: {file_object.id})")
                
            except Exception as e:
                logger.error(f"✗ 文件上传失败 {file_path}: {e}")
                continue
        
        return uploaded_files
    
    def query_direct(
        self,
        question: str,
        context: Optional[str] = None,
        enable_web_search: bool = None,
        document_files: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        直接查询LLM（不使用向量库）
        
        Args:
            question: 用户问题
            context: 可选的上下文信息（用户提供的文本）
            enable_web_search: 是否启用联网搜索
            document_files: 可选的文档文件路径列表，作为附件发送给LLM
            
        Returns:
            包含查询结果的字典:
            - answer: LLM生成的答案
            - web_sources: 联网搜索结果（如果启用）
            - document_sources: 使用的文档文件列表
            - metadata: 元数据信息
        """
        logger.info(LOG_SEPARATOR_HALF)
        logger.info(f"问题 (直接LLM模式): {question}")
        logger.info(LOG_SEPARATOR_HALF)
        
        start_time = datetime.now()
        web_sources = []
        document_sources = []
        uploaded_file_ids = []
        
        try:
            # 处理文档附件 - 使用 Moonshot 文件上传
            if document_files:
                logger.info(f"📎 准备处理 {len(document_files)} 个文档附件...")
                
                # 尝试上传到 Moonshot
                uploaded_files = self._upload_files_to_moonshot(document_files)
                
                if uploaded_files:
                    document_sources = document_files
                    uploaded_file_ids = [f['id'] for f in uploaded_files]
                    logger.info(f"✅ 成功上传 {len(uploaded_files)} 个文件到 Moonshot")
                else:
                    logger.warning("⚠️ 文件上传失败，将回退到文本提取方式")
            
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
            prompt_parts = []
            
            # 添加用户提供的上下文
            if context:
                prompt_parts.append(f"补充上下文:\n{context}")
            
            # 添加网络搜索结果
            if web_sources:
                web_context = "\n\n".join([
                    f"来源 [{i+1}]: {s['title']}\n{s['snippet']}\n网址: {s['url']}"
                    for i, s in enumerate(web_sources)
                ])
                prompt_parts.append(f"网络搜索结果:\n{web_context}")
            
            # 构建完整提示词
            if prompt_parts:
                combined_parts = "\n\n" + ("="*50 + "\n\n").join(prompt_parts)
                prompt = combined_parts + "\n\n" + "="*50 + f"\n\n问题: {question}"
            else:
                prompt = question
            
            # 调用LLM（带文件上传）
            logger.info("正在调用LLM生成回答...")
            logger.debug(f"Prompt 包含 {len(prompt_parts)} 个部分，总长度: {len(prompt)} 字符")
            
            if uploaded_file_ids:
                # 使用 OpenAI SDK 直接调用，支持文件附件
                api_key = os.getenv("LLM_API_KEY")
                api_base = os.getenv("LLM_API_BASE")
                model = os.getenv("LLM_MODEL", "moonshot-v1-8k")
                
                client = OpenAI(api_key=api_key, base_url=api_base)
                
                # 获取文件内容 - 每个文件作为独立的 system 消息
                logger.info(f"📥 正在获取 {len(uploaded_file_ids)} 个文件的内容...")
                file_messages = []
                for i, file_id in enumerate(uploaded_file_ids):
                    try:
                        file_content = client.files.content(file_id=file_id).text
                        file_messages.append({
                            "role": "system",
                            "content": file_content
                        })
                        logger.info(f"✅ 成功获取文件内容 [{i+1}/{len(uploaded_file_ids)}] (ID: {file_id}，长度: {len(file_content)} 字符)")
                    except Exception as e:
                        logger.error(f"✗ 获取文件内容失败 (ID: {file_id}): {e}")
                        continue
                
                if not file_messages:
                    logger.warning("⚠️ 无法获取任何文件内容，将使用标准方式调用")
                    # 回退到标准方式
                    from llama_index.core import Settings
                    llm = Settings.llm
                    response = llm.complete(prompt)
                    answer = str(response)
                else:
                    # 构建消息列表：使用 * 语法解构 file_messages，使其成为 messages 列表的前 N 条消息
                    messages = [
                        *file_messages,  # 解构所有文件内容消息
                        {
                            "role": "system",
                            "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                    
                    logger.debug(f"发送消息到 Moonshot API，包含 {len(file_messages)} 个文件内容")
                    
                    completion = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0.3,
                    )
                    
                    answer = completion.choices[0].message.content
            else:
                # 没有文件上传，直接调用 LLM API
                api_key = os.getenv("LLM_API_KEY")
                api_base = os.getenv("LLM_API_BASE")
                model = os.getenv("LLM_MODEL", "moonshot-v1-8k")
                
                client = OpenAI(api_key=api_key, base_url=api_base)
                
                messages = [
                    {
                        "role": "system",
                        "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手。你会为用户提供安全，有帮助，准确的回答。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
                
                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.3,
                )
                
                answer = completion.choices[0].message.content
            
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            
            logger.success(SUCCESS_QUERY_COMPLETED.format(elapsed))
            
            # 构建结果
            result = {
                'answer': answer,
                'source_nodes': [],  # 直接模式没有源节点
                'web_sources': web_sources,
                'document_sources': document_sources,
                'metadata': {
                    'question': question,
                    'elapsed_time': elapsed,
                    'num_sources': 0,
                    'num_web_sources': len(web_sources),
                    'num_document_sources': len(document_sources),
                    'mode': 'direct_llm',
                    'has_context': bool(context),
                    'has_documents': bool(document_sources),
                    'web_search_enabled': enable_web_search,
                    'uploaded_files': len(uploaded_file_ids),
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"✗ 直接查询失败: {e}", exc_info=True)
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
    
    def _load_document_files(self, file_paths: List[str]) -> str:
        """
        读取文档文件内容，用于LLM直接模式
        
        Args:
            file_paths: 文件路径列表（相对于documents_dir或绝对路径）
            
        Returns:
            合并后的文档内容字符串
        """
        from src.loaders.document_loader import DocumentLoader
        
        all_content = []
        
        for file_path in file_paths:
            try:
                # 处理路径（支持相对和绝对路径）
                path = Path(file_path)
                if not path.is_absolute():
                    path = self.documents_dir / path
                
                if not path.exists():
                    logger.warning(f"⚠ 文件不存在: {path}")
                    continue
                
                logger.debug(f"读取文件: {path.name}")
                
                # 使用 DocumentLoader 读取文件
                loader = DocumentLoader(
                    input_dir=path.parent,
                    recursive=False,
                    clean_text=True,
                )
                
                # 根据文件类型加载
                file_ext = path.suffix.lower()
                if file_ext == '.pdf':
                    docs = loader._load_pdf_files([path])
                elif file_ext in ['.docx', '.doc']:
                    docs = loader._load_docx_files([path])
                elif file_ext == '.md':
                    docs = loader._load_markdown_files([path])
                elif file_ext == '.txt':
                    docs = loader._load_text_files([path])
                else:
                    logger.warning(f"⚠ 不支持的文件格式: {file_ext}")
                    continue
                
                # 合并文档内容
                if docs:
                    file_content = "\n\n".join([doc.text for doc in docs])
                    # 添加文件标识
                    all_content.append(f"=== 文件: {path.name} ===\n\n{file_content}")
                    logger.info(f"✅ 成功读取 {path.name}, 字符数: {len(file_content)}")
                else:
                    logger.warning(f"⚠️ 文件为空: {path.name}")
                
            except Exception as e:
                logger.error(f"✗ 读取文件失败 {file_path}: {e}", exc_info=True)
                continue
        
        if not all_content:
            logger.warning("⚠️ 没有成功读取任何文档")
            return ""
        
        # 合并所有内容
        final_content = "\n\n" + ("="*80 + "\n\n").join(all_content)
        logger.info(f"📚 总共读取 {len(all_content)} 个文档，总字符数: {len(final_content)}")
        return final_content
    
    def list_available_documents(self) -> List[str]:
        """
        列出 documents 目录下的所有可用文档
        
        Returns:
            文档文件名列表
        """
        if not self.documents_dir.exists():
            return []
        
        supported_exts = ['.pdf', '.docx', '.doc', '.md', '.txt']
        files = []
        
        for ext in supported_exts:
            files.extend([f.name for f in self.documents_dir.rglob(f'*{ext}')])
        
        return sorted(files)
    
    def get_statistics(self) -> Dict[str, Any]:
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
            removed_turns = (len(self.chat_history) - max_messages) // 2
            self.chat_history = self.chat_history[-max_messages:]
            logger.debug(f"历史超出限制，已移除最早的 {removed_turns} 轮对话")
        
        logger.debug(f"对话历史已更新，当前轮数: {len(self.chat_history) // 2}/{self.max_history_turns}")
    
    def clear_chat_history(self):
        """清除对话历史"""
        self.chat_history = []
        logger.info("对话历史已清除")
    
    def set_max_history_turns(self, max_turns: int):
        """
        动态设置最大历史轮数
        
        Args:
            max_turns: 最大保留历史轮数（必须 >= 1）
        
        Example:
            >>> agent.set_max_history_turns(50)  # 保留最近50轮对话
            >>> agent.set_max_history_turns(5)   # 只保留最近5轮
        """
        if max_turns < 1:
            raise ValueError(f"max_turns 必须 >= 1，当前值: {max_turns}")
        
        old_value = self.max_history_turns
        self.max_history_turns = max_turns
        
        # 如果新限制更小，立即裁剪历史
        max_messages = max_turns * 2
        if len(self.chat_history) > max_messages:
            self.chat_history = self.chat_history[-max_messages:]
            logger.info(f"历史轮数限制已更新: {old_value} -> {max_turns}，历史已裁剪至 {len(self.chat_history) // 2} 轮")
        else:
            logger.info(f"历史轮数限制已更新: {old_value} -> {max_turns}")
    
    def get_chat_history_info(self) -> Dict[str, Any]:
        """
        获取对话历史信息
        
        Returns:
            包含当前轮数、最大限制、消息数的字典
        
        Example:
            >>> info = agent.get_chat_history_info()
            >>> print(f"当前 {info['current_turns']}/{info['max_turns']} 轮")
        """
        return {
            'current_turns': len(self.chat_history) // 2,
            'max_turns': self.max_history_turns,
            'total_messages': len(self.chat_history),
            'is_full': len(self.chat_history) >= self.max_history_turns * 2
        }
    
    def clear_file_cache(self):
        """清除文件上传缓存"""
        self._uploaded_files_cache = {}
        logger.info("文件上传缓存已清除")
    
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
