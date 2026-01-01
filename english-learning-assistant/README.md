# 🎓 AI英语学习助手

一个基于大语言模型API的智能英语学习平台，提供AI导师对话、翻译解析、写作批改、口语练习、多模态学习等全方位英语学习功能。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app/)

---

## ✨ 核心特性

### 🤖 智能Agent导师
- **自主规划学习内容** - AI根据你的水平定制个性化学习路径
- **主动引导对话练习** - 创造沉浸式英语学习环境
- **实时纠错反馈** - 即时纠正语法、词汇、表达错误
- **复盘总结分析** - 自动总结知识点和薄弱环节
- **自适应难度调整** - 根据学习表现动态调整难度
- **上下文记忆** - 保持连贯的对话体验

### 📚 核心功能模块

#### 1. 💬 AI智能对话
- 与AI英语导师进行自然对话
- 三个难度级别（初级/中级/高级）
- 实时语法和表达纠正
- 学习档案和进度跟踪

#### 2. 🔤 翻译解析
- **通用翻译** - 中英互译 + 详细语言学习解析
- **单词解析** - 音标、词性、搭配、例句、记忆技巧
- **长难句解析** - 句子结构分析、语法讲解、简化理解

#### 3. ✍️ 写作批改
- **作文批改** - 语法错误、拼写、用词、逻辑、评分
- **写作润色** - 提升地道度和流畅度（学术/商务/日常/创意）

#### 4. 🎤 口语练习
- **跟读练习** - 标准发音示范（英式/美式可选）
- **发音评估** - 准确度、流利度、完整度评分
- **语音识别** - 实时将口语转为文字

#### 5. 📄 多模态学习
- **图片解析** - 识别图片中的英文内容并翻译讲解
- **PDF解析** - 提取PDF文本并提供学习辅导
- 支持格式：JPG, PNG, GIF, PDF

#### 6. ⚙️ Prompt管理
- 统一管理所有功能的Prompt模板
- 可视化查看和编辑
- 实时生效（当前会话）

---

## 🏗️ 技术架构

### 技术栈
- **前端界面**: Gradio 4.0+ (支持PC和移动端)
- **后端框架**: Python 3.8+
- **LLM集成**: 支持多种三方API (Qwen、OpenAI等)
- **日志系统**: Loguru
- **配置管理**: Pydantic + python-dotenv

### 核心特点
- ✅ **100%基于API** - 所有AI能力通过第三方LLM API实现，无本地模型
- ✅ **模块化设计** - 清晰的代码结构，易于扩展和维护
- ✅ **流式输出** - 文本对话和Agent回复支持流式输出
- ✅ **完善日志** - 详细的调试日志，每次API调用自动记录Prompt
- ✅ **中文界面** - 全中文UI，交互友好
- ✅ **异常处理** - 完善的错误捕获和中文提示

---

## 🚀 快速开始

### 环境要求
- Python 3.8 或更高版本
- pip 包管理工具
- 稳定的网络连接（用于API调用）

### 安装步骤

#### 1. 克隆项目
```bash
cd Awesome-Agent-Projects
cd english-learning-assistant
```

#### 2. 初始化系统
```bash
python3 init_system.py
```

#### 3. 配置API密钥
编辑 `.env` 文件，填入你的API密钥：
```env
LLM_API_KEY=your_api_key_here
LLM_API_BASE=https://dashscope.aliyuncs.com/api/v1
LLM_MODEL=qwen-plus
```

#### 4. 启动应用
```bash
chmod +x start.sh
./start.sh
```

或者直接运行：
```bash
python3 web_ui.py
```

#### 5. 访问界面
浏览器打开：`http://localhost:7860`

---

## 📖 使用示例

### AI对话练习
```
学生: "How can I improve my English speaking skills?"
AI导师: "Great question! Here are some effective ways to improve 
your speaking skills: 1) Practice daily conversations..."
[AI会根据你的水平提供个性化建议]
```

### 单词解析
```
输入: "serendipity"
输出: 
## 音标
- 英式: /ˌserənˈdɪpəti/
- 美式: /ˌserənˈdɪpəti/

## 词性与释义
noun (名词): 意外发现美好事物的能力；偶然发现的运气
[详细解析...]
```

### 写作批改
```
输入: "I am very happy to meet you yesterday."
输出:
## 错误纠正
### 语法错误
- "yesterday" 应与过去时搭配，应改为 "I was very happy..."
[详细批改...]
```

---

## 🎯 适用场景

- 📚 **自学者** - 个性化英语学习辅导
- 🎓 **学生** - 课后练习和作业批改
- 💼 **职场人士** - 商务英语写作和口语提升
- 🌍 **出国准备** - 雅思托福备考练习
- 👨‍🏫 **教师** - 辅助教学工具

---

## 📊 项目结构

```
english-learning-assistant/
├── config/              # 配置模块
│   ├── settings.py     # 系统配置
│   ├── llm_config.py   # LLM API配置
│   └── prompts.py      # Prompt管理
├── src/
│   ├── agent/          # Agent模块
│   │   └── english_agent.py
│   ├── api/            # API客户端
│   │   ├── llm_client.py
│   │   ├── tts_client.py
│   │   ├── stt_client.py
│   │   └── vision_client.py
│   ├── services/       # 业务服务
│   │   ├── translation.py
│   │   ├── writing.py
│   │   ├── speaking.py
│   │   └── multimodal.py
│   └── utils/          # 工具模块
│       ├── logger.py
│       └── storage.py
├── data/               # 数据目录
│   ├── history/        # 学习记录
│   └── uploads/        # 上传文件
├── logs/               # 日志文件
├── docs/               # 文档
├── web_ui.py           # Web界面主程序
├── init_system.py      # 初始化脚本
├── start.sh            # 启动脚本
└── requirements.txt    # 依赖清单
```

---

## 🔧 配置说明

### 支持的LLM API

#### 1. 通义千问 (Qwen)
```env
LLM_API_KEY=sk-xxx
LLM_API_BASE=https://dashscope.aliyuncs.com/api/v1
LLM_MODEL=qwen-plus
```

#### 2. OpenAI Compatible API
```env
LLM_API_KEY=sk-xxx
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
```

### 模型参数调整
```env
TEMPERATURE=0.7        # 创造性 (0.0-2.0)
MAX_TOKENS=2000       # 最大输出长度
TOP_P=0.8             # 采样参数
API_TIMEOUT=60        # 超时时间(秒)
STREAM_ENABLED=true   # 流式输出
```

---

## 📝 文档

- [用户指南](docs/USER_GUIDE.md) - 详细使用教程
- [开发指南](docs/DEVELOPER_GUIDE.md) - 二次开发文档
- [架构设计](docs/ARCHITECTURE.md) - 系统架构说明

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

## ⚠️ 免责声明

本项目仅供学习交流使用，使用第三方API时请遵守相应服务条款。API调用产生的费用由使用者自行承担。

---

## 📮 联系方式

如有问题或建议，欢迎提交Issue。

---


**⭐ 如果这个项目对你有帮助，请给一个Star！**

Made with ❤️ by English Learning Assistant Team

