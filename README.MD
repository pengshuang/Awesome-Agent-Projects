# 🤖 Awesome Agent Projects

> 精选的 LLM Agent 项目集合，涵盖学术研究、企业应用、工具开发等多个领域

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)


## 📚 目录

- [项目架构](#项目架构)
- [快速开始](#快速开始)
- [学术研究 Agent](#学术研究-agent)
- [企业应用 Agent](#企业应用-agent)
- [数据分析 Agent](#数据分析-agent)
- [如何贡献](#如何贡献)

---

## 项目架构

本项目采用模块化设计，所有子项目共享统一的基础库：

```
Awesome-Agent-Projects/
├── shared/                      # 🆕 共享基础库
│   ├── config/                 # 统一配置管理
│   │   ├── base_config.py     # 基础配置类
│   │   └── llm_config.py      # LLM 配置（支持 OpenAI/DeepSeek/Qwen）
│   └── utils/                  # 通用工具函数
│       ├── logger_setup.py    # 日志配置
│       ├── file_utils.py      # 文件操作
│       └── text_utils.py      # 文本处理
├── academic-paper-qa/          # 学术论文问答系统
├── ai-data-analyst/            # AI 数据分析助手
└── interview-coach/            # AI 面试教练
```

**架构优势**：
- 📦 **模块化设计**：清晰的职责划分
- 🔄 **代码复用**：消除重复，易于维护
- 🚀 **快速开发**：新项目可直接使用共享库
- 📝 **文档完善**：详细的使用说明和示例

---

## 快速开始

### 1. 安装共享库

```bash
git clone https://github.com/pengshuang/Awesome-Agent-Projects.git
cd Awesome-Agent-Projects
pip install -e shared/
```

### 2. 选择项目并启动

```bash
# 学术论文问答系统
cd academic-paper-qa
pip install -r requirements.txt
python web_ui_multi_turn.py

# AI 数据分析助手
cd ai-data-analyst
pip install -r requirements.txt
python web_ui.py

# AI 面试教练
cd interview-coach
pip install -r requirements.txt
python web_ui.py
```

### 3. 配置环境变量

每个项目都需要配置 `.env` 文件：

```bash
cp .env.example .env
# 编辑 .env，添加你的 API Key
```

详细安装说明请查看 [INSTALL.md](./INSTALL.md)

---

## 学术研究 Agent

### 📖 学术论文智能问答系统
> 基于 RAG 技术的智能论文阅读助手，支持多轮对话和深度分析

**项目路径**: [`academic-paper-qa/`](./academic-paper-qa)

**核心特性**:
- 💬 **多轮对话**: 支持上下文记忆，连续追问
- 🧠 **智能问答**: 基于 RAG 的精准问答
- 📝 **Markdown 渲染**: Web UI 自动格式化显示 ⭐
- 📄 **多格式支持**: PDF、DOCX、Markdown、TXT
- 🔍 **语义检索**: 快速精准的向量检索
- 🌐 **联网搜索**: 集成 DuckDuckGo 获取最新信息
- 📊 **来源追溯**: 标注原文出处，可验证
- ⚙️ **Prompt 管理**: 统一配置系统，易于扩展 ⭐

**技术栈**: LlamaIndex, Chroma, Gradio, BAAI/bge-small-zh-v1.5

**适用场景**:
- 📖 快速理解学术论文
- 🔍 文献综述和对比分析
- 💡 研究灵感挖掘
- 🎓 学术教学辅导

[查看详情 →](./academic-paper-qa/README.md)

---

## 企业应用 Agent

### 💼 AI 模拟面试系统
> 智能面试教练，提供简历评估和模拟面试服务

**项目路径**: [`interview-coach/`](./interview-coach)

**核心特性**:
- 📄 **简历分析**: 多维度评估，智能打分
- 💬 **模拟面试**: 技术/行为/综合三种面试模式
- 🌐 **联网增强**: 实时验证技术问题答案
- 💡 **改进建议**: 个性化简历优化建议
- 📝 **Markdown 渲染**: 清晰的结果展示 ⭐
- ⚙️ **Prompt 管理**: 统一配置各类面试场景 ⭐

**技术栈**: OpenAI API, Gradio, DuckDuckGo

**适用场景**:
- 💼 求职面试准备
- 📋 简历优化指导
- 🎯 面试技能提升

[查看详情 →](./interview-coach/README.md)

---

## 开发工具 Agent

🚧 **即将推出更多项目...**

---

## 个人助理 Agent

🚧 **即将推出更多项目...**

---

## 创意内容 Agent

🚧 **即将推出更多项目...**

---

## 数据分析 Agent

### 📊 AI 数据分析助手
> 基于大模型的智能数据分析工具，支持多数据源融合分析和数据可视化

**项目路径**: [`ai-data-analyst/`](./ai-data-analyst)

**核心特性**:
- 🗄️ **多数据源支持**: SQLite、CSV/Excel、知识库、Web搜索
- 🔄 **NL2SQL**: 自然语言转SQL查询，支持语法高亮 ⭐
- 📊 **数据可视化**: 交互式图表（柱状图、折线图、饼图等）⭐ 新功能
- 🧠 **智能分析**: 多数据源融合分析，自动生成报告
- 💬 **多轮对话**: 上下文理解，连贯的对话体验
- 📝 **Markdown 渲染**: 清晰的分析结果展示 ⭐
- ⚙️ **统一配置**: 集中管理Prompt和LLM配置 ⭐
- 🔍 **Debug友好**: 所有LLM调用自动记录Prompt ⭐

**技术栈**: LlamaIndex, Gradio, Pandas, Plotly, SQLite, Loguru

**适用场景**:
- 📈 业务数据分析
- 📊 数据可视化和报告生成
- 🔍 探索性数据分析（EDA）
- 💡 数据驱动决策
- 📚 知识库问答

[查看详情 →](./ai-data-analyst/README.md)

---

## 📖 技术栈

### 共享基础
- **配置管理**: Python-dotenv, Loguru
- **LLM 支持**: OpenAI SDK, LlamaIndex
- **Embedding**: HuggingFace, BAAI/bge-small-zh-v1.5

### 项目特定
- **学术论文问答**: LlamaIndex, Chroma, PyPDF, Gradio
- **AI 数据分析**: Pandas, Plotly, SQLite, LlamaIndex
- **AI 面试教练**: OpenAI API, Gradio, DuckDuckGo

---

## 📚 学习资源

### 官方文档
- [LlamaIndex 官方文档](https://docs.llamaindex.ai/)
- [OpenAI API 文档](https://platform.openai.com/docs/)
- [Gradio 文档](https://www.gradio.app/docs/)

### 设计模式
- [RAG 最佳实践](https://docs.llamaindex.ai/en/stable/optimizing/production_rag/)
- [提示工程指南](https://www.promptingguide.ai/zh)
- [Agent 设计模式](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/)

---

## 🤝 如何贡献

我们欢迎各种形式的贡献！

### 贡献指南

1. **Fork 本仓库**
2. **创建特性分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **开启 Pull Request**

### 贡献方向

- 🐛 **Bug 修复**: 发现问题？提交 Issue 或 PR
- ✨ **新功能**: 有好想法？欢迎实现并分享
- 📝 **文档改进**: 发现文档不清楚？帮助改进
- 🆕 **新项目**: 开发了新的 Agent？加入我们
- 🔧 **共享库扩展**: 通用功能请提交到 `shared/` 目录

### 代码规范

- 遵循 PEP 8 Python 代码风格
- 添加必要的注释和文档字符串
- 编写单元测试
- 更新相关文档

---

## 🌟 项目亮点

### 架构设计
✅ **模块化架构**：清晰的职责划分，易于维护  
✅ **代码复用**：共享基础库，消除重复代码  
✅ **可扩展性**：便于添加新功能和新项目  

### 技术特色
✅ **多 LLM 支持**：OpenAI、DeepSeek、Qwen 等  
✅ **灵活配置**：统一的配置管理系统  
✅ **完善日志**：便于调试和问题追踪  

### 用户体验
✅ **友好界面**：Gradio Web UI，无需命令行  
✅ **详细文档**：完整的使用说明和示例  
✅ **快速上手**：清晰的安装和配置步骤  

---

## 📊 项目统计

- 🎯 **3** 个完整的 Agent 应用
- 🔧 **1** 个共享基础库
- 📝 **10+** 篇详细文档
- ⚡ **60%** 代码重复消除率

---

## 📄 许可证

本项目采用 [MIT License](./LICENSE) 开源协议。

---

## 🔗 相关链接

我们欢迎各种形式的贡献！

### 添加新项目
1. Fork 本仓库
2. 在对应分类下创建项目目录
3. 添加完整的 README.md
4. 在主 README 中添加项目卡片
5. 提交 Pull Request

### 项目要求
- ✅ 完整的项目说明文档
- ✅ 清晰的安装和使用指南
- ✅ 可运行的示例代码
- ✅ 开源协议声明
- ✅ 技术栈和依赖说明

### 改进建议
- 报告 Bug 或问题
- 提出新功能建议
- 改进现有文档
- 分享使用经验

---

## 📊 项目统计

- 🎯 **总项目数**: 3
- 🎓 **学术研究**: 1
- 💼 **企业应用**: 1
- 👨‍💻 **开发工具**: 0
- 🤝 **个人助理**: 0
- 🎨 **创意内容**: 0
- 📊 **数据分析**: 1

---

## ⭐ Star 历史

如果这个项目对你有帮助，欢迎 Star ⭐️

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

感谢所有贡献者的付出！

特别感谢以下开源项目:
- [LlamaIndex](https://www.llamaindex.ai/)
- [LangChain](https://www.langchain.com/)
- [Chroma](https://www.trychroma.com/)
- [Gradio](https://gradio.app/)

---

## 📞 联系方式

- 💬 Discussion: [GitHub Discussions](https://github.com/pengshuang/Awesome-Agent-Projects/discussions)
- 🐛 Issues: [GitHub Issues](https://github.com/pengshuang/Awesome-Agent-Projects/issues)
- 📧 Email: your-email@example.com

---

<div align="center">

**⭐ 如果觉得有用，请给我们一个 Star！⭐**

[开始探索](./academic-paper-qa) · [添加项目](#如何贡献) · [报告问题](https://github.com/pengshuang/Awesome-Agent-Projects/issues)

Made with ❤️ by the community

</div>
