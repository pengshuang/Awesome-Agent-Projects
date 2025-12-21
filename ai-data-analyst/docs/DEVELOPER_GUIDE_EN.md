# Developer Guide

This guide is designed for developers to learn how to perform secondary development and extensions.

## 📋 Table of Contents

- [Project Architecture](#project-architecture)
- [Core Modules](#core-modules)
- [Extension Development](#extension-development)
- [Data Models](#data-models)
- [Best Practices](#best-practices)

## Project Architecture

### Directory Structure

```
ai-data-analyst/
├── config/                 # Configuration module
│   ├── settings.py        # System configuration (Pydantic Settings)
│   ├── llm_config.py      # LLM configuration
│   └── prompts.py         # Prompt templates
├── src/
│   ├── models/            # Pydantic data models
│   │   ├── config.py      # Configuration models
│   │   ├── datasource.py  # Data source models
│   │   └── analysis.py    # Analysis models
│   ├── datasources/       # Data source adapters
│   │   ├── base.py        # Base class
│   │   ├── sqlite_source.py
│   │   ├── file_source.py
│   │   ├── knowledge_base.py
│   │   └── web_source.py
│   ├── analyzers/         # Data analyzers
│   │   └── data_analyzer.py
│   ├── tools/             # Tool modules
│   │   └── nl2sql.py      # NL2SQL conversion
│   ├── ui/                # UI components
│   └── utils/             # Utility functions
├── data/                  # Data directory
│   ├── databases/         # SQLite databases
│   ├── files/             # Data files
│   └── cache/             # Cache
├── docs/                  # Documentation
├── examples/              # Example code
├── logs/                  # Logs
├── web_ui.py             # Web interface entry
└── requirements.txt       # Dependencies
```

### Architecture Design

```
┌─────────────┐
│  Web UI    │  Gradio Interface
└──────┬──────┘
       │
┌──────▼──────────────────┐
│  DataAnalystAgent       │  Core Agent
│  - Dialog management    │
│  - Data source mgmt     │
│  - Analysis scheduling  │
└──────┬──────────────────┘
       │
   ┌───┴───┬─────────┬──────────┐
   │       │         │          │
┌──▼──┐ ┌─▼──┐  ┌───▼───┐  ┌──▼────┐
│ SQL │ │File│  │  KB   │  │  Web  │
└──┬──┘ └─┬──┘  └───┬───┘  └──┬────┘
   │      │         │         │
   └──────┴─────────┴─────────┘
      Data Source Adapter Layer
```

## Core Modules

### 1. Data Models (src/models/)

Using Pydantic v2 for data validation:

```python
from src.models.config import SystemSettings
from src.models.datasource import QueryRequest, QueryResponse

# System configuration (auto-loaded from .env)
settings = SystemSettings()

# Query request
request = QueryRequest(
    query="SELECT * FROM users",
    data_source="my_db",
    limit=100,
)

# Query response (auto-validated)
response = QueryResponse(
    success=True,
    data=[...],
    metadata=QueryMetadata(...)
)
```

See [Pydantic Data Validation Guide](PYDANTIC_GUIDE_EN.md) for details

### 2. Data Source Adapters (src/datasources/)

All data sources inherit from the `DataSource` base class:

```python
from src.datasources.base import DataSource
from src.models.datasource import QueryResponse

class CustomDataSource(DataSource):
    def __init__(self, name: str):
        super().__init__(name, "custom")
    
    def connect(self) -> bool:
        # Implement connection logic
        return True
    
    def query(self, query: str, **kwargs) -> QueryResponse:
        # Implement query logic
        return QueryResponse(
            success=True,
            data=[...],
            metadata=QueryMetadata(...)
        )
    
    def get_schema(self) -> str:
        # Return schema description
        return "..."
    
    def close(self):
        # Cleanup resources
        pass
```

### 3. Agent (src/agent.py)

Core dialog agent:

```python
from src.agent import DataAnalystAgent

# Create Agent
agent = DataAnalystAgent(max_history_turns=10)

# Register data source
agent.register_sqlite_database("my_db", "path/to/db.sqlite")

# Chat query
response = agent.chat("Query sales data", data_sources=["my_db"])
```

## Extension Development

### Adding a New Data Source

1. **Create Data Source Class**

```python
# src/datasources/mysql_source.py
from .base import DataSource
from src.models.datasource import QueryResponse, QueryMetadata
import time

class MySQLDataSource(DataSource):
    def __init__(self, name: str, host: str, database: str):
        super().__init__(name, "mysql")
        self.host = host
        self.database = database
        self.connection = None
    
    def connect(self) -> bool:
        try:
            import pymysql
            self.connection = pymysql.connect(
                host=self.host,
                database=self.database,
                # ...
            )
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def query(self, query: str, **kwargs) -> QueryResponse:
        start_time = time.time()
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            
            return QueryResponse(
                success=True,
                data=data,
                metadata=QueryMetadata(
                    row_count=len(data),
                    execution_time=time.time() - start_time,
                    data_source_type="mysql",
                ),
            )
        except Exception as e:
            return QueryResponse(
                success=False,
                error=str(e),
                metadata=QueryMetadata(
                    row_count=0,
                    execution_time=time.time() - start_time,
                    data_source_type="mysql",
                ),
            )
```

2. **Register to Agent**

```python
# src/agent.py
def register_mysql_database(self, name: str, host: str, database: str):
    from .datasources.mysql_source import MySQLDataSource
    source = MySQLDataSource(name, host, database)
    if source.connect():
        self.analyzer.register_data_source(name, source)
        return True
    return False
```

### Custom Analyzer

```python
# src/analyzers/custom_analyzer.py
class CustomAnalyzer:
    def analyze(self, data, question: str):
        # Custom analysis logic
        insights = []
        # ... analysis code
        return {
            "summary": "...",
            "insights": insights,
        }
```

### Extending Prompt Templates

```python
# config/prompts.py
class CustomPromptTemplates:
    CUSTOM_ANALYSIS = """
    You are a data analysis expert. Please analyze the following data:
    
    Data: {data}
    Question: {question}
    
    Please provide a detailed analysis.
    """
```

### Adding New Chart Types

1. **Extend Enum**

```python
# src/models/analysis.py
class VisualizationType(str, Enum):
    # ... existing types
    CUSTOM = "custom"  # New type
```

2. **Implement Rendering Logic**

```python
# src/analyzers/data_analyzer.py
def create_custom_chart(self, data, config):
    import plotly.graph_objects as go
    
    fig = go.Figure()
    # ... custom chart logic
    
    return fig
```

## Data Models

### Configuration Models

```python
from src.models.config import (
    SystemSettings,    # System configuration
    LLMConfig,        # LLM configuration
    EmbeddingConfig,  # Embedding configuration
)

# Auto-validation and type conversion
settings = SystemSettings()
llm_config = settings.get_llm_config()
```

### Data Source Models

```python
from src.models.datasource import (
    DataSourceConfig,   # Basic configuration
    SQLiteConfig,       # SQLite configuration
    FileConfig,         # File configuration
    QueryRequest,       # Query request
    QueryResponse,      # Query response
    QueryMetadata,      # Metadata
)
```

### Analysis Models

```python
from src.models.analysis import (
    AnalysisRequest,    # Analysis request
    AnalysisResponse,   # Analysis response
    ChartConfig,        # Chart configuration
    VisualizationType,  # Chart type
    ChatSession,        # Session management
)
```

See [Pydantic Data Validation Guide](PYDANTIC_GUIDE_EN.md) for details

## Best Practices

### 1. Use Pydantic Models

✅ **Recommended**
```python
from src.models.datasource import QueryResponse

def query_data(sql: str) -> QueryResponse:
    # Return validated model
    return QueryResponse(
        success=True,
        data=[...],
        metadata=QueryMetadata(...)
    )
```

❌ **Not Recommended**
```python
def query_data(sql: str) -> dict:
    # Return raw dictionary, no validation
    return {"success": True, "data": [...]}
```

### 2. Error Handling

```python
from pydantic import ValidationError

try:
    config = LLMConfig(
        api_key="key",
        temperature=3.0,  # Out of range
    )
except ValidationError as e:
    logger.error(f"Configuration validation failed: {e}")
    for error in e.errors():
        print(f"Field: {error['loc']}, Error: {error['msg']}")
```

### 3. Logging

```python
from loguru import logger

logger.info("Starting query")
logger.debug(f"SQL: {sql}")
logger.error(f"Query failed: {e}")
logger.warning("Data is empty")
```

### 4. Resource Management

```python
# Use context manager
with datasource:
    result = datasource.query("SELECT * FROM users")
```

### 5. Configuration Management

```python
# Use unified settings instance
from config.settings import settings

# Access configuration
api_key = settings.llm_api_key
temperature = settings.temperature

# Ensure directories exist
settings.ensure_directories()
```

## Development Tools

### Running Tests

```bash
# Unit tests (to be added)
pytest tests/

# Run examples
python examples/pydantic_usage.py
```

### Code Checking

```bash
# Type checking
mypy src/

# Code formatting
black src/
```

### Debugging

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use IDE breakpoints for debugging
```

## API Reference

### Agent API

```python
agent = DataAnalystAgent(max_history_turns=10)

# Register data sources
agent.register_sqlite_database(name, db_path)
agent.register_file_datasource(name, file_path)

# Chat
response = agent.chat(question, data_sources)

# Clear history
agent.clear_history()
```

### DataSource API

```python
# Connect
datasource.connect()

# Query
response: QueryResponse = datasource.query(query)

# Get Schema
schema: str = datasource.get_schema()

# Close
datasource.close()
```

## Performance Optimization

1. **Cache query results** - Avoid duplicate queries
2. **Limit returned data volume** - Use LIMIT clause
3. **Asynchronous processing** - Use async for long-running queries
4. **Batch operations** - Merge multiple small queries

## Common Questions

### Q: How to add custom validation?

Use Pydantic's `@field_validator`:

```python
from pydantic import BaseModel, field_validator

class CustomConfig(BaseModel):
    value: int
    
    @field_validator("value")
    @classmethod
    def validate_value(cls, v):
        if v < 0:
            raise ValueError("Value must be greater than 0")
        return v
```

### Q: How to support new LLM?

Just configure an endpoint compatible with OpenAI API:

```bash
LLM_API_BASE=https://your-llm-endpoint/v1
LLM_MODEL=your-model-name
```

### Q: How to debug SQL generation?

Check detailed SQL statements in the `logs/` directory.

## 📚 Reference Resources

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [Gradio Documentation](https://www.gradio.app/docs/)
- [Plotly Documentation](https://plotly.com/python/)

## 🤝 Contributing Guidelines

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
