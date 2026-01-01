# 架构设计文档

本文档详细描述多模态数据合成系统的架构设计、技术选型和设计决策。

---

## 📖 目录

- [系统概述](#系统概述)
- [架构设计](#架构设计)
- [技术选型](#技术选型)
- [核心机制](#核心机制)
- [数据流](#数据流)
- [设计决策](#设计决策)
- [扩展性设计](#扩展性设计)

---

## 🎯 系统概述

### 设计目标

1. **高质量**：生成准确、有深度的多模态问答对
2. **渐进式**：通过 Iterative Curriculum 实现难度递增
3. **可验证**：自动验证数据质量，过滤低质量样本
4. **可扩展**：易于添加新任务类型、新 Agent、新 LLM
5. **易用性**：友好的 Web UI，实时可视化

### 核心特性

- **Multi-Agent 协作**：提议者、求解者、验证者分工协作
- **LangGraph 工作流**：状态机管理复杂流程
- **Pydantic 数据验证**：类型安全的数据处理
- **Gradio Web UI**：现代化的用户界面

---

## 🏗️ 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      表现层 (Presentation Layer)             │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Gradio Web UI (web_ui.py)                   │  │
│  │  • 图片上传界面                                        │  │
│  │  • 任务配置界面                                        │  │
│  │  • 实时进度展示                                        │  │
│  │  • LLM/Prompt 配置                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    业务逻辑层 (Business Logic Layer)          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │     LangGraph Workflow (src/graph.py)                │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │  │
│  │  │ Proposer    │→ │  Solver     │→ │ Validator   │ │  │
│  │  │   Agent     │  │   Agent     │  │   Agent     │ │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │  │
│  │           ↓                ↓                ↓        │  │
│  │         状态管理 (AgentState)                         │  │
│  │         迭代控制 (Iterative Curriculum)               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      服务层 (Service Layer)                  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MultimodalLLMClient (src/agents.py)                 │  │
│  │  • API 调用封装                                        │  │
│  │  • 图片编码处理                                        │  │
│  │  • 错误重试机制                                        │  │
│  │  • 响应解析                                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     基础设施层 (Infrastructure Layer)         │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Configuration│  │ Data Models  │  │   Utilities  │    │
│  │ (config/)    │  │(src/models.py)│  │(src/utils.py)│    │
│  │              │  │              │  │              │    │
│  │• LLM Config  │  │• Pydantic    │  │• Logging     │    │
│  │• Prompts     │  │  Models      │  │• File I/O    │    │
│  │• Settings    │  │• Validation  │  │• JSON Parse  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      外部服务 (External Services)            │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  OpenAI API  │  │  Qwen-VL API │  │ Custom LLM   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 模块划分

#### 1. 表现层 (Presentation Layer)

**职责**：用户交互、界面展示

- **组件**：`web_ui.py`
- **技术**：Gradio
- **功能**：
  - 图片上传和预览
  - 任务配置表单
  - 实时进度展示
  - 结果可视化
  - 配置管理界面

#### 2. 业务逻辑层 (Business Logic Layer)

**职责**：核心业务流程、Agent 协作

- **组件**：`src/graph.py`, `src/agents.py`
- **技术**：LangGraph, LangChain
- **功能**：
  - 工作流编排
  - Agent 协作逻辑
  - 状态管理
  - 迭代控制
  - 难度递增

#### 3. 服务层 (Service Layer)

**职责**：外部服务调用、数据转换

- **组件**：`MultimodalLLMClient`
- **功能**：
  - LLM API 调用
  - 图片编码/解码
  - 错误处理和重试
  - 响应解析

#### 4. 基础设施层 (Infrastructure Layer)

**职责**：配置管理、数据模型、工具函数

- **组件**：`config/`, `src/models.py`, `src/utils.py`
- **功能**：
  - 配置加载和管理
  - 数据验证和序列化
  - 日志记录
  - 文件操作

---

## 🔧 技术选型

### 核心框架

| 技术 | 版本 | 用途 | 选型理由 |
|------|------|------|----------|
| **LangChain** | 0.1.0 | LLM 应用框架 | • 丰富的 LLM 集成<br>• 成熟的社区支持 |
| **LangGraph** | 0.0.26 | 状态机工作流 | • 可视化工作流<br>• 状态管理<br>• 条件分支 |
| **Pydantic** | 2.5+ | 数据验证 | • 类型安全<br>• 自动验证<br>• JSON 序列化 |
| **Gradio** | 4.15+ | Web UI | • 快速原型<br>• 实时更新<br>• 美观界面 |
| **OpenAI SDK** | 1.10+ | LLM API 客户端 | • 官方支持<br>• 多模态能力<br>• 稳定可靠 |

### 为什么选择 LangGraph？

**优势**：

1. **状态管理**：自动处理复杂状态传递
2. **可视化**：工作流图清晰易懂
3. **灵活性**：支持条件分支、循环
4. **集成性**：与 LangChain 无缝集成

**对比其他方案**：

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **纯代码循环** | 简单直接 | 难维护、不可视化 | 简单流程 |
| **Airflow** | 成熟稳定 | 过于重量级 | 大规模数据管道 |
| **LangGraph** | 轻量灵活 | 相对较新 | AI Agent 工作流 ✅ |

### 为什么选择 Pydantic？

1. **类型安全**：编译时类型检查
2. **自动验证**：减少运行时错误
3. **文档生成**：自动生成 API 文档
4. **JSON 支持**：与 LLM JSON 输出完美配合

**示例**：

```python
# 无 Pydantic：易出错
qa = {"question": "...", "difficulty": "0.5"}  # difficulty 应该是 float
if qa["difficulty"] > 1:  # 运行时才发现错误
    ...

# 有 Pydantic：编译时检查
qa = QAPair(question="...", difficulty="0.5")  # ValidationError: 类型错误
```

---

## ⚙️ 核心机制

### 1. Iterative Curriculum（迭代课程）

**设计思想**：模仿人类学习过程，从简单到困难

**实现机制**：

```python
# 难度计算公式
current_difficulty = min(
    initial_difficulty + (iteration - 1) * difficulty_increment,
    max_difficulty
)

# 示例：
# 初始难度 = 0.3，递增 = 0.1，最大 = 1.0
# 迭代1: 0.3
# 迭代2: 0.4
# 迭代3: 0.5
# ...
# 迭代8: 1.0（到达上限）
```

**历史感知生成**：

```python
def propose(self, ..., history_qa_pairs):
    # 构建历史上下文
    history_context = "已生成的问题：\n"
    for qa in history_qa_pairs[-3:]:  # 使用最近 3 个
        history_context += f"- {qa.question} (难度: {qa.difficulty})\n"
    
    # 添加到 Prompt
    prompt = f"""
    {history_context}
    
    请生成比上述问题更难、更新颖的问题。
    目标难度：{current_difficulty}
    """
```

**关键点**：

- ✅ **渐进性**：每次只增加一点难度
- ✅ **上下文**：基于历史避免重复
- ✅ **约束**：设置最大难度上限

### 2. 三 Agent 协作

**设计模式**：Pipeline（管道）模式

```
输入（图片）→ [提议者] → (Q, A) → [求解者] → A' → [验证者] → 评分 → 输出
```

**职责分离**：

| Agent | 输入 | 输出 | 职责 |
|-------|------|------|------|
| Proposer | 图片 + 历史 | 问题 + 答案 | 创造性地生成新问题 |
| Solver | 图片 + 问题 | 预测答案 | 测试问题的可解性 |
| Validator | 参考答案 + 预测答案 | 验证结果 | 评估答案质量 |

**为什么需要 Solver？**

- **质量保证**：如果 Solver 都回答不了，说明问题可能有问题
- **难度校准**：通过 Solver 的表现调整难度
- **数据验证**：确保问题-答案对的一致性

### 3. 状态机管理

**LangGraph 状态机**：

```python
class AgentState(BaseModel):
    # 不变状态
    task: SynthesisTask           # 任务配置
    image_paths: List[str]        # 图片路径
    
    # 累积状态
    history_qa_pairs: List[QAPair]  # 已验证的问答对
    all_iterations: List[IterationState]  # 所有迭代记录
    
    # 当前状态
    current_iteration: int        # 当前迭代次数
    current_difficulty: float     # 当前难度
    current_state: IterationState  # 当前迭代状态
    
    # 控制状态
    is_finished: bool             # 是否完成
    error: Optional[str]          # 错误信息
```

**状态转换**：

```
初始状态
   ↓
[check_continue] → 更新 current_iteration, current_difficulty
   ↓
[propose] → 更新 current_state.proposed_qa
   ↓
[solve] → 更新 current_state.solved_answer
   ↓
[validate] → 更新 current_state.validation
   ↓
[update_state] → 更新 history_qa_pairs（如果通过）
   ↓
[check_continue] → 检查 is_finished
   ↓
最终状态
```

### 4. 错误处理和重试

**多层错误处理**：

```python
# 1. API 级别：OpenAI SDK 自动重试
client = OpenAI(max_retries=3)

# 2. Agent 级别：捕获并记录错误
def propose(self, ...):
    try:
        response = self.llm_client.call_with_images(...)
    except Exception as e:
        logger.error(f"提议者失败: {e}")
        raise

# 3. 节点级别：标记失败状态
def _propose_node(self, state):
    try:
        output = self.proposer.propose(...)
        state.current_state.status = "completed"
    except Exception as e:
        state.current_state.status = "failed"
        state.current_state.error = str(e)
    return state

# 4. 工作流级别：继续执行其他迭代
# 单次迭代失败不影响整体流程
```

---

## 📊 数据流

### 完整数据流程

```
1. 用户上传图片
   ↓
2. 创建 SynthesisTask
   ├─ task_id
   ├─ task_type
   ├─ images: [ImageInfo]
   └─ 配置参数
   ↓
3. 初始化 AgentState
   ├─ task: SynthesisTask
   ├─ image_paths: List[str]
   └─ 空的 history_qa_pairs
   ↓
4. 进入 LangGraph 工作流
   │
   ├─ 迭代 1
   │  ├─ Proposer → ProposerOutput(Q1, A1)
   │  ├─ Solver → SolverOutput(A1')
   │  ├─ Validator → ValidationResult
   │  └─ 如果通过 → QAPair 加入 history
   │
   ├─ 迭代 2（难度 +0.1）
   │  ├─ Proposer（基于 history）→ ProposerOutput(Q2, A2)
   │  ├─ Solver → SolverOutput(A2')
   │  ├─ Validator → ValidationResult
   │  └─ 如果通过 → QAPair 加入 history
   │
   └─ ... 继续迭代
   ↓
5. 达到最大迭代次数
   ↓
6. 生成 SynthesisResult
   ├─ task_id
   ├─ qa_pairs: List[QAPair]
   ├─ iterations: List[IterationState]
   └─ 统计信息
   ↓
7. 保存为 JSON 文件
   ↓
8. 返回给用户
```

### 数据模型关系

```
SynthesisTask
  ├─ task_id: str
  ├─ task_type: str
  ├─ images: List[ImageInfo]
  │    └─ ImageInfo
  │         ├─ path: str
  │         └─ filename: str
  └─ 配置参数

AgentState
  ├─ task: SynthesisTask ────┐
  ├─ history_qa_pairs        │
  │    └─ List[QAPair] ───┐  │
  │                       │  │
  └─ all_iterations       │  │
       └─ List[IterationState]
            ├─ proposed_qa: ProposerOutput
            ├─ solved_answer: str
            └─ validation: ValidationResult

SynthesisResult
  ├─ task: SynthesisTask ────┘
  ├─ qa_pairs: List[QAPair] ─┘
  └─ iterations: List[IterationState]
```

---

## 🎨 设计决策

### 决策 1：为什么使用 base64 编码图片？

**选项**：
1. 直接传递图片 URL
2. base64 编码嵌入请求

**选择**：base64 编码 ✅

**理由**：
- ✅ 兼容性好：所有 LLM API 都支持
- ✅ 无需额外服务器：不需要托管图片
- ✅ 隐私保护：图片不会上传到第三方
- ❌ 请求体积大：但现代网络可以接受

**实现**：

```python
def get_image_data_url(image_path: str) -> str:
    """将图片编码为 data URL"""
    ext = Path(image_path).suffix.lower()
    mime_type = {'jpg': 'image/jpeg', 'png': 'image/png'}[ext]
    
    with open(image_path, 'rb') as f:
        base64_data = base64.b64encode(f.read()).decode()
    
    return f"data:{mime_type};base64,{base64_data}"
```

### 决策 2：验证者是否需要看图片？

**选项**：
1. 验证者看图片，独立判断
2. 验证者只比较文本答案

**选择**：验证者**不强制**看图片 ✅

**理由**：
- 验证目标是答案的**语义等价性**，不是正确性
- Proposer 已经基于图片生成答案（作为参考）
- Solver 基于图片生成答案（作为预测）
- Validator 只需判断两者是否一致

**但保留接口灵活性**：

```python
def validate(self, image_paths, question, ref_answer, pred_answer):
    # 当前实现：不使用 image_paths
    # 未来可以改为：验证者也看图片，独立判断正确性
    ...
```

### 决策 3：历史问答对如何选择？

**选项**：
1. 全部历史
2. 最近 N 个
3. 随机采样
4. 基于难度筛选

**选择**：最近 3-5 个 + 全部难度分布 ✅

**实现**：

```python
def format_proposer_prompt(self, ..., history_qa_pairs):
    if not history_qa_pairs:
        return "这是第一个问题"
    
    # 最近 3 个（详细）
    recent = history_qa_pairs[-3:]
    context = "最近生成的问题：\n"
    for qa in recent:
        context += f"- Q: {qa.question} (难度: {qa.difficulty})\n"
        context += f"  A: {qa.answer}\n"
    
    # 全部难度分布（统计）
    difficulties = [qa.difficulty for qa in history_qa_pairs]
    context += f"\n已生成 {len(history_qa_pairs)} 个问题，"
    context += f"难度范围: {min(difficulties):.1f} - {max(difficulties):.1f}"
    
    return context
```

### 决策 4：如何处理验证失败？

**选项**：
1. 重新生成问题
2. 跳过当前迭代
3. 降低难度重试

**选择**：跳过当前迭代 ✅

**理由**：
- ✅ 简单直接
- ✅ 保持难度递增趋势
- ✅ 允许一定失败率（提高多样性）

**改进方向**：

```python
# 未来可以添加自适应难度
if validation_failed_count > 3:
    current_difficulty -= 0.1  # 降低难度
    logger.info("连续失败，降低难度")
```

---

## 🔄 扩展性设计

### 1. 插件化 Agent

**设计目标**：轻松添加新 Agent

**接口定义**：

```python
class BaseAgent(ABC):
    """Agent 基类"""
    
    @abstractmethod
    def process(self, state: AgentState) -> Any:
        """处理逻辑"""
        pass

class ProposerAgent(BaseAgent):
    def process(self, state):
        return self.propose(...)

# 添加新 Agent
class RefinementAgent(BaseAgent):
    """问题精化 Agent"""
    def process(self, state):
        # 对生成的问题进行精化
        raw_question = state.current_state.proposed_qa.question
        refined = self.refine(raw_question)
        return refined
```

**集成到工作流**：

```python
def _build_graph(self):
    workflow.add_node("propose", self._propose_node)
    workflow.add_node("refine", self._refine_node)  # 新增
    workflow.add_node("solve", self._solve_node)
    
    workflow.add_edge("propose", "refine")
    workflow.add_edge("refine", "solve")
```

### 2. 多模型支持

**设计目标**：支持不同 Agent 使用不同模型

```python
class MultimodalSynthesisGraph:
    def __init__(self, configs: Dict[str, LLMConfig]):
        # 为每个 Agent 配置不同模型
        self.proposer_client = MultimodalLLMClient(configs["proposer"])
        self.solver_client = MultimodalLLMClient(configs["solver"])
        self.validator_client = MultimodalLLMClient(configs["validator"])
        
        self.proposer = ProposerAgent(self.proposer_client)
        self.solver = SolverAgent(self.solver_client)
        self.validator = ValidatorAgent(self.validator_client)

# 使用
configs = {
    "proposer": LLMConfig(model_name="gpt-4-vision"),  # 强模型
    "solver": LLMConfig(model_name="gpt-4o"),          # 中等模型
    "validator": LLMConfig(model_name="gpt-3.5-turbo") # 轻量模型
}
graph = MultimodalSynthesisGraph(configs)
```

### 3. 数据导出格式

**设计目标**：支持多种导出格式

```python
class DataExporter(ABC):
    @abstractmethod
    def export(self, result: SynthesisResult, output_path: Path):
        pass

class JSONExporter(DataExporter):
    def export(self, result, output_path):
        with open(output_path, 'w') as f:
            json.dump(result.dict(), f, ensure_ascii=False)

class JSONLExporter(DataExporter):
    def export(self, result, output_path):
        with open(output_path, 'w') as f:
            for qa in result.qa_pairs:
                item = {
                    "image": result.images[0].path,
                    "question": qa.question,
                    "answer": qa.answer
                }
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

class HuggingFaceExporter(DataExporter):
    def export(self, result, output_path):
        # 导出为 HuggingFace datasets 格式
        ...

# 使用
exporter = JSONLExporter()
exporter.export(result, output_path)
```

### 4. 评估指标

**设计目标**：可插拔的质量评估

```python
class QualityMetric(ABC):
    @abstractmethod
    def compute(self, qa_pairs: List[QAPair]) -> float:
        pass

class DifficultyDistributionMetric(QualityMetric):
    """难度分布均匀度"""
    def compute(self, qa_pairs):
        difficulties = [qa.difficulty for qa in qa_pairs]
        # 计算标准差（越小越均匀）
        return np.std(difficulties)

class DiversityMetric(QualityMetric):
    """问题多样性"""
    def compute(self, qa_pairs):
        # 使用词汇重叠率衡量多样性
        ...

# 使用
metrics = [
    DifficultyDistributionMetric(),
    DiversityMetric()
]

for metric in metrics:
    score = metric.compute(result.qa_pairs)
    print(f"{metric.__class__.__name__}: {score}")
```

---

## 📈 性能考量

### 1. API 调用成本

**每次任务的 API 调用**：

```
迭代次数 × (Proposer + Solver + Validator) = N × 3 次调用
```

**优化策略**：

1. **批量处理**：一次 API 调用处理多个问题
2. **缓存**：相同图片+问题的结果缓存
3. **异步调用**：并行处理多个迭代

### 2. 响应时间

**典型时间分布**：

```
Proposer:  5-10秒
Solver:    5-10秒
Validator: 3-5秒
────────────────────
单次迭代:  13-25秒

10次迭代:  2-4分钟
```

**优化方向**：

- 使用更快的模型（如 GPT-4o mini）
- 减少 max_tokens
- 并行处理多个迭代（需要注意历史依赖）

---

## 🔐 安全性

### 1. API Key 保护

- ✅ 使用环境变量
- ✅ 不提交到代码库
- ✅ UI 中使用密码输入框

### 2. 输入验证

- ✅ Pydantic 自动验证
- ✅ 文件类型检查
- ✅ 文件大小限制

### 3. 错误信息

- ✅ 不暴露敏感信息
- ✅ 详细日志记录到文件
- ✅ 用户界面显示友好提示

---

## 📝 总结

本系统通过**分层架构**、**模块化设计**和**可扩展接口**，实现了一个灵活、高效的多模态数据合成平台。核心的 **Iterative Curriculum** 机制和 **Multi-Agent 协作**确保了生成数据的高质量和渐进性。

**关键设计亮点**：

- ✅ LangGraph 工作流：清晰的状态管理
- ✅ Pydantic 数据模型：类型安全
- ✅ 三 Agent 协作：职责分离
- ✅ 渐进式难度：模仿人类学习
- ✅ 可视化 UI：实时反馈

---

**架构版本**：v1.0 | **更新日期**：2026-01-01
