# 开发指南

> 面向希望进行二次开发的开发者

---

## 📁 项目结构

```
ai-data-analyst/
├── config/                  # 配置模块
│   ├── settings.py         # 系统配置
│   ├── llm_config.py       # LLM 配置
│   └── prompts.py          # Prompt 模板管理
├── src/
│   ├── agent.py            # 核心 Agent
│   ├── datasources/        # 数据源适配器
│   │   ├── base.py        # 数据源基类
│   │   ├── sqlite_source.py
│   │   ├── file_source.py
│   │   ├── knowledge_base.py
│   │   └── web_source.py
│   ├── analyzers/          # 分析引擎
│   │   └── data_analyzer.py
│   ├── tools/              # 工具模块
│   │   └── nl2sql.py
│   └── utils/              # 工具函数
│       ├── logger.py
│       └── helpers.py
├── data/                    # 数据目录
├── logs/                    # 日志目录
├── web_ui.py               # Web 界面
└── init_system.py          # 系统初始化
```

---

## 🏗️ 核心架构

### 模块关系

```
Web UI (Gradio)
    ↓
DataAnalystAgent (Agent)
    ↓
DataAnalyzer (分析引擎)
    ↓
DataSource (数据源接口)
    ├── SQLiteDataSource
    ├── FileDataSource
    ├── KnowledgeBaseSource
    └── WebSearchSource
```

### 核心类说明

#### 1. DataAnalystAgent (`src/agent.py`)

**职责**: 核心对话代理，管理多轮对话和数据源

**关键方法**:
```python
class DataAnalystAgent:
    def __init__(self, max_history_turns: int = 10)
    def register_sqlite_database(self, name: str, db_path: str) -> bool
    def register_file(self, name: str, file_path: str) -> bool
    def chat(self, message: str, source_name: Optional[str] = None) -> str
    def clear_history()
```

#### 2. DataSource (`src/datasources/base.py`)

**职责**: 数据源基类，定义统一接口

**接口定义**:
```python
class DataSource(ABC):
    @abstractmethod
    def connect(self) -> bool
    
    @abstractmethod
    def query(self, query: str, **kwargs) -> Dict[str, Any]
    
    @abstractmethod
    def get_schema(self) -> Optional[str]
    
    @abstractmethod
    def close()
```

#### 3. DataAnalyzer (`src/analyzers/data_analyzer.py`)

**职责**: 数据分析引擎

**关键方法**:
```python
class DataAnalyzer:
    def analyze_single_source(self, question: str, source_name: str) -> Dict
    def analyze_multi_sources(self, question: str, source_names: List[str]) -> Dict
```

#### 4. PromptTemplates (`config/prompts.py`)

**职责**: 统一管理所有 LLM Prompt

**模板分类**:
- `SYSTEM_DEFAULT` - 系统提示词
- `NL2SQL_TEMPLATE` - SQL 生成
- `DATA_ANALYSIS_TEMPLATE` - 数据分析
- `MULTI_SOURCE_ANALYSIS` - 多源分析

---

## 🔧 二次开发

### 添加新数据源

#### 步骤 1: 创建数据源类

在 `src/datasources/` 创建新文件：

```python
# src/datasources/my_source.py
from .base import DataSource
from typing import Any, Dict, Optional
from loguru import logger

class MyDataSource(DataSource):
    """自定义数据源"""
    
    def __init__(self, name: str, connection_params: Dict):
        super().__init__(name, "my_custom_type")
        self.params = connection_params
        self.connection = None
    
    def connect(self) -> bool:
        """建立连接"""
        try:
            # 实现连接逻辑
            self.connection = establish_connection(self.params)
            logger.info(f"✅ 已连接到 {self.name}")
            return True
        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            return False
    
    def query(self, query: str, **kwargs) -> Dict[str, Any]:
        """执行查询"""
        try:
            result = self.connection.execute(query)
            return {
                "success": True,
                "data": result,
                "error": None,
                "metadata": {"row_count": len(result)}
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "metadata": {}
            }
    
    def get_schema(self) -> Optional[str]:
        """返回数据结构描述"""
        return "字段1: 类型\n字段2: 类型..."
    
    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()
```

#### 步骤 2: 在 Agent 中添加注册方法

