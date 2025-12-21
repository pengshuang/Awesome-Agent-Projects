# AI 数据分析助手

<div align="center">

🤖 基于大模型的智能数据分析工具

支持多数据源融合分析 | NL2SQL | 数据可视化 | 报告生成

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## ✨ 项目简介

AI 数据分析助手是一个基于大语言模型的智能数据分析工具。通过自然语言交互，无需编写SQL或代码，即可完成数据查询、分析、可视化和报告生成。

### 🎯 核心特性

- **🗄️ 多数据源** - 支持 SQLite、CSV/Excel、知识库、Web 搜索
- **🔄 NL2SQL** - 自然语言自动转换为 SQL 查询
- **📊 数据可视化** - 交互式图表（柱状图、折线图、饼图等）
- **💬 多轮对话** - 上下文理解，连贯的对话体验
- **📝 报告生成** - 自动生成数据分析报告
- **🔌 LLM 兼容** - 支持 OpenAI、DeepSeek、通义千问等

### 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境
cp .env.example .env
# 编辑 .env 文件，填入 LLM API Key

# 3. 启动服务
python web_ui.py

# 4. 访问界面
# http://localhost:7860
```

### 💡 快速体验

#### 创建示例数据库

```bash
python data/create_example_db.py
```

这将创建一个包含销售数据的示例数据库，包含：
- `sales` 表：销售数据（24条记录）
- `customers` 表：客户数据（8条记录）

#### 完整体验流程

1. **初始化系统**
   - 打开 http://localhost:7860
   - 切换到「⚙️ 系统设置」标签页
   - 点击「🔄 初始化系统」

2. **注册数据源**
   - 切换到「🗄️ 数据源管理」标签页
   - 注册示例数据库：
     - 数据库名称: `sales_db`
     - 数据库路径: `data/databases/sales_example.db`

3. **数据查询分析**
   - 切换到「💬 对话分析」标签页
   - 选择数据源: `sales_db`
   - 示例查询：
     ```
     查询每个月的总销售额，按月份排序
     ```

4. **数据可视化**
   - 切换到「📊 数据可视化」标签页
   - 点击「🔄 加载数据」
   - 配置图表：
     - 图表类型：折线图
     - X轴：date（月份）
     - Y轴：total_revenue（总销售额）
   - 点击「🎨 生成图表」

#### 更多查询示例

**产品销量对比**
```
查询每个产品的总销量和总销售额
```
可视化：柱状图，X轴=product，Y轴=total_quantity

**产品销售占比**
```
查询每个产品的总销售额
```
可视化：饼图，X轴=product，Y轴=total_revenue

**多产品趋势分析**
```
查询每个月每个产品的销售额
```
可视化：折线图，X轴=date，Y轴=revenue，颜色分组=product

### 📚 文档导航

根据您的需求选择相应文档：

| 文档 | 适用人群 | 内容 |
|------|---------|------|
| [📖 功能介绍](docs/FEATURES.md) | 所有用户 | 详细的功能说明和使用场景 |
| [👤 用户指南](docs/USER_GUIDE.md) | 普通用户 | 安装、配置、使用教程 |
| [💻 开发指南](docs/DEVELOPER_GUIDE.md) | 开发者 | 架构设计、API、二次开发 |

### 🎬 使用场景

- **业务分析** - 快速查询和分析业务数据库
- **数据探索** - 探索性数据分析（EDA）
- **报告生成** - 自动生成专业数据分析报告
- **数据可视化** - 零代码创建交互式图表
- **决策支持** - 基于多数据源的智能决策建议

### 🏗️ 技术栈

- **后端**: Python 3.8+, LlamaIndex, Pandas
- **前端**: Gradio 4.0+
- **可视化**: Plotly
- **LLM**: OpenAI/DeepSeek/通义千问 API
- **数据库**: SQLite
- **日志**: Loguru

### 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 📄 许可证

MIT License

本项目参考了 [academic-paper-qa](../academic-paper-qa) 的设计架构。

---

**💡 提示**：使用前请确保已正确配置 `.env` 文件中的 LLM API Key。
