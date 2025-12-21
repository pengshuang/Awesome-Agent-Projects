# AI Data Analyst

<div align="center">

🤖 Intelligent Data Analysis Tool Based on Large Language Models

Natural Language Interaction | Multi-source Support | Auto Visualization | Report Generation

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.0+-green.svg)](https://docs.pydantic.dev/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

[中文](README.md) | English

---

## ✨ Features

Complete data analysis through natural language conversation without writing code:

- 🗄️ **Multi-source Query** - SQLite, CSV/Excel, JSON, Parquet
- 🔄 **NL2SQL** - Automatic natural language to SQL conversion
- 📊 **Smart Visualization** - Auto-generate interactive charts
- 💬 **Contextual Dialogue** - Coherent multi-turn analysis conversations
- 🔌 **LLM Compatible** - OpenAI, DeepSeek, Qwen, etc.
- ✅ **Data Validation** - Type-safe based on Pydantic

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API Key
cp .env.example .env
# Edit .env to fill in your LLM API Key

# 3. Create sample data (optional)
python data/create_example_db.py

# 4. Launch Web interface
python web_ui.py
# Visit http://localhost:7860
```
See unified quick start: `../docs/QUICK_START.md`.

## 📖 Documentation

- [User Guide](docs/USER_GUIDE_EN.md) - For end users
- [Developer Guide](docs/DEVELOPER_GUIDE_EN.md) - For developers
- [Pydantic Data Validation](docs/PYDANTIC_GUIDE_EN.md) - Data model documentation

## 💡 Usage Examples

**Natural Language Query**
```
Query monthly sales trends
```

**Data Analysis**
```
Analyze which product has the best sales and provide a visualization chart
```

**Multi-turn Dialogue**
```
User: Query sales data
Assistant: [Returns sales data]
User: Generate a bar chart for me
Assistant: [Generates visualization chart]
```

## 🛠️ Tech Stack

- **Framework**: Gradio (Web UI)
- **LLM**: LlamaIndex + OpenAI/DeepSeek/Qwen
- **Data Validation**: Pydantic v2
- **Visualization**: Plotly
- **Data Processing**: Pandas

## 📂 Project Structure

```
ai-data-analyst/
├── config/              # Configuration module
├── src/
│   ├── models/         # Pydantic data models
│   ├── datasources/    # Data source adapters
│   ├── analyzers/      # Data analyzers
│   └── tools/          # NL2SQL and other tools
├── data/               # Data directory
├── docs/               # Documentation
└── web_ui.py          # Web interface entry
```

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License
