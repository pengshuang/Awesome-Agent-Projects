# 开发指南

本文档面向想要二次开发、定制或扩展 Multi-Agent 数据合成系统的开发者。

## 📚 目录

- [项目架构](#项目架构)
- [核心组件](#核心组件)
- [开发环境设置](#开发环境设置)
- [代码结构详解](#代码结构详解)
- [自定义开发](#自定义开发)
- [调试技巧](#调试技巧)
- [性能优化](#性能优化)
- [测试](#测试)
- [部署](#部署)

## 项目架构

### 技术栈

```
┌─────────────────────────────────────────┐
│         Gradio Web UI (前端界面)         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       LangGraph (工作流编排)             │
│  ┌──────────────────────────────────┐   │
│  │  StateGraph (状态图)              │   │
│  │  • propose → solve → validate    │   │
│  │  • update → continue/end         │   │
│  └──────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Agent Layer (智能体层)           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │Proposer │ │ Solver  │ │Validator│   │
│  │  Agent  │ │  Agent  │ │  Agent  │   │
│  └─────────┘ └─────────┘ └─────────┘   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      LangChain + OpenAI SDK             │
│           (LLM 调用层)                   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Pydantic (数据验证层)               │
│  • 类型检查  • 数据验证  • 序列化       │
└─────────────────────────────────────────┘
```

### 设计模式

1. **State Machine Pattern**: LangGraph 实现的状态机
2. **Strategy Pattern**: 不同任务类型的处理策略
3. **Chain of Responsibility**: Agent 之间的责任链
4. **Observer Pattern**: Web UI 对状态变化的观察

## 核心组件

### 1. Models (src/models.py)

定义所有数据结构，使用 Pydantic 进行验证。

**核心模型：**

```python
# 任务类型枚举
class TaskType(str, Enum):
    LOGICAL_REASONING = "逻辑推理类"
    NUMERICAL_CALCULATION = "数值计算类"
    INFORMATION_QUERY = "信息查询类"
    SUMMARIZATION = "总结摘要类"

# 问答对
class QAPair(BaseModel):
    question: str
    answer: str
    reasoning: Optional[str]
    task_type: TaskType
    iteration: int
    timestamp: datetime

# LangGraph 状态
class SynthesisState(BaseModel):
    document: str
    task_type: TaskType
    max_iterations: int
    current_iteration: int
    history_buffer: List[QAPair]
    valid_pairs: List[QAPair]
    # ... 其他状态字段
```

**扩展建议：**
- 添加新的任务类型：在 `TaskType` 枚举中添加
- 扩展 QAPair：添加更多元数据（难度评分、主题标签等）

### 2. Agents (src/agents.py)

实现三个核心 Agent。

**Agent 基本结构：**

```python
class ProposerAgent:
    def __init__(self):
        self.llm = get_llm(model_name=settings.proposer_model)
    
    def generate_qa_pair(self, document, task_type, history_buffer):
        # 1. 构建 Prompt
        # 2. 调用 LLM
        # 3. 解析输出
        # 4. 返回结构化结果
        pass
```

**关键实现细节：**

1. **Prompt 构建**：根据是否有历史选择不同模板
2. **JSON 解析**：容错处理，支持带 markdown 标记的 JSON
3. **错误处理**：捕获并记录所有异常
4. **日志记录**：使用 loguru 详细记录每步操作

**自定义 Agent：**

```python
class CustomAgent:
    """自定义智能体示例"""
    
    def __init__(self):
        self.llm = get_llm(model_name="gpt-4")
    
    def process(self, input_data):
        # 实现你的逻辑
        messages = [
            SystemMessage(content="系统提示"),
            HumanMessage(content=f"用户输入: {input_data}")
        ]
        response = self.llm.invoke(messages)
        return self._parse_response(response.content)
    
    def _parse_response(self, content):
        # 解析响应
        pass
```

### 3. Graph (src/graph.py)

使用 LangGraph 编排 Agent 工作流。

**关键概念：**

```python
# 1. 定义节点函数
def _propose_node(self, state: dict) -> dict:
    """提议者节点：生成新问题"""
    output = self.proposer.generate_qa_pair(...)
    state["current_question"] = output.question
    return state

# 2. 构建状态图
workflow = StateGraph(dict)
workflow.add_node("propose", self._propose_node)
workflow.add_node("solve", self._solve_node)
workflow.add_node("validate", self._validate_node)

# 3. 添加边（控制流）
workflow.add_edge("propose", "solve")
workflow.add_conditional_edges(
    "update",
    self._should_continue,
    {"continue": "propose", "end": END}
)

# 4. 编译并运行
graph = workflow.compile()
final_state = graph.invoke(initial_state)
```

**状态流转：**

```
START → propose → solve → validate → update
          ↑                            │
          └────────── continue ─────────┘
                         or
                        END
```

### 4. Configuration (config/)

统一管理所有配置。

**结构：**

```
config/
├── settings.py      # 环境变量和系统设置
├── llm_config.py    # LLM 实例化
└── prompts.py       # Prompt 模板
```

**添加新配置：**

```python
# config/settings.py
class Settings(BaseSettings):
    # 添加新配置项
    new_feature_enabled: bool = False
    new_feature_param: str = "default"
```

### 5. Web UI (web_ui.py)

Gradio 界面实现。

**核心函数：**

```python
def synthesis_workflow(document_text, uploaded_file, task_type, max_iterations):
    """主工作流函数"""
    # 1. 输入验证
    # 2. 创建状态
    # 3. 运行 Graph
    # 4. 格式化结果
    # 5. 返回展示数据
    pass

def create_ui():
    """创建 Gradio 界面"""
    with gr.Blocks() as app:
        # 定义组件
        # 绑定事件
        pass
    return app
```

## 开发环境设置

### 1. 克隆项目

```bash
git clone <repository-url>
cd data-synthesis-system
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
# 安装生产依赖
pip install -r requirements.txt

# 如果需要开发工具
pip install black flake8 pytest ipython
```

### 4. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件，配置 API Key
```

### 5. 初始化系统

```bash
python init_system.py
```

## 代码结构详解

### 目录说明

```
data-synthesis-system/
│
├── config/                    # 配置模块
│   ├── __init__.py           # 导出配置
│   ├── settings.py           # 系统设置（Pydantic Settings）
│   ├── llm_config.py         # LLM 实例化函数
│   └── prompts.py            # 所有 Prompt 模板
│
├── src/                      # 核心源码
│   ├── __init__.py           # 导出核心类
│   ├── models.py             # Pydantic 数据模型
│   ├── agents.py             # Agent 实现
│   ├── graph.py              # LangGraph 工作流
│   └── utils.py              # 工具函数
│
├── data/                     # 数据目录
│   ├── uploads/              # 用户上传的文档
│   └── outputs/              # 生成的问答对
│
├── logs/                     # 日志文件
│
├── docs/                     # 文档
│   ├── USER_GUIDE.md         # 用户指南
│   └── DEVELOPER_GUIDE.md    # 本文档
│
├── web_ui.py                 # Gradio Web UI 入口
├── init_system.py            # 系统初始化脚本
├── start.sh                  # 启动脚本
├── requirements.txt          # 依赖列表
├── .env.example              # 环境变量模板
├── .gitignore                # Git 忽略文件
├── README.md                 # 项目说明
└── LICENSE                   # 许可证
```

### 依赖关系

```
web_ui.py
  ↓
src/graph.py
  ↓
src/agents.py
  ↓
config/llm_config.py + config/prompts.py
  ↓
config/settings.py
```

## 自定义开发

### 1. 添加新的任务类型

**步骤：**

1. 在 `src/models.py` 中添加枚举值：

```python
class TaskType(str, Enum):
    LOGICAL_REASONING = "逻辑推理类"
    NUMERICAL_CALCULATION = "数值计算类"
    INFORMATION_QUERY = "信息查询类"
    SUMMARIZATION = "总结摘要类"
    CODE_GENERATION = "代码生成类"  # 新增
```

2. 在 `config/prompts.py` 中添加对应的 Prompt（如果需要特殊处理）：

```python
PROMPTS = {
    "proposer": {
        "system": """
        ...
        任务类型说明：
        ...
        - 代码生成类：需要根据需求生成代码片段
        """
    }
}
```

3. 更新 UI（`web_ui.py`）中的任务类型选择：

```python
task_type = gr.Radio(
    choices=[t.value for t in TaskType],  # 自动包含新类型
    label="任务类型",
    value=TaskType.LOGICAL_REASONING.value,
)
```

### 2. 自定义 Agent

**场景：**添加一个"难度评估器"Agent，评估生成问题的难度。

```python
# src/agents.py

class DifficultyEvaluatorAgent:
    """评估问题难度的 Agent"""
    
    def __init__(self):
        self.llm = get_llm(model_name=settings.validator_model)
        logger.info("DifficultyEvaluatorAgent initialized")
    
    def evaluate(self, question: str, answer: str) -> dict:
        """
        评估问题难度
        
        Returns:
            {
                "difficulty_score": 1-10,
                "reasoning": "评估理由"
            }
        """
        prompt = f"""
评估以下问题的难度（1-10分）：

问题：{question}
答案：{answer}

考虑因素：
1. 需要的推理步骤数
2. 涉及的知识点数量
3. 答案的复杂度

输出格式（JSON）：
{{
    "difficulty_score": 7,
    "reasoning": "评估理由"
}}
"""
        
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        
        # 解析响应
        content = self._clean_json(response.content)
        result = json.loads(content)
        
        return result
    
    def _clean_json(self, content: str) -> str:
        """清理 JSON 响应"""
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()
```

**集成到 Graph：**

```python
# src/graph.py

class DataSynthesisGraph:
    def __init__(self):
        self.proposer = ProposerAgent()
        self.solver = SolverAgent()
        self.validator = ValidatorAgent()
        self.difficulty_evaluator = DifficultyEvaluatorAgent()  # 新增
    
    def _build_graph(self):
        workflow = StateGraph(dict)
        
        workflow.add_node("propose", self._propose_node)
        workflow.add_node("solve", self._solve_node)
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("evaluate_difficulty", self._evaluate_difficulty_node)  # 新增
        workflow.add_node("update", self._update_node)
        
        # 添加新的边
        workflow.add_edge("validate", "evaluate_difficulty")
        workflow.add_edge("evaluate_difficulty", "update")
        
        # ... 其余配置
    
    def _evaluate_difficulty_node(self, state: dict) -> dict:
        """难度评估节点"""
        if state.get("validation_passed"):
            result = self.difficulty_evaluator.evaluate(
                question=state["current_question"],
                answer=state["current_reference_answer"]
            )
            state["current_difficulty"] = result["difficulty_score"]
        return state
```

### 3. 自定义 Prompt

**最佳实践：**

```python
# config/prompts.py

PROMPTS = {
    "proposer": {
        "system": """你是一个专业的问题提议者。

核心能力：
1. 深度理解文档内容
2. 生成有挑战性的问题
3. 确保答案可从文档推导

生成原则：
{principles}
""",
        "principles": """
- 问题要有深度，避免简单事实查询
- 答案要准确完整
- 如果有历史，生成更难的问题
""",
        "user_first": "...",
        "user_iterative": "...",
    }
}

# 使用时可以动态插值
def build_prompt(template_name, **kwargs):
    template = PROMPTS["proposer"][template_name]
    return template.format(**kwargs)
```

**Prompt 调优技巧：**

1. **结构化输出**：明确指定输出格式（JSON、XML等）
2. **Few-shot Learning**：提供示例
3. **思维链（CoT）**：要求展示推理过程
4. **约束条件**：明确限制和要求

### 4. 扩展数据模型

**场景：**为问答对添加主题标签。

```python
# src/models.py

class QAPair(BaseModel):
    question: str
    answer: str
    reasoning: Optional[str]
    task_type: TaskType
    iteration: int
    timestamp: datetime
    
    # 新增字段
    topics: List[str] = Field(default_factory=list, description="主题标签")
    difficulty: Optional[int] = Field(None, ge=1, le=10, description="难度评分")
    
    @validator('topics')
    def validate_topics(cls, v):
        """验证主题标签"""
        if len(v) > 5:
            raise ValueError("最多5个主题标签")
        return v
```

### 5. 添加新的输出格式

**场景：**支持导出为 CSV 格式。

```python
# src/utils.py

import csv

def save_qa_pairs_csv(qa_pairs: List[dict], task_type: str) -> str:
    """保存为 CSV 格式"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"qa_pairs_{task_type}_{timestamp}.csv"
    filepath = Path(settings.output_dir) / filename
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        if qa_pairs:
            writer = csv.DictWriter(f, fieldnames=qa_pairs[0].keys())
            writer.writeheader()
            writer.writerows(qa_pairs)
    
    logger.info("Saved {} QA pairs to CSV: {}", len(qa_pairs), filepath)
    return str(filepath)
```

## 调试技巧

### 1. 日志系统

**查看实时日志：**

```bash
# 实时查看最新日志
tail -f logs/system_*.log
```

**日志级别：**

```python
# 临时提高日志级别
logger.add(sys.stderr, level="DEBUG")

# 针对特定模块
logger.debug("Detailed info: {}", data)
logger.info("Normal operation")
logger.warning("Warning message")
logger.error("Error occurred")
```

### 2. 单元测试

**测试 Agent：**

```python
# tests/test_agents.py

import pytest
from src.agents import ProposerAgent
from src.models import TaskType

def test_proposer_agent():
    """测试提议者 Agent"""
    agent = ProposerAgent()
    
    output = agent.generate_qa_pair(
        document="测试文档内容...",
        task_type=TaskType.LOGICAL_REASONING,
        history_buffer=[]
    )
    
    assert output.question
    assert output.answer
    assert len(output.question) > 10
```

**运行测试：**

```bash
pytest tests/ -v
```

### 3. 交互式调试

**使用 IPython：**

```python
# 在代码中插入
import IPython; IPython.embed()

# 或使用 pdb
import pdb; pdb.set_trace()
```

**调试 LangGraph：**

```python
# 逐步运行
graph = DataSynthesisGraph()
state = initial_state

# 手动执行每个节点
state = graph._propose_node(state)
print(state["current_question"])

state = graph._solve_node(state)
print(state["current_solver_answer"])
```

### 4. Mock LLM 调用

**加速测试：**

```python
from unittest.mock import Mock, patch

@patch('src.agents.get_llm')
def test_with_mock_llm(mock_get_llm):
    """使用 Mock LLM 测试"""
    mock_llm = Mock()
    mock_llm.invoke.return_value.content = '{"question": "test", "answer": "test"}'
    mock_get_llm.return_value = mock_llm
    
    agent = ProposerAgent()
    output = agent.generate_qa_pair(...)
    
    assert output.question == "test"
```

## 性能优化

### 1. 并行处理

**问题：**串行处理多个文档很慢

**解决：**使用异步或多进程

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

async def process_document_async(document):
    """异步处理单个文档"""
    # 实现异步调用
    pass

async def process_multiple_documents(documents):
    """并行处理多个文档"""
    tasks = [process_document_async(doc) for doc in documents]
    results = await asyncio.gather(*tasks)
    return results
```

### 2. 缓存机制

**场景：**相同文档重复处理

```python
from functools import lru_cache
import hashlib

def get_document_hash(document: str) -> str:
    """计算文档哈希"""
    return hashlib.md5(document.encode()).hexdigest()

@lru_cache(maxsize=100)
def cached_synthesis(document_hash: str, task_type: str):
    """缓存合成结果"""
    # 实现缓存逻辑
    pass
```

### 3. 批量调用

**优化 LLM 调用：**

```python
# 批量生成多个问题
def generate_batch_qa_pairs(documents: List[str]):
    """批量生成"""
    # 使用 LLM 的批量接口（如果支持）
    pass
```

### 4. 数据库存储

**替代文件存储：**

```python
# 使用 SQLite 或 PostgreSQL
import sqlite3

def init_database():
    conn = sqlite3.connect('data/qa_pairs.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS qa_pairs (
            id INTEGER PRIMARY KEY,
            question TEXT,
            answer TEXT,
            task_type TEXT,
            created_at TIMESTAMP
        )
    ''')
    return conn

def save_to_database(qa_pairs):
    conn = init_database()
    cursor = conn.cursor()
    for qa in qa_pairs:
        cursor.execute(
            'INSERT INTO qa_pairs (question, answer, task_type, created_at) VALUES (?, ?, ?, ?)',
            (qa['question'], qa['answer'], qa['task_type'], qa['timestamp'])
        )
    conn.commit()
```

## 测试

### 单元测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_agents.py::test_proposer_agent

# 显示覆盖率
pytest --cov=src tests/
```

### 集成测试

```python
# tests/test_integration.py

def test_full_workflow():
    """测试完整工作流"""
    graph = DataSynthesisGraph()
    
    state = {
        "document": "测试文档...",
        "task_type": "逻辑推理类",
        "max_iterations": 3,
    }
    
    final_state = graph.run(state)
    
    assert len(final_state["valid_pairs"]) > 0
    assert final_state["is_complete"]
```

## 部署

### Docker 部署

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "web_ui.py"]
```

```bash
# 构建
docker build -t data-synthesis-system .

# 运行
docker run -p 7860:7860 --env-file .env data-synthesis-system
```

### 生产环境配置

```python
# config/settings.py

class Settings(BaseSettings):
    # 生产环境配置
    environment: str = "development"  # development, production
    
    @property
    def is_production(self):
        return self.environment == "production"
    
    # 根据环境调整参数
    @property
    def log_level(self):
        return "INFO" if self.is_production else "DEBUG"
```

## 最佳实践

### 1. 代码风格

使用 Black 格式化：

```bash
black src/ config/ web_ui.py
```

### 2. 类型注解

```python
from typing import List, Dict, Optional

def process_data(
    items: List[str],
    config: Dict[str, Any],
    max_count: Optional[int] = None
) -> List[Dict[str, str]]:
    """完整的类型注解"""
    pass
```

### 3. 错误处理

```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error("Operation failed: {}", str(e))
    # 处理或重抛
    raise
finally:
    cleanup()
```

### 4. 文档字符串

```python
def complex_function(param1: str, param2: int) -> dict:
    """
    函数的简短描述。
    
    详细描述函数的功能、用途和注意事项。
    
    Args:
        param1: 参数1的说明
        param2: 参数2的说明
    
    Returns:
        返回值的说明
    
    Raises:
        ValueError: 什么情况下抛出
    
    Examples:
        >>> complex_function("test", 42)
        {"result": "success"}
    """
    pass
```

## 贡献指南

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交改动：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

## 常见开发问题

### Q: 如何添加新的 LLM 提供商？

修改 `config/llm_config.py`：

```python
def get_llm(model_name: str = None) -> BaseChatModel:
    provider = settings.llm_provider  # 新增配置
    
    if provider == "openai":
        return ChatOpenAI(...)
    elif provider == "anthropic":
        return ChatAnthropic(...)
    # 添加更多提供商
```

### Q: 如何修改状态图的流程？

编辑 `src/graph.py` 的 `_build_graph` 方法，添加/删除节点和边。

### Q: 如何自定义 Web UI？

修改 `web_ui.py` 的 `create_ui` 函数，Gradio 支持丰富的组件。

## 资源链接

- [LangChain 文档](https://python.langchain.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [Gradio 文档](https://www.gradio.app/docs/)

---

祝开发顺利！如有问题，欢迎提交 Issue。
