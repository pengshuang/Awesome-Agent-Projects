# Multi-Agent 数据合成系统

<div align="center">

🤖 **基于多智能体协作的高质量训练数据合成系统**

通过 Iterative Curriculum 机制生成高难度、高质量的问答数据

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-green.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📖 目录

- [功能特性](#-功能特性)
- [快速开始](#-快速开始)
- [系统架构](#-系统架构)
- [配置说明](#-配置说明)
- [输出格式](#-输出格式)
- [文档](#-文档)

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
