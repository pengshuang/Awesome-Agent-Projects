# 📖 User Guide

> Complete user manual for end users

## Contents

- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [User Interface](#user-interface)
- [Common Scenarios](#common-scenarios)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### System Requirements

- Python 3.9+
- 4GB+ RAM
- 2GB+ disk space

### Installation Steps

```bash
# 1. Clone the project
git clone https://github.com/pengshuang/Awesome-Agent-Projects.git
cd Awesome-Agent-Projects/academic-paper-qa

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
vim .env  # Edit configuration
```

### Minimum Configuration

Required fields in `.env`:

```bash
# LLM Configuration (Required)
LLM_API_KEY=your-api-key
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo

# Embedding Configuration (Local model recommended)
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL_NAME=BAAI/bge-small-zh-v1.5
```

**Supported LLM Providers:**
- OpenAI: https://platform.openai.com/
- DeepSeek: https://platform.deepseek.com/
- Moonshot: https://platform.moonshot.cn/

---

## Configuration

### Core Configuration Items

| Config Item | Description | Default | Range |
|------------|-------------|---------|-------|
| `LLM_API_KEY` | LLM API Key | - | Required |
| `LLM_MODEL` | Model name | gpt-3.5-turbo | - |
| `TEMPERATURE` | Generation temperature | 0.1 | 0.0-2.0 |
| `CHUNK_SIZE` | Text chunk size | 512 | 1-4096 |
| `RETRIEVAL_TOP_K` | Number of docs to retrieve | 5 | 1-50 |
| `ENABLE_WEB_SEARCH` | Enable web search | true | true/false |

See `.env.example` for complete configuration.

---

## User Interface

### Web UI (Recommended)

```bash
# Multi-turn dialogue (Recommended)
./start_web_multi.sh

# Single-turn Q&A
./start_web_single.sh

# Visit http://127.0.0.1:7860
```

**Features:**
- Document upload and index building
- RAG/LLM mode switching
- Parameter adjustment (Top-K, history turns)
- Enable/disable web search

### Command Line

```bash
# Multi-turn dialogue
./start_cli_multi.sh

# Single-turn Q&A
./start_cli_single.sh
```

**Commands:**
- `query <question>` - Ask a question
- `list` - List documents
- `clear` - Clear history
- `exit` - Exit

---

## Common Scenarios

### Quick Paper Understanding

```bash
# 1. Add paper
cp paper.pdf ./data/documents/

# 2. Start and build index
./start_web_multi.sh

# 3. Ask questions
"What is the main contribution of this paper?"
"How was the experiment designed?"
```

### Literature Review

```bash
# Add multiple papers
cp paper*.pdf ./data/documents/

# Comparative analysis
"What are the differences between the methods in these papers?"
```

### Technical Details Exploration

Use multi-turn dialogue for in-depth discussion:
```
👤: How does the attention mechanism in Transformer work?
🤖: ...
👤: Why use multi-head attention?
🤖: ...
```

---

## Troubleshooting

### API Key Error

**Symptoms:** `API Key validation failed`

**Solution:**
1. Check `LLM_API_KEY` in `.env`
2. Confirm API Key is valid and has balance
3. Verify `LLM_API_BASE` is correct

### Document Loading Failure

**Symptoms:** Error when building index

**Solution:**
1. Check document format (PDF/DOCX/TXT/MD)
2. Check logs: `logs/app.log`
3. Try testing with a single document

### Embedding Model Loading Failure

**Symptoms:** `Failed to load embedding model`

**Solution:**
1. First use requires model download (1-2GB)
2. Or use OpenAI Embedding:
   ```bash
   EMBEDDING_PROVIDER=openai
   EMBEDDING_API_KEY=your-key
   ```

### Poor Answer Quality

**Optimization:**
1. Adjust `RETRIEVAL_TOP_K` (increase retrieval count)
2. Use clearer and more specific questions
3. Check document quality

---

## Advanced Features

### History Control

Multi-turn dialogue supports 1-50+ history turns:

```python
# Code setting
agent = AcademicAgent(max_history_turns=10)

# Environment variable
MAX_HISTORY_TURNS=10
```

**Recommended:**
- Quick Q&A: 1-5 turns
- General dialogue: 5-10 turns
- Deep discussion: 20-30 turns

### Batch Processing

```bash
for paper in *.pdf; do
    python cli_single_turn.py query "Summarize $paper"
done
```

---

**Last Updated:** 2025-12-21
