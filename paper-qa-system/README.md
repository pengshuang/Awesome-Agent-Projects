# 📚 Academic Paper Intelligent Q&A System

> Intelligent paper reading assistant based on RAG technology, supporting multi-turn conversations, Web UI, and web search to help you understand academic papers easily

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LlamaIndex](https://img.shields.io/badge/Powered%20by-LlamaIndex-orange)](https://www.llamaindex.ai/)
[![Pydantic](https://img.shields.io/badge/Config-Pydantic-blue)](https://docs.pydantic.dev/)

English | [中文](README_CN.md)


---

## 📖 Documentation Navigation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | **Project Overview & Quick Start** |
| [docs/USER_GUIDE_EN.md](docs/USER_GUIDE_EN.md) | **User Guide** (Configuration, UI usage, FAQ) |
| [docs/DEVELOPER_GUIDE_EN.md](docs/DEVELOPER_GUIDE_EN.md) | **Developer Guide** (Architecture, API, Pydantic config) |

---

## 🖼️ Web UI

![ui-1](imgs/ui.png)

---

## 🌟 Core Features

- 💬 **Multi-turn Dialogue** - Context memory, continuous questioning
- 🧠 **RAG Q&A** - Precise answers based on vector retrieval
- 🌐 **Web UI** - Beautiful and easy to use, supports Markdown rendering
- 📄 **Multi-format** - PDF, DOCX, Markdown, TXT
- 🔍 **Semantic Retrieval** - Vector database, millisecond response
- 📊 **Source Tracing** - Answers annotated with original sources
- 🌐 **Web Search** - DuckDuckGo for latest information

---

## 🚀 Quick Start

```bash
# 1. Clone and enter directory
git clone https://github.com/pengshuang/Awesome-Agent-Projects.git
cd Awesome-Agent-Projects/academic-paper-qa

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API Key
cp .env.example .env
# Edit .env and fill in your LLM API Key

# 4. Launch Web UI
./start_web_multi.sh
# or: python web_ui_multi_turn.py
# Visit http://127.0.0.1:7860
```

**First Use**: Place papers (PDF/DOCX/TXT) in `data/documents/` folder, then build index in the Web UI.

---

## 💬 Multi-turn Dialogue vs Single-turn Q&A

### 🎯 When to Use Multi-turn Dialogue?

**Suitable Scenarios:**
- 📖 **In-depth Learning**: Gradually understand complex concepts, continuous questioning
- 🔍 **Literature Review**: Compare multiple papers, associate contexts
- 💭 **Academic Discussion**: Brainstorming, in-depth analysis
- 🎓 **Paper Interpretation**: Complete understanding of paper structure and content

**Dialogue Example:**
```
👤: What is Transformer?
🤖: Transformer is a neural network architecture based on attention mechanism...

👤: What are its applications?              # ← Automatically understands "its" refers to Transformer
🤖: Transformer is mainly applied in NLP, CV and other fields...

👤: Can you elaborate on NLP applications?  # ← Continue in-depth based on context
```

### ⚡ When to Use Single-turn Q&A?

**Suitable Scenarios:**
- 🔍 **Quick Query**: Look up definitions, concepts, formulas
- 📝 **Independent Questions**: Each question is independent without correlation
- 💡 **Keyword Extraction**: Extract key information

**Q&A Example:**
```
Q: What is the full name of Transformer?
A: "Attention is All You Need"

Q: What is BERT?
A: BERT (Bidirectional Encoder Representations from Transformers)...
```

---

## 💡 Usage Examples

### Add Documents and Ask Questions

```bash
# 1. Add paper
cp paper.pdf ./data/documents/

# 2. Start Web UI
./start_web_multi.sh

# 3. Build index → Start asking
```

### Dialogue Example

```
👤: What is the main contribution of this paper?
🤖: The main contribution is proposing the Transformer architecture...

👤: What problem does it solve?
🤖: Transformer solves the sequential dependency problem of RNN...
```

Detailed instructions: [User Guide](docs/USER_GUIDE_EN.md)

---

## 🛠️ Tech Stack

- **RAG Framework**: LlamaIndex
- **Vector Database**: Chroma
- **Embedding**: BAAI/bge-small-zh-v1.5
- **LLM**: OpenAI / DeepSeek / Moonshot
- **Web UI**: Gradio 4.0+

---

## ❓ FAQ

**Q: What file formats are supported?**  
A: PDF, DOCX, Markdown, TXT

**Q: Is GPU required?**  
A: No, CPU is sufficient

**Q: Are local models supported?**  
A: Embedding supports local models, LLM requires API

**Q: How to adjust history turns?**  
A: See [User Guide - History Control](docs/USER_GUIDE_EN.md#history-control)

**Q: How many papers can be loaded at once?**  
A: Theoretically unlimited, practically limited by memory. Tested with 100+ papers with good performance.

More questions: [User Guide - Troubleshooting](docs/USER_GUIDE_EN.md#troubleshooting)

---

## 📄 License

MIT License
