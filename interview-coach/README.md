# AI 模拟面试系统

基于大语言模型（LLM）的智能面试模拟系统，帮助求职者准备面试、优化简历。

## ✨ 功能特点

- 📄 **简历导入**：支持 PDF 格式简历解析
- 🔍 **智能评估**：多维度简历评估与打分
- 💬 **模拟面试**：多轮对话模拟真实面试场景
- 🌐 **联网搜索**：面试官可以搜索最新信息验证回答
- 🤖 **多模型支持**：支持 OpenAI、DeepSeek、Qwen 等多种 LLM API

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，至少需要配置：

```ini
LLM_API_KEY=your-api-key-here
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
```

### 4. 启动系统

```bash
# Linux/Mac
chmod +x start.sh
./start.sh

# 或直接运行
python3 web_ui.py
```

访问 http://localhost:7860 开始使用。

## 📖 使用指南

### 1. 上传简历

- 在「简历管理」标签页上传 PDF 格式的简历
- 系统会自动解析并提取内容

### 2. 评估简历

- 在「简历评估」标签页进行评估
- 可选填写目标岗位和岗位要求
- 支持完整评估、快速评分、改进建议三种模式

### 3. 模拟面试

- 在「模拟面试」标签页选择面试类型
- 点击「开始面试」，AI 面试官会根据简历提问
- 输入回答，进行多轮对话
- 可以启用联网搜索增强面试真实性

## 📁 项目结构

```
interview-coach/
├── config/              # 配置模块
│   ├── __init__.py
│   ├── llm_config.py    # LLM 配置
│   └── settings.py      # 系统配置
├── src/                 # 源代码
│   ├── loaders/         # 简历加载器
│   ├── evaluator/       # 简历评估器
│   ├── interview/       # 面试 Agent
│   ├── tools/           # 工具（Web 搜索等）
│   └── utils/           # 工具函数
├── data/                # 数据目录
│   ├── resumes/         # 简历文件
│   └── cache/           # 缓存
├── docs/                # 文档
├── logs/                # 日志
├── web_ui.py            # Web UI 主程序
├── init_system.py       # 系统初始化
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量模板
└── start.sh             # 启动脚本
```

## 🔧 配置说明

### LLM 配置

支持多种 LLM 服务商：

**OpenAI**
```ini
LLM_API_KEY=sk-xxx
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
```

**DeepSeek**
```ini
LLM_API_KEY=sk-xxx
LLM_API_BASE=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

**Qwen (通过 DashScope)**
```ini
LLM_API_KEY=sk-xxx
LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo
```

### Web 搜索配置

```ini
# 是否启用联网搜索
ENABLE_WEB_SEARCH=true

# 搜索引擎
WEB_SEARCH_ENGINE=duckduckgo

# 最大搜索结果数
MAX_SEARCH_RESULTS=5
```

## 📚 文档

- [功能介绍](docs/FEATURES.md) - 详细的功能说明
- [用户指南](docs/USER_GUIDE.md) - 使用教程和最佳实践
- [开发指南](docs/DEVELOPER_GUIDE.md) - 二次开发和扩展指南

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License

## 🙏 致谢

本项目基于以下优秀开源项目：

- [OpenAI Python Client](https://github.com/openai/openai-python) - OpenAI API 客户端
- [Gradio](https://github.com/gradio-app/gradio) - Web UI 框架
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - PDF 解析
