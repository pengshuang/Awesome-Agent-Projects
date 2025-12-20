# 👨‍💻 开发者文档

## 目录
- [项目架构](#项目架构)
- [核心模块](#核心模块)
- [API 参考](#api-参考)
- [扩展开发](#扩展开发)
- [测试指南](#测试指南)
- [部署指南](#部署指南)

---

## 项目架构

### 整体架构

```
┌─────────────────────────────────────────────────────┐
│                    User Layer                        │
│  ┌──────────────┐              ┌──────────────┐    │
│  │   Web UI     │              │   CLI        │    │
│  │  (Gradio)    │              │   (Typer)    │    │
│  └──────────────┘              └──────────────┘    │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                 Application Layer                    │
│  ┌──────────────────────────────────────────────┐  │
│  │              Agent (main.py)                  │  │
│  │  • Query Processing                          │  │
│  │  • Context Management                        │  │
│  │  • Response Generation                       │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌─────────────┐ ┌────────────┐
│   Document   │ │   Retrieval │ │    LLM     │
│   Loader     │ │   Engine    │ │  Service   │
│              │ │             │ │            │
│ • PDF        │ │ • Vector    │ │ • OpenAI   │
│ • DOCX       │ │   Store     │ │ • Moonshot │
│ • Markdown   │ │ • Semantic  │ │ • DeepSeek │
│ • TXT        │ │   Search    │ │            │
└──────────────┘ └─────────────┘ └────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│                  Storage Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │   Chroma     │  │   Config     │  │   Logs   │ │
│  │ Vector Store │  │    (.env)    │  │          │ │
│  └──────────────┘  └──────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────┘
```

### 目录结构

```
academic-paper-qa/
├── src/                        # 核心源代码
│   ├── agent/                  # Agent 模块
│   │   ├── __init__.py
│   │   └── rag_agent.py       # RAG Agent 实现
│   ├── loaders/               # 文档加载器
│   │   ├── __init__.py
│   │   ├── document_loader.py # 文档加载主类
│   │   ├── pdf_loader.py      # PDF 加载器
│   │   ├── docx_loader.py     # DOCX 加载器
│   │   └── markdown_loader.py # Markdown 加载器
│   ├── retrieval/             # 检索引擎
│   │   ├── __init__.py
│   │   ├── vector_store.py    # 向量存储
│   │   └── hybrid_retriever.py # 混合检索器
│   ├── llm/                   # LLM 服务
│   │   ├── __init__.py
│   │   ├── base.py            # LLM 基类
│   │   ├── openai_llm.py      # OpenAI 实现
│   │   └── moonshot_llm.py    # Moonshot 实现
│   ├── config/                # 配置管理
│   │   ├── __init__.py
│   │   ├── llm_config.py      # LLM 配置
│   │   ├── embedding_config.py # Embedding 配置
│   │   └── search_config.py   # 搜索配置
│   └── utils/                 # 工具函数
│       ├── __init__.py
│       ├── logger.py          # 日志工具
│       ├── text_processor.py  # 文本处理
│       └── validators.py      # 验证器
├── web_ui.py                  # Web UI 入口
├── main.py                    # CLI 入口
├── init_system.py             # 系统初始化
├── config/                    # 配置文件
│   └── prompts.yaml          # Prompt 模板
├── data/                      # 数据目录
│   ├── documents/            # 文档存储
│   └── vector_store/         # 向量索引
├── tests/                     # 测试代码
│   ├── unit/                 # 单元测试
│   ├── integration/          # 集成测试
│   └── fixtures/             # 测试数据
├── docs/                      # 文档
│   ├── FEATURES.md           # 功能介绍
│   ├── USER_GUIDE.md         # 使用指南
│   └── DEVELOPER_GUIDE.md    # 开发者文档
├── examples/                  # 示例代码
│   ├── custom_loader.py      # 自定义加载器示例
│   ├── custom_retriever.py   # 自定义检索器示例
│   └── api_usage.py          # API 使用示例
├── .env.example              # 配置模板
├── requirements.txt          # 依赖列表
└── README.md                 # 项目说明
```

---

## 核心模块

### 1. Document Loader（文档加载器）

**位置**：`src/loaders/document_loader.py`

**职责**：
- 加载各种格式的文档
- 文本提取和清理
- 文档元数据管理
- 文本分块

**核心类：**

```python
class DocumentLoader:
    """文档加载器主类"""
    
    def __init__(
        self,
        input_dir: str,
        recursive: bool = True,
        clean_text: bool = True,
        preserve_formatting: bool = False,
        supported_formats: List[str] = None
    ):
        """
        参数:
            input_dir: 文档目录
            recursive: 是否递归扫描子目录
            clean_text: 是否清理文本
            preserve_formatting: 是否保留格式
            supported_formats: 支持的文件格式列表
        """
        pass
    
    def load_documents(self) -> List[Document]:
        """加载所有文档"""
        pass
    
    def _load_single_file(self, file_path: str) -> List[Document]:
        """加载单个文件"""
        pass
```

**使用示例：**

```python
from src.loaders import DocumentLoader

# 基础使用
loader = DocumentLoader(input_dir="./data/documents")
documents = loader.load_documents()

# 高级配置
loader = DocumentLoader(
    input_dir="./data/documents",
    recursive=True,
    clean_text=True,
    preserve_formatting=False,
    supported_formats=[".pdf", ".docx", ".md"]
)
documents = loader.load_documents()

# 统计信息
print(f"加载了 {len(documents)} 个文档块")
for doc in documents:
    print(f"文件: {doc.metadata['file_name']}, 长度: {len(doc.text)}")
```

**扩展开发：添加新的文档格式**

```python
from src.loaders.base import BaseLoader
from typing import List
from llama_index.core import Document

class CustomLoader(BaseLoader):
    """自定义加载器示例"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.supported_extensions = [".custom"]
    
    def load(self, file_path: str) -> List[Document]:
        """加载自定义格式文件"""
        # 实现你的加载逻辑
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 创建文档对象
        doc = Document(
            text=content,
            metadata={
                'file_name': os.path.basename(file_path),
                'file_path': file_path,
                'format': 'custom'
            }
        )
        return [doc]
```

### 2. Vector Store（向量存储）

**位置**：`src/retrieval/vector_store.py`

**职责**：
- 文档向量化
- 向量索引构建
- 语义检索
- 索引持久化

**核心类：**

```python
class VectorStore:
    """向量存储管理器"""
    
    def __init__(
        self,
        persist_dir: str,
        embedding_model: str = "BAAI/bge-small-zh-v1.5",
        collection_name: str = "documents"
    ):
        """
        参数:
            persist_dir: 持久化目录
            embedding_model: Embedding 模型名称
            collection_name: 集合名称
        """
        pass
    
    def build_index(
        self,
        documents: List[Document],
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ) -> VectorStoreIndex:
        """构建向量索引"""
        pass
    
    def query(
        self,
        query_text: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[NodeWithScore]:
        """查询相似文档"""
        pass
    
    def delete_index(self):
        """删除索引"""
        pass
```

**使用示例：**

```python
from src.retrieval import VectorStore
from src.loaders import DocumentLoader

# 1. 加载文档
loader = DocumentLoader(input_dir="./data/documents")
documents = loader.load_documents()

# 2. 构建索引
vector_store = VectorStore(
    persist_dir="./data/vector_store",
    embedding_model="BAAI/bge-small-zh-v1.5"
)
index = vector_store.build_index(
    documents=documents,
    chunk_size=512,
    chunk_overlap=50
)

# 3. 查询
results = vector_store.query(
    query_text="Transformer 模型的核心创新",
    top_k=5,
    similarity_threshold=0.7
)

# 4. 处理结果
for result in results:
    print(f"相似度: {result.score}")
    print(f"内容: {result.node.text[:100]}...")
    print(f"来源: {result.node.metadata['file_name']}")
```

### 3. RAG Agent（问答引擎）

**位置**：`src/agent/rag_agent.py`

**职责**：
- 问题理解
- 文档检索
- 上下文构建
- 答案生成
- 来源追溯

**核心类：**

```python
class RAGAgent:
    """RAG 问答 Agent"""
    
    def __init__(
        self,
        vector_store: VectorStore,
        llm: BaseLLM,
        prompt_template: str = None
    ):
        """
        参数:
            vector_store: 向量存储
            llm: 语言模型
            prompt_template: Prompt 模板
        """
        pass
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        return_sources: bool = True
    ) -> Dict[str, Any]:
        """
        RAG 问答
        
        返回:
            {
                'answer': str,              # 生成的答案
                'sources': List[Dict],      # 来源列表
                'confidence': float,        # 置信度
                'retrieval_time': float,    # 检索耗时
                'generation_time': float    # 生成耗时
            }
        """
        pass
    
    def _build_context(self, retrieved_nodes: List[NodeWithScore]) -> str:
        """构建上下文"""
        pass
    
    def _format_sources(self, nodes: List[NodeWithScore]) -> List[Dict]:
        """格式化来源信息"""
        pass
```

**使用示例：**

```python
from src.agent import RAGAgent
from src.retrieval import VectorStore
from src.llm import MoonshotLLM

# 1. 初始化组件
vector_store = VectorStore(persist_dir="./data/vector_store")
llm = MoonshotLLM()

# 2. 创建 Agent
agent = RAGAgent(
    vector_store=vector_store,
    llm=llm,
    prompt_template="基于以下内容回答问题:\n{context}\n\n问题: {question}"
)

# 3. 提问
result = agent.query(
    question="Transformer 的核心创新是什么？",
    top_k=5,
    return_sources=True
)

# 4. 获取结果
print(f"答案: {result['answer']}")
print(f"置信度: {result['confidence']}")
print(f"检索耗时: {result['retrieval_time']:.2f}s")
print(f"生成耗时: {result['generation_time']:.2f}s")

for i, source in enumerate(result['sources'], 1):
    print(f"\n来源 {i}:")
    print(f"  文件: {source['file_name']}")
    print(f"  相似度: {source['similarity']:.2f}")
    print(f"  内容: {source['text'][:100]}...")
```

### 4. LLM Service（语言模型服务）

**位置**：`src/llm/`

**职责**：
- 统一 LLM 接口
- 多提供商支持
- 请求管理
- 错误处理

**核心接口：**

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLM(ABC):
    """LLM 基类"""
    
    @abstractmethod
    def __init__(self, config: Dict[str, Any]):
        """初始化 LLM"""
        pass
    
    @abstractmethod
    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """文本补全"""
        pass
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """多轮对话"""
        pass
```

**实现示例：**

```python
from src.llm.base import BaseLLM
import requests

class CustomLLM(BaseLLM):
    """自定义 LLM 实现"""
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get('api_key')
        self.api_base = config.get('api_base')
        self.model = config.get('model')
    
    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """实现文本补全"""
        response = requests.post(
            f"{self.api_base}/completions",
            json={
                "model": self.model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()['choices'][0]['text']
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """实现多轮对话"""
        response = requests.post(
            f"{self.api_base}/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()['choices'][0]['message']['content']
```

---

## API 参考

### create_agent()

创建 RAG Agent 实例。

```python
def create_agent(
    documents_dir: str = "./data/documents",
    vector_store_dir: str = "./data/vector_store",
    force_rebuild: bool = False,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    embedding_model: str = "BAAI/bge-small-zh-v1.5",
    llm_provider: str = "moonshot",
    **kwargs
) -> RAGAgent:
    """
    创建 RAG Agent
    
    参数:
        documents_dir: 文档目录
        vector_store_dir: 向量存储目录
        force_rebuild: 是否强制重建索引
        chunk_size: 文本块大小
        chunk_overlap: 文本块重叠
        embedding_model: Embedding 模型
        llm_provider: LLM 提供商
        **kwargs: 其他参数
    
    返回:
        RAGAgent 实例
    
    异常:
        FileNotFoundError: 文档目录不存在
        ValueError: 配置参数无效
    """
```

**使用示例：**

```python
from src.agent import create_agent

# 基础使用
agent = create_agent()

# 自定义配置
agent = create_agent(
    documents_dir="./my_papers",
    force_rebuild=True,
    chunk_size=256,
    llm_provider="openai"
)
```

### query()

执行 RAG 查询。

```python
def query(
    agent: RAGAgent,
    question: str,
    mode: str = "rag",
    web_search: bool = False,
    top_k: int = 5,
    temperature: float = 0.7,
    **kwargs
) -> Dict[str, Any]:
    """
    执行查询
    
    参数:
        agent: RAG Agent 实例
        question: 用户问题
        mode: 查询模式 ('rag' 或 'llm')
        web_search: 是否启用联网搜索
        top_k: 检索数量
        temperature: 温度参数
        **kwargs: 其他参数
    
    返回:
        {
            'answer': str,
            'sources': List[Dict],
            'mode': str,
            'web_results': List[Dict]  # 如果启用联网搜索
        }
    """
```

---

## 扩展开发

### 1. 添加新的 LLM 提供商

**步骤：**

1. 创建新的 LLM 类：

```python
# src/llm/custom_llm.py
from src.llm.base import BaseLLM

class CustomLLM(BaseLLM):
    def __init__(self, config):
        self.api_key = config.get('api_key')
        # 初始化你的 LLM 客户端
    
    def complete(self, prompt, **kwargs):
        # 实现补全逻辑
        pass
    
    def chat(self, messages, **kwargs):
        # 实现对话逻辑
        pass
```

2. 注册到配置：

```python
# src/config/llm_config.py
LLM_PROVIDERS = {
    'openai': OpenAILLM,
    'moonshot': MoonshotLLM,
    'custom': CustomLLM,  # 添加新提供商
}
```

3. 更新 .env.example：

```bash
# 添加新的配置项
LLM_PROVIDER=custom
CUSTOM_API_KEY=your-key
CUSTOM_API_BASE=https://api.custom.com/v1
```

### 2. 自定义检索策略

**示例：实现混合检索（关键词 + 语义）**

```python
# src/retrieval/hybrid_retriever.py
from src.retrieval.vector_store import VectorStore
from typing import List
from llama_index.core import QueryBundle
from llama_index.core.schema import NodeWithScore

class HybridRetriever:
    """混合检索器：结合关键词和语义检索"""
    
    def __init__(
        self,
        vector_store: VectorStore,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7
    ):
        self.vector_store = vector_store
        self.keyword_weight = keyword_weight
        self.semantic_weight = semantic_weight
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> List[NodeWithScore]:
        """混合检索"""
        # 1. 语义检索
        semantic_results = self.vector_store.query(query, top_k=top_k)
        
        # 2. 关键词检索
        keyword_results = self._keyword_search(query, top_k=top_k)
        
        # 3. 融合结果
        merged_results = self._merge_results(
            semantic_results,
            keyword_results
        )
        
        return merged_results[:top_k]
    
    def _keyword_search(self, query: str, top_k: int) -> List[NodeWithScore]:
        """关键词搜索实现"""
        # 实现 BM25 或其他关键词检索算法
        pass
    
    def _merge_results(
        self,
        semantic: List[NodeWithScore],
        keyword: List[NodeWithScore]
    ) -> List[NodeWithScore]:
        """融合检索结果"""
        # 实现 RRF (Reciprocal Rank Fusion) 或其他融合策略
        pass
```

### 3. 自定义 Prompt 模板

**创建 Prompt 配置文件：**

```yaml
# config/prompts.yaml
rag_prompt: |
  你是一个专业的学术论文分析助手。
  
  基于以下文档内容回答用户问题：
  {context}
  
  问题: {question}
  
  要求:
  1. 答案必须基于提供的文档内容
  2. 如果文档中没有相关信息，请明确说明
  3. 引用具体的段落支持你的答案
  
  答案:

analysis_prompt: |
  请深度分析以下论文内容：
  {context}
  
  分析维度：
  1. 研究问题和动机
  2. 技术方法
  3. 实验设计
  4. 主要结论
  5. 创新点和局限性
  
  分析结果:
```

**使用自定义 Prompt：**

```python
from src.utils import load_prompts

# 加载 Prompt 模板
prompts = load_prompts("config/prompts.yaml")

# 创建 Agent 时指定
agent = RAGAgent(
    vector_store=vector_store,
    llm=llm,
    prompt_template=prompts['rag_prompt']
)
```

### 4. 添加后处理器

**示例：答案质量评估**

```python
# src/utils/postprocessor.py
class AnswerQualityEvaluator:
    """答案质量评估器"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def evaluate(self, question: str, answer: str, sources: List[Dict]) -> Dict:
        """评估答案质量"""
        # 1. 相关性评分
        relevance_score = self._evaluate_relevance(question, answer)
        
        # 2. 完整性评分
        completeness_score = self._evaluate_completeness(answer, sources)
        
        # 3. 准确性评分
        accuracy_score = self._evaluate_accuracy(answer, sources)
        
        return {
            'relevance': relevance_score,
            'completeness': completeness_score,
            'accuracy': accuracy_score,
            'overall': (relevance_score + completeness_score + accuracy_score) / 3
        }
    
    def _evaluate_relevance(self, question: str, answer: str) -> float:
        """评估相关性"""
        prompt = f"问题: {question}\n答案: {answer}\n\n请评估答案与问题的相关性(0-1):"
        # 使用 LLM 评估
        pass
```

---

## 测试指南

### 单元测试

**位置**：`tests/unit/`

**运行测试：**

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/unit/test_document_loader.py

# 运行并查看覆盖率
pytest --cov=src tests/

# 生成HTML报告
pytest --cov=src --cov-report=html tests/
```

**测试示例：**

```python
# tests/unit/test_document_loader.py
import pytest
from src.loaders import DocumentLoader

class TestDocumentLoader:
    """DocumentLoader 单元测试"""
    
    @pytest.fixture
    def loader(self):
        """测试fixture"""
        return DocumentLoader(
            input_dir="tests/fixtures/documents",
            recursive=True
        )
    
    def test_load_pdf(self, loader):
        """测试 PDF 加载"""
        documents = loader.load_documents()
        assert len(documents) > 0
        assert any(doc.metadata['format'] == 'pdf' for doc in documents)
    
    def test_metadata(self, loader):
        """测试元数据"""
        documents = loader.load_documents()
        for doc in documents:
            assert 'file_name' in doc.metadata
            assert 'file_path' in doc.metadata
            assert 'format' in doc.metadata
```

### 集成测试

**位置**：`tests/integration/`

```python
# tests/integration/test_rag_pipeline.py
import pytest
from src.agent import create_agent

class TestRAGPipeline:
    """RAG 管道集成测试"""
    
    @pytest.fixture(scope="class")
    def agent(self):
        """创建测试 Agent"""
        return create_agent(
            documents_dir="tests/fixtures/documents",
            force_rebuild=True
        )
    
    def test_end_to_end_query(self, agent):
        """端到端查询测试"""
        result = agent.query(
            question="测试问题",
            top_k=3
        )
        
        assert 'answer' in result
        assert 'sources' in result
        assert len(result['sources']) <= 3
    
    def test_query_performance(self, agent):
        """性能测试"""
        import time
        
        start = time.time()
        result = agent.query("测试问题")
        elapsed = time.time() - start
        
        assert elapsed < 10  # 10秒内完成
```

---

## 部署指南

### Docker 部署

**创建 Dockerfile：**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data/documents /app/data/vector_store /app/logs

# 暴露端口
EXPOSE 7860

# 启动应用
CMD ["python", "web_ui.py", "--server-port", "7860", "--server-name", "0.0.0.0"]
```

**创建 docker-compose.yml：**

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "7860:7860"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
      - LLM_API_BASE=${LLM_API_BASE}
      - LLM_MODEL=${LLM_MODEL}
    restart: unless-stopped
```

**部署命令：**

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 贡献指南

### 代码风格

- 遵循 PEP 8
- 使用类型注解
- 编写文档字符串
- 保持函数简洁（< 50 行）

### 提交流程

1. Fork 项目
2. 创建功能分支
3. 编写代码和测试
4. 提交 Pull Request

---

## 下一步

- 📋 查看 [功能介绍](FEATURES.md) 了解系统能力
- 📖 阅读 [使用指南](USER_GUIDE.md) 开始使用
- 🚀 开始开发你的扩展功能
