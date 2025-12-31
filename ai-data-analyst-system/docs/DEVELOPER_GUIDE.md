# 开发者指南

**本指南面向开发者**，介绍如何进行二次开发和扩展。

> 💡 **设计原则**：模块化架构、类型安全、易于扩展

---

## 📋 目录

- [项目架构](#项目架构)
- [核心模块](#核心模块)
- [UI 开发](#ui-开发)
- [扩展开发](#扩展开发)
- [最佳实践](#最佳实践)

---

## 项目架构

### 目录结构

```
ai-data-analyst-system/
├── config/                    # 配置模块
│   ├── __init__.py
│   ├── settings.py           # 系统配置（Pydantic Settings）
│   ├── llm_config.py         # LLM 和 Embedding 配置
│   └── prompts.py            # Prompt 模板管理
│
├── src/
│   ├── models/               # Pydantic 数据模型（类型安全）
│   │   ├── config.py         # 配置模型
│   │   ├── datasource.py     # 数据源模型
│   │   └── analysis.py       # 分析结果模型
│   │
│   ├── datasources/          # 数据源适配器（策略模式）
│   │   ├── base.py           # 抽象基类
│   │   ├── sqlite_source.py  # SQLite 适配器
│   │   ├── file_source.py    # 文件适配器
│   │   ├── knowledge_base.py # 知识库适配器
│   │   └── web_source.py     # Web 搜索适配器
│   │
│   ├── analyzers/            # 数据分析器
│   │   └── data_analyzer.py  # 核心分析逻辑
│   │
│   ├── tools/                # 工具模块
│   │   └── nl2sql.py         # NL2SQL 转换工具
│   │
│   ├── ui/                   # UI 组件（Gradio）
│   │   ├── constants.py      # UI 常量
│   │   ├── helpers.py        # UI 辅助函数
│   │   └── datasource_manager.py  # 数据源管理组件
│   │
│   ├── utils/                # 工具函数
│   │   ├── logger.py         # 日志配置
│   │   └── helpers.py        # 通用辅助函数
│   │
│   └── agent.py              # 核心 Agent 类
│
├── data/                     # 数据目录
│   ├── databases/            # SQLite 数据库
│   ├── files/                # CSV/Excel/JSON 文件
│   ├── knowledge_base/       # 知识库文档
│   └── cache/                # Embedding 缓存
│
├── docs/                     # 项目文档
├── logs/                     # 运行日志
├── output/                   # 输出文件
│
├── init_system.py            # 系统初始化脚本
├── web_ui.py                 # Web UI 入口（Gradio）
├── requirements.txt          # 项目依赖
└── .env                      # 环境配置
```

### 核心架构设计

```
┌──────────────────────────────────────────┐
│           Web UI (Gradio)                │
│  - 单屏设计，自动初始化                   │
│  - 实时可视化更新                         │
└────────────────┬─────────────────────────┘
                 │
┌────────────────▼─────────────────────────┐
│        DataAnalystAgent                  │
│  - 对话管理（上下文保持）                 │
│  - 数据源注册与管理                       │
│  - 查询调度与结果处理                     │
└────────────────┬─────────────────────────┘
                 │
        ┌────────┼────────┐
        │        │        │
┌───────▼───┐ ┌─▼──────┐ ┌─▼────────┐
│ Analyzer  │ │LLM API │ │Embedding │
│ 分析器    │ │配置层  │ │模型      │
└───────┬───┘ └────────┘ └──────────┘
        │
  ┌─────┴──────┬──────────┬────────┐
  │            │          │        │
┌─▼────┐  ┌───▼───┐  ┌──▼──┐  ┌──▼───┐
│SQLite│  │ File  │  │ KB  │  │ Web  │
│Source│  │Source │  │     │  │Search│
└──────┘  └───────┘  └─────┘  └──────┘
         数据源适配层（插件化）
```

### 关键设计模式

1. **策略模式** - 数据源适配器，统一接口不同实现
2. **单例模式** - Agent 实例管理
3. **工厂模式** - LLM 和 Embedding 模型创建
4. **观察者模式** - UI 组件状态更新

---

## 核心模块

### 1. 数据模型 (src/models/)

使用 **Pydantic v2** 进行数据验证和序列化。

#### 配置模型 (models/config.py)

```python
from pydantic import BaseModel, Field
from typing import Optional

class LLMConfig(BaseModel):
    """LLM 配置模型"""
    api_key: str = Field(..., description="API密钥")
    api_base: str = Field(default="https://api.openai.com/v1")
    model: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    
    class Config:
        str_strip_whitespace = True  # 自动去除空白

class EmbeddingConfig(BaseModel):
    """Embedding 配置模型"""
    provider: str = Field(default="huggingface")
    model_name: str
    api_key: Optional[str] = None
```

#### 数据源模型 (models/datasource.py)

```python
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str = Field(..., description="查询问题")
    data_source: str = Field(..., description="数据源名称")
    limit: Optional[int] = Field(default=100, ge=1, le=10000)

class QueryMetadata(BaseModel):
    """查询元数据"""
    rows_returned: int
    execution_time: float
    sql_query: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class QueryResponse(BaseModel):
    """查询响应模型"""
    success: bool
    data: List[Dict[str, Any]] = []
    metadata: QueryMetadata
    error: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### 2. 数据源适配器 (src/datasources/)

#### 基类设计 (datasources/base.py)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from llama_index.core import VectorStoreIndex

class BaseDataSource(ABC):
    """数据源抽象基类"""
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.config = kwargs
    
    @abstractmethod
    def get_index(self) -> VectorStoreIndex:
        """获取 LlamaIndex 索引"""
        pass
    
    @abstractmethod
    def get_schema(self) -> str:
        """获取数据源结构信息"""
        pass
    
    @abstractmethod
    def query(self, query_str: str) -> Dict[str, Any]:
        """执行查询"""
        pass
    
    def validate_config(self) -> bool:
        """验证配置"""
        return True
```

#### SQLite 适配器 (datasources/sqlite_source.py)

```python
from llama_index.core import SQLDatabase, VectorStoreIndex
from sqlalchemy import create_engine, text
import pandas as pd

class SQLiteDataSource(BaseDataSource):
    """SQLite 数据源适配器"""
    
    def __init__(self, name: str, db_path: str):
        super().__init__(name, db_path=db_path)
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.sql_database = SQLDatabase(self.engine)
    
    def get_index(self) -> VectorStoreIndex:
        """获取索引"""
        from llama_index.core import VectorStoreIndex
        return VectorStoreIndex.from_documents([])
    
    def get_schema(self) -> str:
        """获取表结构"""
        return self.sql_database.get_table_info()
    
    def query(self, query_str: str) -> Dict[str, Any]:
        """执行 SQL 查询"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query_str))
                rows = result.fetchall()
                columns = result.keys()
                
                data = [dict(zip(columns, row)) for row in rows]
                
                return {
                    "success": True,
                    "data": data,
                    "rows": len(data)
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": []
            }
```

### 3. 核心 Agent (src/agent.py)

```python
from typing import Dict, List, Optional
from src.datasources.base import BaseDataSource
from src.analyzers.data_analyzer import DataAnalyzer
from config.llm_config import get_llm, get_embedding_model

class DataAnalystAgent:
    """数据分析 Agent 核心类"""
    
    def __init__(self, max_history_turns: int = 10):
        self.data_sources: Dict[str, BaseDataSource] = {}
        self.llm = get_llm()
        self.embedding = get_embedding_model()
        self.analyzer = DataAnalyzer(self)
        self.chat_history: List[Dict] = []
        self.max_history_turns = max_history_turns
    
    def register_data_source(self, source: BaseDataSource):
        """注册数据源"""
        self.data_sources[source.name] = source
        logger.info(f"注册数据源: {source.name}")
    
    def register_sqlite_database(self, name: str, db_path: str) -> bool:
        """注册 SQLite 数据库"""
        from src.datasources.sqlite_source import SQLiteDataSource
        try:
            source = SQLiteDataSource(name, db_path)
            self.register_data_source(source)
            return True
        except Exception as e:
            logger.error(f"注册失败: {e}")
            return False
    
    def list_data_sources(self) -> Dict[str, str]:
        """列出所有数据源"""
        return {
            name: type(source).__name__ 
            for name, source in self.data_sources.items()
        }
    
    def _add_to_history(self, role: str, content: str):
        """添加对话历史"""
        self.chat_history.append({"role": role, "content": content})
        
        # 保持历史轮数限制
        if len(self.chat_history) > self.max_history_turns * 2:
            self.chat_history = self.chat_history[-self.max_history_turns * 2:]
    
    def clear_history(self):
        """清空对话历史"""
        self.chat_history = []
```

### 4. 数据分析器 (src/analyzers/data_analyzer.py)

```python
class DataAnalyzer:
    """数据分析器 - 负责查询分析和执行"""
    
    def __init__(self, agent: 'DataAnalystAgent'):
        self.agent = agent
    
    def analyze_single_source(
        self, 
        question: str, 
        source_name: str,
        chat_history: str = ""
    ) -> Dict[str, Any]:
        """分析单个数据源"""
        
        # 1. 获取数据源
        source = self.agent.data_sources.get(source_name)
        if not source:
            return {"success": False, "error": "数据源不存在"}
        
        # 2. 生成 SQL（如果是数据库）
        if isinstance(source, SQLiteDataSource):
            sql = self._generate_sql(question, source)
            result = source.query(sql)
            result["sql"] = sql
        else:
            # 3. 其他数据源使用向量检索
            result = self._query_index(question, source)
        
        # 4. 生成自然语言回答
        if result["success"]:
            answer = self._generate_answer(question, result["data"])
            result["answer"] = answer
        
        return result
    
    def _generate_sql(self, question: str, source) -> str:
        """使用 LLM 生成 SQL"""
        from config.prompts import SQL_GENERATION_PROMPT
        
        schema = source.get_schema()
        prompt = SQL_GENERATION_PROMPT.format(
            schema=schema,
            question=question
        )
        
        response = self.agent.llm.complete(prompt)
        sql = self._extract_sql(response.text)
        return sql
```

---

## UI 开发

### Gradio 界面设计

#### 核心特性

1. **自动初始化** - 使用 `demo.load()` 事件
2. **单屏布局** - 避免标签页切换
3. **实时更新** - 使用 `.change()` 事件监听
4. **状态管理** - AppState 类统一管理

#### 关键代码 (web_ui.py)

```python
class AppState:
    """全局状态管理"""
    def __init__(self):
        self.agent: Optional[DataAnalystAgent] = None
        self.last_query_result: Optional[pd.DataFrame] = None
        self.query_history: List[dict] = []
        self.auto_visualize: bool = True

# 自动初始化
demo.load(
    fn=lambda: (initialize_agent()[1], update_source_list()),
    outputs=[system_status, source_dropdown]
)

# 实时图表更新
for component in [chart_type, x_column, y_column, color_column]:
    component.change(
        fn=update_chart,
        inputs=[chart_type, x_column, y_column, color_column],
        outputs=viz_chart
    )
```

#### 自动可视化实现

```python
def chat_response(message: str, history: List, source: str):
    """对话响应 + 自动可视化"""
    
    # 1. 执行查询
    result = agent.analyzer.analyze_single_source(...)
    
    # 2. 自动生成图表
    if result.get("data"):
        df = pd.DataFrame(result["data"])
        
        # 智能选择图表类型
        chart_type = "bar"
        if df[y_col].dtype in ['float64', 'int64'] and len(df) > 10:
            chart_type = "line"
        
        # 生成图表
        viz_chart = create_chart_from_dataframe(
            df=df,
            chart_type=chart_type,
            x_col=cols[0],
            y_col=cols[1]
        )
    
    return history, viz_chart, df, ...
```

### UI 组件封装 (src/ui/)

```python
# ui/helpers.py
def create_chart_from_dataframe(
    df: pd.DataFrame,
    chart_type: str,
    x_col: str,
    y_col: str,
    color_col: Optional[str] = None,
    title: Optional[str] = None
) -> go.Figure:
    """创建 Plotly 图表"""
    
    if chart_type == "bar":
        fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
    elif chart_type == "line":
        fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title)
    # ...
    
    return fig
```

---

## 扩展开发

### 添加新数据源

#### 1. 创建适配器类

```python
# src/datasources/my_source.py
from src.datasources.base import BaseDataSource

class MyDataSource(BaseDataSource):
    """自定义数据源"""
    
    def __init__(self, name: str, **config):
        super().__init__(name, **config)
        # 初始化连接
        self.client = MyClient(**config)
    
    def get_index(self) -> VectorStoreIndex:
        """实现索引获取"""
        documents = self._load_documents()
        return VectorStoreIndex.from_documents(documents)
    
    def get_schema(self) -> str:
        """返回数据结构描述"""
        return "数据源结构信息..."
    
    def query(self, query_str: str) -> Dict[str, Any]:
        """执行查询"""
        try:
            result = self.client.query(query_str)
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

#### 2. 在 Agent 中注册

```python
# src/agent.py
def register_my_datasource(self, name: str, **config) -> bool:
    """注册自定义数据源"""
    from src.datasources.my_source import MyDataSource
    try:
        source = MyDataSource(name, **config)
        self.register_data_source(source)
        return True
    except Exception as e:
        logger.error(f"注册失败: {e}")
        return False
```

#### 3. 添加 UI 入口

```python
# web_ui.py - 在数据源管理面板添加选项
ds_type = gr.Radio(
    choices=["SQLite数据库", "文件(CSV/Excel)", "知识库", "我的数据源"],
    value="SQLite数据库",
    label="类型"
)

# 添加处理逻辑
def quick_register_datasource(ds_type: str, name: str, path: str):
    if ds_type == "我的数据源":
        result = app_state.agent.register_my_datasource(name, path=path)
    # ...
```

### 自定义 Prompt

```python
# config/prompts.py
SQL_GENERATION_PROMPT = """
你是一个 SQL 专家。根据以下数据库结构和用户问题生成 SQL 查询。

数据库结构：
{schema}

用户问题：
{question}

要求：
1. 只返回 SQL 语句，不要其他内容
2. 使用 SELECT 语句
3. 限制返回 100 条记录

SQL:
"""

# 使用
from config.prompts import SQL_GENERATION_PROMPT
prompt = SQL_GENERATION_PROMPT.format(schema=schema, question=question)
response = llm.complete(prompt)
```

### 添加新图表类型

```python
# src/ui/helpers.py
def create_chart_from_dataframe(...):
    """扩展图表类型"""
    
    if chart_type == "heatmap":
        # 热力图
        fig = px.density_heatmap(df, x=x_col, y=y_col, title=title)
    
    elif chart_type == "treemap":
        # 树状图
        fig = px.treemap(df, path=[x_col], values=y_col, title=title)
    
    elif chart_type == "sunburst":
        # 旭日图
        fig = px.sunburst(df, path=[x_col], values=y_col, title=title)
    
    return fig
```

---

## 最佳实践

### 1. 代码规范

```python
# ✅ 好的实践
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    """清晰的文档字符串"""
    name: str = Field(..., description="名称")
    value: Optional[int] = Field(default=None, ge=0)
    
    def process(self) -> Dict[str, Any]:
        """方法也要有文档字符串"""
        return {"name": self.name, "value": self.value}

# ❌ 避免
def process(data):  # 缺少类型注解
    return data  # 缺少文档字符串
```

### 2. 错误处理

```python
# ✅ 完善的错误处理
def query_database(sql: str) -> Dict[str, Any]:
    try:
        result = execute_sql(sql)
        return {"success": True, "data": result}
    except SQLError as e:
        logger.error(f"SQL 错误: {e}")
        return {"success": False, "error": f"SQL 错误: {str(e)}"}
    except Exception as e:
        logger.error(f"未知错误: {e}", exc_info=True)
        return {"success": False, "error": "系统错误"}

# ❌ 避免裸露的异常
def query_database(sql):
    result = execute_sql(sql)  # 可能抛出异常
    return result
```

### 3. 日志记录

```python
from src.utils.logger import logger

# ✅ 适当的日志级别
logger.debug("详细的调试信息")
logger.info("重要操作: 注册数据源 {name}")
logger.warning("警告: 数据可能不完整")
logger.error("错误: 查询失败", exc_info=True)  # 包含堆栈

# ❌ 避免
print("调试信息")  # 不使用 print
logger.info("...")  # 所有日志都用 info
```

### 4. 配置管理

```python
# ✅ 使用环境变量
from config.settings import settings

api_key = settings.llm_api_key
model = settings.llm_model

# ❌ 避免硬编码
api_key = "sk-xxxxx"  # 不要硬编码密钥
```

### 5. 测试

```python
# tests/test_datasource.py
import pytest
from src.datasources.sqlite_source import SQLiteDataSource

def test_sqlite_query():
    """测试 SQLite 查询"""
    source = SQLiteDataSource("test", "test.db")
    result = source.query("SELECT * FROM users LIMIT 10")
    
    assert result["success"] is True
    assert len(result["data"]) <= 10
    assert "id" in result["data"][0]

def test_invalid_sql():
    """测试无效 SQL"""
    source = SQLiteDataSource("test", "test.db")
    result = source.query("INVALID SQL")
    
    assert result["success"] is False
    assert "error" in result
```

---

## 性能优化

### 1. Embedding 缓存

```python
# 启用持久化缓存
from llama_index.core import StorageContext, load_index_from_storage

# 首次创建
index = VectorStoreIndex.from_documents(documents)
index.storage_context.persist(persist_dir="./data/cache")

# 后续加载
storage_context = StorageContext.from_defaults(persist_dir="./data/cache")
index = load_index_from_storage(storage_context)
```

### 2. 查询限制

```python
# 限制返回行数
def query(self, sql: str, limit: int = 100) -> Dict:
    """添加 LIMIT 子句"""
    if "LIMIT" not in sql.upper():
        sql = f"{sql} LIMIT {limit}"
    
    return self.execute(sql)
```

### 3. 异步处理

```python
import asyncio
from typing import List

async def batch_query(queries: List[str]) -> List[Dict]:
    """批量异步查询"""
    tasks = [query_async(q) for q in queries]
    results = await asyncio.gather(*tasks)
    return results
```

---

## 调试技巧

### 1. 启用详细日志

```bash
# .env
LOG_LEVEL=DEBUG
```

### 2. 使用 IPython 调试

```python
# 在代码中插入断点
from IPython import embed
embed()  # 进入交互式调试
```

### 3. 查看 LLM 请求

```python
# 启用 LlamaIndex 调试
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("llama_index").setLevel(logging.DEBUG)
```

---

## 部署

### 本地部署

```bash
python web_ui.py
```

### Docker 部署

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "web_ui.py"]
```

```bash
docker build -t ai-data-analyst .
docker run -p 7860:7860 -v $(pwd)/data:/app/data ai-data-analyst
```

---

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

**更新日期**: 2025-12-31  
**版本**: v2.0 - 优化架构

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
