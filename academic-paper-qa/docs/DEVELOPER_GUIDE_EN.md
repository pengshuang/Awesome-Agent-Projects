# 👨‍💻 Developer Guide

> For developers who need secondary development and feature extensions

## Contents

- [Project Architecture](#project-architecture)
- [Core Modules](#core-modules)
- [Pydantic Configuration System](#pydantic-configuration-system)
- [API Reference](#api-reference)
- [Extension Development](#extension-development)
- [Testing](#testing)

---

## Project Architecture

### Directory Structure

```
academic-paper-qa/
├── config/              # Configuration module (Pydantic)
│   ├── models.py       # Pydantic config models
│   ├── settings.py     # Global settings
│   ├── llm_config.py   # LLM configuration
│   └── prompts.py      # Prompt templates
├── src/                # Core code
│   ├── agent.py        # Agent core
│   ├── models.py       # Data models (Pydantic)
│   ├── indexing/       # Index building
│   ├── query/          # Query engine
│   ├── loaders/        # Document loading
│   ├── tools/          # Tools (search, etc.)
│   └── utils/          # Utilities
├── data/               # Data directory
├── examples/           # Example code
├── docs/               # Documentation
└── *.py               # Launch scripts
```

### Tech Stack

- **RAG Framework**: LlamaIndex
- **Vector Database**: Chroma
- **Configuration Management**: Pydantic 2.0+
- **Web UI**: Gradio 4.0+
- **Embedding**: HuggingFace / OpenAI

---

## Core Modules

### AcademicAgent

Core Agent class responsible for document management and Q&A.

```python
from src.agent import AcademicAgent

# Initialize
agent = AcademicAgent(
    documents_dir="data/documents",
    index_dir="data/vector_store",
    max_history_turns=10
)

# Build index
agent.build_index()

# Single-turn Q&A
response = agent.query("What does this paper discuss?")

# Multi-turn dialogue
response = agent.chat("What is Transformer?")
response = agent.chat("What are its advantages?")  # With context
```

### Document Loading

```python
from src.loaders import DocumentLoader

loader = DocumentLoader()
documents = loader.load_documents("data/documents")
```

Supported formats: PDF, DOCX, Markdown, TXT

### Index Building

```python
from src.indexing import Indexer

indexer = Indexer()
index = indexer.build_index(documents)
indexer.save_index(index, "data/vector_store")
```

### Query Engine

```python
from src.query import QAEngine

qa_engine = QAEngine(index, top_k=5)
answer = qa_engine.query("question")
```

---

## Pydantic Configuration System

### Configuration Loading

```python
from config.models import get_config

# Get global configuration (singleton)
config = get_config()

# Access configuration (type-safe)
api_key = config.llm.api_key
model = config.llm.model
chunk_size = config.rag.chunk_size
```

### Configuration Models

#### LLMConfig

```python
class LLMConfig(BaseSettings):
    api_key: str                    # API Key
    api_base: str = "..."          # API endpoint
    model: str = "gpt-3.5-turbo"   # Model
    temperature: float = 0.1        # Temperature (0-2)
    max_tokens: Optional[int] = None
```

#### RAGConfig

```python
class RAGConfig(BaseSettings):
    chunk_size: int = 512           # Chunk size (1-4096)
    chunk_overlap: int = 50         # Overlap size
    retrieval_top_k: int = 5        # Top-K (1-50)
    retrieval_similarity_threshold: float = 0.7
    enable_reranking: bool = False
```

### Data Models

```python
from src.models import QueryRequest, QueryResponse

# Query request
request = QueryRequest(
    question="What is machine learning?",
    top_k=5,
    similarity_threshold=0.7
)

# Query response
response = QueryResponse(
    answer="Machine learning is...",
    sources=[...],
    query_time=1.23
)
```

### Backward Compatibility

```python
from config import SystemConfig

# Old code still works
chunk_size = SystemConfig.CHUNK_SIZE
docs_dir = SystemConfig.DOCUMENTS_DIR
```

---

## API Reference

### AcademicAgent API

#### Initialization

```python
agent = AcademicAgent(
    documents_dir: str = "data/documents",
    index_dir: str = "data/vector_store",
    auto_load: bool = True,
    max_history_turns: int = 10
)
```

#### Methods

**Index Management:**
- `build_index(force_rebuild=False)` - Build index
- `load_index()` - Load index
- `list_papers()` - List documents

**Q&A:**
- `query(question, mode="rag", enable_web_search=False)` - Single-turn Q&A
- `chat(question, mode="rag", enable_web_search=False)` - Multi-turn dialogue

**History Management:**
- `get_chat_history()` - Get history
- `clear_chat_history()` - Clear history

### Configuration API

```python
from config.models import get_config, reload_config

# Get configuration
config = get_config()

# Reload
config = reload_config()

# Export configuration
json_str = config.model_dump_json(indent=2)
dict_data = config.model_dump()
```

---

## Extension Development

### Custom Prompts

Edit `config/prompts.py`:

```python
CUSTOM_SYSTEM_PROMPT = """
You are a professional academic assistant...
"""
```

### Add New Document Loader

```python
from src.loaders import DocumentLoader

class MyLoader(DocumentLoader):
    def load_my_format(self, file_path):
        # Implement loading logic
        pass
```

### Integrate New Search Engine

```python
from src.tools import WebSearchTool

class MySearchTool(WebSearchTool):
    def search(self, query):
        # Implement search logic
        pass
```

### Custom Data Models

```python
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    field1: str = Field(..., description="Field 1")
    field2: int = Field(default=0, ge=0)
```

---

## Testing

### Run Tests

```bash
# All tests
pytest tests/

# Specific test
pytest tests/test_agent_core.py

# Verbose output
pytest -v tests/
```

### Write Tests

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

## Development Standards

### Code Style

- Follow PEP 8
- Use type annotations
- Add docstrings

```python
def my_function(param: str) -> int:
    """
    Function description
    
    Args:
        param: Parameter description
        
    Returns:
        Return value description
    """
    pass
```

### Git Workflow

```bash
# 1. Create branch
git checkout -b feature/my-feature

# 2. Develop and test
# ...

# 3. Commit
git commit -m "Add: new feature description"

# 4. Push
git push origin feature/my-feature

# 5. Create Pull Request
```

### Commit Message Convention

- `Add:` New feature
- `Fix:` Bug fix
- `Update:` Update feature
- `Refactor:` Refactor code
- `Docs:` Documentation update

---

## Performance Optimization

### Index Optimization

```python
# Adjust chunk parameters
config.rag.chunk_size = 1024
config.rag.chunk_overlap = 100

# Adjust retrieval parameters
config.rag.retrieval_top_k = 10
```

### Caching

```python
# Enable cache
config.system.enable_cache = True
```

---

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "web_ui_multi_turn.py"]
```

### Environment Variables

Production environment should use environment variables:

```bash
export LLM_API_KEY=xxx
export LLM_MODEL=gpt-4
export LOG_LEVEL=INFO
```

---

## Get Help

- 📚 Check example code: `examples/`
- 📖 Read [Pydantic Configuration Guide](PYDANTIC_GUIDE_EN.md)
- 🐛 Submit Issue
- 💬 Join discussions

---

**Last Updated:** 2025-12-21
