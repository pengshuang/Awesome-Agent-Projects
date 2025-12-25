# 开发者指南

本指南面向需要进行二次开发的开发者，包含项目结构、核心代码说明和扩展指南。

---

## 目录

- [项目结构](#项目结构)
- [技术栈](#技术栈)
- [核心模块](#核心模块)
- [扩展开发](#扩展开发)
- [调试技巧](#调试技巧)

---

## 项目结构

```
data-synthesis-system/
├── config/                      # 配置模块
│   ├── settings.py             # 系统设置（环境变量）
│   ├── llm_config.py           # LLM实例化
│   └── prompts.py              # Prompt模板
│
├── src/                        # 核心代码
│   ├── models.py               # Pydantic数据模型
│   ├── agents.py               # 三个Agent实现
│   ├── graph.py                # LangGraph工作流
│   └── utils.py                # 工具函数
│
├── data/                       # 数据目录
│   ├── uploads/                # 上传文档
│   └── outputs/                # 输出JSON
│
├── logs/                       # 日志文件
├── docs/                       # 文档
├── web_ui.py                   # Web界面入口
└── requirements.txt            # 依赖列表
```

### 核心文件说明

| 文件 | 说明 | 修改场景 |
|------|------|----------|
| `config/settings.py` | 环境变量配置 | 添加新配置项 |
| `config/prompts.py` | Prompt模板 | 优化生成质量 |
| `src/models.py` | 数据模型 | 扩展数据结构 |
| `src/agents.py` | Agent实现 | 修改Agent行为 |
| `src/graph.py` | 工作流编排 | 调整流程逻辑 |
| `web_ui.py` | Web界面 | 修改UI功能 |

---

## 技术栈

### 核心框架

- **LangGraph**: 多Agent工作流编排
- **LangChain**: LLM调用和管理
- **Pydantic**: 数据验证
- **Gradio**: Web UI

### 依赖库

```
langgraph>=0.0.30
langchain>=0.1.0
langchain-openai>=0.0.5
gradio>=4.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
loguru>=0.7.0
python-dotenv>=1.0.0
```

---

## 核心模块

### 1. 数据模型 (src/models.py)

**主要模型**：

```python
class TaskType(Enum):
    """任务类型枚举"""
    LOGICAL_REASONING = "逻辑推理类"
    NUMERICAL_CALCULATION = "数值计算类"
    INFORMATION_QUERY = "信息查询类"
    SUMMARIZATION = "总结摘要类"

class QAPair(BaseModel):
    """问答对"""
    question: str
    answer: str
    reasoning: str
    task_type: TaskType
    iteration: int
    score: float
    timestamp: datetime

class ProposerOutput(BaseModel):
    """提议者输出"""
    question: str
    answer: str
    reasoning: str

class SolverOutput(BaseModel):
    """求解者输出"""
    reasoning_steps: List[str]
    final_answer: str

class ValidatorOutput(BaseModel):
    """验证者输出（评分制）"""
    score: float  # 1-10分
    reasoning: str
    feedback: str
```

### 2. Agent实现 (src/agents.py)

**三个Agent**：

```python
class ProposerAgent:
    """提议者：生成问答对"""
    def generate_qa_pair(
        document: str,
        task_type: TaskType,
        history_buffer: List[QAPair]
    ) -> ProposerOutput

class SolverAgent:
    """求解者：尝试回答"""
    def solve(
        document: str,
        question: str
    ) -> SolverOutput

class ValidatorAgent:
    """验证者：评分1-10"""
    def validate(
        question: str,
        reference_answer: str,
        solver_answer: str
    ) -> ValidatorOutput
```

**错误处理**：
- JSON解析容错
- 返回默认值而非抛出异常
- 优雅降级机制

### 3. 工作流编排 (src/graph.py)

**LangGraph状态图**：

```python
class DataSynthesisGraph:
    """数据合成工作流"""
    
    # 四个节点
    def _propose_node(state) -> dict
    def _solve_node(state) -> dict
    def _validate_node(state) -> dict
    def _update_node(state) -> dict
    
    # 条件分支
    def _should_continue(state) -> str
    
    # 流式执行
    def stream(state_dict) -> Iterator[dict]
```

**节点流转**：
```
START → propose → solve → validate → update
         ↑                             ↓
         └────────── 循环 ──────────────┘
                                       ↓
                                      END
```

### 4. Web UI (web_ui.py)

**主要功能**：
- 文档输入（文本/文件）
- 参数配置（温度/阈值）
- Prompts编辑
- 实时监控
- 停止控制

**关键函数**：
```python
def synthesis_workflow_generator(...)
    """生成器函数，流式输出状态"""
    
def format_iteration_detail(detail, iteration)
    """格式化迭代详情，彩色区块显示"""
    
def stop_synthesis()
    """停止控制"""
```

---

## 扩展开发

### 添加新任务类型

**1. 修改模型 (src/models.py)**

```python
class TaskType(str, Enum):
    LOGICAL_REASONING = "逻辑推理类"
    # ...现有类型...
    YOUR_NEW_TYPE = "你的新类型"  # 添加这里
```

**2. 更新Prompt (config/prompts.py)**

在proposer的system prompt中添加新类型说明：

```python
任务类型说明：
- 逻辑推理类：...
- 你的新类型：特点和要求  # 添加这里
```

**3. 更新UI (web_ui.py)**

Task type选择器会自动读取TaskType枚举，无需修改。

### 添加新Agent

**1. 实现Agent类 (src/agents.py)**

```python
class YourNewAgent:
    def __init__(self):
        self.llm = get_llm(...)
    
    def your_method(self, ...):
        # 实现逻辑
        pass
```

**2. 更新工作流 (src/graph.py)**

```python
def __init__(self):
    self.your_agent = YourNewAgent()
    
def _your_node(self, state):
    output = self.your_agent.your_method(...)
    state["your_output"] = output
    return state

# 在_build_graph中添加节点
workflow.add_node("your_node", self._your_node)
workflow.add_edge("validate", "your_node")
workflow.add_edge("your_node", "update")
```

### 自定义评分标准

**修改 config/prompts.py**：

```python
"validator": {
    "system": """
    你是专业评估者，使用以下标准：
    1. 自定义标准1（权重40%）
    2. 自定义标准2（权重30%）
    ...
    """
}
```

**修改 src/graph.py**：

```python
# 可以实现自定义阈值逻辑
score_threshold = state.get("score_threshold", settings.score_threshold)
custom_threshold = calculate_custom_threshold(...)  # 自定义计算
is_valid = score >= custom_threshold
```

### 添加新配置参数

**1. 添加到 settings.py**：

```python
class Settings(BaseSettings):
    # ...现有配置...
    your_new_param: str = "default_value"
```

**2. 在 .env 中设置**：

```bash
YOUR_NEW_PARAM=your_value
```

**3. 在代码中使用**：

```python
from config import settings
value = settings.your_new_param
```

---

## 调试技巧

### 日志查看

**实时日志**：
```bash
tail -f logs/web_ui_*.log
```

**筛选错误**：
```bash
grep ERROR logs/*.log
```

**查看特定Agent**：
```bash
grep "ProposerAgent" logs/*.log
```

### 调试模式

**启用详细日志** (config/llm_config.py)：

```python
def get_llm(...):
    return ChatOpenAI(
        ...
        verbose=True,  # 添加这行
    )
```

**调试单个Agent**：

```python
from src.agents import ProposerAgent
from src.models import TaskType

agent = ProposerAgent()
output = agent.generate_qa_pair(
    document="测试文档",
    task_type=TaskType.LOGICAL_REASONING,
    history_buffer=[]
)
print(output)
```

### 测试工作流

```python
from src.graph import DataSynthesisGraph

state = {
    "document": "测试文档",
    "task_type": "逻辑推理类",
    "max_iterations": 3,
    "score_threshold": 7.0,
}

graph = DataSynthesisGraph()
result = graph.run(state)
print(f"生成{len(result['valid_pairs'])}个问答对")
```

### 常见问题排查

**1. JSON解析错误**
- 检查LLM返回格式
- 查看logs中的"Raw content"
- 调整Prompt使输出更规范

**2. 验证总是失败**
- 降低score_threshold
- 检查Validator的prompt
- 查看feedback了解失败原因

**3. 生成速度慢**
- 检查API响应时间
- 考虑使用更快的模型
- 减少max_tokens

**4. 内存占用高**
- 清理history_buffer
- 减少max_iterations
- 优化文档长度

---

## API参考

### 主要类和函数

**DataSynthesisGraph**：
```python
graph = DataSynthesisGraph()
# 流式执行
for output in graph.stream(state):
    process(output)
# 或一次性执行
result = graph.run(state)
```

**工具函数** (src/utils.py)：
```python
# 保存问答对
save_qa_pairs(qa_pairs, task_type) -> str

# 读取文档
read_document_file(file_path) -> str

# 格式化显示
format_qa_for_display(qa, index) -> str
```

---

## 贡献指南

### 代码规范

- 使用类型提示
- 添加docstring
- 遵循PEP 8
- 编写单元测试

### 提交流程

1. Fork项目
2. 创建特性分支
3. 提交代码
4. 发起Pull Request

### 测试

```bash
# 运行测试（如果有）
python -m pytest tests/

# 代码检查
flake8 src/
mypy src/
```

---

## 性能优化

### 并行处理

可以修改为并行生成：

```python
import asyncio
from langchain.callbacks import get_openai_callback

async def parallel_generation():
    tasks = [
        agent.generate_qa_pair_async(...)
        for _ in range(batch_size)
    ]
    results = await asyncio.gather(*tasks)
    return results
```

### 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_llm_call(prompt):
    return llm.invoke(prompt)
```

---

## 联系与支持

- 📧 提交Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 讨论区: [GitHub Discussions](https://github.com/your-repo/discussions)
- 📖 文档: [docs/](docs/)
