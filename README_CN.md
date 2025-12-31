# 🤖 Awesome Agent Projects

> 精选的 LLM Agent 项目集合，涵盖学术研究、企业应用、工具开发等多个领域

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

[English](README.md) | 中文


## 📚 目录

- [项目列表](#项目列表)
- [快速开始](#快速开始)
- [如何贡献](#如何贡献)

---

## 项目列表

本仓库包含 4 个独立的 Agent 项目：

- 📖 **[学术论文问答系统](./academic-paper-qa)** - 基于 RAG 的智能论文阅读助手
- 📊 **[AI 数据分析助手](./ai-data-analyst)** - 支持多数据源的智能数据分析工具
- 💼 **[AI 面试教练](./interview-coach)** - 提供简历评估和模拟面试服务
- 🤖 **[数据合成系统](./multi-agent-data-synthesis-system)** - 基于多智能体协作的高质量训练数据生成系统

---

## 快速开始

```bash
git clone https://github.com/pengshuang/Awesome-Agent-Projects.git
cd Awesome-Agent-Projects
```

然后进入具体项目目录，按照其 README 说明进行详细设置。

---

## 项目详情

### 📖 学术论文智能问答系统

基于 RAG 技术的智能论文阅读助手，支持多轮对话和深度分析。

**核心特性**: 多轮对话 · RAG 检索 · 联网搜索 · 多格式支持 (PDF/DOCX/TXT/MD)

**技术栈**: LlamaIndex · Chroma · Gradio · BGE Embedding

[📂 查看项目](./academic-paper-qa) | [📖 中文文档](./academic-paper-qa/README_CN.md) | [📖 English Doc](./academic-paper-qa/README.md)

---

### 📊 AI 数据分析助手

智能数据分析工具，支持多数据源融合分析和交互式可视化。

**核心特性**: NL2SQL · 多数据源 (SQLite/CSV/Excel) · 数据可视化 · 智能报告

**技术栈**: LlamaIndex · Pandas · Plotly · Gradio

[📂 查看项目](./ai-data-analyst) | [📖 中文文档](./ai-data-analyst/README_CN.md) | [📖 English Doc](./ai-data-analyst/README.md)

---

### 💼 AI 面试教练

智能面试辅导系统，提供简历评估和模拟面试服务。

**核心特性**: 简历分析 · 模拟面试 (技术/行为/综合) · 联网增强 · 改进建议

**技术栈**: OpenAI API · Gradio · DuckDuckGo

[📂 查看项目](./interview-coach) | [📖 中文文档](./interview-coach/README_CN.md) | [📖 English Doc](./interview-coach/README.md)

---

### 🤖 Multi-Agent 数据合成系统

基于多智能体协作的高质量训练数据合成系统，采用 Iterative Curriculum 机制生成高难度数据。

**核心特性**: Iterative Curriculum · 三智能体协作 (提议者/求解者/验证者) · 质量保证 · 实时可视化

**技术栈**: LangGraph · LangChain · Pydantic · Gradio

[📂 查看项目](./data-synthesis-system) | [📖 文档](./data-synthesis-system/README.md)

---

## 💡 技术特点

- 🤖 **多 LLM 支持**: OpenAI、DeepSeek、Qwen 等
- 🎨 **友好界面**: 基于 Gradio 的 Web UI
- 🔍 **RAG 增强**: 向量检索 + 语义搜索
- 📊 **可视化**: 数据图表和 Markdown 渲染
- 🌐 **联网能力**: 实时信息获取

---

## 🤝 如何贡献

欢迎贡献！你可以：

- 🐛 提交 Bug 报告或修复
- ✨ 添加新功能或新项目
- 📝 改进文档
- 💡 分享使用经验

贡献步骤：Fork → 创建分支 → 提交更改 → 发起 Pull Request

---

## 📄 许可证

[MIT License](./LICENSE)

---

<div align="center">

⭐ **觉得有用？给个 Star 吧！** ⭐

[报告问题](https://github.com/pengshuang/Awesome-Agent-Projects/issues) · [参与讨论](https://github.com/pengshuang/Awesome-Agent-Projects/discussions)

</div>
