# 开发指南

本文档面向需要对系统进行二次开发、定制或深入理解代码的开发者。

---

## 📖 目录

- [项目结构](#项目结构)
- [核心模块详解](#核心模块详解)
- [开发环境搭建](#开发环境搭建)
- [扩展开发](#扩展开发)
- [调试技巧](#调试技巧)
- [性能优化](#性能优化)

---

## 📁 项目结构

```
multimodal-data-synthesis-system/
├── config/                      # 配置模块
│   ├── __init__.py
│   ├── llm_config.py           # LLM API 配置
│   ├── prompts.py              # Prompt 模板配置
│   └── settings.py             # 系统设置
├── src/                         # 源代码
│   ├── __init__.py
│   ├── agents.py               # Agent 实现
│   ├── graph.py                # LangGraph 工作流
│   ├── models.py               # 数据模型（Pydantic）
│   └── utils.py                # 工具函数
├── data/                        # 数据目录
│   ├── uploads/                # 上传的图片
│   └── outputs/                # 生成的数据集
├── logs/                        # 日志文件
├── docs/                        # 文档
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   └── ARCHITECTURE.md
├── web_ui.py                    # Gradio Web 界面
├── init_system.py               # 系统初始化脚本
├── requirements.txt             # Python 依赖
├── start.sh                     # 启动脚本
├── .env.example                 # 环境变量示例
└── README.md                    # 项目说明
```

---

## 🔧 核心模块详解

### 1. 配置模块 (`config/`)

#### `llm_config.py` - LLM 配置

**职责**：管理 LLM API 的配置参数

```python
from config.llm_config import llm_config

# 访问配置
print(llm_config.api_key)
print(llm_config.model_name)

# 修改配置
llm_config.temperature = 0.5
```

**关键属性**：
- `api_key`: API 密钥
- `base_url`: API 地址
- `model_name`: 模型名称
- `temperature`: 温度参数
- `max_tokens`: 最大 token 数

**扩展示例**：添加新模型配置

```python
# 在 llm_config.py 中添加
class LLMConfig(BaseModel):
    # ... 现有配置 ...
    
    # 新增：支持多个模型配置
    models: Dict[str, str] = Field(
        default={
            "vision": "gpt-4-vision-preview",
            "text": "gpt-4-turbo",
            "embedding": "text-embedding-3-large"
        }
    )
```

#### `prompts.py` - Prompt 配置

**职责**：管理所有 Agent 的 Prompt 模板

**核心方法**：

```python
from config.prompts import prompts_config

# 格式化提议者 Prompt
system_prompt, user_prompt = prompts_config.format_proposer_prompt(
    task_type="图片问答类",
    difficulty_level=0.5,
    history_qa_pairs=[...]
)
```

**扩展示例**：添加新的任务类型

```python
# 在 prompts.py 的 PromptsConfig 类中
task_descriptions: Dict[str, str] = Field(
    default={
        # ... 现有任务类型 ...
        
        # 新增：图表分析类
        "图表分析类": "生成关于图表数据解读、趋势分析、对比的问题",
        
        # 新增：艺术鉴赏类
        "艺术鉴赏类": "生成关于艺术作品风格、技法、情感表达的问题"
    }
)
```

#### `settings.py` - 系统设置

**职责**：管理系统级别的配置

**关键配置**：

```python
from config.settings import settings

# 访问目录配置
print(settings.UPLOAD_DIR)
print(settings.OUTPUT_DIR)

# 访问运行参数
print(settings.MAX_ITERATIONS)
print(settings.DIFFICULTY_INCREMENT)
```

**自定义配置**：

```python
# 创建自定义设置实例
custom_settings = SystemSettings(
    MAX_ITERATIONS=20,
    INITIAL_DIFFICULTY=0.5
)
```

---

### 2. 数据模型 (`src/models.py`)

**使用 Pydantic 进行数据验证和序列化**

#### 核心模型

**`QAPair` - 问答对**

```python
from src.models import QAPair

qa = QAPair(
    question="图片中有什么？",
    answer="一只猫",
    difficulty=0.3,
    iteration=1
)

# 验证会自动进行
print(qa.dict())  # 转换为字典
print(qa.json())  # 转换为 JSON
```

**`SynthesisTask` - 合成任务**

```python
from src.models import SynthesisTask, ImageInfo

task = SynthesisTask(
    task_id="task_001",
    task_type="图片问答类",
    images=[ImageInfo(path="/path/to/img.jpg", filename="img.jpg")],
    max_iterations=10
)
```

**`AgentState` - Agent 状态**

这是 LangGraph 的核心状态对象：

```python
from src.models import AgentState

state = AgentState(
    task=task,
    image_paths=["/path/to/img.jpg"],
    current_iteration=0,
    history_qa_pairs=[]
)
```

#### 扩展新模型

**场景**：添加用户反馈功能

```python
# 在 models.py 中添加
class UserFeedback(BaseModel):
    """用户反馈"""
    qa_id: str = Field(..., description="问答对ID")
    rating: int = Field(..., ge=1, le=5, description="评分1-5")
    comment: Optional[str] = Field(None, description="评论")
    created_at: datetime = Field(default_factory=datetime.now)

# 扩展 QAPair
class QAPair(BaseModel):
    # ... 现有字段 ...
    
    feedbacks: List[UserFeedback] = Field(
        default_factory=list,
        description="用户反馈列表"
    )
```

---

### 3. Agent 模块 (`src/agents.py`)

#### `MultimodalLLMClient` - LLM 客户端

**职责**：封装多模态 LLM API 调用

**核心方法**：

```python
from src.agents import MultimodalLLMClient

client = MultimodalLLMClient()

response = client.call_with_images(
    system_prompt="你是一个助手",
    user_prompt="描述这张图片",
    image_paths=["/path/to/image.jpg"],
    temperature=0.7
)
```

**内部实现**：

```python
def call_with_images(self, system_prompt, user_prompt, image_paths, temperature):
    # 1. 构建消息
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt},
                # 将图片编码为 base64
                *[{"type": "image_url", "image_url": {"url": get_image_data_url(path)}}
                  for path in image_paths]
            ]
        }
    ]
    
    # 2. 调用 OpenAI API
    response = self.client.chat.completions.create(
        model=self.config.model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=self.config.max_tokens
    )
    
    return response.choices[0].message.content
```

#### `ProposerAgent` - 提议者

**职责**：生成新的问答对

**关键方法**：

```python
def propose(self, image_paths, task_type, difficulty, history_qa_pairs):
    # 1. 格式化 Prompt
    system_prompt, user_prompt = self.prompts_config.format_proposer_prompt(...)
    
    # 2. 调用 LLM
    response = self.llm_client.call_with_images(...)
    
    # 3. 解析 JSON 响应
    result = extract_json_from_text(response)
    
    # 4. 返回结构化输出
    return ProposerOutput(
        question=result["question"],
        answer=result["answer"]
    )
```

**扩展示例**：添加问题多样性检查

```python
def propose(self, image_paths, task_type, difficulty, history_qa_pairs):
    max_retries = 3
    
    for attempt in range(max_retries):
        output = self._generate_qa(...)
        
        # 检查问题是否与历史重复
        if self._is_diverse_enough(output.question, history_qa_pairs):
            return output
        
        logger.warning(f"问题重复，重试 {attempt + 1}/{max_retries}")
    
    raise Exception("无法生成多样化的问题")

def _is_diverse_enough(self, new_question, history):
    # 使用编辑距离或语义相似度判断
    from difflib import SequenceMatcher
    
    for qa in history:
        similarity = SequenceMatcher(None, new_question, qa.question).ratio()
        if similarity > 0.8:  # 相似度过高
            return False
    
    return True
```

#### `SolverAgent` - 求解者

**职责**：尝试回答问题

```python
def solve(self, image_paths, question):
    # 调用 LLM 基于图片回答问题
    system_prompt, user_prompt = self.prompts_config.format_solver_prompt(question)
    response = self.llm_client.call_with_images(...)
    result = extract_json_from_text(response)
    return SolverOutput(answer=result["answer"])
```

#### `ValidatorAgent` - 验证者

**职责**：评估答案质量

```python
def validate(self, image_paths, question, reference_answer, predicted_answer):
    # 调用 LLM 比较两个答案的语义相似度
    system_prompt, user_prompt = self.prompts_config.format_validator_prompt(...)
    response = self.llm_client.call_with_images(...)
    result = extract_json_from_text(response)
    
    return ValidationResult(
        is_valid=result["is_valid"],
        similarity_score=result["similarity_score"],
        reason=result["reason"]
    )
```

**扩展示例**：添加基于规则的验证

```python
def validate(self, image_paths, question, reference_answer, predicted_answer):
    # 1. LLM 验证
    llm_validation = self._llm_validate(...)
    
    # 2. 规则验证
    rule_validation = self._rule_validate(reference_answer, predicted_answer)
    
    # 3. 综合判断
    final_score = 0.7 * llm_validation.similarity_score + \
                  0.3 * rule_validation.score
    
    return ValidationResult(
        is_valid=final_score > self.validation_threshold,
        similarity_score=final_score,
        reason=f"LLM: {llm_validation.reason}, 规则: {rule_validation.reason}"
    )

def _rule_validate(self, ref, pred):
    """基于规则的验证"""
    # 示例：关键词匹配
    ref_keywords = set(ref.lower().split())
    pred_keywords = set(pred.lower().split())
    
    overlap = len(ref_keywords & pred_keywords)
    score = overlap / len(ref_keywords) if ref_keywords else 0
    
    return SimpleNamespace(
        score=score,
        reason=f"关键词重叠度: {score:.2f}"
    )
```

---

### 4. 工作流模块 (`src/graph.py`)

**基于 LangGraph 实现状态机工作流**

#### 工作流结构

```
check_continue → propose → solve → validate → update_state → check_continue
       ↓                                                            ↑
      END ←─────────────────────────────────────────────────────────┘
```

#### 核心方法

**`_build_graph()` - 构建工作流**

```python
def _build_graph(self):
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("check_continue", self._check_continue)
    workflow.add_node("propose", self._propose_node)
    workflow.add_node("solve", self._solve_node)
    workflow.add_node("validate", self._validate_node)
    workflow.add_node("update_state", self._update_state_node)
    
    # 设置入口
    workflow.set_entry_point("check_continue")
    
    # 添加条件边
    workflow.add_conditional_edges(
        "check_continue",
        self._should_continue,
        {"continue": "propose", "end": END}
    )
    
    # 添加顺序边
    workflow.add_edge("propose", "solve")
    workflow.add_edge("solve", "validate")
    workflow.add_edge("validate", "update_state")
    workflow.add_edge("update_state", "check_continue")
    
    return workflow.compile()
```

**节点函数**：

每个节点函数接收 `AgentState`，修改并返回：

```python
def _propose_node(self, state: AgentState) -> AgentState:
    try:
        output = self.proposer.propose(...)
        state.current_state.proposed_qa = output
        state.current_state.status = "proposing"
    except Exception as e:
        state.current_state.error = str(e)
        state.current_state.status = "failed"
    
    return state
```

#### 扩展工作流

**场景 1：添加人工审核节点**

```python
def _build_graph(self):
    workflow = StateGraph(AgentState)
    
    # ... 现有节点 ...
    
    # 新增：人工审核节点
    workflow.add_node("human_review", self._human_review_node)
    
    # 修改边：validate → human_review → update_state
    workflow.add_edge("validate", "human_review")
    workflow.add_edge("human_review", "update_state")
    
    return workflow.compile()

def _human_review_node(self, state: AgentState) -> AgentState:
    """人工审核节点"""
    qa = state.current_state.proposed_qa
    validation = state.current_state.validation
    
    # 如果验证分数在临界区间，触发人工审核
    if 0.7 <= validation.similarity_score < 0.8:
        # 实现：发送到审核队列，等待人工标注
        approved = self._request_human_approval(qa, validation)
        
        if not approved:
            state.current_state.status = "rejected_by_human"
            validation.is_valid = False
    
    return state
```

**场景 2：添加重试机制**

```python
def _propose_node(self, state: AgentState) -> AgentState:
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            output = self.proposer.propose(...)
            state.current_state.proposed_qa = output
            state.current_state.status = "proposing"
            return state
        except Exception as e:
            logger.warning(f"提议失败，重试 {attempt + 1}/{max_retries}: {e}")
            if attempt == max_retries - 1:
                state.current_state.error = str(e)
                state.current_state.status = "failed"
    
    return state
```

---

### 5. Web UI 模块 (`web_ui.py`)

**基于 Gradio 实现**

#### 核心组件

**`MultimodalSynthesisUI` 类**

```python
class MultimodalSynthesisUI:
    def __init__(self):
        self.graph = None
        self.current_task_id = None
    
    def create_interface(self):
        """创建 Gradio 界面"""
        with gr.Blocks() as interface:
            # 构建 UI 组件
            ...
        return interface
```

#### 事件处理

**图片上传**：

```python
def handle_image_upload(files):
    if not files:
        return []
    return [file.name for file in files]

image_input.change(
    fn=handle_image_upload,
    inputs=[image_input],
    outputs=[uploaded_images]
)
```

**开始合成**：

```python
def start_synthesis(files, task_type, ...):
    # 使用 yield 实现流式更新
    for iteration in range(max_iterations):
        # 执行一次迭代
        ...
        
        # 更新 UI
        yield progress_md, iteration_md, validated_md
```

#### 自定义 UI 样式

```python
custom_css = """
.proposer-output {
    background: #e3f2fd;
    border-left: 4px solid #2196F3;
}
.solver-output {
    background: #f3e5f5;
    border-left: 4px solid #9c27b0;
}
"""

interface = gr.Blocks(css=custom_css)
```

#### 扩展 UI

**场景：添加数据统计仪表板**

```python
with gr.Tab("📊 数据统计"):
    gr.Markdown("### 生成数据统计")
    
    # 统计图表
    stats_chart = gr.Plot(label="难度分布")
    qa_count = gr.Number(label="总问答对数", interactive=False)
    avg_difficulty = gr.Number(label="平均难度", interactive=False)
    
    refresh_stats_btn = gr.Button("🔄 刷新统计")
    
    def refresh_statistics():
        # 读取所有输出文件，计算统计
        import json
        from pathlib import Path
        
        all_qa = []
        for file in Path("data/outputs").glob("*.json"):
            with open(file) as f:
                data = json.load(f)
                all_qa.extend(data["qa_pairs"])
        
        # 计算统计
        difficulties = [qa["difficulty"] for qa in all_qa]
        avg_diff = sum(difficulties) / len(difficulties) if difficulties else 0
        
        # 绘制分布图
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.hist(difficulties, bins=10)
        ax.set_xlabel("难度")
        ax.set_ylabel("数量")
        
        return fig, len(all_qa), avg_diff
    
    refresh_stats_btn.click(
        fn=refresh_statistics,
        outputs=[stats_chart, qa_count, avg_difficulty]
    )
```

---

## 🛠️ 开发环境搭建

### 本地开发

```bash
# 1. 克隆项目
git clone <your-repo>
cd multimodal-data-synthesis-system

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装开发依赖
pip install -r requirements.txt
pip install pytest black flake8 mypy  # 开发工具

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 5. 运行测试
pytest tests/

# 6. 启动开发服务器
python web_ui.py
```

### 代码规范

**使用 Black 格式化**：

```bash
black src/ config/ web_ui.py
```

**使用 Flake8 检查**：

```bash
flake8 src/ config/ --max-line-length=100
```

**类型检查**：

```bash
mypy src/ config/
```

---

## 🧪 测试

### 单元测试示例

**测试 ProposerAgent**：

```python
# tests/test_agents.py
import pytest
from src.agents import ProposerAgent, MultimodalLLMClient
from config.llm_config import llm_config

def test_proposer_basic():
    client = MultimodalLLMClient(llm_config)
    proposer = ProposerAgent(client)
    
    output = proposer.propose(
        image_paths=["tests/fixtures/test_image.jpg"],
        task_type="图片问答类",
        difficulty=0.3,
        history_qa_pairs=[]
    )
    
    assert output.question
    assert output.answer
    assert len(output.question) > 10
```

**测试数据模型**：

```python
# tests/test_models.py
from src.models import QAPair

def test_qa_pair_validation():
    qa = QAPair(
        question="测试问题",
        answer="测试答案",
        difficulty=0.5,
        iteration=1
    )
    
    assert qa.difficulty == 0.5
    assert 0 <= qa.difficulty <= 1

def test_qa_pair_invalid_difficulty():
    with pytest.raises(ValidationError):
        QAPair(
            question="测试",
            answer="测试",
            difficulty=1.5,  # 超出范围
            iteration=1
        )
```

---

## 🚀 性能优化

### 1. 并行处理

**批量处理多个图片**：

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_batch(image_list, task_config):
    with ThreadPoolExecutor(max_workers=5) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                process_single_image,
                image
            )
            for image in image_list
        ]
        results = await asyncio.gather(*tasks)
    return results
```

### 2. 缓存机制

**缓存 LLM 响应**：

```python
from functools import lru_cache

class MultimodalLLMClient:
    @lru_cache(maxsize=128)
    def call_with_images_cached(self, system_prompt, user_prompt, image_hash):
        # 使用图片哈希作为缓存键
        return self.call_with_images(...)
```

### 3. 减少 API 调用

**批量验证**：

```python
def batch_validate(self, qa_pairs, batch_size=5):
    """批量验证多个问答对"""
    results = []
    for i in range(0, len(qa_pairs), batch_size):
        batch = qa_pairs[i:i+batch_size]
        # 在一次 API 调用中验证多个
        batch_result = self._validate_batch(batch)
        results.extend(batch_result)
    return results
```

---

## 📝 常见开发任务

### 任务 1：添加新的任务类型

1. 在 `config/prompts.py` 的 `task_descriptions` 中添加
2. 更新 `src/models.py` 的 `TaskType` 枚举
3. 在 UI 的下拉菜单中添加选项

### 任务 2：自定义验证逻辑

1. 修改 `src/agents.py` 的 `ValidatorAgent.validate()`
2. 添加自定义验证规则
3. 调整 `VALIDATION_THRESHOLD`

### 任务 3：集成新的 LLM API

1. 修改 `src/agents.py` 的 `MultimodalLLMClient`
2. 适配新 API 的请求格式
3. 更新配置文件

---

**开发愉快！💻**
