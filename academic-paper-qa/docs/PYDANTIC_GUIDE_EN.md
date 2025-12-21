# Pydantic Configuration System Guide

> This project uses Pydantic 2.0+ for configuration management and data validation

## Quick Start

### Basic Usage

```python
from config.models import get_config

# Get configuration (auto-loads .env)
config = get_config()

# Type-safe access
api_key: str = config.llm.api_key
model: str = config.llm.model
temperature: float = config.llm.temperature
chunk_size: int = config.rag.chunk_size
```

### Configuration Models

The project includes the following configuration models:

- `LLMConfig` - LLM configuration
- `EmbeddingConfig` - Embedding configuration  
- `RAGConfig` - RAG configuration
- `VectorStoreConfig` - Vector store configuration
- `WebSearchConfig` - Web search configuration
- `SystemConfig` - System configuration

---

## Main Advantages

### 1. Type Safety

```python
config = get_config()

# IDE provides auto-completion and type checking
model: str = config.llm.model
temperature: float = config.llm.temperature
```

### 2. Automatic Validation

Pydantic automatically validates:
- `temperature` must be between 0.0-2.0
- `chunk_overlap` must be less than `chunk_size`
- URLs must be in valid format
- Required fields cannot be empty

### 3. Environment Variable Integration

Automatically loads configuration from `.env` file:

```bash
# .env
LLM_API_KEY=your-key
LLM_MODEL=gpt-3.5-turbo
TEMPERATURE=0.1
```

---

## Configuration Models Explained

### LLMConfig

```python
class LLMConfig(BaseSettings):
    api_key: str                    # API Key (required)
    api_base: str = "..."          # API endpoint
    model: str = "gpt-3.5-turbo"   # Model name
    temperature: float = 0.1        # Temperature (0.0-2.0)
    max_tokens: Optional[int] = None
    timeout: int = 60
```

### RAGConfig

```python
class RAGConfig(BaseSettings):
    chunk_size: int = 512           # Chunk size (1-4096)
    chunk_overlap: int = 50         # Overlap size
    retrieval_top_k: int = 5        # Top-K (1-50)
    retrieval_similarity_threshold: float = 0.7
    enable_reranking: bool = False
```

---

## Data Models

### QueryRequest

```python
from src.models import QueryRequest

request = QueryRequest(
    question="What is machine learning?",
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

session.add_message("user", "Hello")
session.add_message("assistant", "Hello!")
```

---

## Backward Compatibility

Old code still works:

```python
from config import SystemConfig

# Still available
chunk_size = SystemConfig.CHUNK_SIZE
docs_dir = SystemConfig.DOCUMENTS_DIR
```

Recommended new code uses Pydantic configuration:

```python
from config.models import get_config

config = get_config()
chunk_size = config.rag.chunk_size
docs_dir = config.system.documents_dir
```

---

## Common Operations

### Export Configuration

```python
config = get_config()

# Export as JSON
json_str = config.model_dump_json(indent=2)

# Export as dictionary
dict_data = config.model_dump()
```

### Reload Configuration

```python
from config.models import reload_config

config = reload_config()
```

### Custom Configuration

```python
from config.models import LLMConfig

custom_llm = LLMConfig(
    api_key="custom-key",
    model="gpt-4",
    temperature=0.5
)
```

---

## Reference

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Developer Guide](DEVELOPER_GUIDE_EN.md)
