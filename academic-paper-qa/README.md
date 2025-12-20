# 📚 学术论文智能问答系统

> 基于大语言模型的智能论文阅读助手，支持多轮对话，让您像和专家聊天一样轻松理解学术论文

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LlamaIndex](https://img.shields.io/badge/Powered%20by-LlamaIndex-orange)](https://www.llamaindex.ai/)

---

## 🌟 核心特性

| 特性 | 说明 |
|------|------|
| 💬 **多轮对话** | 支持上下文记忆和连续追问，自然流畅的对话体验 |
| 🧠 **智能问答** | 基于 RAG 技术的精准问答，理解复杂学术内容 |
| 🌐 **Web UI** | 美观易用的图形化界面，支持单轮和多轮两种模式 |
| 📄 **多格式支持** | PDF、DOCX、Markdown、TXT 文档自动加载 |
| 🔍 **语义检索** | 基于向量数据库的快速语义检索，毫秒级响应 |
| 📊 **来源追溯** | 每个答案标注原文出处，可验证可追溯 |
| 🌐 **联网搜索** | 集成 DuckDuckGo，获取最新研究进展 |
| 🎨 **双模式** | RAG 模式（基于文档）+ LLM 模式（开放对话） |
| 💻 **多界面** | Web UI + 命令行，单轮/多轮灵活切换 |

---

## 🚀 快速开始（3 步上手）

### 1. 安装依赖

```bash
git clone https://github.com/yourusername/academic-paper-qa.git
cd academic-paper-qa
pip install -r requirements.txt
```

### 2. 配置 API

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
vim .env
```

**必填配置：**
```bash
LLM_API_BASE=https://api.moonshot.cn/v1  # API 端点（必须带 /v1）
LLM_API_KEY=your-api-key-here             # 从服务商获取
LLM_MODEL=moonshot-v1-8k                  # 模型名称
```

**支持的 LLM：**
- [Moonshot](https://platform.moonshot.cn/) - 推荐，中文优化
- [OpenAI](https://platform.openai.com/) - GPT-3.5/GPT-4
- [DeepSeek](https://platform.deepseek.com/) - 高性价比

### 3. 启动使用

#### 🎯 方式一：Web UI（推荐新手）

```bash
# 多轮对话模式（推荐，支持连续追问）
./start_web_multi.sh
# 或
python web_ui_multi_turn.py

# 单轮问答模式（快速查询）
./start_web_single.sh
# 或
python web_ui_single_turn.py

# 访问 http://127.0.0.1:7860
```

#### 💻 方式二：命令行

```bash
# 多轮对话模式（交互式，适合深入讨论）
./start_cli_multi.sh
# 或
python cli_multi_turn.py

# 单轮问答模式（快速查询，支持脚本调用）
./start_cli_single.sh
# 或
python cli_single_turn.py
```

**💡 选择建议：**
- 🎓 **学习研究** → 多轮对话模式（记忆上下文，连续追问）
- ⚡ **快速查询** → 单轮问答模式（独立问题，响应更快）

---

## 💬 多轮对话 vs 单轮问答

### 🎯 什么时候用多轮对话？

**适合场景：**
- 📖 **深入学习**：逐步理解复杂概念，连续追问
- 🔍 **文献综述**：对比多篇论文，关联上下文
- 💭 **学术讨论**：头脑风暴，深入分析
- 🎓 **论文解读**：完整理解论文结构和内容

**对话示例：**
```
👤: 什么是 Transformer？
🤖: Transformer 是一种基于注意力机制的神经网络架构...

👤: 它有哪些应用？              # ← 自动理解"它"指 Transformer
🤖: Transformer 主要应用于 NLP、CV 等领域...

👤: 能详细说说 NLP 中的应用吗？  # ← 结合上下文继续深入
🤖: 在自然语言处理中，Transformer 用于...
```

### ⚡ 什么时候用单轮问答？

**适合场景：**
- 🔬 **快速查询**：独立问题，无需上下文
- 📊 **批量处理**：脚本自动化，批量查询
- 💻 **事实查找**：明确的信息检索
- 📈 **数据提取**：结构化信息提取

**查询示例：**
```bash
# 快速查询单个问题
python cli_single_turn.py query "这篇论文的主要贡献是什么？"

# 脚本批量处理
for paper in papers; do
    python cli_single_turn.py query "总结 $paper"
done
```

---

## 📖 使用示例

### 场景 1：快速理解新论文

```bash
# 1. 添加论文到文档目录
cp ~/Downloads/transformer_paper.pdf ./data/documents/

# 2. 启动 Web UI（多轮对话模式）
./start_web_multi.sh

# 3. 在界面中：
#    - 首次使用：点击「构建索引」
#    - 在对话框中提问
```

**对话示例：**
```
👤: 这篇论文的主要贡献是什么？
🤖: 主要贡献是提出了 Transformer 架构...

👤: 它解决了什么问题？
🤖: Transformer 主要解决了 RNN 的序列依赖问题...

👤: 具体的技术细节是什么？
🤖: 核心技术是自注意力机制（Self-Attention）...
```

### 场景 2：文献综述

```bash
# 1. 批量添加论文
cp ~/Downloads/nlp_papers/*.pdf ./data/documents/

# 2. 使用命令行多轮对话
./start_cli_multi.sh

# 3. 对比分析
> 这些论文的研究方法有什么区别？
> 哪些论文关注 Transformer 架构？
> 它们的实验效果如何？
```

### 场景 3：跟踪最新进展

```bash
# 使用 Web UI，启用联网搜索
# 在高级设置中勾选「启用网络搜索」
# 提问：2024年 Transformer 有哪些新进展？
```

---

## 📚 文档导航

| 文档 | 内容 | 适合人群 |
|------|------|----------|
| [功能介绍](docs/FEATURES.md) | 详细功能说明、技术架构、应用场景 | 所有用户 |
| [使用指南](docs/USER_GUIDE.md) | 安装配置、操作步骤、问题排查 | 新手用户 |
| [开发者文档](docs/DEVELOPER_GUIDE.md) | 代码架构、API 参考、扩展开发 | 开发者 |
| [项目结构](PROJECT_STRUCTURE.md) | 目录结构、文件说明、快速导航 | 开发者 |

---

## 🛠️ 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| **RAG 框架** | LlamaIndex | Latest |
| **向量数据库** | Chroma | Latest |
| **Embedding** | BAAI/bge-small-zh-v1.5 | - |
| **LLM** | OpenAI / Moonshot / DeepSeek | - |
| **Web UI** | Gradio | 4.0+ |
| **搜索引擎** | DuckDuckGo | - |
| **文档解析** | LlamaIndex SimpleDirectoryReader | - |

---

## ❓ 常见问题

<details>
<summary><b>Q: 支持英文论文吗？</b></summary>

A: 支持。系统主要针对中文优化，英文论文建议使用 OpenAI 的模型以获得更好效果。
</details>

<details>
<summary><b>Q: 一次可以加载多少篇论文？</b></summary>

A: 理论上无限制，实际受限于内存和模型上下文长度。测试过 100+ 篇论文，检索性能依然良好。
</details>

<details>
<summary><b>Q: 多轮对话和单轮问答有什么区别？</b></summary>

A: 
- **多轮对话**：支持上下文记忆，可以连续追问，适合深入讨论
- **单轮问答**：每次查询独立，响应更快，适合快速查询和批量处理
</details>

<details>
<summary><b>Q: 如何提高答案质量？</b></summary>

A: 
1. 提供清晰具体的问题
2. 使用 RAG 模式获取基于文档的准确答案
3. 调整 Top-K 参数增加检索范围（建议 3-10）
4. 必要时开启联网搜索获取最新信息
</details>

<details>
<summary><b>Q: 构建索引失败怎么办？</b></summary>

A: 
1. 检查文档格式是否正确（支持 PDF、DOCX、MD、TXT）
2. 检查文档是否损坏
3. 查看日志文件：`logs/app.log`
4. 尝试使用命令行构建：`python cli_single_turn.py`
</details>

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发流程
1. Fork 本项目
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

### 代码规范
- 遵循 PEP 8
- 添加类型注解
- 编写文档字符串
- 补充单元测试

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [LlamaIndex](https://www.llamaindex.ai/) - 强大的 RAG 框架
- [Chroma](https://www.trychroma.com/) - 高效的向量数据库
- [Gradio](https://gradio.app/) - 快速构建 ML Web 应用
- [BAAI](https://www.baai.ac.cn/) - 优秀的中文 Embedding 模型

---

## 📞 联系方式

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/academic-paper-qa/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/academic-paper-qa/discussions)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个 Star！**

[开始使用](docs/USER_GUIDE.md) · [查看文档](docs/FEATURES.md) · [报告问题](https://github.com/yourusername/academic-paper-qa/issues)

</div>