```python
# src/agent.py
def register_my_datasource(self, name: str, **params) -> bool:
    """注册自定义数据源"""
    try:
        source = MyDataSource(name, params)
        if source.connect():
            self.analyzer.register_data_source(name, source)
            return True
        return False
    except Exception as e:
        logger.error(f"注册失败: {e}")
        return False
```

#### 步骤 3: 在 Web UI 中添加界面

```python
# web_ui.py
def register_my_source(name: str, param1: str, param2: str):
    """Web UI 回调"""
    if not INITIALIZED:
        return "❌ 请先初始化系统"
    
    success = AGENT.register_my_datasource(
        name=name,
        param1=param1,
        param2=param2
    )
    
    if success:
        return f"## ✅ 注册成功\n\n数据源名称: {name}"
    else:
        return "❌ 注册失败"

# 添加 Gradio 组件
with gr.Column():
    gr.Markdown("### 自定义数据源")
    my_name = gr.Textbox(label="名称")
    my_param1 = gr.Textbox(label="参数1")
    my_param2 = gr.Textbox(label="参数2")
    my_register_btn = gr.Button("➕ 注册")
    my_result = gr.Markdown()

my_register_btn.click(
    fn=register_my_source,
    inputs=[my_name, my_param1, my_param2],
    outputs=my_result
)
```

### 自定义 Prompt 模板

#### 添加新模板

```python
# config/prompts.py
class PromptTemplates:
    # 添加自定义模板
    MY_CUSTOM_TEMPLATE = """你是一个专业的{domain}分析师。

任务：{task}

数据：
{data}

要求：
1. {requirement1}
2. {requirement2}

输出："""

class PromptBuilder:
    @staticmethod
    def build_my_custom_prompt(domain: str, task: str, 
                                data: str, **kwargs) -> str:
        """构建自定义 Prompt"""
        return PromptTemplates.MY_CUSTOM_TEMPLATE.format(
            domain=domain,
            task=task,
            data=data,
            requirement1=kwargs.get("req1", ""),
            requirement2=kwargs.get("req2", "")
        )
```

#### 使用自定义模板

```python
# 在分析引擎或 Agent 中使用
from config.prompts import PromptBuilder

prompt = PromptBuilder.build_my_custom_prompt(
    domain="金融",
    task="分析股票趋势",
    data=stock_data,
    req1="识别关键转折点",
    req2="提供投资建议"
)

response = self.llm.complete(prompt)
```

### 扩展分析功能

#### 添加自定义分析器

```python
# src/analyzers/custom_analyzer.py
from typing import Dict, Any
from loguru import logger

class CustomAnalyzer:
    """自定义分析器"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def analyze(self, data: Any, question: str) -> Dict[str, Any]:
        """执行自定义分析"""
        try:
            # 构建 Prompt
            prompt = self._build_prompt(data, question)
            
            # 调用 LLM
            response = self.llm.complete(prompt)
            
            return {
                "success": True,
                "result": response.text,
                "insights": self._extract_insights(response.text)
            }
        except Exception as e:
            logger.error(f"分析失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _build_prompt(self, data, question):
        """构建分析 Prompt"""
        return f"数据: {data}\n\n问题: {question}\n\n分析:"
    
    def _extract_insights(self, text):
        """提取关键洞察"""
        # 实现提取逻辑
        return []
```

#### 集成到系统

```python
# src/agent.py
from src.analyzers.custom_analyzer import CustomAnalyzer

class DataAnalystAgent:
    def __init__(self, max_history_turns: int = 10):
        # ... 现有代码
        self.custom_analyzer = CustomAnalyzer(self.llm)
    
    def custom_analysis(self, data: Any, question: str) -> str:
        """执行自定义分析"""
        result = self.custom_analyzer.analyze(data, question)
        if result["success"]:
            return result["result"]
        else:
            return f"分析失败: {result['error']}"
```

---

## 🧪 测试

### 单元测试示例

```python
# tests/test_my_source.py
import pytest
from src.datasources.my_source import MyDataSource

def test_my_source_connect():
    """测试连接"""
    source = MyDataSource("test", {"host": "localhost"})
    assert source.connect() == True

def test_my_source_query():
    """测试查询"""
    source = MyDataSource("test", {"host": "localhost"})
    source.connect()
    result = source.query("SELECT * FROM table")
    assert result["success"] == True
    assert result["data"] is not None
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_my_source.py

# 带覆盖率报告
pytest --cov=src tests/
```

