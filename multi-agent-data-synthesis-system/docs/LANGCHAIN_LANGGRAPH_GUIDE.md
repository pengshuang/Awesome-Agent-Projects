# LangChain & LangGraph 应用详解

> 本文档深入讲解项目如何使用 LangChain 和 LangGraph，结合实际代码剖析设计思路和实现细节。

---

## 📋 目录

- [技术栈概览](#技术栈概览)
- [LangChain 应用详解](#langchain-应用详解)
- [LangGraph 应用详解](#langgraph-应用详解)
- [完整工作流解析](#完整工作流解析)
- [高级技巧](#高级技巧)
- [常见问题](#常见问题)

---

## 🎯 技术栈概览

### 为什么选择 LangChain + LangGraph？

**LangChain**：
- 🔗 **统一的 LLM 接口**：抽象不同 LLM 提供商（OpenAI、Anthropic、HuggingFace 等）
- 💬 **消息管理**：SystemMessage、HumanMessage、AIMessage 结构化对话
- 🔄 **可组合性**：Chain、Agent、Tool 等可复用组件

**LangGraph**：
- 📊 **状态管理**：自动管理复杂的状态流转
- 🔀 **流程控制**：支持条件分支、循环、并行执行
- 📡 **流式输出**：实时反馈进度
- 🐛 **可调试性**：清晰的节点和边，易于追踪

### 项目中的使用层级

```
┌─────────────────────────────────────────┐
│         Web UI (Gradio)                 │  ← 用户交互层
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    LangGraph (工作流编排)                │  ← 流程控制层
│  - StateGraph                           │
│  - 节点 (propose, solve, validate)      │
│  - 条件边 (should_continue)             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    Agents (业务逻辑)                     │  ← 业务逻辑层
│  - ProposerAgent                        │
│  - SolverAgent                          │
│  - ValidatorAgent                       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    LangChain (LLM 抽象)                 │  ← LLM 接口层
│  - ChatOpenAI                           │
│  - Messages (System, Human, AI)         │
│  - invoke() / stream()                  │
└─────────────────────────────────────────┘
```

---

## 🔗 LangChain 应用详解

### 1. LLM 配置与初始化

**文件**: [config/llm_config.py](../config/llm_config.py)

```python
from langchain_openai import ChatOpenAI
from .settings import settings

def get_llm(
    model_name: str = None,
    temperature: float = None,
    max_tokens: int = None
) -> ChatOpenAI:
    """
    获取配置好的 LLM 实例
    
    核心设计：
    - 工厂模式：统一创建 LLM 实例
    - 参数覆盖：支持动态调整参数
    - 配置分离：从 settings 读取默认值
    """
    return ChatOpenAI(
        model=model_name or settings.proposer_model,  # 默认使用 proposer_model
        temperature=temperature or settings.temperature,  # 控制随机性
        max_tokens=max_tokens or settings.max_tokens,  # 限制输出长度
        openai_api_key=settings.openai_api_key,  # API 密钥
        openai_api_base=settings.openai_api_base,  # 支持自定义 API 端点
    )
```

**设计亮点**：

1. **灵活配置**：
   - 默认值从 `settings` 读取
   - 运行时可覆盖参数
   - 支持不同 Agent 使用不同模型

2. **多模型支持**：
   ```python
   # Proposer 使用更强大的模型
   proposer_llm = get_llm(model_name="gpt-4", temperature=0.7)
   
   # Solver 使用性价比模型
   solver_llm = get_llm(model_name="gpt-3.5-turbo", temperature=0.3)
   ```

3. **自定义 API 端点**：
   ```bash
   # .env
   OPENAI_API_BASE=https://api.custom-provider.com/v1
   ```
   支持兼容 OpenAI API 的其他提供商（Azure、OneAPI 等）

### 2. 消息结构设计

**LangChain 的消息系统**：

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
```

**在 ProposerAgent 中的应用**：

**文件**: [src/agents.py](../src/agents.py#L58-L68)

```python
def generate_qa_pair(self, document: str, task_type: TaskType, history_buffer: list) -> ProposerOutput:
    """生成问答对"""
    
    # 1. 构造 system 消息（角色定义）
    system_msg = SystemMessage(content=PROMPTS["proposer"]["system"])
    
    # 2. 构造 user 消息（具体任务）
    if not history_buffer:
        # 首次提问：低难度
        user_prompt = PROMPTS["proposer"]["user_first"].format(
            document=document,
            task_type=task_type.value
        )
    else:
        # 后续提问：基于历史递增难度
        history_text = "\n\n".join([
            f"问题 {i+1}: {qa['question']}\n答案: {qa['answer']}"
            for i, qa in enumerate(history_buffer)
        ])
        user_prompt = PROMPTS["proposer"]["user_iterative"].format(
            document=document,
            task_type=task_type.value,
            history=history_text  # 传入历史问答
        )
    
    user_msg = HumanMessage(content=user_prompt)
    
    # 3. 组装消息列表
    messages = [system_msg, user_msg]
    
    # 4. 调用 LLM
    response = self.llm.invoke(messages)
    content = response.content  # 获取文本响应
```

**设计原理**：

```
┌──────────────────────────────────────┐
│       SystemMessage                  │  ← 设定 Agent 角色和能力
│  "你是一个专业的问题生成专家..."      │     (相当于"人设")
└──────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│       HumanMessage                   │  ← 具体任务和上下文
│  文档内容: ...                        │
│  任务类型: 逻辑推理类                 │
│  历史问答: ...                        │
└──────────────────────────────────────┘
                 ↓
          [LLM 推理]
                 ↓
┌──────────────────────────────────────┐
│       AIMessage (response)           │  ← LLM 的响应
│  {                                   │
│    "question": "...",                │
│    "answer": "...",                  │
│    "reasoning": "..."                │
│  }                                   │
└──────────────────────────────────────┘
```

**为什么这样设计？**

1. **角色分离**：
   - `SystemMessage`：定义"我是谁"、"我能做什么"
   - `HumanMessage`：定义"具体做什么"、"基于什么信息"

2. **上下文管理**：
   - 首次调用：只传入文档和任务类型
   - 后续调用：额外传入历史问答（实现 Curriculum Learning）

3. **结构化输出**：
   - Prompt 要求返回 JSON 格式
   - 便于解析和验证

### 3. 结构化输出与 Pydantic 集成

**从 LLM 响应到 Pydantic 模型**：

```python
def generate_qa_pair(self, ...):
    # ... 调用 LLM ...
    response = self.llm.invoke(messages)
    content = response.content
    
    # === 1. 清理响应内容 ===
    content = content.strip()
    # 移除 Markdown 代码块标记
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    
    # === 2. 解析 JSON ===
    try:
        result = json.loads(content)
    except json.JSONDecodeError as json_error:
        logger.error("Failed to parse JSON: {}", str(json_error))
        # 返回默认结构（容错处理）
        return {
            "question": "[JSON解析失败]",
            "answer": "生成的内容格式错误",
            "reasoning": f"JSON解析错误: {str(json_error)}"
        }
    
    # === 3. Pydantic 验证 ===
    try:
        output = ProposerOutput(**result)  # 自动类型校验
    except Exception as validation_error:
        logger.error("Failed to validate output: {}", str(validation_error))
        # 如果验证失败，返回原始 dict
        return result
    
    return output  # 返回 Pydantic 模型实例
```

**Pydantic 模型定义**：

**文件**: [src/models.py](../src/models.py)

```python
from pydantic import BaseModel, Field

class ProposerOutput(BaseModel):
    """Proposer 的输出模型"""
    question: str = Field(..., description="生成的问题")
    answer: str = Field(..., description="参考答案")
    difficulty_score: int = Field(..., ge=1, le=10, description="难度分数 1-10")
    reasoning: str = Field(..., description="生成理由")
```

**优势**：
- ✅ **自动验证**：`difficulty_score` 必须在 1-10 之间
- ✅ **类型安全**：`question` 必须是字符串
- ✅ **IDE 支持**：自动补全、类型提示
- ✅ **文档生成**：自动生成 API 文档

### 4. 三个 Agent 的实现对比

| Agent | 模型选择 | Temperature | 核心任务 | 特殊处理 |
|-------|---------|-------------|---------|---------|
| **Proposer** | `proposer_model` | 0.7（创造性） | 生成问题和参考答案 | 历史感知、难度递增 |
| **Solver** | `solver_model` | 0.3（准确性） | 基于文档回答问题 | 推理步骤展示、final_answer 必须是字符串 |
| **Validator** | `validator_model` | 0.3（一致性） | 评分和验证答案 | 对比参考答案、给出详细反馈 |

**SolverAgent 的特殊处理**：

```python
# src/agents.py - SolverAgent
def solve(self, document: str, question: str) -> SolverOutput:
    # ... LLM 调用 ...
    result = json.loads(content)
    
    # 关键：确保 final_answer 是字符串
    if "final_answer" in result and not isinstance(result["final_answer"], str):
        result["final_answer"] = str(result["final_answer"])
    
    output = SolverOutput(**result)
    return output
```

**为什么需要这个处理？**
- LLM 可能返回复杂结构（列表、字典）
- 但我们要求 `final_answer` 必须是字符串
- 显式转换确保类型一致性

**ValidatorAgent 的评分逻辑**：

```python
class ValidatorAgent:
    def validate(self, question: str, reference_answer: str, solver_answer: str) -> ValidatorOutput:
        # Prompt 包含详细评分标准
        user_prompt = PROMPTS["validator"]["user"].format(
            question=question,
            reference_answer=reference_answer,
            solver_answer=solver_answer
        )
        
        # ... 调用 LLM ...
        
        # 解析评分结果
        result = json.loads(content)
        return ValidatorOutput(**result)  # 包含 score, is_valid, reasoning, feedback
```

**评分标准**（在 Prompt 中定义）：

```
评估标准：
1. 核心信息是否一致（30%权重）
2. 关键事实是否准确（25%权重）
3. 推理过程是否清晰完整（20%权重）
4. 答案的详细程度和深度（10%权重）
5. 逻辑连贯性和表达流畅性（15%权重）

评分规则：
9-10分：完美答案，所有维度优秀
7-8分：正确答案，小瑕疵
5-6分：基本正确，有明显不足
3-4分：部分正确，重要错误
1-2分：错误答案
```

---

## 📊 LangGraph 应用详解

### 1. StateGraph 核心概念

**什么是 StateGraph？**

StateGraph 是 LangGraph 的核心抽象，管理：
- **State（状态）**：一个字典，存储工作流中的所有数据
- **Nodes（节点）**：执行具体任务的函数
- **Edges（边）**：定义节点间的流转关系

### 2. 项目中的 StateGraph 设计

**文件**: [src/graph.py](../src/graph.py#L15-L29)

```python
from langgraph.graph import StateGraph, END

class DataSynthesisGraph:
    """LangGraph 工作流"""
    
    def __init__(self):
        # 初始化三个 Agent
        self.proposer = ProposerAgent()
        self.solver = SolverAgent()
        self.validator = ValidatorAgent()
        
        # 构建图
        self.graph = self._build_graph()
        logger.info("DataSynthesisGraph initialized")
    
    def _build_graph(self) -> StateGraph:
        """构建状态图"""
        # 1. 创建工作流（state 是 dict 类型）
        workflow = StateGraph(dict)
        
        # 2. 添加节点
        workflow.add_node("propose", self._propose_node)
        workflow.add_node("solve", self._solve_node)
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("update", self._update_node)
        
        # 3. 设置入口点
        workflow.set_entry_point("propose")
        
        # 4. 添加固定边（顺序执行）
        workflow.add_edge("propose", "solve")
        workflow.add_edge("solve", "validate")
        workflow.add_edge("validate", "update")
        
        # 5. 添加条件边（根据 state 决定）
        workflow.add_conditional_edges(
            "update",
            self._should_continue,  # 判断函数
            {
                "continue": "propose",  # 继续下一轮
                "end": END              # 结束流程
            }
        )
        
        # 6. 编译图
        return workflow.compile()
```

### 3. 图结构可视化

```
         ┌──────────┐
         │  START   │
         └─────┬────┘
               │
               ▼
       ┌───────────────┐
       │   propose     │  生成问题
       │  (Proposer)   │
       └───────┬───────┘
               │ (固定边)
               ▼
       ┌───────────────┐
       │    solve      │  求解问题
       │   (Solver)    │
       └───────┬───────┘
               │ (固定边)
               ▼
       ┌───────────────┐
       │   validate    │  验证答案
       │  (Validator)  │
       └───────┬───────┘
               │ (固定边)
               ▼
       ┌───────────────┐
       │    update     │  更新计数
       │               │
       └───────┬───────┘
               │ (条件边)
          ┌────┴────┐
          │  判断   │
          └────┬────┘
               │
         ┌─────┴─────┐
        Yes         No
         │           │
    "continue"    "end"
         │           │
         │           ▼
         │      ┌────────┐
         │      │  END   │
         │      └────────┘
         │
         └──────┐
                │
                ▼
          (回到 propose)
```

### 4. State 设计详解

**State 是什么？**

State 是一个字典，贯穿整个工作流，存储所有中间状态：

```python
state = {
    # === 输入参数 ===
    "document": str,              # 文档内容
    "task_type": str,             # 任务类型
    "max_iterations": int,        # 最大迭代次数
    "score_threshold": float,     # 验证阈值
    
    # === 迭代控制 ===
    "current_iteration": int,     # 当前迭代次数（从 0 开始）
    "is_complete": bool,          # 是否完成
    "failed_attempts": int,       # 失败次数
    
    # === 当前迭代的临时数据 ===
    "current_question": str,           # 当前问题
    "current_reference_answer": str,   # 参考答案
    "current_reasoning": str,          # 生成理由
    "current_solver_answer": str,      # Solver 的答案
    
    # === 累积结果 ===
    "history_buffer": List[Dict],      # 历史问答（用于 Curriculum Learning）
    "valid_pairs": List[Dict],         # 通过验证的问答对（最终输出）
    "iteration_details": List[Dict],   # 每次迭代的详细信息（用于 UI 展示）
    
    # === 临时字段 ===
    "current_iteration_detail": Dict,  # 当前迭代详情（临时）
}
```

**State 的生命周期**：

```
初始化 state
    ↓
propose_node (修改 state)
    ↓
solve_node (修改 state)
    ↓
validate_node (修改 state)
    ↓
update_node (修改 state)
    ↓
should_continue (读取 state，返回 "continue" 或 "end")
    ↓
如果 "continue"：回到 propose_node（state 保留所有修改）
如果 "end"：流程结束，返回最终 state
```

### 5. 节点实现详解

#### propose_node（生成问题）

```python
def _propose_node(self, state: dict) -> dict:
    """Proposer 节点：生成新的问答对"""
    
    logger.info(
        "=== Iteration {}/{} ===",
        state["current_iteration"] + 1,
        state["max_iterations"]
    )
    
    # 1. 初始化迭代详情（用于 UI 展示）
    iteration_detail = {
        "iteration": state["current_iteration"] + 1,
        "proposer_output": None,
        "solver_output": None,
        "validator_output": None,
        "is_valid": False,
    }
    
    try:
        # 2. 调用 ProposerAgent
        output = self.proposer.generate_qa_pair(
            document=state["document"],
            task_type=TaskType(state["task_type"]),
            history_buffer=state["history_buffer"]  # 传入历史
        )
        
        # 3. 处理返回结果（兼容 Pydantic 模型和 dict）
        if isinstance(output, dict):
            question = output.get("question", "")
            answer = output.get("answer", "")
            reasoning = output.get("reasoning", "")
        else:
            question = output.question
            answer = output.answer
            reasoning = output.reasoning
        
        # 4. 更新 state
        state["current_question"] = question
        state["current_reference_answer"] = answer
        state["current_reasoning"] = reasoning
        
        # 5. 保存到迭代详情
        iteration_detail["proposer_output"] = {
            "question": question,
            "answer": answer,
            "reasoning": reasoning,
        }
        
        logger.success("Question generated: {}", question[:100])
        
    except Exception as e:
        # 6. 错误处理：不中断流程，使用默认值
        logger.error("Proposer failed: {}", str(e))
        state["current_question"] = "[生成失败]"
        state["current_reference_answer"] = "发生错误"
        iteration_detail["proposer_output"] = {
            "question": "[生成失败]",
            "answer": "发生错误",
            "reasoning": f"错误: {str(e)}",
        }
    
    # 7. 暂存迭代详情（后续节点会继续更新）
    state["current_iteration_detail"] = iteration_detail
    
    return state  # 返回修改后的 state
```

**设计要点**：

1. **错误容忍**：即使 Proposer 失败，也不抛出异常，用默认值继续
2. **历史感知**：传入 `history_buffer` 实现 Curriculum Learning
3. **详情记录**：保存详细信息供 UI 展示
4. **兼容性处理**：同时支持 Pydantic 模型和 dict 返回

#### solve_node（求解问题）

```python
def _solve_node(self, state: dict) -> dict:
    """Solver 节点：尝试回答问题"""
    
    logger.info("Solver attempting to answer...")
    
    try:
        # 1. 调用 SolverAgent
        output = self.solver.solve(
            document=state["document"],
            question=state["current_question"]  # 使用 Proposer 生成的问题
        )
        
        # 2. 处理返回结果
        if isinstance(output, dict):
            reasoning_steps = output.get("reasoning_steps", [])
            final_answer = output.get("final_answer", "")
        else:
            reasoning_steps = output.reasoning_steps
            final_answer = output.final_answer
        
        # 3. 类型安全检查（关键！）
        if not isinstance(final_answer, str):
            logger.warning("final_answer is not a string, converting: {}", type(final_answer))
            final_answer = str(final_answer)
        
        # 4. 更新 state
        state["current_solver_answer"] = final_answer
        
        # 5. 保存到迭代详情
        if "current_iteration_detail" in state:
            state["current_iteration_detail"]["solver_output"] = {
                "reasoning_steps": reasoning_steps,
                "final_answer": final_answer,
            }
        
        # 6. 安全的日志输出（避免 slice 错误）
        preview = final_answer[:100] if len(final_answer) > 100 else final_answer
        logger.success("Solver answer: {}", preview)
        
    except Exception as e:
        logger.error("Solver failed: {}", str(e))
        state["current_solver_answer"] = f"求解失败: {str(e)}"
        if "current_iteration_detail" in state:
            state["current_iteration_detail"]["solver_output"] = {
                "reasoning_steps": ["发生错误"],
                "final_answer": f"错误: {str(e)}",
            }
    
    return state
```

**设计要点**：

1. **类型转换**：确保 `final_answer` 是字符串（修复了之前的 bug）
2. **安全日志**：先检查长度再 slice，避免"unhashable type"错误
3. **错误传递**：失败时将错误信息保存到 state，供后续节点处理

#### validate_node（验证答案）

```python
def _validate_node(self, state: dict) -> dict:
    """Validator 节点：验证答案质量"""
    
    logger.info("Validator checking answer...")
    
    try:
        # 1. 调用 ValidatorAgent
        output = self.validator.validate(
            question=state["current_question"],
            reference_answer=state["current_reference_answer"],
            solver_answer=state["current_solver_answer"]
        )
        
        # 2. 处理返回结果
        if isinstance(output, dict):
            score = output.get("score", 0)
            reasoning = output.get("reasoning", "")
            feedback = output.get("feedback", "")
        else:
            score = output.score
            reasoning = output.reasoning
            feedback = output.feedback
        
        # 3. 判断是否通过验证
        score_threshold = state.get("score_threshold", settings.score_threshold)
        is_valid = score >= score_threshold
        
        # 4. 保存验证结果到迭代详情
        if "current_iteration_detail" in state:
            state["current_iteration_detail"]["validator_output"] = {
                "score": score,
                "is_valid": is_valid,
                "reasoning": reasoning,
                "feedback": feedback,
            }
            state["current_iteration_detail"]["is_valid"] = is_valid
        
        # 5. 如果通过验证
        if is_valid:
            logger.success("✓ Validation PASSED (score: {}/10)", score)
            
            # 5.1 创建问答对
            qa_pair = {
                "question": state["current_question"],
                "answer": state["current_reference_answer"],
                "reasoning": state["current_reasoning"],
                "task_type": state["task_type"],
                "iteration": state["current_iteration"] + 1,
                "score": score,  # 保存分数
            }
            
            # 5.2 添加到 valid_pairs（最终输出）
            if "valid_pairs" not in state:
                state["valid_pairs"] = []
            state["valid_pairs"].append(qa_pair)
            
            # 5.3 添加到 history_buffer（用于后续生成）
            if "history_buffer" not in state:
                state["history_buffer"] = []
            state["history_buffer"].append(qa_pair)
            
            logger.info("Valid QA pairs: {}", len(state["valid_pairs"]))
        
        # 6. 如果未通过验证
        else:
            logger.warning("✗ Validation FAILED (score: {}/10): {}", score, feedback)
            state["failed_attempts"] = state.get("failed_attempts", 0) + 1
        
    except Exception as e:
        logger.error("Validator failed: {}", str(e))
        # 错误视为验证失败
        state["failed_attempts"] = state.get("failed_attempts", 0) + 1
    
    return state
```

**设计要点**：

1. **双重存储**：
   - `valid_pairs`：通过验证的问答对（最终输出到文件）
   - `history_buffer`：所有通过验证的问答对（用于 Curriculum Learning）

2. **分数保存**：将 score 保存到 QA pair，便于后续分析

3. **失败计数**：跟踪失败次数，可用于自适应策略

#### update_node（更新状态）

```python
def _update_node(self, state: dict) -> dict:
    """Update 节点：更新迭代计数，整理数据"""
    
    # 1. 将当前迭代详情添加到列表
    if "current_iteration_detail" in state:
        if "iteration_details" not in state:
            state["iteration_details"] = []
        state["iteration_details"].append(state["current_iteration_detail"])
        
        # 清理临时字段
        del state["current_iteration_detail"]
    
    # 2. 迭代计数 +1
    state["current_iteration"] += 1
    
    # 3. 检查是否应该结束
    if state["current_iteration"] >= state["max_iterations"]:
        state["is_complete"] = True
        logger.info("Max iterations reached. Synthesis complete.")
    elif state.get("error"):
        state["is_complete"] = True
        logger.error("Error occurred. Stopping synthesis.")
    
    return state
```

**设计要点**：

1. **数据整理**：将临时字段移到持久列表
2. **终止条件**：检查是否达到最大迭代次数或发生错误
3. **清理临时数据**：删除 `current_iteration_detail`，避免混淆

### 6. 条件边：流程控制

```python
def _should_continue(self, state: dict) -> str:
    """判断是否继续迭代"""
    
    if state.get("is_complete", False):
        return "end"  # 结束流程
    
    return "continue"  # 继续下一轮
```

**条件边的作用**：

```python
workflow.add_conditional_edges(
    "update",                # 从 update 节点出发
    self._should_continue,   # 调用判断函数
    {
        "continue": "propose",  # 返回 "continue" → 跳转到 propose
        "end": END              # 返回 "end" → 结束流程
    }
)
```

**实现循环**：

```
┌─────────────┐
│   propose   │ ◀────────┐
└──────┬──────┘          │
       ↓                 │
┌─────────────┐          │
│    solve    │          │
└──────┬──────┘          │
       ↓                 │
┌─────────────┐          │
│  validate   │          │
└──────┬──────┘          │
       ↓                 │
┌─────────────┐          │
│   update    │          │
└──────┬──────┘          │
       ↓                 │
 [should_continue?]      │
       │                 │
  ┌────┴────┐            │
 "continue" "end"        │
       │      │          │
       └──────┘          │
      (循环回去)  (结束)
```

### 7. 执行工作流

**在 Web UI 中的调用**：

```python
# web_ui.py
def run_synthesis(document, task_type, max_iterations, score_threshold, ...):
    # 1. 初始化 state
    state = {
        "document": document,
        "task_type": task_type,
        "max_iterations": max_iterations,
        "score_threshold": score_threshold,
        "current_iteration": 0,
        "history_buffer": [],
        "valid_pairs": [],
        "iteration_details": [],
        "is_complete": False,
    }
    
    # 2. 流式执行 Graph
    for step in graph.stream(state):
        # step 是每次节点执行后的 state 快照
        
        # 提取当前迭代详情
        if "iteration_details" in step and len(step["iteration_details"]) > 0:
            latest_detail = step["iteration_details"][-1]
            
            # 实时更新 UI
            yield format_iteration_detail(latest_detail)
    
    # 3. 返回最终结果
    return step["valid_pairs"]
```

**流式输出的优势**：

```
传统方式：                LangGraph stream：
┌────────────┐           ┌────────────┐
│  开始执行  │           │  开始执行  │
└─────┬──────┘           └─────┬──────┘
      │                        │
   [等待]                   ┌──▼──────┐
   [等待]                   │ Step 1  │ → yield state
   [等待]                   └──┬──────┘
   [等待]                      │
   [等待]                   ┌──▼──────┐
      │                     │ Step 2  │ → yield state
      ▼                     └──┬──────┘
┌────────────┐                 │
│  返回结果  │              ┌──▼──────┐
└────────────┘              │ Step 3  │ → yield state
                            └──┬──────┘
                               ▼
                          ┌────────────┐
                          │  最终结果  │
                          └────────────┘
```

用户体验：
- **传统**：等待全部完成才看到结果（数分钟）
- **流式**：每完成一步立即反馈（实时进度）

---

## 🔄 完整工作流解析

### 端到端示例

假设用户输入：
- 文档：关于"光合作用"的科普文章
- 任务类型：逻辑推理类
- 最大迭代：5 次
- 验证阈值：7 分

**第一次迭代**：

```
1. propose_node:
   输入: state["document"] = "光合作用是..."
        state["history_buffer"] = []  # 首次为空
   
   Proposer 生成:
   {
     "question": "光合作用的主要产物是什么？",
     "answer": "氧气和葡萄糖",
     "difficulty_score": 2  # 低难度（1-2分）
   }
   
   输出: state["current_question"] = "光合作用的主要产物是什么？"
        state["current_reference_answer"] = "氧气和葡萄糖"

2. solve_node:
   输入: state["current_question"] = "光合作用的主要产物是什么？"
   
   Solver 回答:
   {
     "reasoning_steps": [
       "1. 根据文档，光合作用利用光能",
       "2. 将二氧化碳和水转化为有机物",
       "3. 主要产物是葡萄糖和氧气"
     ],
     "final_answer": "氧气和葡萄糖"
   }
   
   输出: state["current_solver_answer"] = "氧气和葡萄糖"

3. validate_node:
   输入: question = "光合作用的主要产物是什么？"
        reference_answer = "氧气和葡萄糖"
        solver_answer = "氧气和葡萄糖"
   
   Validator 评分:
   {
     "score": 9.5,
     "is_valid": True,
     "reasoning": "答案完全正确，简洁明了",
     "feedback": "优秀答案"
   }
   
   输出: state["valid_pairs"].append({...})  # 通过验证！
        state["history_buffer"].append({...})

4. update_node:
   输出: state["current_iteration"] = 1
        state["is_complete"] = False  # 未达到 5 次

5. should_continue:
   返回: "continue"  # 回到 propose_node
```

**第二次迭代**：

```
1. propose_node:
   输入: state["history_buffer"] = [
           {"question": "光合作用的主要产物是什么？", "answer": "...", "difficulty_score": 2}
         ]
   
   Proposer 生成:  # 基于历史，难度递增
   {
     "question": "光合作用的光反应和暗反应有何区别？",
     "answer": "光反应需要光能，发生在类囊体膜；暗反应不需要光，发生在叶绿体基质...",
     "difficulty_score": 5  # 难度提升
   }
   
   # 后续流程类似...
```

**最终输出**（5 次迭代后）：

```json
{
  "valid_pairs": [
    {
      "question": "光合作用的主要产物是什么？",
      "answer": "氧气和葡萄糖",
      "score": 9.5,
      "difficulty_score": 2,
      "iteration": 1
    },
    {
      "question": "光合作用的光反应和暗反应有何区别？",
      "answer": "...",
      "score": 8.7,
      "difficulty_score": 5,
      "iteration": 2
    },
    // ... 更多问答对
  ],
  "iteration_details": [
    {
      "iteration": 1,
      "proposer_output": {...},
      "solver_output": {...},
      "validator_output": {...},
      "is_valid": true
    },
    // ... 更多迭代详情
  ]
}
```

### State 变化追踪

| 迭代 | current_iteration | history_buffer 大小 | valid_pairs 大小 | 难度趋势 |
|------|------------------|---------------------|------------------|---------|
| 0 | 0 | 0 | 0 | - |
| 1 | 1 | 1 | 1 | 2 分（低难度） |
| 2 | 2 | 2 | 2 | 5 分（中等） |
| 3 | 3 | 3 | 3 | 7 分（较难） |
| 4 | 4 | 4 | 4 | 8 分（难） |
| 5 | 5 | 5 | 5 | 9 分（高难度） |

---

## 🎓 高级技巧

### 1. 自定义节点

**添加 Refiner 节点**（精炼问答对）：

```python
def _build_graph(self):
    workflow = StateGraph(dict)
    
    # 添加新节点
    workflow.add_node("refine", self._refine_node)
    
    # 调整边
    workflow.add_edge("validate", "refine")  # validate → refine
    workflow.add_edge("refine", "update")    # refine → update
    
    return workflow.compile()

def _refine_node(self, state: dict) -> dict:
    """精炼节点：优化问答对的表述"""
    
    # 只对通过验证的问答对进行精炼
    if not state["current_iteration_detail"]["is_valid"]:
        return state  # 跳过未通过的
    
    # 调用 RefinerAgent
    refined_qa = self.refiner.refine(
        question=state["current_question"],
        answer=state["current_reference_answer"]
    )
    
    # 更新 state
    state["current_question"] = refined_qa["question"]
    state["current_reference_answer"] = refined_qa["answer"]
    
    return state
```

### 2. 并行节点

**同时运行多个 Solver**：

```python
def _build_graph(self):
    workflow = StateGraph(dict)
    
    workflow.add_node("propose", self._propose_node)
    
    # 添加多个 Solver 节点
    workflow.add_node("solve_1", self._solve_node_1)
    workflow.add_node("solve_2", self._solve_node_2)
    workflow.add_node("solve_3", self._solve_node_3)
    
    # 并行执行 Solvers
    workflow.add_edge("propose", "solve_1")
    workflow.add_edge("propose", "solve_2")
    workflow.add_edge("propose", "solve_3")
    
    # 添加 merge 节点
    workflow.add_node("merge", self._merge_solvers)
    workflow.add_edge("solve_1", "merge")
    workflow.add_edge("solve_2", "merge")
    workflow.add_edge("solve_3", "merge")
    
    workflow.add_node("validate", self._validate_node)
    workflow.add_edge("merge", "validate")
    
    return workflow.compile()

def _merge_solvers(self, state: dict) -> dict:
    """合并多个 Solver 的答案"""
    
    answers = [
        state["solver_1_answer"],
        state["solver_2_answer"],
        state["solver_3_answer"]
    ]
    
    # 使用投票、平均或其他策略选择最佳答案
    state["current_solver_answer"] = self._select_best_answer(answers)
    
    return state
```

### 3. 子图（Subgraph）

**将验证逻辑封装为子图**：

```python
def _build_validation_subgraph(self):
    """构建验证子图"""
    subgraph = StateGraph(dict)
    
    subgraph.add_node("validate", self._validate_node)
    subgraph.add_node("review", self._review_node)  # 人工审核
    
    subgraph.set_entry_point("validate")
    
    subgraph.add_conditional_edges(
        "validate",
        lambda state: "review" if state["score"] < 7 else "end",
        {
            "review": "review",
            "end": END
        }
    )
    
    return subgraph.compile()

def _build_graph(self):
    workflow = StateGraph(dict)
    
    # 使用子图
    workflow.add_node("validation_flow", self.validation_subgraph)
    
    return workflow.compile()
```

### 4. 持久化 State

**保存和恢复工作流状态**：

```python
import pickle

def save_state(state: dict, filepath: str):
    """保存 state 到文件"""
    with open(filepath, 'wb') as f:
        pickle.dump(state, f)

def load_state(filepath: str) -> dict:
    """从文件加载 state"""
    with open(filepath, 'rb') as f:
        return pickle.load(f)

# 使用示例
def run_synthesis_with_checkpoints(document, task_type, ...):
    # 尝试加载之前的 state
    checkpoint_file = "checkpoint.pkl"
    if os.path.exists(checkpoint_file):
        state = load_state(checkpoint_file)
        logger.info("Resuming from iteration {}", state["current_iteration"])
    else:
        # 初始化新的 state
        state = {...}
    
    # 执行 Graph
    for step in graph.stream(state):
        # 定期保存 checkpoint
        if step["current_iteration"] % 5 == 0:
            save_state(step, checkpoint_file)
        
        yield step
    
    # 完成后删除 checkpoint
    os.remove(checkpoint_file)
```

### 5. 动态修改 Graph

**运行时调整流程**：

```python
def create_dynamic_graph(use_refiner: bool = False):
    """根据配置动态构建 Graph"""
    
    workflow = StateGraph(dict)
    
    workflow.add_node("propose", propose_node)
    workflow.add_node("solve", solve_node)
    workflow.add_node("validate", validate_node)
    
    if use_refiner:
        workflow.add_node("refine", refine_node)
        workflow.add_edge("validate", "refine")
        workflow.add_edge("refine", "update")
    else:
        workflow.add_edge("validate", "update")
    
    workflow.add_node("update", update_node)
    
    # ... 其他配置 ...
    
    return workflow.compile()

# 使用
graph_with_refiner = create_dynamic_graph(use_refiner=True)
graph_without_refiner = create_dynamic_graph(use_refiner=False)
```

---

## ❓ 常见问题

### Q1: State 修改不生效？

**问题**：
```python
def my_node(self, state: dict) -> dict:
    state["key"] = "value"
    # 忘记 return state！
```

**解决**：
```python
def my_node(self, state: dict) -> dict:
    state["key"] = "value"
    return state  # 必须返回！
```

**原理**：LangGraph 要求节点函数返回修改后的 state，返回值会成为下一个节点的输入。

### Q2: 条件边不执行？

**问题**：
```python
def _should_continue(self, state: dict) -> str:
    if state["is_complete"]:
        return "finished"  # 错误的键名
    return "continue"

workflow.add_conditional_edges(
    "update",
    self._should_continue,
    {
        "continue": "propose",
        "end": END  # "finished" 不在这里！
    }
)
```

**解决**：确保返回值匹配字典的键：
```python
def _should_continue(self, state: dict) -> str:
    if state["is_complete"]:
        return "end"  # 匹配字典键
    return "continue"
```

### Q3: 如何调试 Graph？

**方法 1：日志**：
```python
def _propose_node(self, state: dict) -> dict:
    logger.debug("State before: {}", state.keys())
    
    # ... 处理逻辑 ...
    
    logger.debug("State after: {}", state.keys())
    return state
```

**方法 2：可视化**：
```python
# 生成 Mermaid 流程图
from langgraph.graph import StateGraph

workflow = StateGraph(dict)
# ... 构建 Graph ...
graph = workflow.compile()

# 输出 Mermaid 代码
print(graph.get_graph().draw_mermaid())
```

**方法 3：断点**：
```python
def _propose_node(self, state: dict) -> dict:
    breakpoint()  # 暂停在这里
    
    output = self.proposer.generate_qa_pair(...)
    return state
```

### Q4: LangChain 的 invoke() 和 stream() 区别？

**invoke()**：
```python
response = llm.invoke(messages)
# 等待完整响应
print(response.content)  # 一次性输出全部内容
```

**stream()**：
```python
for chunk in llm.stream(messages):
    # 逐块接收响应
    print(chunk.content, end="", flush=True)  # 打字机效果
```

**项目中的选择**：
- **Agent 调用 LLM**：使用 `invoke()`（需要完整 JSON）
- **Graph 执行**：使用 `stream()`（实时反馈进度）

### Q5: 如何处理 LLM 返回的非 JSON？

**问题**：LLM 返回 `Here is the answer: {"question": "..."}`（包含前缀）

**解决方案**（项目中的实现）：

```python
def parse_llm_response(content: str) -> dict:
    """鲁棒的 JSON 解析"""
    
    # 1. 移除 Markdown 代码块
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    
    # 2. 尝试找到 JSON 部分
    try:
        # 尝试直接解析
        return json.loads(content)
    except json.JSONDecodeError:
        # 3. 尝试提取 {...} 或 [...]
        import re
        
        # 查找第一个 { 到最后一个 }
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        
        # 查找第一个 [ 到最后一个 ]
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        
        # 4. 完全失败，抛出异常
        raise ValueError(f"Cannot extract JSON from: {content[:100]}")
```

### Q6: 如何限制 LLM 调用次数？

**方法 1：在 Graph 层面**：
```python
def _should_continue(self, state: dict) -> str:
    # 检查总调用次数
    total_calls = state["current_iteration"] * 3  # 每次迭代 3 个 Agent
    if total_calls >= 100:
        logger.warning("Reached max LLM calls")
        return "end"
    
    # ... 其他判断 ...
    return "continue"
```

**方法 2：在 Agent 层面**：
```python
class ProposerAgent:
    def __init__(self):
        self.llm = get_llm()
        self.call_count = 0
        self.max_calls = 50
    
    def generate_qa_pair(self, ...):
        if self.call_count >= self.max_calls:
            raise Exception("Max LLM calls reached")
        
        self.call_count += 1
        response = self.llm.invoke(messages)
        # ...
```

---

## 📚 扩展阅读

### 官方文档

- **LangChain**: https://python.langchain.com/docs/
  - [Chat Models](https://python.langchain.com/docs/integrations/chat/)
  - [Messages](https://python.langchain.com/docs/concepts/messages/)
  
- **LangGraph**: https://langchain-ai.github.io/langgraph/
  - [State Management](https://langchain-ai.github.io/langgraph/concepts/low_level/#state-management)
  - [Conditional Edges](https://langchain-ai.github.io/langgraph/how-tos/branching/)

### 相关项目

- **LangChain Templates**: https://github.com/langchain-ai/langchain/tree/master/templates
- **LangGraph Examples**: https://github.com/langchain-ai/langgraph/tree/main/examples

### 最佳实践

1. **State 设计**：
   - 保持 state 扁平化，避免深层嵌套
   - 明确区分临时数据和持久数据
   - 使用类型提示（TypedDict）

2. **错误处理**：
   - 在节点内部捕获异常，不要让错误中断流程
   - 记录详细日志，便于排查问题
   - 设置超时和重试机制

3. **性能优化**：
   - 并行执行独立节点
   - 缓存重复调用的结果
   - 限制 history_buffer 大小

4. **可观测性**：
   - 记录每个节点的输入输出
   - 保存完整的 iteration_details
   - 使用结构化日志（JSON）

---

## 🎯 总结

本项目充分利用了 LangChain 和 LangGraph 的优势：

**LangChain**：
- ✅ 统一的 LLM 接口（`ChatOpenAI`）
- ✅ 结构化消息（`SystemMessage`, `HumanMessage`）
- ✅ 灵活的配置（`get_llm` 工厂函数）

**LangGraph**：
- ✅ 清晰的状态管理（`state` 字典）
- ✅ 模块化的节点设计（`propose`, `solve`, `validate`, `update`）
- ✅ 灵活的流程控制（条件边实现循环）
- ✅ 流式输出（实时反馈进度）

**核心设计模式**：
- 🎨 三智能体协作（Proposer → Solver → Validator）
- 🔄 Iterative Curriculum（基于历史递增难度）
- 📊 状态驱动（所有数据存储在 state 中）
- 🔀 条件循环（动态决定是否继续）

通过这种架构，项目实现了：
- 🚀 **高扩展性**：易于添加新 Agent、新节点
- 🛡️ **高容错性**：单个 Agent 失败不影响整体流程
- 📈 **高可观测性**：完整的日志和进度反馈
- 🎯 **高质量输出**：三智能体协作确保问答对质量

---

**文档版本**: v1.0  
**最后更新**: 2025-12-27  
**作者**: Data Synthesis System Team
