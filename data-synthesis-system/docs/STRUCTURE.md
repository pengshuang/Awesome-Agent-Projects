# 项目结构说明

```
data-synthesis-system/
│
├── 📄 README.md                    # 项目主文档
├── 📄 LICENSE                      # MIT 许可证
├── 📄 QUICKSTART.md                # 5分钟快速开始指南
├── 📄 .env.example                 # 环境变量模板
├── 📄 .gitignore                   # Git 忽略文件
│
├── 📄 requirements.txt             # Python 依赖列表
├── 📄 start.sh                     # 一键启动脚本 ⭐
├── 📄 init_system.py               # 系统初始化脚本
├── 📄 web_ui.py                    # Gradio Web UI 入口 ⭐
├── 📄 cli.py                       # 命令行工具
│
├── 📁 config/                      # 配置模块
│   ├── __init__.py                 # 导出配置
│   ├── settings.py                 # 系统设置（Pydantic Settings）
│   ├── llm_config.py               # LLM 配置和实例化
│   └── prompts.py                  # 所有 Agent 的 Prompt 模板
│
├── 📁 src/                         # 核心源代码
│   ├── __init__.py                 # 导出核心类
│   ├── models.py                   # Pydantic 数据模型 ⭐
│   ├── agents.py                   # 三个 Agent 实现 ⭐
│   │                               #   - ProposerAgent (提议者)
│   │                               #   - SolverAgent (求解者)
│   │                               #   - ValidatorAgent (验证者)
│   ├── graph.py                    # LangGraph 工作流编排 ⭐
│   └── utils.py                    # 工具函数
│
├── 📁 data/                        # 数据目录
│   ├── example_document.md         # 示例测试文档
│   ├── uploads/                    # 用户上传的文档
│   │   └── .gitkeep
│   └── outputs/                    # 生成的问答对（JSON）
│       └── .gitkeep
│
├── 📁 logs/                        # 日志文件目录
│   └── .gitkeep
│
└── 📁 docs/                        # 文档目录
    ├── USER_GUIDE.md               # 用户使用指南
    ├── DEVELOPER_GUIDE.md          # 开发者指南
    └── STRUCTURE.md                # 本文档
```

## 核心文件说明

### 🚀 入口文件

| 文件 | 说明 | 使用场景 |
|------|------|----------|
| `start.sh` | 一键启动脚本 | 首次使用或日常启动 |
| `web_ui.py` | Web 界面入口 | 图形化操作 |
| `cli.py` | 命令行工具 | 批量处理、脚本自动化 |

### ⚙️ 配置文件

| 文件 | 说明 | 修改场景 |
|------|------|----------|
| `.env` | 环境变量（API Key 等） | 配置 LLM API |
| `config/settings.py` | 系统设置 | 调整系统参数 |
| `config/prompts.py` | Prompt 模板 | 优化生成质量 |
| `config/llm_config.py` | LLM 配置 | 切换模型 |

### 🤖 核心代码

| 文件 | 说明 | 修改场景 |
|------|------|----------|
| `src/models.py` | 数据模型定义 | 扩展数据结构 |
| `src/agents.py` | Agent 实现 | 修改 Agent 行为 |
| `src/graph.py` | LangGraph 工作流 | 调整流程逻辑 |
| `src/utils.py` | 工具函数 | 添加辅助功能 |

## 数据流

```
┌─────────────────────────────────────────────────────────────┐
│  用户输入                                                     │
│  • 文档内容 (document)                                        │
│  • 任务类型 (task_type)                                       │
│  • 迭代次数 (max_iterations)                                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  web_ui.py 或 cli.py                                         │
│  • 验证输入                                                   │
│  • 创建初始状态                                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  src/graph.py - DataSynthesisGraph                          │
│                                                              │
│  状态流转:                                                   │
│  START → propose → solve → validate → update → (循环)        │
│                                                              │
│  每个节点调用对应的 Agent:                                   │
│  • propose_node → ProposerAgent.generate_qa_pair()          │
│  • solve_node → SolverAgent.solve()                         │
│  • validate_node → ValidatorAgent.validate()                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  src/agents.py - Agent 实现                                  │
│                                                              │
│  每个 Agent:                                                 │
│  1. 使用 config/llm_config.py 获取 LLM 实例                  │
│  2. 使用 config/prompts.py 构建 Prompt                       │
│  3. 调用 LLM API                                             │
│  4. 解析响应（使用 src/models.py 中的 Pydantic 模型）        │
│  5. 返回结构化结果                                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  最终输出                                                     │
│  • JSON 文件 (data/outputs/qa_pairs_*.json)                  │
│  • 日志文件 (logs/*.log)                                     │
└─────────────────────────────────────────────────────────────┘
```