---

## 📊 日志和调试

### 日志系统

所有 LLM 调用自动记录：

```python
# 日志位置
logs/ai_data_analyst_YYYY-MM-DD.log

# 日志内容
2024-12-21 10:00:00 | INFO | Prompt: [完整的 Prompt]
2024-12-21 10:00:05 | INFO | Response: [LLM 响应]
```

### 添加自定义日志

```python
from loguru import logger

# 不同级别的日志
logger.debug("调试信息")
logger.info("常规信息")
logger.warning("警告信息")
logger.error("错误信息")

# 带上下文的日志
logger.info(f"处理请求: {request_id}", extra={"user": user_id})
```

---

## 🚀 部署

### 生产环境配置

```bash
# .env.production
LLM_API_KEY=your-production-key
MAX_HISTORY_TURNS=5
LOG_LEVEL=INFO
```

### Docker 部署（可选）

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

CMD ["python", "web_ui.py"]
```

```bash
# 构建和运行
docker build -t ai-data-analyst .
docker run -p 7860:7860 --env-file .env ai-data-analyst
```

---

## 📚 API 参考

### DataSource 接口

```python
def connect() -> bool
    """建立连接，返回是否成功"""

def query(query: str, **kwargs) -> Dict[str, Any]
    """执行查询，返回标准格式结果"""
    # 返回: {"success": bool, "data": Any, "error": str, "metadata": dict}

def get_schema() -> Optional[str]
    """获取数据结构描述"""

def close()
    """关闭连接，释放资源"""
```

### Agent 接口

```python
def chat(message: str, source_name: Optional[str] = None) -> str
    """处理用户消息，返回回复"""

def clear_history()
    """清空对话历史"""

def list_data_sources() -> Dict[str, Any]
    """列出所有数据源"""
```

---

## 🔗 相关资源

- [📖 功能介绍](FEATURES.md) - 了解所有功能
- [👤 用户指南](USER_GUIDE.md) - 使用教程
- [LlamaIndex 文档](https://docs.llamaindex.ai/) - LLM 框架
- [Gradio 文档](https://www.gradio.app/docs/) - UI 框架

---

## 💡 最佳实践

### 代码规范

- 使用类型注解
- 添加文档字符串
- 遵循 PEP 8
- 错误处理完整

### Prompt 设计

- 明确任务目标
- 提供示例
- 分步骤指导
- 输出格式化

### 性能优化

- 缓存常用查询
- 异步处理IO
- 限制LLM调用
- 数据分批处理

---

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交代码
4. 编写测试
5. 提交 Pull Request

欢迎贡献！
- 单数据源分析
- 多数据源融合分析
- 调用 LLM 生成分析结果

**关键方法**：
```python
class DataAnalyzer:
    def analyze_single_source(self, question: str, source_name: str, **kwargs) -> Dict[str, Any]
    def analyze_multi_sources(self, question: str, source_names: List[str], **kwargs) -> Dict[str, Any]
```

#### 4. NL2SQL 工具（`src/tools/nl2sql.py`）

`NL2SQLConverter` 负责自然语言到 SQL 的转换：

```python
class NL2SQLConverter:
    def convert(self, question: str, database_schema: str, dialect: str = "sqlite", chat_history: Optional[str] = None) -> Dict[str, Any]
    def correct_sql(self, sql: str, error: str, database_schema: str, dialect: str = "sqlite") -> Dict[str, Any]
```

#### 5. Prompt 管理（`config/prompts.py`）

所有 Prompt 模板集中管理：

```python
class PromptTemplates:
    SYSTEM_DEFAULT = "..."
    NL2SQL_TEMPLATE = "..."
    DATA_ANALYSIS_TEMPLATE = "..."
    # ... 更多模板

class PromptBuilder:
    @staticmethod
    def build_nl2sql_prompt(...)
    @staticmethod
    def build_data_analysis_prompt(...)
    @staticmethod
    def build_multi_source_prompt(...)
```

## 二次开发指南

### 添加新的数据源

#### 步骤 1：创建数据源类

在 `src/datasources/` 目录下创建新文件：

```python
from .base import DataSource
from typing import Any, Dict, Optional

