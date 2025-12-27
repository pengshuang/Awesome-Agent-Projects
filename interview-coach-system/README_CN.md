# 🎯 AI 模拟面试系统

基于大语言模型的智能面试辅助系统，帮助求职者优化简历、准备面试、提升面试竞争力。

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README.md) | 中文

---

## 📖 项目简介

AI 模拟面试系统是一个完整的面试准备解决方案，集成了简历优化、岗位分析和面试模拟三大核心功能。通过大语言模型技术，系统能够：

- 🎓 从专业角度评估简历质量，提供具体改进建议
- 🎯 根据岗位 JD 自动生成针对性面试问题
- 💬 模拟真实面试场景，支持多轮深度对话
- 🌐 可选联网搜索，实时验证答案准确性

**适用场景：** 求职准备、面试练习、简历优化、技能评估

---

## ✨ 核心功能

### 1. 📄 简历管理与解析
- **智能解析**：自动提取 PDF 简历的文本内容
- **格式支持**：优先使用 PyMuPDF，兼容 PyPDF2
- **数据验证**：基于 Pydantic 的严格数据校验
- **快速加载**：支持示例简历，无需上传即可体验

### 2. 🔍 多维度简历评估
**评分体系**（6个维度，每项 0-10 分）：
- 基本信息完整性
- 工作经验相关性
- 项目经验质量
- 技能匹配度
- 教育背景
- 整体印象

**评估模式**：
- 完整评估：详细分析每个维度，提供改进建议
- 快速评分：30秒内获取总体评分
- 改进建议：针对性优化方案

### 3. 🎯 岗位解读与问题生成
- **智能分析**：解读岗位 JD，提取核心要求
- **定制问题**：根据简历和岗位生成 5-20 个面试问题
- **全面覆盖**：技术能力、项目经验、软技能等

### 4. 💼 智能模拟面试
**面试类型**：
- 💻 技术面试：聚焦技术能力和问题解决
- 🤝 行为面试：考察软技能和团队协作
- 🎯 综合面试：技术 + 行为全面评估

**核心特性**：
- 多轮对话，自动生成追问
- 基于简历内容的深度提问
- 可选联网搜索验证答案
- 面试统计与总结

---

## 🖼️ 界面预览

<div align="center">
<img src="imgs/ui-1.png" alt="简历管理界面" width="45%"/>
<img src="imgs/ui-2.png" alt="简历评估界面" width="45%"/>
<br/>
<img src="imgs/ui-3.png" alt="模拟面试界面" width="90%"/>
</div>

---

## 🚀 快速开始

### 安装与配置

```bash
# 1. 克隆项目
git clone https://github.com/pengshuang/Awesome-Agent-Projects.git
cd Awesome-Agent-Projects/interview-coach

# 2. 安装依赖（推荐使用 conda 环境）
conda create -n interview-coach python=3.10
conda activate interview-coach
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写以下必需配置：
# LLM_API_KEY=your-api-key-here
# LLM_API_BASE=https://api.openai.com/v1  # 或其他兼容端点
# LLM_MODEL=gpt-3.5-turbo  # 或其他模型
```

### 启动应用

```bash
# 方式 1: 直接运行
python web_ui.py

# 方式 2: 使用启动脚本（包含环境检查）
./start.sh

# 应用将在 http://127.0.0.1:7860 启动
# 浏览器会自动打开，或手动访问该地址
```

### 使用流程

1. **📤 上传简历**：在「简历管理」页面上传 PDF 简历，或使用示例简历
2. **📊 评估简历**：在「简历评估」页面选择评估方式，获取专业反馈
3. **🎯 分析岗位**：在「岗位解读」页面粘贴 JD，生成面试问题
4. **💬 开始面试**：在「模拟面试」页面选择面试类型，开始对话练习

> 💡 **提示**：首次使用建议先查看 [用户指南](docs/USER_GUIDE.md) 了解详细功能

---

## 🛠️ 技术栈

| 类别 | 技术 | 说明 |
|------|------|------|
| **语言** | Python 3.10+ | 核心开发语言 |
| **Web UI** | Gradio 4.x | 交互式界面框架 |
| **LLM 集成** | OpenAI SDK | 兼容多种 LLM 服务 |
| **数据验证** | Pydantic v2 | 类型安全与数据建模 |
| **PDF 解析** | PyMuPDF / PyPDF2 | 简历文件解析 |
| **日志管理** | Loguru | 结构化日志记录 |
| **联网搜索** | DuckDuckGo | 可选的实时搜索 |

---

## 🤖 支持的 LLM 模型

系统兼容所有 OpenAI API 格式的服务，包括但不限于：

- **OpenAI**：GPT-3.5-turbo, GPT-4, GPT-4-turbo
- **DeepSeek**：deepseek-chat
- **阿里云通义千问**：qwen-turbo, qwen-plus, qwen-max
- **智谱 AI**：glm-4
- **其他兼容服务**：Ollama、vLLM 等本地部署方案

配置方式：在 `.env` 文件中设置对应的 `LLM_API_BASE` 和 `LLM_MODEL`

---

## 📚 文档导航

| 文档 | 适用人群 | 内容概要 |
|------|----------|----------|
| [用户指南](docs/USER_GUIDE.md) | 普通用户 | 详细使用说明、功能介绍、常见问题 |
| [开发指南](docs/DEVELOPER_GUIDE.md) | 开发者 | 二次开发、模块扩展、代码说明 |
| [架构文档](ARCHITECTURE.md) | 技术人员 | 系统架构、设计原则、数据流 |

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

**贡献领域**：
- 🐛 Bug 修复
- ✨ 新功能开发
- 📝 文档完善
- 🌍 多语言支持
- 🎨 UI/UX 优化

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## ⭐ Star History

如果这个项目对你有帮助，欢迎 Star ⭐️

---

**维护者**: [@pengshuang](https://github.com/pengshuang)  
**最后更新**: 2025-12-27
