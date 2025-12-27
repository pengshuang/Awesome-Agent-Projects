# 架构设计文档

> 本文档描述系统的整体架构、设计决策和技术选型，面向架构师和高级开发者。

---

## 📋 目录

- [系统概览](#系统概览)
- [核心架构](#核心架构)
- [技术选型](#技术选型)
- [设计模式](#设计模式)
- [数据流](#数据流)
- [扩展性设计](#扩展性设计)

---

## 🌐 系统概览

### 系统定位

基于大模型的**自适应难度数据合成系统**，通过三智能体协作生成高质量问答对。

**核心价值**：
- **自动化**：无需人工标注，文档即可生成训练数据
- **高质量**：三智能体协作确保质量（Proposer提问 → Solver求解 → Validator验证）
- **自适应**：Iterative Curriculum机制实现难度递增

### 设计原则

1. **单一职责**：每个Agent只负责一件事
2. **可扩展性**：易于添加新任务类型、新Agent
3. **可观测性**：完整的日志、实时进度反馈
4. **用户友好**：Web UI + CLI，适合不同场景

---

## 🏗️ 核心架构

### 系统分层

```
┌─────────────────────────────────────────┐
│          Presentation Layer              │  ← Web UI (Gradio) / CLI
├─────────────────────────────────────────┤
│         Orchestration Layer              │  ← LangGraph工作流编排
├─────────────────────────────────────────┤
│            Agent Layer                   │  ← Proposer, Solver, Validator
├─────────────────────────────────────────┤
│         Foundation Layer                 │  ← LangChain LLM抽象
├─────────────────────────────────────────┤
│         Infrastructure Layer             │  ← 配置、日志、存储
└─────────────────────────────────────────┘
```

### 模块划分

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Web UI     │────▶│    Graph     │────▶│   Agents     │
│  (Gradio)    │     │ (LangGraph)  │     │ (3 Agents)   │
└──────────────┘     └──────────────┘     └──────────────┘
       │                     │                     │
       │                     │                     │
       ▼                     ▼                     ▼
┌──────────────────────────────────────────────────────┐
│                   Shared Components                   │
│  - Models (Pydantic)                                 │
│  - Utils (格式化、文件操作)                            │
│  - Config (Prompts, Settings, LLM)                   │
└──────────────────────────────────────────────────────┘
```

### 三智能体架构

```
┌─────────────┐
│  Proposer   │ 提出问题
│  (提议者)    │ - 生成问题和参考答案
│             │ - 分配难度分数 (1-10)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Solver    │ 尝试回答
│  (求解者)    │ - 基于文档推理
│             │ - 输出推理步骤
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Validator  │ 验证答案
│  (验证者)    │ - 对比参考答案
│             │ - 评分 & 反馈
└─────────────┘
```

**优势**：
- **去耦合**：每个Agent独立，互不干扰
- **可替换**：可单独升级某个Agent
- **可测试**：每个Agent可独立测试

---

## 🔧 技术选型

### 核心技术栈

| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|----------|
| **Python** | 3.10+ | 主语言 | AI生态完善，LangChain支持 |
| **LangGraph** | 0.0.30+ | 工作流编排 | 状态管理清晰，支持streaming |
| **LangChain** | 0.1.0+ | LLM抽象层 | 统一接口，支持多种LLM |
| **Gradio** | 4.15.0+ | Web UI | 快速构建，实时交互 |
| **Pydantic** | 2.x | 数据验证 | 类型安全，自动校验 |
| **Loguru** | 0.7.x | 日志 | 简洁API，自动轮转 |

### LLM选择

**主要支持**：
- OpenAI GPT-4/GPT-3.5
- Anthropic Claude
- 其他兼容OpenAI API的模型

**考虑因素**：
- 推理能力：复杂问题需要GPT-4级别
- 成本：GPT-3.5更经济，Claude 3.5 Sonnet平衡性价比
- 速度：Claude通常更快

### 为什么选择LangGraph？

**对比其他方案**：

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **LangGraph** | 状态管理清晰、streaming支持 | 学习曲线 | 复杂多步骤工作流 |
| 原生LangChain Chain | 简单易用 | 状态管理困难 | 简单链式调用 |
| 自定义循环 | 灵活 | 代码冗余 | 简单迭代 |

**选择LangGraph原因**：
1. **状态管理**：自动维护state，无需手动传递
2. **流式输出**：实时反馈进度
3. **条件分支**：灵活的流程控制
4. **可视化**：可生成工作流图

---

## 🎨 设计模式

### 1. Strategy Pattern (策略模式)

**应用**：Agent实现

```python
# Agent接口
class BaseAgent(ABC):
    @abstractmethod
    def execute(self, input_data):
        pass

# 具体实现
class ProposerAgent(BaseAgent):
    def execute(self, input_data):
        # Proposer逻辑
        pass

class SolverAgent(BaseAgent):
    def execute(self, input_data):
        # Solver逻辑
        pass
```

**优势**：
- 易于添加新Agent
- Agent可独立测试、替换

### 2. State Pattern (状态模式)

**应用**：工作流状态管理

```python
state = {
    "current_iteration": 0,
    "history_buffer": [],
    "is_complete": False,
    # ...
}

def check_continue(state):
    if state["is_complete"]:
        return "end"
    if state["current_iteration"] >= state["max_iterations"]:
        return "end"
    return "propose"
```

**优势**：
- 状态转换清晰
- 易于调试和追踪

### 3. Template Method Pattern (模板方法)

**应用**：Prompt模板

```python
PROMPTS = {
    "proposer": {
        "system": "...",  # 固定系统提示
        "user_first": "...",  # 首次问题模板
        "user_iterative": "..."  # 后续问题模板
    }
}

# 运行时填充变量
prompt = PROMPTS["proposer"]["user_first"].format(
    document=document,
    task_type=task_type
)
```

### 4. Observer Pattern (观察者模式)

**应用**：进度回调

```python
def run_synthesis(document, ..., progress_callback=None):
    for iteration in range(max_iterations):
        # 执行逻辑
        if progress_callback:
            progress_callback({
                "iteration": iteration,
                "status": "...",
                "data": {...}
            })
```

---

## 🔄 数据流

### 完整流程

```
用户输入 → Web UI → Graph初始化 → 迭代循环 → 结果输出
```

### 详细流程图

```
┌─────────────┐
│  用户上传    │
│  文档内容    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│          Graph初始化State                 │
│  {                                       │
│    document: "...",                      │
│    task_type: "逻辑推理类",               │
│    max_iterations: 5,                    │
│    current_iteration: 0,                 │
│    history_buffer: [],                   │
│    valid_pairs: []                       │
│  }                                       │
└──────┬──────────────────────────────────┘
       │
       ▼
   ┌───────────────────┐
   │  Iteration Loop   │
   └───────────────────┘
       │
       ├──▶ ┌──────────────┐
       │    │  Proposer    │ 生成问题
       │    │  生成问题     │ - question
       │    │  和参考答案   │ - answer
       │    └──────┬───────┘ - difficulty_score
       │           │
       │           ▼
       ├──▶ ┌──────────────┐
       │    │   Solver     │ 尝试回答
       │    │   求解问题   │ - reasoning_steps
       │    └──────┬───────┘ - final_answer
       │           │
       │           ▼
       ├──▶ ┌──────────────┐
       │    │  Validator   │ 验证答案
       │    │  验证答案质量 │ - score (1-10)
       │    └──────┬───────┘ - is_valid (bool)
       │           │          - feedback
       │           │
       │           ▼
       │    ┌──────────────┐
       │    │ Check Score  │
       │    │ score >= 7?  │
       │    └──────┬───────┘
       │           │
       │      ┌────┴────┐
       │      │         │
       │     Yes       No
       │      │         │
       │      ▼         ▼
       │  加入valid   加入history
       │   _pairs      _buffer
       │      │         │
       │      └────┬────┘
       │           │
       │           ▼
       │    ┌──────────────┐
       │    │ current_iter │
       │    │   ++ 1       │
       │    └──────┬───────┘
       │           │
       │      ┌────┴────────┐
       │      │ Continue?   │
       │      │ iter < max? │
       │      └────┬────────┘
       │           │
       │      ┌────┴────┐
       │     Yes       No
       │      │         │
       └──────┘         ▼
                   ┌──────────┐
                   │   End    │
                   └────┬─────┘
                        │
                        ▼
                ┌───────────────┐
                │  返回结果      │
                │  - valid_pairs│
                │  - history    │
                └───────────────┘
```

### State更新机制

```python
# 初始state
state = {
    "document": "...",
    "current_iteration": 0,
    "history_buffer": [],
    "valid_pairs": []
}

# Proposer更新
state["current_question"] = proposer_output.question
state["current_reference_answer"] = proposer_output.answer

# Solver更新
state["current_solver_answer"] = solver_output.final_answer

# Validator更新
if validator_output.is_valid:
    state["valid_pairs"].append({...})
else:
    state["history_buffer"].append({...})

# 迭代计数更新
state["current_iteration"] += 1
```

### 数据模型转换

```
用户输入 (dict)
    ↓
Pydantic Models (类型校验)
    ↓
LLM调用 (JSON)
    ↓
Pydantic Models (解析验证)
    ↓
State更新 (dict)
    ↓
UI展示 (HTML/Markdown)
    ↓
文件保存 (JSON)
```

---

## 📈 扩展性设计

### 水平扩展

**多文档并行处理**：

```python
from concurrent.futures import ThreadPoolExecutor

def batch_process(documents, task_type):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(run_synthesis, doc, task_type)
            for doc in documents
        ]
        results = [f.result() for f in futures]
    return results
```

### 垂直扩展

**1. 添加新Agent**

```python
class RefinerAgent(BaseAgent):
    """精炼Agent - 优化问答对表述"""
    def execute(self, qa_pair):
        # 精炼逻辑
        return refined_qa_pair

# 在Graph中添加节点
graph.add_node("refine", self._refine_node)
graph.add_edge("validate", "refine")
graph.add_edge("refine", "check_continue")
```

**2. 添加新任务类型**

仅需修改：
- `src/models.py`: 添加枚举值
- `config/prompts.py`: 添加任务说明
- `web_ui.py`: UI自动更新（读取枚举）

**3. 支持新LLM**

```python
# config/llm_config.py
def get_llm():
    if settings.llm_provider == "openai":
        return ChatOpenAI(...)
    elif settings.llm_provider == "anthropic":
        return ChatAnthropic(...)
    elif settings.llm_provider == "custom":
        return YourCustomLLM(...)
```

### 插件化设计

**未来可扩展为插件系统**：

```python
# plugins/custom_agent.py
class CustomAgent(BaseAgent):
    name = "custom"
    version = "1.0.0"
    
    def execute(self, input_data):
        # 自定义逻辑
        pass

# 动态加载
plugin_manager.load_plugin("custom_agent")
graph.register_agent("custom", CustomAgent())
```

---

## 🔒 安全性设计

### API密钥管理

- 使用 `.env` 文件（不提交到Git）
- 支持环境变量
- 敏感信息不写入日志

### 输入验证

```python
class ProposerOutput(BaseModel):
    question: str = Field(..., min_length=10, max_length=1000)
    answer: str = Field(..., min_length=5)
    difficulty_score: int = Field(..., ge=1, le=10)
```

### 错误处理

```python
try:
    output = self.proposer.generate_qa_pair(...)
except ValidationError as e:
    logger.error(f"Validation error: {e}")
    # 降级策略：使用默认值
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    # 重试或跳过
```

---

## 📊 性能优化

### LLM调用优化

1. **Streaming**：实时返回结果，提升体验
2. **缓存**：相同问题复用答案（可选）
3. **批处理**：多文档并行处理

### 内存优化

```python
# 限制history_buffer大小
MAX_HISTORY = 10
if len(state["history_buffer"]) > MAX_HISTORY:
    state["history_buffer"] = state["history_buffer"][-MAX_HISTORY:]
```

### 日志轮转

```python
# 自动轮转，避免日志文件过大
logger.add(
    "logs/system_{time}.log",
    rotation="100 MB",  # 100MB轮转
    retention="7 days",  # 保留7天
    compression="zip"  # 压缩旧日志
)
```

---

## 🧪 测试策略

### 单元测试

- 每个Agent独立测试
- Mock LLM输出，测试解析逻辑
- Pydantic模型验证测试

### 集成测试

- 完整工作流测试
- 多种任务类型测试
- 边界情况测试

### 性能测试

- 并发处理能力
- 内存占用监控
- LLM调用延迟

---

## 🚀 部署架构

### 本地部署

```
用户机器
├── Python 3.10环境
├── 依赖包安装
└── 启动Web UI / CLI
```

### Docker部署（未来）

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "web_ui.py"]
```

### 云部署（未来）

```
┌──────────────┐
│  Nginx       │ 负载均衡
└──────┬───────┘
       │
   ┌───┴───┐
   │       │
┌──▼──┐ ┌──▼──┐
│ UI  │ │ UI  │ 多实例
└──┬──┘ └──┬──┘
   │       │
   └───┬───┘
       │
┌──────▼───────┐
│   API层      │ 共享LLM API
└──────────────┘
```

---

## 📝 设计决策记录

### 为什么使用三智能体？

**决策**：Proposer + Solver + Validator

**理由**：
- **职责分离**：生成、求解、验证各司其职
- **质量保证**：独立验证避免"自己检查自己"
- **可解释**：每步清晰可追溯

**备选方案**：
- 单Agent：质量难保证
- 双Agent（Proposer + Validator）：缺少独立求解视角

### 为什么用难度分数而非二分类？

**决策**：1-10分连续评分

**理由**：
- **细粒度**：区分"完美"和"正确"
- **梯度学习**：支持Curriculum Learning
- **灵活阈值**：可调整验证标准

### 为什么Solver需要文档？

**决策**：Solver可访问原始文档

**理由**：
- **现实场景**：模拟RAG应用场景
- **质量提升**：基于事实回答
- **难度验证**：确保问题可解

---

## 🔮 未来演进

### 短期（3-6个月）

- [ ] 支持更多LLM（通义千问、文心一言）
- [ ] 添加多语言支持
- [ ] Web API接口
- [ ] Docker镜像

### 中期（6-12个月）

- [ ] 分布式处理（Celery）
- [ ] 数据集管理面板
- [ ] A/B测试框架
- [ ] 细粒度质量分析

### 长期（1年+）

- [ ] Agent自动优化（强化学习）
- [ ] 社区Prompt市场
- [ ] 企业级权限管理
- [ ] SaaS服务

---

## 📚 参考架构

**灵感来源**：
- **AlphaGeometry** (Google DeepMind): 提议-求解验证范式
- **Constitutional AI** (Anthropic): 自我批判机制
- **Curriculum Learning**: 渐进式难度提升

**相关论文**：
- "Curriculum Learning" (Bengio et al., 2009)
- "Self-Consistency Improves Chain of Thought Reasoning" (Wang et al., 2022)

---

**架构版本**: v1.0  
**最后更新**: 2024-12-27