class MyDataSource(DataSource):
    """自定义数据源"""
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name, "my_type")
        # 初始化参数
    
    def connect(self) -> bool:
        """连接数据源"""
        try:
            # 实现连接逻辑
            return True
        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False
    
    def query(self, query: str, **kwargs) -> Dict[str, Any]:
        """查询数据"""
        try:
            # 实现查询逻辑
            return {
                "success": True,
                "data": ...,
                "error": None,
                "metadata": {}
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "metadata": {}
            }
    
    def get_schema(self) -> Optional[str]:
        """获取schema"""
        # 返回数据源的结构描述
        return "数据源结构信息"
    
    def close(self):
        """关闭连接"""
        pass
```

#### 步骤 2：注册到 Agent

在 `src/agent.py` 中添加注册方法：

```python
def register_my_datasource(self, name: str, **kwargs) -> bool:
    """注册自定义数据源"""
    try:
        my_source = MyDataSource(name, **kwargs)
        if my_source.connect():
            self.analyzer.register_data_source(name, my_source)
            return True
        return False
    except Exception as e:
        logger.error(f"注册失败: {e}")
        return False
```

#### 步骤 3：添加到分析器

在 `src/analyzers/data_analyzer.py` 的 `analyze_single_source` 方法中添加处理逻辑：

```python
def analyze_single_source(self, question: str, source_name: str, **kwargs):
    data_source = self.data_sources[source_name]
    
    if isinstance(data_source, MyDataSource):
        return self._analyze_my_datasource(question, data_source, **kwargs)
    # ... 其他类型
```

#### 步骤 4：更新 UI

在 `web_ui.py` 中添加注册界面和按钮。

### 自定义 Prompt

#### 修改现有 Prompt

编辑 `config/prompts.py`：

```python
class PromptTemplates:
    # 修改现有模板
    NL2SQL_TEMPLATE = """
    你的自定义 Prompt...
    
    数据库信息：
    {database_schema}
    
    用户问题：{question}
    """
```

#### 添加新 Prompt

```python
class PromptTemplates:
    # 添加新模板
    MY_CUSTOM_TEMPLATE = """
    你的自定义任务 Prompt...
    
    输入：{input}
    要求：{requirements}
    """

class PromptBuilder:
    @staticmethod
    def build_my_custom_prompt(input_data: str, requirements: str) -> str:
        return PromptTemplates.MY_CUSTOM_TEMPLATE.format(
            input=input_data,
            requirements=requirements,
        )
```

### 扩展分析功能

#### 添加新的分析类型

在 `src/analyzers/` 创建新分析器：

```python
class CustomAnalyzer:
    """自定义分析器"""
    
    def __init__(self):
        self.llm = get_llm()
    
    def analyze(self, data: Any, question: str) -> Dict[str, Any]:
        """执行分析"""
        # 构建 Prompt
        prompt = self._build_prompt(data, question)
        
        # 记录日志
        logger.info("=" * 70)
        logger.info("📝 [LLM调用] 自定义分析")
        logger.info("=" * 70)
        logger.info(f"输入Prompt:\n{prompt}")
        logger.info("=" * 70)
        
        # 调用 LLM
        response = self.llm.complete(prompt)
        answer = str(response)
        
        logger.info(f"LLM响应:\n{answer}")
        logger.info("=" * 70)
        
        return {
            "success": True,
            "answer": answer,
            "error": None,
        }
```

### 自定义 UI 组件

修改 `web_ui.py` 添加新的界面元素：

```python
def create_ui():
    with gr.Blocks(...) as demo:
        # 添加新的 Tab
        with gr.Tab("🆕 新功能"):
            gr.Markdown("### 自定义功能")
            
            # 添加输入组件
            input_field = gr.Textbox(label="输入")
            output_field = gr.Markdown()
            
            # 添加按钮
            submit_btn = gr.Button("提交")
            
            # 绑定事件
            submit_btn.click(
                fn=your_function,
                inputs=input_field,
                outputs=output_field
            )
