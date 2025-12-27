# 开发者指南

> 本指南面向需要进行二次开发的开发者，包含项目结构、核心代码说明和扩展指南。

---

## 📋 目录

- [项目结构](#项目结构)
- [核心模块](#核心模块)
- [扩展开发](#扩展开发)
- [调试技巧](#调试技巧)

---

## 📁 项目结构

```
data-synthesis-system/
├── config/                  # 配置模块
│   ├── settings.py         # 环境变量配置
│   ├── llm_config.py       # LLM实例化
│   └── prompts.py          # Prompt模板
│
├── src/                    # 核心代码
│   ├── models.py           # 数据模型（Pydantic）
│   ├── agents.py           # 三个Agent实现
│   ├── graph.py            # LangGraph工作流
│   └── utils.py            # 工具函数
│
├── data/                   # 数据目录
│   ├── outputs/            # 输出JSON
│   └── uploads/            # 上传文档
│
├── docs/                   # 文档
├── logs/                   # 日志
├── web_ui.py               # Web界面入口
├── cli.py                  # 命令行工具
└── requirements.txt        # 依赖列表
```

### 核心文件说明

| 文件 | 作用 | 修改场景 |
|------|------|----------|
| `config/settings.py` | 环境变量、系统配置 | 添加新配置项 |
| `config/prompts.py` | Prompt模板 | 优化生成质量 |
| `config/llm_config.py` | LLM实例化 | 更换模型 |
| `src/models.py` | 数据模型定义 | 扩展数据结构 |
| `src/agents.py` | Agent实现 | 修改Agent行为 |
| `src/graph.py` | 工作流编排 | 调整流程逻辑 |
| `src/utils.py` | 工具函数 | 添加辅助功能 |
| `web_ui.py` | Gradio界面 | 修改UI |
| `cli.py` | 命令行工具 | 批量处理 |

---

## 🔧 核心模块

### 1. 数据模型 (`src/models.py`)

**TaskType枚举**：

```python
class TaskType(Enum):
    """任务类型"""
    LOGICAL_REASONING = "逻辑推理类"
    NUMERICAL_CALCULATION = "数值计算类"
    INFORMATION_QUERY = "信息查询类"
    SUMMARIZATION = "总结摘要类"
```

**ProposerOutput**：

```python
class ProposerOutput(BaseModel):
    """提议者输出"""
    question: str                # 生成的问题
    answer: str                  # 参考答案
    difficulty_score: int        # 难度分数 1-10
    reasoning: str               # 生成理由
```

**SolverOutput**：

```python
class SolverOutput(BaseModel):
    """求解者输出"""
    reasoning_steps: List[str]   # 推理步骤列表
    final_answer: str            # 最终答案（必须是字符串）
```

**ValidatorOutput**：

```python
class ValidatorOutput(BaseModel):
    """验证者输出"""
    score: float                 # 评分 1-10
    is_valid: bool              # 是否通过验证
    reasoning: str              # 评分理由
    feedback: str               # 详细反馈
```

### 2. Agent实现 (`src/agents.py`)

**ProposerAgent**（提议者）：

```python
class ProposerAgent:
    def generate_qa_pair(
        self,
        document: str,
        task_type: TaskType,
        history_buffer: List[Dict]
    ) -> ProposerOutput:
        """
        生成问答对
        
        参数:
            document: 文档内容
            task_type: 任务类型
            history_buffer: 历史问答对列表
            
        返回:
            ProposerOutput: 包含问题、答案、难度分数
        """
```

**关键逻辑**：
- 首次调用：使用`user_first` prompt（低难度1-2分）
- 后续调用：使用`user_iterative` prompt（难度递增）
- 从history_buffer中提取最高难度分数，确保新问题难度不低于此

**SolverAgent**（求解者）：

```python
class SolverAgent:
    def solve(
        self,
        document: str,
        question: str
    ) -> SolverOutput:
        """
        尝试回答问题
        
        参数:
            document: 文档内容
            question: 问题
            
        返回:
            SolverOutput: 推理步骤和最终答案
        """
```

**关键逻辑**：
- 基于文档内容回答问题
- 展示推理步骤（List[str]）
- final_answer必须是字符串（即使是复杂答案）

**ValidatorAgent**（验证者）：

```python
class ValidatorAgent:
    def validate(
        self,
        question: str,
        reference_answer: str,
        solver_answer: str
    ) -> ValidatorOutput:
        """
        验证答案质量
        
        参数:
            question: 问题
            reference_answer: 提议者的参考答案
            solver_answer: 求解者的答案
            
        返回:
            ValidatorOutput: 评分、是否通过、反馈
        """
```

**评分标准**：
- 9-10分：完美答案
- 7-8分：正确答案
- 5-6分：基本正确
- 3-4分：部分正确
- 1-2分：错误答案

### 3. 工作流编排 (`src/graph.py`)

**DataSynthesisGraph类**：

```python
class DataSynthesisGraph:
    def __init__(self):
        """初始化工作流"""
        self.proposer = ProposerAgent()
        self.solver = SolverAgent()
        self.validator = ValidatorAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> CompiledGraph:
        """构建LangGraph工作流"""
```

**工作流节点**：

1. **propose_node**：调用Proposer生成问题
2. **solve_node**：调用Solver求解问题
3. **validate_node**：调用Validator验证答案
4. **check_continue**：判断是否继续迭代

**State管理**：

```python
state = {
    "document": str,              # 文档内容
    "task_type": str,             # 任务类型
    "max_iterations": int,        # 最大迭代次数
    "current_iteration": int,     # 当前迭代
    "history_buffer": List[Dict], # 历史问答对
    "valid_pairs": List[Dict],    # 通过验证的问答对
    "failed_attempts": int,       # 失败次数
    "current_question": str,      # 当前问题
    "current_solver_answer": str, # 当前答案
    "iteration_details": List[Dict],  # 迭代详情
    "is_complete": bool           # 是否完成
}
```

**流程控制**：

```python
def _check_continue(state: dict) -> str:
    """判断是否继续迭代"""
    if state["current_iteration"] >= state["max_iterations"]:
        return "end"  # 达到最大次数
    if state["is_complete"]:
        return "end"  # 用户停止
    return "propose"  # 继续下一轮
```

### 4. 工具函数 (`src/utils.py`)

**文件操作**：

```python
def save_qa_pairs(qa_pairs: List[Dict], task_type: str) -> str:
    """保存问答对到JSON文件"""
    
def read_document_file(file_path: str) -> str:
    """读取文档文件内容"""
    
def ensure_directories():
    """确保必要的目录存在"""
```

**格式化函数**：

```python
def format_qa_for_display(qa_dict: Dict, index: int) -> str:
    """格式化问答对为HTML（可折叠卡片）"""
    
def format_iteration_status(detail: Dict, iteration: int) -> str:
    """格式化迭代详情为Markdown"""
```

---

## 🔨 扩展开发

### 添加新的任务类型

**步骤1：修改TaskType枚举**

```python
# src/models.py
class TaskType(Enum):
    # ... 现有类型 ...
    CODE_GENERATION = "代码生成类"  # 新增
```

**步骤2：更新Prompt说明**

```python
# config/prompts.py
PROMPTS = {
    "proposer": {
        "system": """
        任务类型说明：
        - 代码生成类：需要生成代码片段、解释代码逻辑
        """
    }
}
```

**步骤3：更新UI选项**

```python
# web_ui.py
task_type = gr.Radio(
    choices=[t.value for t in TaskType],  # 自动包含新类型
    label="任务类型"
)
```

### 自定义Agent行为

**示例：添加重试机制**

```python
# src/agents.py
class ProposerAgent:
    def generate_qa_pair(self, document, task_type, history_buffer):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                output = self._generate(document, task_type, history_buffer)
                return output
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Retry {attempt + 1}/{max_retries}")
                time.sleep(1)
```

### 修改评分逻辑

**示例：添加额外评分维度**

```python
# config/prompts.py
PROMPTS = {
    "validator": {
        "system": """
        评估标准：
        1. 核心信息是否一致（30%权重）
        2. 关键事实是否准确（25%权重）
        3. 推理过程是否清晰完整（20%权重）
        4. 答案的详细程度和深度（10%权重）
        5. 答案的创新性和启发性（15%权重）  # 新增
        """
    }
}
```

### 集成自定义LLM

**步骤1：修改LLM配置**

```python
# config/llm_config.py
from langchain_community.llms import YourCustomLLM

def get_llm():
    if settings.use_custom_llm:
        return YourCustomLLM(
            api_key=settings.custom_api_key,
            # ... 其他参数
        )
    else:
        return ChatOpenAI(...)
```

**步骤2：更新环境变量**

```bash
# .env
USE_CUSTOM_LLM=true
CUSTOM_API_KEY=your-key
```

### 添加自定义Prompt模板

**方法1：通过Web UI**

1. 打开"⚙️ Prompts配置"标签页
2. 修改Prompt内容
3. 实时生效，测试效果
4. 满意后复制到`config/prompts.py`

**方法2：直接修改配置文件**

```python
# config/prompts.py
PROMPTS = {
    "proposer": {
        "system": """
        你是一个专业的XXX...
        
        自定义指令：
        - ...
        - ...
        """,
        "user_first": """
        自定义首次提示：
        {custom_variable}
        """
    }
}
```

### 导出为Python包

**创建setup.py**：

```python
from setuptools import setup, find_packages

setup(
    name="data-synthesis-system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "langgraph>=0.0.30",
        "langchain>=0.1.0",
        # ... 其他依赖
    ],
    entry_points={
        'console_scripts': [
            'data-synthesis=cli:main',
        ],
    },
)
```

**安装和使用**：

```bash
# 安装
pip install -e .

# 使用
data-synthesis --input doc.md --task-type logical
```

---

## 🐛 调试技巧

### 日志系统

**查看日志**：

```bash
# 实时查看最新日志
tail -f logs/system_*.log

# 搜索错误
grep "ERROR" logs/*.log

# 搜索特定Agent
grep "Proposer" logs/*.log
```

**调整日志级别**：

```python
# web_ui.py 或 cli.py
logger.remove()
logger.add(sys.stderr, level="DEBUG")  # DEBUG/INFO/WARNING/ERROR
```

### 断点调试

**使用pdb**：

```python
# 在需要调试的地方插入
import pdb; pdb.set_trace()

# 或使用 breakpoint()（Python 3.7+）
breakpoint()
```

**常用pdb命令**：
- `n` (next): 下一行
- `s` (step): 进入函数
- `c` (continue): 继续执行
- `p variable`: 打印变量
- `l` (list): 查看代码
- `q` (quit): 退出

### 单元测试

**创建测试文件**：

```python
# tests/test_agents.py
import pytest
from src.agents import ProposerAgent
from src.models import TaskType

def test_proposer_generate():
    proposer = ProposerAgent()
    document = "测试文档内容..."
    task_type = TaskType.LOGICAL_REASONING
    
    output = proposer.generate_qa_pair(document, task_type, [])
    
    assert output.question is not None
    assert output.answer is not None
    assert 1 <= output.difficulty_score <= 10
```

**运行测试**：

```bash
pytest tests/
```

### 性能分析

**使用cProfile**：

```python
import cProfile
import pstats

# 分析函数性能
profiler = cProfile.Profile()
profiler.enable()

# 执行代码
result = graph.stream(state)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # 显示前20个最耗时的函数
```

### 常见问题排查

**问题1：LLM返回格式错误**

```python
# src/agents.py
def _parse_llm_output(self, output: str) -> dict:
    """安全解析LLM输出"""
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse: {output}")
        # 尝试修复常见问题
        output = output.strip()
        if not output.startswith('{'):
            output = '{' + output
        if not output.endswith('}'):
            output = output + '}'
        return json.loads(output)
```

**问题2：final_answer不是字符串**

```python
# src/graph.py
def _solve_node(self, state: dict) -> dict:
    output = self.solver.solve(...)
    
    # 确保final_answer是字符串
    if not isinstance(output.final_answer, str):
        output.final_answer = str(output.final_answer)
    
    state["current_solver_answer"] = output.final_answer
    return state
```

**问题3：内存占用过高**

```python
# 限制history_buffer大小
MAX_HISTORY_SIZE = 10

if len(state["history_buffer"]) > MAX_HISTORY_SIZE:
    state["history_buffer"] = state["history_buffer"][-MAX_HISTORY_SIZE:]
```

---

## 📚 参考资源

- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **LangChain**: https://python.langchain.com/docs/
- **Gradio**: https://www.gradio.app/docs/
- **Pydantic**: https://docs.pydantic.dev/

---

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交代码（遵循PEP 8）
4. 编写测试
5. 提交Pull Request

**代码规范**：
- 使用类型提示
- 编写docstring
- 保持函数简洁（<50行）
- 添加必要的日志

---

**Happy Coding!** 🎉