## 代码调用关系

```
web_ui.py
  │
  ├─> src/graph.py::DataSynthesisGraph
  │     │
  │     ├─> src/agents.py::ProposerAgent
  │     │     └─> config/llm_config.py::get_llm()
  │     │           └─> config/settings.py::settings
  │     │
  │     ├─> src/agents.py::SolverAgent
  │     │     └─> config/llm_config.py::get_llm()
  │     │
  │     └─> src/agents.py::ValidatorAgent
  │           └─> config/llm_config.py::get_llm()
  │
  └─> src/utils.py
        ├─> ensure_directories()
        ├─> save_qa_pairs()
        └─> format_qa_for_display()
```

## 配置层级

```
环境变量 (.env)
    ↓
config/settings.py (Pydantic Settings)
    ↓
    ├─> config/llm_config.py (LLM 实例化)
    ├─> config/prompts.py (Prompt 模板)
    └─> src/* (业务逻辑)
```

## 状态管理（LangGraph）

```python
# 状态结构
state = {
    # 输入
    "document": str,              # 文档内容
    "task_type": str,             # 任务类型
    "max_iterations": int,        # 最大迭代次数
    
    # 运行状态
    "current_iteration": int,     # 当前迭代
    "history_buffer": List[dict], # 历史问答对
    
    # 当前迭代数据
    "current_question": str,      # 当前问题
    "current_reference_answer": str,  # 参考答案
    "current_solver_answer": str, # 求解者答案
    "current_reasoning": str,     # 生成理由
    
    # 结果
    "valid_pairs": List[dict],    # 有效问答对
    "failed_attempts": int,       # 失败次数
    
    # 控制
    "is_complete": bool,          # 是否完成
    "error": str,                 # 错误信息
}
```

## 扩展点

### 1. 添加新 Agent

在 `src/agents.py` 中添加新的 Agent 类，然后在 `src/graph.py` 中集成。

### 2. 修改工作流

编辑 `src/graph.py` 的 `_build_graph()` 方法，添加/删除节点和边。

### 3. 自定义 Prompt

编辑 `config/prompts.py`，修改各 Agent 的提示词。

### 4. 扩展数据模型

在 `src/models.py` 中添加新字段或新模型。

### 5. 新增任务类型

1. 在 `src/models.py` 的 `TaskType` 枚举中添加
2. 在 `config/prompts.py` 中添加对应说明
3. UI 自动支持新类型

## 日志系统

```
logs/
├── system_YYYYMMDD_HHMMSS.log    # 系统日志（init_system.py）
├── web_ui_YYYYMMDD_HHMMSS.log    # Web UI 日志
└── cli_YYYYMMDD_HHMMSS.log       # CLI 日志

日志级别：
- DEBUG: 详细调试信息
- INFO: 正常运行信息
- WARNING: 警告信息
- ERROR: 错误信息
```

## 依赖关系图

```
项目依赖:

LangGraph (工作流)
    └─> LangChain (LLM 调用)
          └─> OpenAI SDK (API 通信)

Pydantic (数据验证)

Gradio (Web UI)

Loguru (日志)

Python 标准库
```

## 文件大小估算

| 类型 | 大小 |
|------|------|
| 源代码 | ~50 KB |
| 配置文件 | ~10 KB |
| 文档 | ~100 KB |
| 日志（每天） | ~1-10 MB |
| 生成数据（每次） | ~10-100 KB |

## 性能特征

- **启动时间**: 3-5秒（首次需安装依赖）
- **单次迭代**: 30-60秒（取决于 LLM API 响应时间）
- **内存占用**: ~200-500 MB
- **磁盘占用**: ~100 MB（含依赖）

---

这个结构设计注重：
✅ **模块化**: 各组件职责清晰
✅ **可扩展**: 易于添加新功能
✅ **可维护**: 代码组织合理
✅ **可测试**: 各模块独立可测
