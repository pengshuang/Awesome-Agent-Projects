# 项目架构文档

## 📋 项目概述

AI 模拟面试系统是一个基于大语言模型的智能面试模拟平台，提供简历评估、岗位解读和模拟面试功能。

**技术栈：** Python 3.10+, Gradio, Pydantic, OpenAI API, DuckDuckGo Search

**运行环境：** conda 环境 `paper-qa-clean`

---

## 🏗️ 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    Web UI (Gradio)                      │
│                     web_ui.py                           │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┬───────────────┐
        │                         │               │
┌───────▼────────┐    ┌──────────▼──────┐  ┌────▼─────────┐
│ Resume Loader  │    │ Resume Evaluator│  │Interview Agent│
│  (PDF解析)     │    │   (LLM评估)     │  │  (对话代理)   │
└────────────────┘    └─────────────────┘  └──────────────┘
                               │                    │
                      ┌────────▼────────────────────▼───────┐
                      │      LLM Client (OpenAI API)        │
                      │      Web Search Tool (Optional)     │
                      └─────────────────────────────────────┘
```

### 分层架构

**1. 表现层 (Presentation Layer)**
- `web_ui.py` - Gradio Web 界面
  - 简历管理 Tab
  - 简历评估 Tab
  - 岗位解读 Tab
  - 模拟面试 Tab

**2. 业务逻辑层 (Business Logic Layer)**
- `src/loaders/` - 文件加载与解析
  - `resume_loader.py` - PDF 简历解析（PyMuPDF/PyPDF2）
- `src/evaluator/` - 简历评估逻辑
  - `resume_evaluator.py` - 多维度评估、打分、建议生成
- `src/interview/` - 面试对话代理
  - `interview_agent.py` - 多轮对话管理、上下文维护

**3. 数据模型层 (Data Model Layer)**
- `src/models/` - Pydantic 数据模型
  - `resume.py` - ResumeData, ResumeMetadata
  - `evaluation.py` - EvaluationResult, ScoreDetails
  - `interview.py` - InterviewMessage, InterviewSession

**4. 工具与配置层 (Utils & Config Layer)**
- `config/` - 系统配置管理
  - `settings.py` - SystemConfig (Pydantic Settings)
  - `llm_config.py` - LLM 客户端配置
  - `prompts.py` - 提示词模板管理
- `src/tools/` - 外部工具集成
  - `web_search.py` - DuckDuckGo/SearXNG 搜索
- `src/utils/` - 通用工具
  - `logger.py` - 日志配置
  - `helpers.py` - 辅助函数

---

## 📁 目录结构

```
interview-coach/
├── web_ui.py              # 主应用入口（Gradio UI）
├── init_system.py         # 系统初始化脚本
├── quick_start.py         # 快速入门示例（CLI 演示）
├── start.sh               # Shell 启动脚本
│
├── config/                # 配置模块
│   ├── __init__.py
│   ├── settings.py        # 系统配置（Pydantic Settings）
│   ├── llm_config.py      # LLM 客户端配置
│   └── prompts.py         # 提示词模板
│
├── src/                   # 核心业务逻辑
│   ├── __init__.py
│   ├── constants.py       # 常量定义
│   ├── exceptions.py      # 自定义异常
│   │
│   ├── loaders/           # 文件加载器
│   │   ├── __init__.py
│   │   └── resume_loader.py
│   │
│   ├── evaluator/         # 简历评估器
│   │   ├── __init__.py
│   │   └── resume_evaluator.py
│   │
│   ├── interview/         # 面试代理
│   │   ├── __init__.py
│   │   └── interview_agent.py
│   │
│   ├── models/            # 数据模型
│   │   ├── __init__.py
│   │   ├── resume.py
│   │   ├── evaluation.py
│   │   └── interview.py
│   │
│   ├── tools/             # 外部工具
│   │   ├── __init__.py
│   │   └── web_search.py
│   │
│   └── utils/             # 通用工具
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
│
├── data/                  # 数据目录
│   ├── resumes/           # 简历文件存储
│   └── cache/             # 缓存数据
│
├── logs/                  # 日志文件（自动生成）
├── output/                # 输出文件
│
├── tests/                 # 单元测试
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_loader.py
│   └── README.md
│
├── docs/                  # 文档
│   ├── USER_GUIDE.md      # 用户指南（中文）
│   ├── USER_GUIDE_EN.md   # 用户指南（英文）
│   ├── DEVELOPER_GUIDE.md # 开发指南（中文）
│   └── DEVELOPER_GUIDE_EN.md
│
├── imgs/                  # UI 截图
│   ├── ui-1.png
│   ├── ui-2.png
│   └── ui-3.png
│
├── scripts/               # 辅助脚本
│   ├── format_code.sh     # 代码格式化
│   └── check_quality.sh   # 代码质量检查
│
├── requirements.txt       # 依赖列表
├── requirements-dev.txt   # 开发依赖
├── pyproject.toml         # 项目配置
├── setup.cfg              # Setup 配置
├── .env.example           # 环境变量模板
├── .gitignore
├── LICENSE
├── README.md              # 项目说明（英文）
└── README_CN.md           # 项目说明（中文）
```

---

## 🔄 数据流

### 1. 简历评估流程

```
用户上传 PDF
    ↓
