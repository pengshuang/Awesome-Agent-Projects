# 🎯 AI 模拟面试系统

基于大语言模型（LLM）的智能面试辅助系统，帮助求职者优化简历、准备面试、提升竞争力。

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 核心功能

### 📄 简历智能管理
- **PDF解析**：自动解析PDF格式简历，提取完整文本内容
- **快速预览**：即时查看简历解析结果和关键信息

### 🔍 多维度简历评估
- **专业评估**：从6个维度对简历进行量化评分（0-100分）
  - 基本信息完整性
  - 工作经验相关性  
  - 项目经验质量
  - 技能匹配度
  - 教育背景
  - 整体印象
- **快速评分**：快速获取总体评分和简短评价
- **改进建议**：获取具体可操作的优化建议
- **岗位匹配**：根据目标岗位提供针对性评估

### 🎯 岗位解读
- **JD分析**：智能解读岗位描述，提取核心要求
- **问题生成**：根据岗位要求和简历背景，生成5-20个针对性面试问题
- **匹配分析**：评估简历与岗位的匹配程度

### 💼 智能模拟面试
- **多种面试类型**：
  - 技术面试：考察专业技能和项目经验
  - 行为面试：评估软技能和价值观  
  - 综合面试：技术与行为相结合
- **多轮对话**：基于简历内容的深度追问
- **联网搜索**：面试官可搜索最新信息验证回答（可选）
- **面试总结**：查看面试统计和关键指标

### 🤖 多模型支持
- **OpenAI**：GPT-3.5-turbo, GPT-4, GPT-4-turbo
- **DeepSeek**：DeepSeek-chat, DeepSeek-coder
- **阿里云**：Qwen-turbo, Qwen-plus, Qwen-max
- **其他兼容OpenAI API的模型**

## 🚀 快速开始

### 环境要求
- Python 3.9+
- pip 包管理器

### 安装步骤

1. **克隆项目**（或下载源码）
```bash
git clone https://github.com/yourusername/interview-coach.git
cd interview-coach
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填写必要配置
# 至少需要配置：LLM_API_KEY, LLM_API_BASE, LLM_MODEL
```

4. **启动系统**
```bash
# 方式1：使用启动脚本（推荐）
chmod +x start.sh
./start.sh

# 方式2：直接运行
python web_ui.py
```

5. **访问应用**  
打开浏览器访问：http://127.0.0.1:7861

## ⚙️ 配置说明

### LLM配置（必需）

在 `.env` 文件中配置LLM服务：

**使用OpenAI**
```ini
LLM_API_KEY=sk-xxxxxxxxxxxxxxxx
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.7
```

**使用DeepSeek**
```ini
LLM_API_KEY=sk-xxxxxxxxxxxxxxxx
LLM_API_BASE=https://api.deepseek.com
LLM_MODEL=deepseek-chat
LLM_TEMPERATURE=0.7
```

**使用阿里云通义千问**
```ini
LLM_API_KEY=sk-xxxxxxxxxxxxxxxx
LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo
LLM_TEMPERATURE=0.7
```

### Web搜索配置（可选）

```ini
# 是否启用联网搜索
ENABLE_WEB_SEARCH=true

# 搜索引擎选择：duckduckgo 或 searxng
WEB_SEARCH_ENGINE=duckduckgo

# 搜索结果数量
MAX_SEARCH_RESULTS=5

# SearXNG实例地址（如使用searxng）
SEARXNG_BASE_URL=https://searx.example.com
```

### 系统配置（可选）

```ini
# 对话历史保留轮数
MAX_HISTORY_TURNS=20

# 日志级别：DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO
```

## 📖 使用流程

### 1️⃣ 上传简历
- 进入「📄 简历管理」标签页
- 点击上传按钮，选择PDF格式简历
- 系统自动解析并显示简历信息

### 2️⃣ 评估简历
- 进入「🔍 简历评估」标签页
- （可选）填写目标岗位和岗位要求
- 选择评估方式：
  - **完整评估**：获取详细的多维度分析报告
  - **快速评分**：快速获取总体评分
  - **改进建议**：获取优化建议

### 3️⃣ 岗位解读
- 进入「🎯 岗位解读」标签页
- 粘贴目标岗位的JD（Job Description）
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
