# 📚 学术论文智能问答系统

> 基于 RAG 技术的智能论文阅读助手，支持多轮对话、Web UI、联网搜索，轻松理解学术论文

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LlamaIndex](https://img.shields.io/badge/Powered%20by-LlamaIndex-orange)](https://www.llamaindex.ai/)
[![Pydantic](https://img.shields.io/badge/Config-Pydantic-blue)](https://docs.pydantic.dev/)

---

## Web 界面

![ui](imgs/ui.png)

## 📖 文档导航

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | **项目功能介绍**（面向所有用户） |
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | **用户使用指南**（快速上手系统） |
| [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) | **开发者指南**（二次开发必读） |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | **架构设计文档**（系统设计详解） |

---

## 🌟 核心功能

### 💬 智能多轮对话
- **上下文理解**：自动记忆前 N 轮对话，理解代词指代
- **连续追问**：像与人对话一样自然地追问细节
- **历史管理**：支持查看、清空对话历史

### 🧠 RAG 精准问答
- **向量检索**：基于语义相似度快速定位相关内容
- **来源标注**：每个答案都标注了来源文档和页码
- **多文档整合**：跨多篇论文综合回答问题

### 🖥️ 友好的 Web UI
- **Gradio 界面**：简洁美观，无需编程即可使用
- **实时响应**：支持流式输出，打字机效果
- **Markdown 渲染**：支持代码高亮、公式显示

### 📄 多格式文档支持
- **PDF**：学术论文的主流格式
- **DOCX**：Word 文档
- **TXT/Markdown**：纯文本和 Markdown 文档

### 🌐 联网搜索增强
- **实时信息**：通过 DuckDuckGo 获取最新资讯
- **智能判断**：自动决定何时需要联网搜索
- **结果整合**：将网络信息与文档内容结合

---

## 🎯 适用场景

### 📖 学术研究者
- **快速阅读**：快速了解论文核心思想
- **文献综述**：对比分析多篇论文
- **深度理解**：逐步追问技术细节

### 🎓 学生学习
- **课程论文**：理解课程指定论文
- **毕业设计**：查阅相关文献资料
- **知识学习**：系统学习某个领域

### 💼 工程师
- **技术调研**：快速了解新技术
- **方案选型**：对比不同技术方案
- **问题解决**：查找特定问题的解决方案

---

## 🚀 快速开始

### 环境要求
- Python 3.9+
- 8GB+ 内存（使用本地 Embedding 模型）
- LLM API Key（OpenAI、DeepSeek、Moonshot、Qwen 等）

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/pengshuang/Awesome-Agent-Projects.git
cd Awesome-Agent-Projects/paper-qa-system

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key

# 4. 启动 Web UI
./start_web_multi.sh
# 或者: python web_ui_multi_turn.py

# 5. 访问系统
# 浏览器打开 http://127.0.0.1:7860
```

### 首次使用

1. **上传文档**：将论文（PDF/DOCX/TXT）放入 `data/documents/` 文件夹
2. **构建索引**：在 Web UI 中点击「构建索引」按钮
3. **开始提问**：等待索引构建完成后，即可开始提问

---

## 💡 使用示例

### 示例 1：快速理解论文

```
👤: 这篇论文讲了什么？

🤖: 这篇论文《Attention is All You Need》提出了 Transformer 模型，
    这是一个完全基于注意力机制的神经网络架构。论文的主要贡献包括：
    1. 抛弃了传统的 RNN 和 CNN 结构
    2. 使用多头自注意力机制捕捉序列关系
    3. 在机器翻译任务上取得了 SOTA 性能
    
    来源：Transformer.pdf 第 1-2 页

👤: 什么是自注意力机制？

🤖: 自注意力机制（Self-Attention）是 Transformer 的核心组件。
    它通过计算序列中每个位置与其他所有位置的相关性，来建模
    序列内部的依赖关系。具体来说...
    
    来源：Transformer.pdf 第 3 页
```

### 示例 2：对比多篇论文

```
👤: BERT 和 GPT 有什么区别？

🤖: BERT 和 GPT 是两种不同的预训练语言模型：
    
    **BERT（Bidirectional）**：
    - 双向编码器，能同时看到上下文
    - 适合理解类任务（分类、问答）
    
    **GPT（Autoregressive）**：
    - 单向解码器，从左到右生成
    - 适合生成类任务（文本生成、续写）
    
    来源：
    - BERT.pdf 第 2 页
    - GPT.pdf 第 1 页
```

### 示例 3：技术细节探讨

```
👤: Transformer 的位置编码是怎么实现的？

🤖: Transformer 使用正弦余弦函数来编码位置信息...
    
👤: 为什么要用正弦余弦函数？

🤖: 使用正弦余弦函数的原因主要有两点：
    1. 能够处理任意长度的序列
    2. 相对位置关系可以通过简单的线性变换表示...
```

---

## 🛠️ 技术栈

| 技术 | 用途 |
|-----|------|
| **LlamaIndex** | RAG 框架 |
| **Pydantic 2.0** | 配置管理 |
| **Gradio 4.0** | Web UI |
| **Chroma** | 向量数据库 |
| **HuggingFace** | 本地 Embedding |

---

## 📊 性能特点

- ⚡ **快速检索**：毫秒级向量相似度搜索
- 💾 **资源友好**：支持本地 Embedding 模型，无需 GPU
- 🔄 **增量更新**：支持增量索引构建
- 📈 **可扩展**：轻松扩展到数千篇论文

---

## ❓ 常见问题

### Q: 支持哪些 LLM？
A: 支持所有 OpenAI 兼容的 API，包括：
- OpenAI GPT 系列
- DeepSeek
- Moonshot (Kimi)
- Qwen (通义千问)
- 其他兼容 OpenAI 接口的 LLM

### Q: 必须联网才能使用吗？
A: 不一定。你可以：
- **纯本地**：使用本地 Embedding + LLM API（只需网络调用 LLM）
- **纯云端**：使用 OpenAI Embedding + OpenAI GPT
- **混合**：本地 Embedding + 云端 LLM（推荐）

### Q: 索引构建需要多久？
A: 取决于文档数量和 Embedding 模型：
- **10 篇论文**：约 1-2 分钟（本地 Embedding）
- **100 篇论文**：约 10-20 分钟
- 可通过批量处理和 GPU 加速优化

### Q: 答案质量如何保证？
A: 多重保障机制：
1. **高质量检索**：向量相似度 + 关键词过滤
2. **来源标注**：每个答案都标注来源，可追溯
3. **LLM 生成**：基于检索结果生成答案，减少幻觉
4. **重排序**：可选的 reranker 提升召回精度

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 🔗 相关链接

- [LlamaIndex 官方文档](https://docs.llamaindex.ai/)
- [Pydantic 官方文档](https://docs.pydantic.dev/)
- [Gradio 官方文档](https://www.gradio.app/docs/)

---

**最后更新**: 2026-01-01
