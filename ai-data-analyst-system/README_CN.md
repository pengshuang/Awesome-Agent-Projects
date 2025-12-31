# AI 数据分析助手

🤖 基于大模型的智能数据分析工具

自然语言交互 | 一键可视化 | 多数据源支持

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[English](README.md) | 中文

---

## 🖼️ 界面预览

![ui-1](imgs/ui-1.png)

**极简设计，3步完成分析**：添加数据源 → 输入问题 → 自动生成图表

## ✨ 核心特性

- 🗨️ **自然语言分析** - 无需 SQL，用中文提问即可查询数据
- 📊 **自动可视化** - 查询结果自动生成图表，支持 6 种图表类型
- 🗄️ **多数据源** - 支持 SQLite、CSV/Excel、JSON 等
- 💬 **上下文对话** - 支持多轮连续对话分析
- 🔌 **兼容多 LLM** - OpenAI、DeepSeek、Qwen、Moonshot 等
- 📈 **历史查询** - 保存查询历史，随时切换查看

## ⚡ 主要优势

- **零学习成本** - 页面自动初始化，内置操作指引
- **单屏设计** - 左侧对话右侧可视化，无需切换标签
- **实时预览** - 图表参数修改即时生效
- **智能推荐** - 自动选择最佳图表类型和数据列

<div style="background-color: #f0f7ff; padding: 20px; border-radius: 8px; border-left: 4px solid #0969da;">

## 🚀 快速开始

```bash
# 1. 克隆并进入目录
git clone https://github.com/pengshuang/Awesome-Agent-Projects.git
cd Awesome-Agent-Projects/ai-data-analyst

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key
cp .env.example .env
# 编辑 .env 文件，填入你的 LLM API Key

# 4. 创建示例数据（可选）
python data/create_example_db.py

# 5. 启动 Web 界面
python web_ui.py
# 访问 http://localhost:7860
```

</div>

## 📖 文档

- [用户使用指南](docs/USER_GUIDE.md) - 面向普通用户
- [开发者指南](docs/DEVELOPER_GUIDE.md) - 面向开发者

## 💡 使用示例

**查看界面指引**
- 打开页面后，顶部蓝色卡片显示 3 步操作流程
- 自动初始化，无需手动配置

**快速添加数据源**
- 点击底部「➕ 快速添加数据源」
- 选择类型、填写名称和路径即可

**自然语言查询**
```
查询销售额最高的前 10 个产品
```
→ 自动生成 SQL → 执行查询 → 右侧自动显示图表

**查看历史查询**
- 右侧可视化区域的下拉框可切换历史查询
- 每次查询自动保存，随时回看

**调整图表样式**
- 点击「⚙️ 图表设置」可修改图表类型和坐标轴
- 修改后实时更新，无需点击生成按钮

## 🛠️ 技术栈

- **UI 框架**: Gradio 4.x - 单屏设计，自动初始化
- **LLM 集成**: LlamaIndex - 支持多种 LLM 提供商
- **可视化**: Plotly - 交互式图表，实时更新
- **数据处理**: Pandas - 高效数据处理
- **配置管理**: Pydantic v2 - 类型安全的配置验证

---

## 📄 许可证

MIT License
