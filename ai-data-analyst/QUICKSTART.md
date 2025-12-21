# 快速开始

## 🚀 5分钟快速启动指南

### 1. 安装依赖（首次运行）

```bash
cd ai-data-analyst
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，至少配置以下内容：
# LLM_API_KEY=your-api-key-here
# LLM_API_BASE=https://api.openai.com/v1
# LLM_MODEL=gpt-3.5-turbo
```

**常用配置示例**：

#### 使用 OpenAI
```bash
LLM_API_KEY=sk-...
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
```

#### 使用 DeepSeek（推荐，性价比高）
```bash
LLM_API_KEY=sk-...
LLM_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

#### 使用阿里云通义千问
```bash
LLM_API_KEY=sk-...
LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo
```

### 3. 创建示例数据库（可选）

```bash
python data/create_example_db.py
```

这会创建一个包含销售数据的示例数据库，用于测试。

### 4. 启动服务

```bash
bash start.sh
# 或
python web_ui.py
```

### 5. 访问界面

打开浏览器访问：http://localhost:7860

### 6. 使用系统

#### 步骤 1：初始化系统
- 切换到「⚙️ 系统设置」标签页
- 点击「🔄 初始化系统」按钮

#### 步骤 2：注册数据源
- 切换到「🗄️ 数据源管理」标签页
- 注册示例数据库：
  - 名称：`sales_db`
  - 路径：`data/databases/example_sales.db`

#### 步骤 3：开始提问
- 切换到「💬 对话分析」标签页
- 选择数据源：`sales_db`
- 输入问题，例如：
  - "查询销售总额最高的产品"
  - "分析各地区的销售情况"
  - "统计每月的销售趋势"

## 📝 示例对话

### 示例 1：查询数据
```
👤 用户：查询销售总额最高的产品

🤖 助手：
### 生成的SQL查询

​```sql
SELECT 
    p.product_name,
    SUM(s.quantity * p.price) as total_revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_revenue DESC
LIMIT 1
​```

### 分析结果

根据查询结果，笔记本电脑是销售总额最高的产品...
```

### 示例 2：多轮对话
```
👤 用户：查询各地区的销售情况
🤖 助手：[展示各地区销售数据]

👤 用户：哪个地区最好？
🤖 助手：华东地区销售最好，订单数量和销售额都位居第一

👤 用户：给出详细数据
🤖 助手：[展示华东地区的详细数据和分析]
```

### 示例 3：数据分析
```
👤 用户：分析销售趋势，给出改进建议

🤖 助手：
根据数据分析：

**趋势分析**：
- 最近3个月销售呈上升趋势
- 电子产品类别占比最高
- 华东和华南地区表现突出

**改进建议**：
1. 加大华中和西南地区的市场推广
2. 丰富家具类产品线
3. 针对热销产品制定促销策略
...
```

## 🔧 常见问题

### Q: 启动失败？
- 检查 Python 版本（需要 3.8+）
- 确保已安装所有依赖
- 查看 `.env` 文件配置是否正确

### Q: LLM 调用失败？
- 检查 API Key 是否正确
- 确认网络可以访问 API 地址
- 查看日志：`logs/ai_data_analyst_*.log`

### Q: SQL 生成不准确？
- 提供更详细的问题描述
- 使用多轮对话逐步明确需求
- 检查数据库 schema 是否正确加载

## 📚 下一步

- 查看 [功能介绍](docs/FEATURES.md) 了解完整功能
- 阅读 [用户指南](docs/USER_GUIDE.md) 学习详细用法
- 查看 [开发指南](docs/DEVELOPER_GUIDE.md) 进行二次开发

## 🎉 开始探索吧！

现在您已经完成了基本设置，可以开始探索 AI 数据分析助手的强大功能了！

有问题？查看文档或提交 Issue。
