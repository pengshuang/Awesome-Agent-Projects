# Pydantic 数据验证指南

本项目使用 Pydantic v2 进行数据验证和配置管理。

## 快速开始

已包含在 `requirements.txt` 中：

```bash
pip install -r requirements.txt
```

## 核心模型

### 1. 配置管理

```python
from src.models.config import SystemSettings

# 自动从 .env 加载并验证
settings = SystemSettings()
print(settings.llm_model)
print(settings.temperature)  # 已验证范围 [0.0, 2.0]
```

### 2. 查询模型

```python
from src.models.datasource import QueryRequest, QueryResponse

# 查询请求
request = QueryRequest(
    query="SELECT * FROM users",
    data_source="my_db",
    limit=100,
)

# 查询响应（自动验证）
response: QueryResponse = datasource.query(request.query)
if response.has_data():
    columns = response.get_column_names()
```

### 3. 图表配置

```python
from src.models.analysis import ChartConfig, VisualizationType

chart = ChartConfig(
    chart_type=VisualizationType.BAR,
    title="销售趋势",
    x_column="month",
    y_column="sales",
    width=1000,
    height=600,
)
```

## 主要特性

### 自动验证

```python
from src.models.config import LLMConfig

# 温度自动验证范围 [0.0, 2.0]
config = LLMConfig(
    api_key="sk-key",
    temperature=0.7,  # ✅ 有效
)

config = LLMConfig(
    api_key="sk-key",
    temperature=3.0,  # ❌ ValidationError
)
```

### 类型安全

```python
# IDE 完整支持类型提示
response: QueryResponse = datasource.query("SELECT * FROM users")
if response.success:  # IDE 知道是 bool
    data = response.data  # IDE 知道是 List[Dict]
```

### 序列化

```python
# 导出为字典/JSON
data = config.model_dump()
json_str = config.model_dump_json(indent=2)

# 从字典/JSON 加载
config = LLMConfig.model_validate(data)
config = LLMConfig.model_validate_json(json_str)
```

## 最佳实践

### 使用类型提示

```python
from src.models.datasource import QueryResponse

def query_data(sql: str) -> QueryResponse:
    return QueryResponse(...)
```

### 错误处理

```python
from pydantic import ValidationError

try:
    config = LLMConfig(temperature=3.0)
except ValidationError as e:
    for error in e.errors():
        print(f"{error['loc']}: {error['msg']}")
```

### 环境变量配置

`.env` 文件：

```bash
LLM_API_KEY=sk-your-key
LLM_MODEL=gpt-3.5-turbo
TEMPERATURE=0.1
```

自动加载：

```python
from config.settings import settings
# 自动从 .env 加载并验证
```

## 运行示例

```bash
python examples/pydantic_usage.py
```

## 参考

- [Pydantic 文档](https://docs.pydantic.dev/)
- [开发者指南](DEVELOPER_GUIDE.md)
