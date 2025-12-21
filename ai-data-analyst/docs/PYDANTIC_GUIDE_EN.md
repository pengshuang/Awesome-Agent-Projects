# Pydantic Data Validation Guide

This project uses Pydantic v2 for data validation and configuration management.

## Quick Start

Already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Core Models

### 1. Configuration Management

```python
from src.models.config import SystemSettings

# Auto-loads and validates from .env
settings = SystemSettings()
print(settings.llm_model)
print(settings.temperature)  # Validated range [0.0, 2.0]
```

### 2. Query Models

```python
from src.models.datasource import QueryRequest, QueryResponse

# Query request
request = QueryRequest(
    query="SELECT * FROM users",
    data_source="my_db",
    limit=100,
)

# Query response (auto-validated)
response: QueryResponse = datasource.query(request.query)
if response.has_data():
    columns = response.get_column_names()
```

### 3. Chart Configuration

```python
from src.models.analysis import ChartConfig, VisualizationType

chart = ChartConfig(
    chart_type=VisualizationType.BAR,
    title="Sales Trend",
    x_column="month",
    y_column="sales",
    width=1000,
    height=600,
)
```

## Main Features

### Automatic Validation

```python
from src.models.config import LLMConfig

# Temperature auto-validates range [0.0, 2.0]
config = LLMConfig(
    api_key="sk-key",
    temperature=0.7,  # ✅ Valid
)

config = LLMConfig(
    api_key="sk-key",
    temperature=3.0,  # ❌ ValidationError
)
```

### Type Safety

```python
# IDE full support for type hints
response: QueryResponse = datasource.query("SELECT * FROM users")
if response.success:  # IDE knows it's bool
    data = response.data  # IDE knows it's List[Dict]
```

### Serialization

```python
# Export as dict/JSON
data = config.model_dump()
json_str = config.model_dump_json(indent=2)

# Load from dict/JSON
config = LLMConfig.model_validate(data)
config = LLMConfig.model_validate_json(json_str)
```

## Best Practices

### Use Type Hints

```python
from src.models.datasource import QueryResponse

def query_data(sql: str) -> QueryResponse:
    return QueryResponse(...)
```

### Error Handling

```python
from pydantic import ValidationError

try:
    config = LLMConfig(temperature=3.0)
except ValidationError as e:
    for error in e.errors():
        print(f"{error['loc']}: {error['msg']}")
```

### Environment Variable Configuration

`.env` file:

```bash
LLM_API_KEY=sk-your-key
LLM_MODEL=gpt-3.5-turbo
TEMPERATURE=0.1
```

Auto-load:

```python
from config.settings import settings
# Auto-loads and validates from .env
```

## Run Examples

```bash
python examples/pydantic_usage.py
```

## Reference

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Developer Guide](DEVELOPER_GUIDE_EN.md)
