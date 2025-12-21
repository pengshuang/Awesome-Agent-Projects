# 开发者指南

本指南面向开发者，介绍如何进行二次开发和扩展。

## 📋 目录

- [项目架构](#项目架构)
- [核心模块](#核心模块)
- [扩展开发](#扩展开发)
- [数据模型](#数据模型)
- [最佳实践](#最佳实践)

## 项目架构

### 目录结构

```
ai-data-analyst/
├── config/                 # 配置模块
│   ├── settings.py        # 系统配置（Pydantic Settings）
│   ├── llm_config.py      # LLM 配置
│   └── prompts.py         # Prompt 模板
├── src/
│   ├── models/            # Pydantic 数据模型
│   │   ├── config.py      # 配置模型
│   │   ├── datasource.py  # 数据源模型
│   │   └── analysis.py    # 分析模型
│   ├── datasources/       # 数据源适配器
│   │   ├── base.py        # 基类
│   │   ├── sqlite_source.py
│   │   ├── file_source.py
│   │   ├── knowledge_base.py
│   │   └── web_source.py
│   ├── analyzers/         # 数据分析器
│   │   └── data_analyzer.py
│   ├── tools/             # 工具模块
│   │   └── nl2sql.py      # NL2SQL 转换
│   ├── ui/                # UI 组件
│   └── utils/             # 工具函数
├── data/                  # 数据目录
│   ├── databases/         # SQLite 数据库
│   ├── files/             # 数据文件
│   └── cache/             # 缓存
├── docs/                  # 文档
├── examples/              # 示例代码
├── logs/                  # 日志
├── web_ui.py             # Web 界面入口
└── requirements.txt       # 依赖
```

### 架构设计

```
┌─────────────┐
│  Web UI    │  Gradio 界面
└──────┬──────┘
       │
┌──────▼──────────────────┐
│  DataAnalystAgent       │  核心 Agent
│  - 对话管理             │
│  - 数据源管理           │
│  - 分析调度             │
└──────┬──────────────────┘
       │
   ┌───┴───┬─────────┬──────────┐
   │       │         │          │
┌──▼──┐ ┌─▼──┐  ┌───▼───┐  ┌──▼────┐
│ SQL │ │File│  │  KB   │  │  Web  │
└──┬──┘ └─┬──┘  └───┬───┘  └──┬────┘
   │      │         │         │
   └──────┴─────────┴─────────┘
          数据源适配层
```

## 核心模块

### 1. 数据模型 (src/models/)

使用 Pydantic v2 进行数据验证：

```python
from src.models.config import SystemSettings
from src.models.datasource import QueryRequest, QueryResponse

# 系统配置（自动从 .env 加载）
settings = SystemSettings()

# 查询请求
request = QueryRequest(
    query="SELECT * FROM users",
    data_source="my_db",
    limit=100,
)

# 查询响应（自动验证）
response = QueryResponse(
    success=True,
    data=[...],
    metadata=QueryMetadata(...)
)
```

详见 [Pydantic 数据验证指南](PYDANTIC_GUIDE.md)

### 2. 数据源适配器 (src/datasources/)

所有数据源继承 `DataSource` 基类：

```python
from src.datasources.base import DataSource
from src.models.datasource import QueryResponse

class CustomDataSource(DataSource):
    def __init__(self, name: str):
        super().__init__(name, "custom")
    
    def connect(self) -> bool:
        # 实现连接逻辑
        return True
    
    def query(self, query: str, **kwargs) -> QueryResponse:
        # 实现查询逻辑
        return QueryResponse(
            success=True,
            data=[...],
            metadata=QueryMetadata(...)
        )
    
    def get_schema(self) -> str:
        # 返回 schema 描述
        return "..."
    
    def close(self):
        # 清理资源
        pass
```

### 3. Agent (src/agent.py)

核心对话代理：

```python
from src.agent import DataAnalystAgent

# 创建 Agent
agent = DataAnalystAgent(max_history_turns=10)

# 注册数据源
agent.register_sqlite_database("my_db", "path/to/db.sqlite")

# 对话查询
response = agent.chat("查询销售数据", data_sources=["my_db"])
```

## 扩展开发

### 添加新数据源

1. **创建数据源类**

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
            logger.error(f"连接失败: {e}")
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

2. **注册到 Agent**

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

### 自定义分析器

```python
# src/analyzers/custom_analyzer.py
class CustomAnalyzer:
    def analyze(self, data, question: str):
        # 自定义分析逻辑
        insights = []
        # ... 分析代码
        return {
            "summary": "...",
            "insights": insights,
        }
```

### 扩展 Prompt 模板

```python
# config/prompts.py
class CustomPromptTemplates:
    CUSTOM_ANALYSIS = """
    你是数据分析专家，请分析以下数据：
    
    数据: {data}
    问题: {question}
    
    请给出详细分析。
    """
```

### 添加新的图表类型

1. **扩展枚举**

```python
# src/models/analysis.py
class VisualizationType(str, Enum):
    # ... 现有类型
    CUSTOM = "custom"  # 新增类型
```

2. **实现渲染逻辑**

```python
# src/analyzers/data_analyzer.py
def create_custom_chart(self, data, config):
    import plotly.graph_objects as go
    
    fig = go.Figure()
    # ... 自定义图表逻辑
    
    return fig
```

## 数据模型

### 配置模型

```python
from src.models.config import (
    SystemSettings,    # 系统配置
    LLMConfig,        # LLM 配置
    EmbeddingConfig,  # Embedding 配置
)

# 自动验证和类型转换
settings = SystemSettings()
llm_config = settings.get_llm_config()
```

### 数据源模型

```python
from src.models.datasource import (
    DataSourceConfig,   # 基础配置
    SQLiteConfig,       # SQLite 配置
    FileConfig,         # 文件配置
    QueryRequest,       # 查询请求
    QueryResponse,      # 查询响应
    QueryMetadata,      # 元数据
)
```

### 分析模型

```python
from src.models.analysis import (
    AnalysisRequest,    # 分析请求
    AnalysisResponse,   # 分析响应
    ChartConfig,        # 图表配置
    VisualizationType,  # 图表类型
    ChatSession,        # 会话管理
)
```

详细说明见 [Pydantic 数据验证指南](PYDANTIC_GUIDE.md)

## 最佳实践

### 1. 使用 Pydantic 模型

✅ **推荐**
```python
from src.models.datasource import QueryResponse

def query_data(sql: str) -> QueryResponse:
    # 返回验证过的模型
    return QueryResponse(
        success=True,
        data=[...],
        metadata=QueryMetadata(...)
    )
```

❌ **不推荐**
```python
def query_data(sql: str) -> dict:
    # 返回原始字典，无验证
    return {"success": True, "data": [...]}
```

### 2. 错误处理

```python
from pydantic import ValidationError

try:
    config = LLMConfig(
        api_key="key",
        temperature=3.0,  # 超出范围
    )
except ValidationError as e:
    logger.error(f"配置验证失败: {e}")
    for error in e.errors():
        print(f"字段: {error['loc']}, 错误: {error['msg']}")
```

### 3. 日志记录

```python
from loguru import logger

logger.info("开始查询")
logger.debug(f"SQL: {sql}")
logger.error(f"查询失败: {e}")
logger.warning("数据为空")
```

### 4. 资源管理

```python
# 使用上下文管理器
with datasource:
    result = datasource.query("SELECT * FROM users")
```

### 5. 配置管理

```python
# 统一使用 settings 实例
from config.settings import settings

# 访问配置
api_key = settings.llm_api_key
temperature = settings.temperature

# 确保目录存在
settings.ensure_directories()
```

## 开发工具

### 运行测试

```bash
# 单元测试（待添加）
pytest tests/

# 运行示例
python examples/pydantic_usage.py
```

### 代码检查

```bash
# 类型检查
mypy src/

# 代码格式化
black src/
```

### 调试

```python
# 在代码中添加断点
import pdb; pdb.set_trace()

# 或使用 IDE 断点调试
```

## API 参考

### Agent API

```python
agent = DataAnalystAgent(max_history_turns=10)

# 注册数据源
agent.register_sqlite_database(name, db_path)
agent.register_file_datasource(name, file_path)

# 对话
response = agent.chat(question, data_sources)

# 清空历史
agent.clear_history()
```

### DataSource API

```python
# 连接
datasource.connect()

# 查询
response: QueryResponse = datasource.query(query)

# 获取 Schema
schema: str = datasource.get_schema()

# 关闭
datasource.close()
```

## 性能优化

1. **缓存查询结果** - 避免重复查询
2. **限制返回数据量** - 使用 LIMIT 子句
3. **异步处理** - 对于长时间查询使用异步
4. **批量操作** - 合并多个小查询

## 常见问题

### Q: 如何添加自定义验证？

使用 Pydantic 的 `@field_validator`:

```python
from pydantic import BaseModel, field_validator

class CustomConfig(BaseModel):
    value: int
    
    @field_validator("value")
    @classmethod
    def validate_value(cls, v):
        if v < 0:
            raise ValueError("值必须大于 0")
        return v
```

### Q: 如何支持新的 LLM?

只需配置兼容 OpenAI API 的 endpoint：

```bash
LLM_API_BASE=https://your-llm-endpoint/v1
LLM_MODEL=your-model-name
```

### Q: 如何调试 SQL 生成？

查看日志文件 `logs/` 中的详细 SQL 语句。

## 📚 参考资源

- [Pydantic 文档](https://docs.pydantic.dev/)
- [LlamaIndex 文档](https://docs.llamaindex.ai/)
- [Gradio 文档](https://www.gradio.app/docs/)
- [Plotly 文档](https://plotly.com/python/)

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request
