# Multi-Agent 数据合成系统

<div align="center">

🤖 **基于多智能体协作的高质量训练数据合成系统**

自动生成高难度、高质量的问答对，用于LLM训练和评估

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-green.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 💁 简介

这是一个基于**多智能体协作**和**Iterative Curriculum**机制的数据合成系统，能够：

- 🎯 **自动生成问答对**：基于你的文档，生成高质量的问答数据
- 📈 **难度递增**：从简单问题开始，逐步生成更难的问题
- ✅ **质量保证**：通过1-10分的评分机制，只保留高分数据
- 🛠️ **灵活可配**：Web UI实时调整Prompt和参数

### 适用场景

- 📚 **LLM训练数据**：为大语言模型生成微调数据
- 📊 **评测数据集**：创建模型评估的Benchmark
- 🏫 **教育题库**：自动生成练习题和考试题
- 🤖**智能客服**：为客服系统准备FAQ数据

### 交互界面

![ui-1](/Users/pengshuang/Awesome-Agent-Projects/multi-agent-data-synthesis-system/imgs/ui-1.png)

![ui-2](/Users/pengshuang/Awesome-Agent-Projects/multi-agent-data-synthesis-system/imgs/ui-2.png)

---

## ✨ 核心特性

### 👥 三智能体协作

```
📝 提议者 (Proposer)  →  🔍 求解者 (Solver)  →  ✅ 验证者 (Validator)
     |生成问题               |尝试回答             |评分验证
     └──────────────────────────────────────┘
                         |
                    评分 >= 阈值？
                    /          \
                  是           否
                  |            |
              保存       继续迭代
```

**工作流程**：
1. **提议者**基于文档和历史问答对，生成新问题（难度递增）
2. **求解者**尝试回答问题，展示推理过程
3. **验证者**评估答案质量，给1-10分
4. 高分答案保存，低分答案继续迭代

### 📈 Iterative Curriculum 机制

```
难度曲线：
10 ┤                                      ●
   │
 9 ┤                                  ●
   │
 8 ┤                             ●
   │
 7 ┤                      ●
   │
 6 ┤               ●
   │
 5 ┤          ●
   │
 4 ┤      ●
   │
 3 ┤  ●
   │
 2 ┤●
   └─────────────────────────────────────▶
    1  2  3  4  5  6  7  8  9  10 11  (迭代轮次)
```

- **第1轮**：从低难度（1-2分）开始
- **后续轮**：新问题难度 >= 历史最高难度
- **难度上限**：9-10分（保持该水平，从不同角度出题）

### 🎯 多任务支持

| 任务类型 | 说明 | 示例 |
|----------|------|------|
| 🧠 逻辑推理 | 需要多步推理、因果分析 | “如果A则B，如果B则C，那么？” |
| 🔢 数值计算 | 数学计算、数据分析 | “计算复利和投资回报率” |
| 📚 信息查询 | 查找、整合多处信息 | “AI发展史上的关键事件？” |
| 📝 总结摘要 | 概括、提炼核心内容 | “总结文章的主要观点” |

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- OpenAI API Key（或兼容的API服务）

### 三步启动

**1️⃣ 安装依赖**

```bash
cd data-synthesis-system
pip install -r requirements.txt
```

**2️⃣ 配置API**

复制 `.env.example` 并重命名为 `.env`，编辑配置：

