# 🎯 AI 模拟面试系统

基于大语言模型（LLM）的智能面试辅助系统，帮助求职者优化简历、准备面试、提升竞争力。

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-blue.svg)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

中文 | [English](README_EN.md)

## ✨ 核心功能

### 📄 简历管理
- 自动解析 PDF 格式简历
- 提取并结构化简历内容
- 数据验证和安全检查

### 🔍 简历评估
- 6 维度量化评分（0-100分）
- 针对性改进建议
- 岗位匹配分析

### 💼 模拟面试
- 技术面试、行为面试、综合面试
- 基于简历的多轮深度对话
- 可选联网搜索验证
- 面试数据统计分析

### 🤖 多模型支持
- OpenAI (GPT-3.5/4)
- DeepSeek
- 阿里云通义千问
- 其他 OpenAI 兼容 API

## 🚀 快速开始

### 1. 环境要求
```bash
Python 3.9+
```

### 2. 安装

### 安装步骤

1. **克隆项目**（或下载源码）
```bash
git clone https://github.com/yourusername/interview-coach.git
cd interview-coach
```

```bash
# 克隆项目
git clone <repository-url>
cd interview-coach

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件（必须配置 LLM API）
vim .env
```

最少配置：
```ini
LLM_API_KEY=your_api_key_here
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
```

### 4. 启动
```bash
# Web 界面
python web_ui.py

# 命令行示例
python quick_start.py
```

访问：http://127.0.0.1:7861

## 📖 使用指南

详细使用说明请查看：[用户指南](docs/USER_GUIDE.md)

### 基本流程
1. **上传简历** → 📄 简历管理
2. **评估简历** → 🔍 简历评估（完整评估/快速评分/改进建议）
3. **模拟面试** → 💼 模拟面试（选择面试类型，开始对话）

## 🛠️ 技术架构

### 核心技术栈
- **语言**: Python 3.9+
- **数据验证**: Pydantic v2
- **LLM**: OpenAI API 兼容接口
- **Web UI**: Gradio 4.0+
- **PDF 解析**: PyMuPDF

### 项目结构
```
interview-coach/
├── src/                  # 核心代码
│   ├── models/          # Pydantic 数据模型
│   ├── loaders/         # 简历加载器
│   ├── evaluator/       # 评估引擎
│   ├── interview/       # 面试代理
│   └── tools/           # 工具模块
├── config/              # 配置管理
├── docs/                # 文档
├── tests/               # 测试
├── web_ui.py           # Web 界面
└── quick_start.py      # CLI 示例
```

## 📚 文档

- [用户指南](docs/USER_GUIDE.md) - 详细使用说明
- [开发指南](docs/DEVELOPER_GUIDE.md) - 二次开发文档

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 开源协议

MIT License

## 🔗 相关链接

- 文档：[docs/](docs/)
- 问题反馈：GitHub Issues
- 选择生成问题数量（5-20个）
- 点击「生成面试问题」获取针对性问题清单

### 4️⃣ 模拟面试
- 进入「💼 模拟面试」标签页
- 选择面试类型（技术/行为/综合）
- 决定是否启用联网搜索
- 点击「开始面试」开始模拟
- 输入回答进行多轮对话
- 可随时查看面试总结

## 📁 项目结构

```
interview-coach/
├── config/                 # 配置模块
│   ├── llm_config.py      # LLM配置与客户端
│   ├── prompts.py         # Prompt模板管理
│   └── settings.py        # 系统配置
├── src/                   # 核心代码
│   ├── loaders/           # 简历加载器
│   │   └── resume_loader.py
│   ├── evaluator/         # 简历评估器
│   │   └── resume_evaluator.py
│   ├── interview/         # 面试Agent
│   │   └── interview_agent.py
│   ├── tools/             # 工具集
│   │   └── web_search.py
│   └── utils/             # 工具函数
│       ├── logger.py
│       └── helpers.py
├── data/                  # 数据目录
│   ├── resumes/          # 简历存储
│   └── cache/            # 缓存文件
├── docs/                  # 文档
│   ├── USER_GUIDE.md     # 用户使用指南
│   └── DEVELOPER_GUIDE.md # 开发指南
├── logs/                  # 日志文件
├── web_ui.py             # Web界面主程序
├── init_system.py        # 系统初始化
├── requirements.txt      # Python依赖
├── .env.example          # 环境变量模板
└── start.sh              # 启动脚本
```

## 🔧 技术栈

- **LLM集成**：OpenAI Python SDK (>= 1.0.0)
- **Web框架**：Gradio 4.0+
- **PDF解析**：PyMuPDF (fitz)
- **Web搜索**：duckduckgo-search
- **日志系统**：Loguru
- **配置管理**：python-dotenv

## 📚 文档

- [用户使用指南](docs/USER_GUIDE.md) - 详细使用教程和最佳实践
- [开发指南](docs/DEVELOPER_GUIDE.md) - 二次开发和功能扩展指南

## 🤝 贡献

欢迎提交Issue和Pull Request！

如果这个项目对你有帮助，请给个⭐️支持一下！

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

感谢以下开源项目：
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Gradio](https://github.com/gradio-app/gradio)
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF)
- [duckduckgo-search](https://github.com/deedy5/duckduckgo_search)

---

**注意事项**：
1. 本系统需要配置有效的LLM API密钥才能使用
2. 建议使用性能较好的模型以获得更佳体验
3. 首次使用建议阅读[用户使用指南](docs/USER_GUIDE.md)
