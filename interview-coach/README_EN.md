# 🎯 AI Interview Coach System

An intelligent interview assistance system based on Large Language Models (LLM) to help job seekers optimize resumes, prepare for interviews, and improve competitiveness.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-blue.svg)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[中文](README.md) | English

## ✨ Core Features

### 📄 Resume Management
- Automatic PDF resume parsing
- Extract and structure resume content
- Data validation and security checks

### 🔍 Resume Evaluation
- 6-dimension quantitative scoring (0-100 points)
- Targeted improvement suggestions
- Job matching analysis

### 💼 Mock Interview
- Technical, behavioral, and comprehensive interviews
- Multi-turn in-depth dialogue based on resume
- Optional web search verification
- Interview data statistics and analysis

### 🤖 Multi-model Support
- OpenAI (GPT-3.5/4)
- DeepSeek
- Alibaba Cloud Qwen
- Other OpenAI-compatible APIs

## 🚀 Quick Start

See unified quick start: `../docs/QUICK_START.md`.

## 📖 User Guide

For detailed instructions, see: [User Guide](docs/USER_GUIDE_EN.md)

### Basic Workflow
1. **Upload Resume** → 📄 Resume Management
2. **Evaluate Resume** → 🔍 Resume Evaluation (Complete evaluation/Quick score/Improvement suggestions)
3. **Mock Interview** → 💼 Mock Interview (Select interview type, start dialogue)

## 🛠️ Technical Architecture

### Core Tech Stack
- **Language**: Python 3.9+
- **Data Validation**: Pydantic v2
- **LLM**: OpenAI API compatible interface
- **Web UI**: Gradio 4.0+
- **PDF Parsing**: PyMuPDF

### Project Structure
```
interview-coach/
├── src/                  # Core code
│   ├── models/          # Pydantic data models
│   ├── loaders/         # Resume loaders
│   ├── evaluator/       # Evaluation engine
│   ├── interview/       # Interview agent
│   └── tools/           # Tool modules
├── config/              # Configuration management
├── docs/                # Documentation
├── tests/               # Tests
├── web_ui.py           # Web interface
└── quick_start.py      # CLI example
```

## 📚 Documentation

- [User Guide](docs/USER_GUIDE_EN.md) - Detailed usage instructions
- [Developer Guide](docs/DEVELOPER_GUIDE_EN.md) - Secondary development documentation

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License

## 🔗 Related Links

- Documentation: [docs/](docs/)
- Issue Tracker: GitHub Issues

## 📁 Detailed Project Structure

```
interview-coach/
├── config/                 # Configuration module
│   ├── llm_config.py      # LLM configuration and client
│   ├── prompts.py         # Prompt template management
│   └── settings.py        # System configuration
├── src/                   # Core code
│   ├── loaders/           # Resume loaders
│   │   └── resume_loader.py
│   ├── evaluator/         # Resume evaluator
│   │   └── resume_evaluator.py
│   ├── interview/         # Interview Agent
│   │   └── interview_agent.py
│   ├── tools/             # Tools
│   │   └── web_search.py
│   └── utils/             # Utility functions
│       ├── logger.py
│       └── helpers.py
├── data/                  # Data directory
│   ├── resumes/          # Resume storage
│   └── cache/            # Cache files
├── docs/                  # Documentation
│   ├── USER_GUIDE_EN.md     # User Guide
│   └── DEVELOPER_GUIDE_EN.md # Developer Guide
├── logs/                  # Log files
├── web_ui.py             # Web interface main program
├── init_system.py        # System initialization
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
└── start.sh              # Launch script
```

## 🔧 Technology Stack

- **LLM Integration**: OpenAI Python SDK (>= 1.0.0)
- **Web Framework**: Gradio 4.0+
- **PDF Parsing**: PyMuPDF (fitz)
- **Web Search**: duckduckgo-search
- **Logging System**: Loguru
- **Configuration Management**: python-dotenv

## 🙏 Acknowledgments

Thanks to the following open-source projects:
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Gradio](https://github.com/gradio-app/gradio)
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF)
- [duckduckgo-search](https://github.com/deedy5/duckduckgo_search)

---

**Notes**:
1. This system requires a valid LLM API key to use
2. It is recommended to use a high-performance model for better experience
3. First-time users are advised to read the [User Guide](docs/USER_GUIDE_EN.md)