```bash
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

**3️⃣ 启动系统**

```bash
python web_ui.py
```

浏览器访问：http://localhost:7860

### 5分钟体验

1. 点击**快速开始**中的示例文档按钮（如“🏫 学术报告”）
2. 选择**任务类型**（建议选“逻辑推理类”）
3. 设置**最大迭代次数**为5次
4. 点击**🚀 开始合成**
5. 实时查看生成过程，完成后下载JSON文件

---

## 📊 输出示例

生成的JSON文件格式：

```json
[
  {
    "question": "量子计算相比经典计算机的核心优势是什么？",
    "answer": "量子计算的核心优势在于量子比特可以同时处于0和1的叠加态...",
    "reasoning": "这个问题考察对量子计算基本原理的理解...",
    "task_type": "逻辑推理类",
    "iteration": 1,
    "score": 8.5,
    "metadata": {
      "difficulty_score": 6,
      "timestamp": "2025-12-27T14:30:00"
    }
  }
]
```

---

## 📚 文档

- **[👤 用户指南](docs/USER_GUIDE.md)** - 详细使用说明，适合普通用户
- **[👨‍💻 开发指南](docs/DEVELOPER_GUIDE.md)** - 二次开发文档，适合开发者
- **[🏛️ 架构设计](docs/ARCHITECTURE.md)** - 系统架构和设计思路
- **[🔗 LangChain & LangGraph 应用详解](docs/LANGCHAIN_LANGGRAPH_GUIDE.md)** - 深入讲解核心技术栈
- **[📝 更新日志](CHANGELOG.md)** - 版本变更记录

---

## ❓ 常见问题

<details>
<summary><b>如何调整问题难度？</b></summary>

1. 进入Web UI的“⚙️ Prompts配置”标签页
2. 展开“Proposer（提议者）”
3. 修改`difficulty_score`的初始值和递增策略
4. 点击开始合成，实时生效
</details>

<details>
<summary><b>如何更换LLM模型？</b></summary>

编辑`.env`文件，修改以下配置：
```bash
MODEL_NAME=gpt-4-turbo-preview  # 主模型
FALLBACK_MODEL=gpt-3.5-turbo    # 备用模型
```
</details>

<details>
<summary><b>如何提高生成速度？</b></summary>

- 使用较快的模型（如gpt-3.5-turbo）
- 降低最大迭代次数
- 降低评分阈值（会降低质量）
</details>

<details>
<summary><b>如何增加新的任务类型？</b></summary>

参考[开发指南](docs/DEVELOPER_GUIDE.md)中的“扩展开发”章节
</details>

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📝 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) & [LangGraph](https://github.com/langchain-ai/langgraph) - 强大的LLM工作流框架
- [Gradio](https://github.com/gradio-app/gradio) - 简洁优雅的Web UI框架
- [OpenAI](https://openai.com/) - 强大的语言模型

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

---

## ✨ 功能特性

### 🎯 核心能力

- **Iterative Curriculum Learning**：问题难度递增，从简单到复杂
- **Multi-Agent 协作**：提议者、求解者、验证者三智能体协同工作
- **评分制验证**：1-10分精细化质量评估（可配置阈值）
- **多任务支持**：逻辑推理、数值计算、信息查询、总结摘要

### 🎨 用户界面

- **可配置 Prompts**：Web UI 中直接修改三个 Agent 的提示词
- **灵活参数**：Temperature、评分阈值实时调整
- **停止控制**：随时中断并保存已生成数据
- **彩色区块**：三个 Agent 输出颜色区分，易于阅读

---

## 🚀 快速开始

### 前置要求

- Python 3.8+
- OpenAI API Key（或兼容 API）

### 三步启动

**1. 安装依赖**

```bash
pip install -r requirements.txt
```

**2. 配置 API**

创建 `.env` 文件：

```bash
OPENAI_API_KEY=your-api-key
OPENAI_API_BASE=https://api.openai.com/v1
```

**3. 启动系统**

```bash
python web_ui.py
```

访问：http://localhost:7860

### 使用流程

1. 输入文档内容（或上传 .txt/.md 文件）
2. 选择任务类型（逻辑推理/数值计算/信息查询/总结摘要）
3. 设置参数（迭代次数、Temperature、评分阈值）
4. 点击"开始合成"，实时查看进度
5. 下载 JSON 格式结果

---

## 🏗️ 系统架构

```
用户输入文档 + 配置参数
         ↓
┌─────────────────────────────┐
│  LangGraph 工作流           │
│                             │
│  Proposer → Solver          │
│      ↓         ↓            │
│  Validator (评分1-10)       │
│      ↓                      │
│  score >= threshold?        │
│   Yes ↓    No ↓             │
│  保存    继续迭代            │
└─────────────────────────────┘
         ↓
高质量问答对（JSON）
```

### 核心机制

**Iterative Curriculum**：
- 第1轮：基于文档生成简单问题
- 后续轮：参考历史生成更难问题
- 难度递增：逐步提升挑战性

**评分制验证**：
- 9-10分：完美答案
- 7-8分：正确答案
- 5-6分：基本正确
- 3-4分：部分正确
- 1-2分：错误答案

---

## 🔧 配置说明

### 环境变量 (.env)

```bash
# API 配置
OPENAI_API_KEY=your-api-key
OPENAI_API_BASE=https://api.openai.com/v1

# 模型选择
PROPOSER_MODEL=gpt-4-turbo-preview
SOLVER_MODEL=gpt-4-turbo-preview
VALIDATOR_MODEL=gpt-4-turbo-preview

# 参数配置（也可在 Web UI 中调整）
TEMPERATURE=0.7              # 生成随机性（0.0-2.0）
SCORE_THRESHOLD=7.0          # 评分阈值（1.0-10.0）
MAX_ITERATIONS=10            # 最大迭代次数
```

### Prompts 定制

**方式一：Web UI（推荐）**
- 打开"⚙️ Prompts 配置"标签页
- 展开 Agent 面板修改提示词
- 实时生效，便于测试

**方式二：配置文件**
- 编辑 `config/prompts.py`
- 永久修改默认提示词

---

## 📊 输出格式

```json
[
  {
    "question": "问题内容",
    "answer": "参考答案",
    "reasoning": "生成理由",
    "task_type": "逻辑推理类",
    "iteration": 1,
    "score": 8.5,
    "timestamp": "2025-12-25T22:30:00"
  }
]
```

---

## 📚 文档

- **[用户指南](docs/USER_GUIDE.md)**：详细使用说明
- **[开发指南](docs/DEVELOPER_GUIDE.md)**：二次开发文档
- **[更新日志](CHANGELOG.md)**：版本变更记录

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) & [LangGraph](https://github.com/langchain-ai/langgraph)
- [Gradio](https://github.com/gradio-app/gradio)
