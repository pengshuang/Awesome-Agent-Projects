# Multi-Agent 数据合成系统

<div align="center">

🤖 **基于多智能体协作的高质量训练数据合成系统**

通过 Iterative Curriculum 机制生成高难度、高质量的长文问答数据

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-green.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## ✨ 核心特性

- 🎯 **Iterative Curriculum Learning**: 问题难度递增，从简单到复杂逐步生成更具挑战性的数据
- 🤝 **Multi-Agent 协作**: 提议者、求解者、验证者三个智能体紧密配合，确保数据质量
- 📊 **多任务类型支持**: 逻辑推理、数值计算、信息查询、总结摘要四大类任务
- ✅ **质量保证机制**: 只保留通过验证的高质量问答对，确保训练数据可靠性
- 🔄 **自动迭代优化**: 基于历史问答对生成更难、更多样的新问题
- 🎨 **美观的 Web UI**: 基于 Gradio 的现代化界面，实时展示生成过程
- 📝 **完备的日志系统**: 详细记录每一步操作，便于调试和优化

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户输入文档 + 任务类型                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph 状态图                           │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ 提议者 Agent  │───▶│ 求解者 Agent  │───▶│ 验证者 Agent  │ │
│  │  生成问答对   │    │  尝试解答     │    │  检查质量     │ │
│  └──────────────┘    └──────────────┘    └──────┬───────┘ │
│         ▲                                         │         │
│         │                                         ▼         │
│         │                                  ┌─────────────┐ │
│         │                                  │  验证通过？  │ │
│         │                                  └─────┬───────┘ │
│         │                                        │         │
│         │                    Yes ┌───────────────┘         │
│         │                        ▼                         │
│         │              ┌──────────────────┐               │
│         └──────────────│  加入历史缓冲区   │               │
│                        │  继续下一轮迭代   │               │
│                        └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              输出高质量问答对（JSON 格式）                     │
└─────────────────────────────────────────────────────────────┘
```

### 核心机制：Iterative Curriculum

1. **第一轮**：提议者基于原始文档生成简单的"种子问题"
2. **后续轮次**：提议者同时参考原始文档和历史问答对，生成比已有问题更难、更创新的新问题
3. **质量筛选**：求解者尝试回答，验证者检查答案质量，只有通过验证的才加入历史
4. **难度递增**：随着历史积累，问题复杂度自然提升，覆盖更深层次的推理挑战

## 🚀 快速开始

### 前置要求

- Python 3.8+
- OpenAI API Key（或兼容的 API，如 Qwen、Kimi 等）

### 安装步骤

1. **克隆项目**

```bash
cd data-synthesis-system
```

2. **配置环境变量**

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置你的 API Key：

```bash
# 使用 OpenAI
OPENAI_API_KEY=sk-your-api-key
OPENAI_API_BASE=https://api.openai.com/v1

# 或使用 Qwen
# OPENAI_API_KEY=your-qwen-api-key
# OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

# 或使用 Kimi
# OPENAI_API_KEY=your-kimi-api-key
# OPENAI_API_BASE=https://api.moonshot.cn/v1
```

3. **启动系统**

```bash
chmod +x start.sh
./start.sh
```

系统会自动：
- 创建虚拟环境
- 安装依赖
- 初始化目录结构
- 启动 Gradio Web UI

4. **访问界面**

打开浏览器访问：http://localhost:7860

## 📖 使用指南

详细使用说明请参考：[用户使用指南](docs/USER_GUIDE.md)

### 基本流程

1. **输入文档**：在文本框中粘贴内容，或上传 `.txt`/`.md` 文件
2. **选择任务类型**：
   - 逻辑推理类：需要多步推理、因果分析
   - 数值计算类：需要数学计算、数据分析
   - 信息查询类：需要查找、整合多处信息
   - 总结摘要类：需要概括、提炼核心内容
3. **设置迭代次数**：建议 5-15 次（次数越多生成越多但耗时更长）
4. **开始合成**：系统自动运行，实时显示进度
5. **下载结果**：获取 JSON 格式的问答对，可直接用于模型训练

## 🛠️ 开发指南

详细开发文档请参考：[开发指南](docs/DEVELOPER_GUIDE.md)

### 项目结构

```
data-synthesis-system/
├── config/                 # 配置文件
│   ├── __init__.py
│   ├── settings.py        # 系统设置
│   ├── llm_config.py      # LLM 配置
│   └── prompts.py         # Prompt 模板
├── src/                   # 源代码
│   ├── __init__.py
│   ├── models.py          # Pydantic 数据模型
│   ├── agents.py          # Agent 实现
│   ├── graph.py           # LangGraph 状态图
│   └── utils.py           # 工具函数
├── data/                  # 数据目录
│   ├── uploads/           # 上传的文档
│   └── outputs/           # 输出的问答对
├── logs/                  # 日志文件
├── docs/                  # 文档
│   ├── USER_GUIDE.md
│   └── DEVELOPER_GUIDE.md
├── web_ui.py             # Gradio Web UI
├── init_system.py        # 系统初始化
├── start.sh              # 启动脚本
├── requirements.txt      # 依赖列表
├── .env.example          # 环境变量模板
└── README.md             # 本文件
```

### 技术栈

- **LangGraph**: 多智能体工作流编排
- **LangChain**: LLM 调用和管理
- **Pydantic**: 数据验证和解析
- **Gradio**: Web UI 界面
- **Loguru**: 日志系统

## 📋 任务类型说明

### 1. 逻辑推理类
- 需要多步推理链条
- 涉及因果关系分析
- 需要演绎或归纳推理
- 适合训练模型的推理能力

### 2. 数值计算类
- 需要数学计算
- 涉及数据分析和统计
- 需要数值推导
- 适合训练模型的计算能力

### 3. 信息查询类
- 需要从文档中查找信息
- 需要整合多处信息点
- 需要理解上下文关系
- 适合训练模型的信息检索能力

### 4. 总结摘要类
- 需要概括文档内容
- 需要提炼核心观点
- 需要压缩信息密度
- 适合训练模型的总结能力

## 🔧 配置说明

### LLM 配置

在 `.env` 文件中配置：

```bash
# 模型选择（可为每个 Agent 使用不同模型）
PROPOSER_MODEL=gpt-4-turbo-preview
SOLVER_MODEL=gpt-4-turbo-preview
VALIDATOR_MODEL=gpt-4-turbo-preview

# 生成参数
TEMPERATURE=0.7
MAX_TOKENS=2000

# 系统参数
MAX_ITERATIONS=10
```

### Prompt 定制

编辑 `config/prompts.py` 来定制各个 Agent 的 Prompt：

- `proposer`: 提议者的 System 和 User Prompt
- `solver`: 求解者的 System 和 User Prompt
- `validator`: 验证者的 System 和 User Prompt

## 📊 输出格式

生成的 JSON 文件格式：

```json
[
  {
    "question": "问题内容",
    "answer": "答案内容",
    "reasoning": "生成理由",
    "task_type": "逻辑推理类",
    "iteration": 1,
    "timestamp": "2024-12-24T10:30:00"
  }
]
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

本项目基于以下优秀开源项目：
- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Gradio](https://github.com/gradio-app/gradio)

## 📮 联系方式

如有问题或建议，欢迎通过 Issue 联系我们。

---

<div align="center">
Made with ❤️ by the Data Synthesis Team
</div>
