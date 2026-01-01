# 👨‍💻 开发者指南

> 面向需要二次开发和功能扩展的开发者

## 目录

- [项目结构](#项目结构)
- [核心模块详解](#核心模块详解)
- [配置系统](#配置系统)
- [扩展开发](#扩展开发)
- [测试与调试](#测试与调试)
- [最佳实践](#最佳实践)

---

## 项目结构

```
paper-qa-system/
├── config/                 # 配置模块
│   ├── __init__.py
│   ├── models.py          # Pydantic 配置模型
│   ├── llm_config.py      # LLM 和 Embedding 配置
│   ├── settings.py        # 全局设置
│   └── prompts.py         # Prompt 模板
│
├── src/                   # 核心代码
│   ├── agent.py           # Agent 核心逻辑
│   ├── models.py          # 数据模型
│   ├── constants.py       # 常量定义
│   │
│   ├── indexing/          # 索引模块
│   │   ├── indexer.py     # 索引构建
│   │   └── vector_store.py # 向量存储
│   │
│   ├── query/             # 查询模块
│   │   ├── qa_engine.py   # 问答引擎
│   │   └── rag_pipeline.py # RAG 流程
│   │
│   ├── loaders/           # 文档加载
│   │   └── document_loader.py
│   │
│   ├── tools/             # 工具模块
│   │   └── web_search.py  # 网络搜索
│   │
│   └── utils/             # 工具函数
│       ├── helpers.py
│       └── logger.py
│
├── data/                  # 数据目录
│   ├── documents/         # 原始文档
│   ├── vector_store/      # 向量存储
│   └── processed/         # 处理后的数据
│
├── examples/              # 示例代码
│   ├── quick_start.py     # 快速开始
│   ├── agent_demo.py      # Agent 示例
│   ├── build_index.py     # 索引构建示例
│   └── history_control_demo.py # 历史管理示例
│
├── tests/                 # 测试代码
│   ├── test_agent_core.py
│   ├── test_loader_documents.py
│   └── test_multi_turn_chat.py
│
├── docs/                  # 文档
│   ├── USER_GUIDE.md      # 用户指南
│   ├── DEVELOPER_GUIDE.md # 开发者指南
│   └── ARCHITECTURE.md    # 架构文档
│
├── web_ui_multi_turn.py   # Web UI（多轮）
├── start_web_multi.sh     # 启动脚本
├── init_system.py         # 系统初始化
├── requirements.txt       # 依赖列表
├── .env.example           # 配置模板
└── README.md              # 项目说明
```

---

## 核心模块详解

### 1. Agent 模块 (`src/agent.py`)

Agent 是系统的核心，负责对话管理、查询路由和工具调用。

#### 核心类：`AcademicAgent`

```python
class AcademicAgent:
    """学术论文智能问答 Agent
    
    功能：
    - 多轮对话管理
    - RAG 查询
    - 工具调用（网络搜索）
    - 流式输出
    """
    
    def __init__(
        self,
        documents_dir: str = "data/documents",
        index_dir: str = "data/vector_store",
        auto_load: bool = True,
        max_history_turns: int = 10,
        enable_web_search: bool = True
    ):
        """初始化 Agent
        
        Args:
            documents_dir: 文档目录
            index_dir: 索引目录
            auto_load: 是否自动加载索引
            max_history_turns: 最大历史轮数
            enable_web_search: 是否启用网络搜索
        """
```

#### 关键方法

**1. 构建索引**

```python
def build_index(
    self, 
    force_rebuild: bool = False
) -> Dict[str, Any]:
    """构建文档索引
    
    Args:
        force_rebuild: 是否强制重建（删除已有索引）
        
    Returns:
        {
            "status": "success" | "error",
            "message": "构建成功" | "错误信息",
            "stats": {
                "documents": 10,      # 文档数量
                "chunks": 150,        # 分块数量
                "time": 12.5         # 耗时（秒）
            }
        }
    """
```

**2. 多轮对话**

```python
def chat(
    self,
    question: str,
    stream: bool = False,
    **kwargs
) -> Union[str, Generator[str, None, None]]:
    """多轮对话（带上下文）
    
    Args:
        question: 用户问题
        stream: 是否流式输出
        **kwargs: 其他参数（top_k, threshold 等）
        
    Returns:
        - stream=False: 完整回答字符串
        - stream=True: 生成器，逐字返回
    """
```

**3. 单次查询**

```python
def query(
    self,
    question: str,
    use_rag: bool = True,
    **kwargs
) -> str:
    """单次查询（无上下文）
    
    Args:
        question: 问题
        use_rag: 是否使用 RAG（False 则直接调用 LLM）
        
    Returns:
        答案字符串
    """
```

**4. 历史管理**

```python
def get_chat_history(self) -> List[Dict[str, str]]:
    """获取对话历史"""
    return self.chat_history

def clear_history(self):
    """清空对话历史"""
    self.chat_history = []
    logger.info("对话历史已清空")

def set_max_history_turns(self, turns: int):
    """设置最大历史轮数"""
    self.max_history_turns = max(0, turns)
```

#### 内部逻辑

**对话历史管理**：

```python
# 添加新对话
self.chat_history.append({
    "role": "user",
    "content": question
})
self.chat_history.append({
    "role": "assistant",
    "content": response
})

# 保持最近 N 轮
if len(self.chat_history) > self.max_history_turns * 2:
    self.chat_history = self.chat_history[-(self.max_history_turns * 2):]
```

**查询路由**：

```python
# 1. 判断是否需要网络搜索
if self._need_web_search(question):
    web_results = self.web_search_tool.search(question)
    # 整合网络信息
    
# 2. RAG 检索
documents = self.query_engine.retrieve(question)

# 3. 构建上下文
context = self._build_context(documents, web_results)

# 4. LLM 生成
response = self.llm.generate(context + question)
```

---

### 2. 索引模块 (`src/indexing/`)

负责文档加载、分块、向量化和存储。

#### 核心类：`Indexer`

```python
from src.indexing import Indexer

indexer = Indexer(
    documents_dir="data/documents",
    index_dir="data/vector_store"
)

# 构建索引
indexer.build_index(force_rebuild=False)

# 加载索引
index = indexer.load_index()
```

#### 索引流程

```python
def build_index(self, force_rebuild: bool = False):
    """索引构建流程
    
    1. 加载文档
    2. 文本分块
    3. 向量化
    4. 存储到向量数据库
    """
    
    # 1. 加载文档
    documents = self.load_documents_from_directory(self.documents_dir)
    
    # 2. 创建向量存储
    storage_context = self.vector_store.get_storage_context()
    
    # 3. 构建索引
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True
    )
    
    # 4. 持久化
    index.storage_context.persist(persist_dir=self.index_dir)
```

#### 向量存储配置

```python
# config/models.py
class VectorStoreConfig(BaseSettings):
    store_type: Literal["chroma", "faiss", "simple"] = "chroma"
    collection_name: str = "papers"
    persist_dir: str = "data/vector_store"
```

---

### 3. 文档加载模块 (`src/loaders/`)

支持多种文档格式的加载和解析。

#### 核心类：`DocumentLoader`

```python
from src.loaders import DocumentLoader

loader = DocumentLoader(
    recursive=True,           # 递归加载子目录
    clean_text=True,         # 清洗文本
    preserve_formatting=True  # 保留格式
)

# 加载单个文件
documents = loader.load_single_document("paper.pdf")

# 加载整个目录
documents = loader.load_documents("data/documents/")
```

#### 支持的格式

| 格式 | 读取器 | 依赖库 |
|------|--------|--------|
| **PDF** | `PDFReader` | PyMuPDF, PyPDF2 |
| **DOCX** | `DOCXReader` | python-docx |
| **TXT/MD** | `SimpleDirectoryReader` | 内置 |

#### 扩展新格式

```python
from llama_index.core.readers import BaseReader
from llama_index.core.schema import Document

class CustomReader(BaseReader):
    """自定义文档读取器"""
    
    def load_data(self, file_path: Path) -> List[Document]:
        # 实现你的加载逻辑
        text = self._load_custom_format(file_path)
        
        return [Document(
            text=text,
            metadata={
                "file_name": file_path.name,
                "file_path": str(file_path)
            }
        )]

# 注册到 DocumentLoader
loader.readers['.custom'] = CustomReader()
```

---

### 4. 查询模块 (`src/query/`)

实现 RAG 查询和答案生成。

#### RAG Pipeline

```python
from src.query import RAGPipeline

pipeline = RAGPipeline(
    index=index,
    llm=llm,
    top_k=5,
    similarity_threshold=0.7
)

# 查询
response = pipeline.query("Transformer 是什么？")
print(response.response)

# 查看检索到的文档
for source in response.source_nodes:
    print(f"来源：{source.metadata['file_name']} 第 {source.metadata['page']} 页")
    print(f"相似度：{source.score}")
```

#### 自定义 Prompt

```python
# config/prompts.py

CHAT_PROMPT = """你是一个专业的学术论文分析助手。

上下文信息：
{context}

对话历史：
{history}

用户问题：{question}

请基于上下文和历史对话，给出准确、专业的回答。如果无法从上下文中找到答案，请诚实地说明。
"""

# 使用自定义 Prompt
from config.prompts import CHAT_PROMPT

agent = AcademicAgent()
agent.prompt_template = CHAT_PROMPT
```

---

## 配置系统

本项目使用 Pydantic 2.0 进行配置管理，提供类型安全和自动验证。

### 配置模型

#### LLM 配置

```python
# config/models.py

class LLMConfig(BaseSettings):
    """LLM 配置模型"""
    
    model_config = SettingsConfigDict(
        env_prefix="LLM_",           # 环境变量前缀
        env_file=".env",             # 配置文件
        env_file_encoding="utf-8",
        extra="ignore"               # 忽略额外字段
    )
    
    api_key: str = Field(..., description="API Key")
    api_base: str = Field(
        default="https://api.openai.com/v1",
        description="API Base URL"
    )
    model: str = Field(
        default="gpt-3.5-turbo",
        description="模型名称"
    )
    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="温度参数"
    )
    
    @field_validator("api_base")
    @classmethod
    def validate_api_base(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("API Base 必须以 http:// 或 https:// 开头")
        return v.rstrip("/")
```

#### Embedding 配置

```python
class EmbeddingConfig(BaseSettings):
    """Embedding 配置模型"""
    
    provider: Literal["openai", "huggingface", "fastembed", "qwen3"] = Field(
        default="huggingface",
        description="提供商"
    )
    model_name: str = Field(
        default="BAAI/bge-small-zh-v1.5",
        description="模型名称"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API Key（云端 Embedding 需要）"
    )
```

### 获取配置

```python
from config.models import get_config

# 获取配置实例
config = get_config()

# 访问配置
print(config.llm.api_key)
print(config.embedding.provider)
print(config.rag.chunk_size)

# 配置会自动从 .env 和环境变量加载
```

### 动态修改配置

```python
# 临时修改（不持久化）
config.rag.chunk_size = 1024

# 重新加载配置
from config.models import reload_config
config = reload_config()
```

---

## 扩展开发

### 添加新的 Embedding 提供商

**步骤 1**：更新配置模型

```python
# config/models.py

class EmbeddingConfig(BaseSettings):
    provider: Literal["openai", "huggingface", "fastembed", "qwen3", "custom"] = ...
```

**步骤 2**：实现 Embedding 逻辑

```python
# config/llm_config.py

def get_embedding_model(provider: Optional[str] = None) -> BaseEmbedding:
    config = get_config()
    provider = provider or config.embedding.provider
    
    # ... 其他 provider 的代码 ...
    
    elif provider == "custom":
        from llama_index.embeddings.custom import CustomEmbedding
        
        logger.info("使用自定义 Embedding")
        return CustomEmbedding(
            api_key=config.embedding.api_key,
            model=config.embedding.model_name
        )
```

**步骤 3**：更新配置文件

```bash
# .env
EMBEDDING_PROVIDER=custom
EMBEDDING_MODEL_NAME=your-model-name
EMBEDDING_API_KEY=your-api-key
```

### 添加新的工具（Tool）

**步骤 1**：创建工具类

```python
# src/tools/calculator.py

from llama_index.core.tools import FunctionTool

def calculator(expression: str) -> float:
    """计算数学表达式
    
    Args:
        expression: 数学表达式，如 "2 + 3 * 4"
        
    Returns:
        计算结果
    """
    try:
        return eval(expression)
    except Exception as e:
        return f"计算错误：{e}"

# 包装为 Tool
calculator_tool = FunctionTool.from_defaults(
    fn=calculator,
    name="calculator",
    description="计算数学表达式"
)
```

**步骤 2**：注册到 Agent

```python
# src/agent.py

from src.tools.calculator import calculator_tool

class AcademicAgent:
    def __init__(self, ...):
        # ... 其他初始化 ...
        
        # 注册工具
        self.tools = [
            self.web_search_tool,
            calculator_tool
        ]
        
    def _call_tool(self, tool_name: str, **kwargs):
        """调用工具"""
        for tool in self.tools:
            if tool.metadata.name == tool_name:
                return tool(**kwargs)
```

### 自定义 RAG 流程

```python
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor

def create_custom_query_engine(index, top_k=5, threshold=0.7):
    """自定义查询引擎"""
    
    # 1. 配置检索器
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=top_k,
    )
    
    # 2. 配置后处理器
    postprocessor = SimilarityPostprocessor(
        similarity_cutoff=threshold
    )
    
    # 3. 组装查询引擎
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        node_postprocessors=[postprocessor],
    )
    
    return query_engine
```

---

## 测试与调试

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_agent_core.py

# 运行特定测试函数
pytest tests/test_agent_core.py::test_agent_initialization

# 显示详细输出
pytest -v tests/

# 显示 print 输出
pytest -s tests/
```

### 编写测试

```python
# tests/test_my_feature.py

import pytest
from src.agent import AcademicAgent

@pytest.fixture
def agent():
    """创建测试用 Agent"""
    return AcademicAgent(
        documents_dir="tests/data/documents",
        index_dir="tests/data/index",
        auto_load=False
    )

def test_agent_initialization(agent):
    """测试 Agent 初始化"""
    assert agent is not None
    assert agent.documents_dir.exists()

def test_build_index(agent):
    """测试索引构建"""
    result = agent.build_index()
    assert result["status"] == "success"
    assert result["stats"]["documents"] > 0
```

### 调试技巧

**1. 启用详细日志**

```python
# config/.env
LOG_LEVEL=DEBUG

# 或代码中设置
from src.utils.logger import logger
logger.setLevel("DEBUG")
```

**2. 查看检索结果**

```python
response = agent.query("Transformer 是什么？")

# 查看检索到的文档
print("检索到的文档：")
for i, source in enumerate(response.source_nodes):
    print(f"\n--- 文档 {i+1} ---")
    print(f"文件：{source.metadata['file_name']}")
    print(f"相似度：{source.score:.3f}")
    print(f"内容：{source.text[:200]}...")
```

**3. 测试单个组件**

```python
# 单独测试 Embedding
from config.llm_config import get_embedding_model

embed_model = get_embedding_model()
vector = embed_model.embed_query("测试文本")
print(f"向量维度：{len(vector)}")

# 单独测试 LLM
from config.llm_config import get_llm

llm = get_llm()
response = llm.complete("你好")
print(response.text)
```

---

## 最佳实践

### 代码规范

**1. 类型注解**

```python
from typing import List, Dict, Optional

def process_documents(
    documents: List[Document],
    max_length: int = 512
) -> List[Dict[str, Any]]:
    """处理文档"""
    ...
```

**2. 文档字符串**

```python
def build_index(self, force_rebuild: bool = False) -> Dict[str, Any]:
    """构建文档索引
    
    Args:
        force_rebuild: 是否强制重建索引
        
    Returns:
        包含构建结果的字典，格式：
        {
            "status": "success" | "error",
            "message": "构建成功" | "错误信息",
            "stats": {...}
        }
        
    Raises:
        RuntimeError: 当文档目录不存在时
    """
```

**3. 错误处理**

```python
try:
    result = self.build_index()
except FileNotFoundError as e:
    logger.error(f"文档目录不存在：{e}")
    raise RuntimeError(f"请确保文档目录存在：{self.documents_dir}")
except Exception as e:
    logger.error(f"索引构建失败：{e}")
    raise
```

### 性能优化

**1. 批量处理**

```python
# 批量向量化
batch_size = 10
for i in range(0, len(texts), batch_size):
    batch = texts[i:i+batch_size]
    vectors = embed_model.embed_documents(batch)
```

**2. 缓存结果**

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def embed_query(self, text: str) -> List[float]:
    """缓存常见问题的向量"""
    return self._embed(text)
```

**3. 异步处理**

```python
import asyncio

async def process_documents_async(documents):
    tasks = [process_single(doc) for doc in documents]
    return await asyncio.gather(*tasks)
```

### 安全建议

**1. API Key 管理**

```python
# ❌ 不要硬编码
api_key = "sk-1234567890abcdef"

# ✅ 使用环境变量
import os
api_key = os.getenv("LLM_API_KEY")
```

**2. 输入验证**

```python
from pydantic import BaseModel, validator

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    
    @validator("question")
    def validate_question(cls, v):
        if len(v) > 1000:
            raise ValueError("问题过长")
        return v.strip()
```

---

## 常见开发任务

### 任务 1：修改 Prompt

```python
# config/prompts.py

# 修改系统 Prompt
SYSTEM_PROMPT = """你是一个专业的学术论文分析助手。

特点：
- 回答准确、专业
- 引用来源
- 承认不知道

请始终保持这个角色。"""

# 修改对话 Prompt
CHAT_PROMPT = """基于以下信息回答问题：

上下文：{context}

历史对话：{history}

问题：{question}

回答："""
```

### 任务 2：添加日志

```python
from src.utils.logger import logger

logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")

# 带变量
logger.info(f"正在处理文档：{doc_name}")
```

### 任务 3：导出对话历史

```python
import json

def export_history(agent: AcademicAgent, output_file: str):
    """导出对话历史"""
    history = agent.get_chat_history()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    logger.info(f"对话历史已导出到：{output_file}")

# 使用
export_history(agent, "history.json")
```

---

## 参考资源

- **LlamaIndex 官方文档**：https://docs.llamaindex.ai/
- **Pydantic 文档**：https://docs.pydantic.dev/
- **Gradio 文档**：https://www.gradio.app/docs/
- **项目架构文档**：[ARCHITECTURE.md](ARCHITECTURE.md)

---

**最后更新**: 2026-01-01
