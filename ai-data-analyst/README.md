# AI 数据分析助手

<div align="center">

🤖 基于大模型的智能数据分析工具

自然语言交互 | 多数据源支持 | 自动可视化 | 报告生成

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.0+-green.svg)](https://docs.pydantic.dev/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

中文 | [English](README_EN.md)

</div>

---

## ✨ 功能特性

通过自然语言对话，无需编写代码，即可完成：

- 🗄️ **多数据源查询** - SQLite、CSV/Excel、JSON、Parquet
- 🔄 **NL2SQL** - 自然语言自动转换为 SQL
- 📊 **智能可视化** - 自动生成交互式图表
- 💬 **上下文对话** - 连贯的多轮分析对话
- 🔌 **LLM 兼容** - OpenAI、DeepSeek、Qwen 等
- ✅ **数据验证** - 基于 Pydantic 的类型安全

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env 填入你的 LLM API Key

# 3. 创建示例数据（可选）
python data/create_example_db.py

# 4. 启动 Web 界面
python web_ui.py
# 访问 http://localhost:7860
```

## 📖 文档

- [用户使用指南](docs/USER_GUIDE.md) - 面向普通用户
- [开发者指南](docs/DEVELOPER_GUIDE.md) - 面向开发者
- [Pydantic 数据验证](docs/PYDANTIC_GUIDE.md) - 数据模型说明

## 💡 使用示例

**自然语言查询**
```
查询每个月的销售额趋势
```

**数据分析**
```
分析哪个产品销量最好，给出可视化图表
```

**多轮对话**
```
用户: 查询销售数据
助手: [返回销售数据]
用户: 帮我生成柱状图
助手: [生成可视化图表]
```

## 💡 使用示例

**自然语言查询**
```
查询每个月的销售额趋势
分析哪个产品销量最好
```

**多轮对话**
```
用户: 查询销售数据
助手: [返回销售数据]
用户: 帮我生成柱状图
助手: [生成可视化图表]
```

## 🛠️ 技术栈

- **框架**: Gradio (Web UI)
- **LLM**: LlamaIndex + OpenAI/DeepSeek/Qwen
- **数据验证**: Pydantic v2
- **可视化**: Plotly
- **数据处理**: Pandas

## 📂 项目结构

```
ai-data-analyst/
├── config/              # 配置模块
├── src/
│   ├── models/         # Pydantic 数据模型
│   ├── datasources/    # 数据源适配器
│   ├── analyzers/      # 数据分析器
│   └── tools/          # NL2SQL 等工具
├── data/               # 数据目录
├── docs/               # 文档
└── web_ui.py          # Web 界面入口
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
