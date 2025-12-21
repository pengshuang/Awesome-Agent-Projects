# 📚 学术论文智能问答系统

> 基于 RAG 技术的智能论文阅读助手，支持多轮对话、Web UI、联网搜索，让您轻松理解学术论文

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LlamaIndex](https://img.shields.io/badge/Powered%20by-LlamaIndex-orange)](https://www.llamaindex.ai/)
[![Pydantic](https://img.shields.io/badge/Config-Pydantic-blue)](https://docs.pydantic.dev/)

中文 | [English](README_EN.md)

---

## 📖 文档导航

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | **项目介绍 & 快速开始** |
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | **使用指南**（配置、界面使用、常见问题） |
| [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) | **开发指南**（架构、API、Pydantic 配置） |

---

## 🌟 核心特性

- 💬 **多轮对话** - 上下文记忆，连续追问
- 🧠 **RAG 问答** - 基于向量检索的精准回答
- 🌐 **Web UI** - 美观易用，支持 Markdown 渲染
- 📄 **多格式** - PDF、DOCX、Markdown、TXT
- 🔍 **语义检索** - 向量数据库，毫秒级响应
- 📊 **来源追溯** - 答案标注原文出处
- 🌐 **联网搜索** - DuckDuckGo 获取最新信息
- 🎨 **双模式** - RAG（文档）+ LLM（开放对话）
- ⚙️ **Pydantic 配置** - 类型安全，自动验证

---

## 🚀 快速开始

### 1. 安装

```bash
git clone <repository-url>
cd academic-paper-qa
pip install -r requirements.txt
```

### 2. 配置

```bash
cp .env.example .env
vim .env  # 编辑配置
LLM_API_KEY=your-api-key          # API Key

请参阅统一快速启动说明：`../docs/QUICK_START.md`。
```
👤: 什么是 Transformer？
🤖: Transformer 是一种基于注意力机制的神经网络架构...

👤: 它有哪些应用？              # ← 自动理解"它"指 Transformer
🤖: Transformer 主要应用于 NLP、CV 等领域...

👤: 能详细说说 NLP 中的应用吗？  # ← 结合上下文继续深入
---

## 💡 使用示例

### 添加文档并提问

```bash
# 1. 添加论文
cp paper.pdf ./data/documents/

# 2. 启动 Web UI
./start_web_multi.sh

# 3. 构建索引 → 开始提问
```

### 对话示例

```
👤: 这篇论文的主要贡献是什么？
🤖: 主要贡献是提出了 Transformer 架构...

👤: 它解决了什么问题？
🤖: Transformer 解决了 RNN 的序列依赖问题...
```

详细使用说明：[使用指南](docs/USER_GUIDE.md)

---

## 🛠️ 技术栈

- **RAG 框架**: LlamaIndex
- **向量数据库**: Chroma
- **Embedding**: BAAI/bge-small-zh-v1.5
- **LLM**: OpenAI / DeepSeek / Moonshot
- **Web UI**: Gradio 4.0+
- **配置管理**: Pydantic 2.0+

---

## 📁 项目结构

```
academic-paper-qa/
├── config/              # 配置模块（Pydantic）
├── src/                 # 核心代码
│   ├── agent.py        # Agent 核心
│   ├── models.py       # 数据模型
│   ├── indexing/       # 索引构建
│   ├── query/          # 查询引擎
│   ├── loaders/        # 文档加载
│   └── tools/          # Web 搜索等工具
├── data/               # 数据目录
│   ├── documents/      # 放置论文（PDF/DOCX/TXT）
│   └── vector_store/   # 向量索引
├── examples/           # 示例代码
├── docs/               # 文档
└── *.py               # 启动脚本
```

---

## ❓ 常见问题

**Q: 支持哪些文件格式？**  
A: PDF、DOCX、Markdown、TXT

**Q: 需要 GPU 吗？**  
A: 不需要，CPU 即可运行

**Q: 支持本地模型吗？**  
A: Embedding 支持本地模型，LLM 需要 API

**Q: 如何调整历史轮数？**  
A: 参见 [使用指南 - 历史轮数控制](docs/USER_GUIDE.md#历史轮数控制)

更多问题：[使用指南 - 问题排查](docs/USER_GUIDE.md#问题排查)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

<details>
<summary><b>Q: 一次可以加载多少篇论文？</b></summary>

A: 理论上无限制，实际受限于内存和模型上下文长度。测试过 100+ 篇论文，检索性能依然良好。
</details>

