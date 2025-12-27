# 👨‍💻 开发指南

> 面向需要二次开发、扩展功能的开发者

## 目录

- [项目架构](#项目架构)
- [核心模块](#核心模块)
- [Pydantic 配置系统](#pydantic-配置系统)
- [API 参考](#api-参考)
- [扩展开发](#扩展开发)
- [测试](#测试)

---

## 项目架构

### 目录结构

```
academic-paper-qa/
├── config/              # 配置模块（Pydantic）
│   ├── models.py       # Pydantic 配置模型
│   ├── settings.py     # 全局设置
│   ├── llm_config.py   # LLM 配置
│   └── prompts.py      # Prompt 模板
├── src/                # 核心代码
│   ├── agent.py        # Agent 核心
│   ├── models.py       # 数据模型（Pydantic）
│   ├── indexing/       # 索引构建
│   ├── query/          # 查询引擎
│   ├── loaders/        # 文档加载
│   ├── tools/          # 工具（搜索等）
│   └── utils/          # 工具函数
├── data/               # 数据目录
├── examples/           # 示例代码
├── docs/               # 文档
└── *.py               # 启动脚本
```

### 技术栈

- **RAG 框架**: LlamaIndex
- **向量数据库**: Chroma
- **配置管理**: Pydantic 2.0+
- **Web UI**: Gradio 4.0+
- **Embedding**: HuggingFace / OpenAI

---

## 核心模块

### AcademicAgent

核心 Agent 类，负责文档管理和问答。

```python
from src.agent import AcademicAgent

# 初始化
agent = AcademicAgent(
    documents_dir="data/documents",
    index_dir="data/vector_store",
    max_history_turns=10
)

# 构建索引
agent.build_index()

# 单轮问答
response = agent.query("这篇论文讲什么？")

# 多轮对话
response = agent.chat("什么是Transformer？")
response = agent.chat("它的优势是什么？")  # 带上下文
```

### 文档加载

```python
from src.loaders import DocumentLoader

loader = DocumentLoader()
documents = loader.load_documents("data/documents")
```

支持格式：PDF、DOCX、Markdown、TXT

### 索引构建

```python
from src.indexing import Indexer

indexer = Indexer()
index = indexer.build_index(documents)
indexer.save_index(index, "data/vector_store")
```

### 查询引擎

```python
from src.query import QAEngine

qa_engine = QAEngine(index, top_k=5)
answer = qa_engine.query("问题")
```

---

## Pydantic 配置系统

### 配置加载

```python
from config.models import get_config

# 获取全局配置（单例）
config = get_config()

# 访问配置（类型安全）
api_key = config.llm.api_key
model = config.llm.model
chunk_size = config.rag.chunk_size
```

### 配置模型

#### LLMConfig

```python
class LLMConfig(BaseSettings):
    api_key: str                    # API Key
    api_base: str = "..."          # API 端点
    model: str = "gpt-3.5-turbo"   # 模型
    temperature: float = 0.1        # 温度 (0-2)
    max_tokens: Optional[int] = None
```

#### RAGConfig

```python
class RAGConfig(BaseSettings):
    chunk_size: int = 512           # 分块大小 (1-4096)
    chunk_overlap: int = 50         # 重叠大小
    retrieval_top_k: int = 5        # Top-K (1-50)
    retrieval_similarity_threshold: float = 0.7
    enable_reranking: bool = False
```

### 数据模型

```python
from src.models import QueryRequest, QueryResponse

# 查询请求
request = QueryRequest(
    question="什么是机器学习？",
    top_k=5,
    similarity_threshold=0.7
)

# 查询响应
response = QueryResponse(
    answer="机器学习是...",
    sources=[...],
    query_time=1.23
)
```

### 向后兼容

```python
from config import SystemConfig

# 旧代码仍然有效
chunk_size = SystemConfig.CHUNK_SIZE
docs_dir = SystemConfig.DOCUMENTS_DIR
```

---

## API 参考

### AcademicAgent API

#### 初始化

```python
agent = AcademicAgent(
    documents_dir: str = "data/documents",
    index_dir: str = "data/vector_store",
    auto_load: bool = True,
    max_history_turns: int = 10
)
```

#### 方法

**索引管理：**
- `build_index(force_rebuild=False)` - 构建索引
- `load_index()` - 加载索引
- `list_papers()` - 列出文档

**问答：**
- `query(question, mode="rag", enable_web_search=False)` - 单轮问答
- `chat(question, mode="rag", enable_web_search=False)` - 多轮对话

**历史管理：**
- `get_chat_history()` - 获取历史
- `clear_chat_history()` - 清空历史

### 配置 API

```python
from config.models import get_config, reload_config

# 获取配置
config = get_config()

# 重新加载
config = reload_config()

# 导出配置
json_str = config.model_dump_json(indent=2)
dict_data = config.model_dump()
```

---

## 扩展开发

### 自定义 Prompt

编辑 `config/prompts.py`：

```python
CUSTOM_SYSTEM_PROMPT = """
你是一个专业的学术助手...
"""
```

### 添加新的文档加载器

```python
from src.loaders import DocumentLoader

class MyLoader(DocumentLoader):
    def load_my_format(self, file_path):
        # 实现加载逻辑
        pass
```

### 集成新的搜索引擎

```python
from src.tools import WebSearchTool

class MySearchTool(WebSearchTool):
    def search(self, query):
        # 实现搜索逻辑
        pass
```

### 自定义数据模型

```python
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    field1: str = Field(..., description="字段1")
    field2: int = Field(default=0, ge=0)
```

---

## 测试

### 运行测试

```bash
# 所有测试
pytest tests/

# 特定测试
pytest tests/test_agent_core.py

# 详细输出
pytest -v tests/
```

### 编写测试

```python
import pytest
from src.agent import AcademicAgent

def test_agent_initialization():
    agent = AcademicAgent()
    assert agent is not None

def test_query():
    agent = AcademicAgent()
    response = agent.query("test question")
    assert isinstance(response, str)
```

---

## 开发规范

### 代码风格

- 遵循 PEP 8
- 使用类型注解
- 添加文档字符串

```python
def my_function(param: str) -> int:
    """
    函数说明
    
    Args:
        param: 参数说明
        
    Returns:
        返回值说明
    """
    pass
```

### Git 工作流

```bash
# 1. 创建分支
git checkout -b feature/my-feature

# 2. 开发和测试
# ...

# 3. 提交
git commit -m "Add: 新功能说明"

# 4. 推送
git push origin feature/my-feature

# 5. 创建 Pull Request
```

### 提交信息规范

- `Add:` 新增功能
- `Fix:` 修复 Bug
- `Update:` 更新功能
- `Refactor:` 重构代码
- `Docs:` 文档更新

---

## 性能优化

### 索引优化

```python
# 调整 chunk 参数
config.rag.chunk_size = 1024
config.rag.chunk_overlap = 100

# 调整检索参数
config.rag.retrieval_top_k = 10
```

### 缓存

```python
# 启用缓存
config.system.enable_cache = True
```

---

## 部署

### Docker 部署

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "web_ui_multi_turn.py"]
```

### 环境变量

生产环境建议通过环境变量配置：

```bash
export LLM_API_KEY=xxx
export LLM_MODEL=gpt-4
export LOG_LEVEL=INFO
```

---

## 获取帮助

- 📚 查看示例代码：`examples/`
- 📖 阅读 [Pydantic 配置指南](PYDANTIC_GUIDE.md)
- 🐛 提交 Issue
- 💬 参与讨论

---

**更新时间：** 2025-12-21