```

### 集成新的 LLM

#### 方式 1：OpenAI 兼容 API

如果新 LLM 兼容 OpenAI API 格式，只需配置 `.env`：

```bash
LLM_API_KEY=your-key
LLM_API_BASE=https://your-llm-endpoint/v1
LLM_MODEL=your-model-name
```

#### 方式 2：自定义 LLM 类

在 `config/llm_config.py` 中添加：

```python
def get_llm(...):
    provider = os.getenv("LLM_PROVIDER", "openai")
    
    if provider == "my_llm":
        from llama_index.llms.my_llm import MyLLM
        return MyLLM(
            api_key=api_key,
            model=model,
            # ... 其他参数
        )
```

## 调试技巧

### 1. 查看日志

所有 LLM 调用都会记录 Prompt 和响应：

```bash
tail -f logs/ai_data_analyst_$(date +%Y-%m-%d).log
```

### 2. 断点调试

使用 Python 调试器：

```python
import pdb; pdb.set_trace()
```

或使用 IDE 的调试功能。

### 3. 测试单个模块

创建测试脚本：

```python
from src.datasources import SQLiteDataSource

# 测试数据源
db = SQLiteDataSource("test", "data/databases/test.db")
db.connect()
result = db.query("SELECT * FROM users LIMIT 10")
print(result)
```

### 4. Prompt 优化

1. 查看日志中的 Prompt
2. 复制到 LLM playground 测试
3. 调整 Prompt 模板
4. 重新测试

## 性能优化

### 1. 缓存机制

实现查询结果缓存：

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(query: str) -> Dict:
    # 执行查询
    pass
```

### 2. 并发处理

使用异步或多线程处理多个请求：

```python
import asyncio

async def process_multiple_queries(queries: List[str]):
    tasks = [process_query(q) for q in queries]
    return await asyncio.gather(*tasks)
```

### 3. 数据库优化

- 为常用查询字段添加索引
- 使用查询计划分析
- 限制返回数据量

### 4. LLM 调用优化

- 使用更快的模型
- 批处理相似请求
- 实现请求去重

## 测试

### 单元测试

创建 `tests/` 目录并添加测试：

```python
import unittest
from src.datasources import SQLiteDataSource

class TestSQLiteDataSource(unittest.TestCase):
    def setUp(self):
        self.db = SQLiteDataSource("test", ":memory:")
        self.db.connect()
    
    def test_query(self):
        result = self.db.query("SELECT 1")
        self.assertTrue(result["success"])
    
    def tearDown(self):
        self.db.close()
```

运行测试：

```bash
python -m unittest discover tests/
```

### 集成测试

测试完整流程：

```python
def test_full_workflow():
    # 初始化 Agent
    agent = DataAnalystAgent()
    
    # 注册数据源
    agent.register_sqlite_database("test", "test.db")
    
    # 执行查询
    result = agent.chat("查询所有用户", source_name="test")
    
    # 验证结果
    assert "SQL" in result or "数据" in result
```

## 部署

### Docker 部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "web_ui.py"]
```

构建和运行：

```bash
docker build -t ai-data-analyst .
docker run -p 7860:7860 ai-data-analyst
```

### 生产环境配置

1. 使用 Gunicorn 或 uWSGI
2. 配置反向代理（Nginx）
3. 设置环境变量
4. 启用 HTTPS
5. 配置日志轮转
6. 监控和告警

## 贡献指南

### 提交代码

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8
- 添加类型注解
- 编写文档字符串
- 添加必要的注释
- 编写单元测试

### 文档更新

修改功能后同步更新：
- README.md
- FEATURES.md
- USER_GUIDE.md
- DEVELOPER_GUIDE.md

## 常见问题

### Q: 如何支持新的 SQL 方言？

修改 `src/tools/nl2sql.py`，添加方言特定的处理逻辑。

### Q: 如何优化大数据集的处理？

1. 实现分页查询
2. 添加数据采样
3. 使用流式处理
4. 优化 SQL 查询

### Q: 如何添加用户认证？

在 `web_ui.py` 中集成 Gradio 的认证功能：

```python
demo.launch(auth=("username", "password"))
```

## 参考资源

- [LlamaIndex 文档](https://docs.llamaindex.ai/)
- [Gradio 文档](https://gradio.app/docs/)
- [Loguru 文档](https://loguru.readthedocs.io/)
- [Pandas 文档](https://pandas.pydata.org/docs/)

## 联系方式

- GitHub Issues
- Email: [your-email]
- 文档反馈：提交 PR

---

祝开发愉快！🚀
