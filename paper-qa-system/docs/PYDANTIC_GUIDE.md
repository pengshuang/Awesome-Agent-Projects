# Pydantic 配置系统指南

> 本项目使用 Pydantic 2.0+ 进行配置管理和数据验证

## 快速开始

### 基本用法

```python
from config.models import get_config

# 获取配置（自动加载 .env）
config = get_config()

# 类型安全的访问
api_key: str = config.llm.api_key
model: str = config.llm.model
temperature: float = config.llm.temperature
chunk_size: int = config.rag.chunk_size
```

### 配置模型

项目包含以下配置模型：

- `LLMConfig` - LLM 配置
- `EmbeddingConfig` - Embedding 配置  
- `RAGConfig` - RAG 配置
- `VectorStoreConfig` - 向量存储配置
- `WebSearchConfig` - Web 搜索配置
- `SystemConfig` - 系统配置

---

## 主要优势

### 1. 类型安全

```python
config = get_config()

# IDE 提供自动补全和类型检查
model: str = config.llm.model
temperature: float = config.llm.temperature
```

### 2. 自动验证

Pydantic 自动验证：
- `temperature` 必须在 0.0-2.0 之间
- `chunk_overlap` 必须小于 `chunk_size`
- URL 必须是有效格式
- 必填字段不能为空

### 3. 环境变量集成

自动从 `.env` 文件加载配置：

```bash
# .env
LLM_API_KEY=your-key
LLM_MODEL=gpt-3.5-turbo
TEMPERATURE=0.1
```

---

## 配置模型详解

### LLMConfig

```python
class LLMConfig(BaseSettings):
    api_key: str                    # API Key（必填）
    api_base: str = "..."          # API 端点
    model: str = "gpt-3.5-turbo"   # 模型名称
    temperature: float = 0.1        # 温度 (0.0-2.0)
    max_tokens: Optional[int] = None
    timeout: int = 60
```

### RAGConfig

```python
class RAGConfig(BaseSettings):
    chunk_size: int = 512           # 分块大小 (1-4096)
    chunk_overlap: int = 50         # 重叠大小
    retrieval_top_k: int = 5        # Top-K (1-50)
    retrieval_similarity_threshold: float = 0.7
    enable_reranking: bool = False
```

---

## 数据模型

### QueryRequest

```python
from src.models import QueryRequest

request = QueryRequest(
    question="什么是机器学习？",
    top_k=5,
    similarity_threshold=0.7,
    enable_web_search=False
)
```

### ChatSession

```python
from src.models import ChatSession

session = ChatSession(
    session_id="user-123",
    max_history_turns=10
)

session.add_message("user", "你好")
session.add_message("assistant", "你好！")
```

---

## 向后兼容

旧代码仍然有效：

```python
from config import SystemConfig

# 仍然可用
chunk_size = SystemConfig.CHUNK_SIZE
docs_dir = SystemConfig.DOCUMENTS_DIR
```

推荐新代码使用 Pydantic 配置：

```python
from config.models import get_config

config = get_config()
chunk_size = config.rag.chunk_size
docs_dir = config.system.documents_dir
```

---

## 常见操作

### 导出配置

```python
config = get_config()

# 导出为 JSON
json_str = config.model_dump_json(indent=2)

# 导出为字典
dict_data = config.model_dump()
```

### 重新加载配置

```python
from config.models import reload_config

config = reload_config()
```

### 自定义配置

```python
from config.models import LLMConfig

custom_llm = LLMConfig(