ResumeLoader.load_resume()
    ↓ (PyMuPDF/PyPDF2)
ResumeData (Pydantic Model)
    ↓
ResumeEvaluator.evaluate()
    ↓ (调用 LLM API)
EvaluationResult (Pydantic Model)
    ↓
Gradio UI 展示
```

### 2. 模拟面试流程

```
用户点击"开始面试"
    ↓
InterviewAgent.start_interview()
    ↓ (生成开场白)
用户输入回答
    ↓
InterviewAgent.chat(user_message)
    ↓ (可选: WebSearchTool.search())
    ↓ (调用 LLM API with context)
面试官回复
    ↓
历史记录更新 (tuple format for Gradio Chatbot)
```

---

## 🔧 核心组件说明

### 1. ResumeLoader
**职责：** 解析 PDF 简历并提取文本内容

**关键方法：**
- `load_resume(file_path)` - 加载并解析简历
- `_load_pdf_pymupdf()` - 使用 PyMuPDF 解析
- `_load_pdf_pypdf2()` - 使用 PyPDF2 解析（fallback）

**依赖库：** pymupdf, PyPDF2

### 2. ResumeEvaluator
**职责：** 基于 LLM 评估简历质量

**关键方法：**
- `evaluate(resume_content, position, requirements)` - 完整评估
- `quick_score(resume_content)` - 快速评分
- `suggest_improvements(resume_content)` - 改进建议

**提示词：** 使用 `PromptTemplates` 管理

### 3. InterviewAgent
**职责：** 模拟面试官进行多轮对话

**关键方法：**
- `start_interview()` - 生成开场白
- `chat(user_message, use_web_search)` - 对话回复
- `clear_history()` - 清空历史
- `get_interview_summary()` - 获取面试统计

**特性：**
- 多轮历史管理（可配置最大轮数）
- 可选联网搜索验证
- 支持三种面试类型：技术/行为/综合

### 4. SystemConfig
**职责：** 系统配置管理（基于 Pydantic Settings）

**配置项：**
- LLM 配置：`llm_api_key`, `llm_api_base`, `llm_model`, `temperature`
- Web 搜索：`enable_web_search`, `web_search_engine`, `max_search_results`
- 面试配置：`max_history_turns`, `interview_mode`
- 路径配置：`base_dir`, `data_dir`, `logs_dir` 等

**环境变量：** 从 `.env` 文件加载

---

## 🚀 启动流程

### 1. 初始化阶段 (init_system.py)
```python
initialize_system()
├── get_config()           # 加载配置
├── ensure_directories()   # 创建必要目录
├── configure_logger()     # 配置 loguru
└── validate_llm_config()  # 验证 LLM 配置
```

### 2. UI 启动 (web_ui.py)
```python
main()
├── initialize_components()
│   ├── ResumeLoader()
│   └── ResumeEvaluator()
├── create_ui()            # 构建 Gradio Blocks
└── app.launch()           # 启动服务器
```

---

## 📦 依赖管理

**核心依赖：**
- `gradio` - Web UI 框架
- `pydantic` & `pydantic-settings` - 数据验证与配置
- `openai` - LLM API 客户端
- `pymupdf` / `PyPDF2` - PDF 解析
- `duckduckgo-search` - 联网搜索
- `loguru` - 日志管理

**安装方式：**
```bash
# 方式 1: 使用 requirements.txt
pip install -r requirements.txt

# 方式 2: 使用 pyproject.toml (推荐)
pip install -e .
```

---

## 🐛 已知问题与解决方案

### 1. Gradio Chatbot 数据格式
**问题：** Gradio v4+ Chatbot 组件要求 tuple 格式 `[(user, bot), ...]`

**解决：** 所有聊天历史使用 tuple 而非字典格式

### 2. Pydantic computed_field 与 Gradio 冲突
**问题：** Pydantic 的 `@computed_field` 生成的 JSON Schema 可能导致 Gradio API 生成失败

**解决：** 
- 设置 `show_api=False` 禁用 API 文档生成
- 或将 computed_field 改为普通方法

### 3. SystemConfig 属性访问
**问题：** `SystemConfig` 是 Pydantic 模型，需实例化后访问属性

**解决：** 使用 `get_config()` 单例函数获取配置实例

---

## 📝 开发规范

### 代码风格
- 使用 Black 格式化（配置在 `pyproject.toml`）
- 使用 isort 排序导入
- 类型提示：所有公共函数需添加类型注解

### 日志规范
```python
from loguru import logger

logger.info("正常信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.debug("调试信息")
```

### 提交规范
```
feat: 新增功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建/工具相关
```

---

## 🔮 未来优化方向

1. **性能优化**
   - 增加 LLM 响应缓存机制
   - 简历解析结果缓存
   - 异步处理长时间任务

2. **功能扩展**
   - 支持更多简历格式（Word, TXT）
   - 岗位 JD 链接自动爬取
   - 面试评分与反馈报告
   - 多语言支持（英文面试）

3. **架构改进**
   - 引入消息队列处理异步任务
   - 数据库存储面试历史
   - 用户认证与多用户支持

4. **测试覆盖**
   - 增加单元测试覆盖率（目标 >80%）
   - 集成测试自动化
   - UI 端到端测试

---

## 📞 维护者

如有问题或建议，请提交 Issue 或 Pull Request。

最后更新：2025-12-27
