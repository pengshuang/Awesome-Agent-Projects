# 📖 使用指南

> 面向普通用户的完整使用手册

## 目录

- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用界面](#使用界面)
- [常见场景](#常见场景)
- [问题排查](#问题排查)

---

## 快速开始

### 系统要求

- Python 3.9+
- 4GB+ RAM
- 2GB+ 磁盘空间

### 安装步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd academic-paper-qa

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
vim .env  # 编辑配置
```

### 最小配置

`.env` 文件必填项：

```bash
# LLM 配置（必填）
LLM_API_KEY=your-api-key
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo

# Embedding 配置（推荐本地模型）
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL_NAME=BAAI/bge-small-zh-v1.5
```

**支持的 LLM 服务商：**
- OpenAI: https://platform.openai.com/
- DeepSeek: https://platform.deepseek.com/
- Moonshot: https://platform.moonshot.cn/

---

## 配置说明

### 核心配置项

| 配置项 | 说明 | 默认值 | 范围 |
|--------|------|--------|------|
| `LLM_API_KEY` | LLM API Key | - | 必填 |
| `LLM_MODEL` | 模型名称 | gpt-3.5-turbo | - |
| `TEMPERATURE` | 生成温度 | 0.1 | 0.0-2.0 |
| `CHUNK_SIZE` | 文本分块大小 | 512 | 1-4096 |
| `RETRIEVAL_TOP_K` | 检索文档数 | 5 | 1-50 |
| `ENABLE_WEB_SEARCH` | 启用网络搜索 | true | true/false |

完整配置参见 `.env.example` 文件。

---

## 使用界面

### Web UI（推荐）

```bash
# 多轮对话（推荐）
./start_web_multi.sh

# 单轮问答
./start_web_single.sh

# 访问 http://127.0.0.1:7860
```

**功能：**
- 文档上传和索引构建
- RAG/LLM 模式切换
- 参数调整（Top-K、历史轮数）
- 启用/禁用网络搜索

### 命令行

```bash
# 多轮对话
./start_cli_multi.sh

# 单轮问答
./start_cli_single.sh
```

**命令：**
- `query <问题>` - 提问
- `list` - 列出文档
- `clear` - 清除历史
- `exit` - 退出

---

## 常见场景

### 论文快速理解

```bash
# 1. 添加论文
cp paper.pdf ./data/documents/

# 2. 启动并构建索引
./start_web_multi.sh

# 3. 提问
"这篇论文的主要贡献是什么？"
"实验是如何设计的？"
```

### 文献综述

```bash
# 添加多篇论文
cp paper*.pdf ./data/documents/

# 对比分析
"比较这些论文的方法有什么区别？"
```

### 技术细节挖掘

使用多轮对话深入讨论：
```
👤: Transformer 的注意力机制是如何工作的？
🤖: ...
👤: 为什么要使用多头注意力？
🤖: ...
```

---

## 问题排查

### API Key 错误

**症状：** `API Key validation failed`

**解决：**
1. 检查 `.env` 中 `LLM_API_KEY`
2. 确认 API Key 有效且有余额
3. 检查 `LLM_API_BASE` 正确

### 文档加载失败

**症状：** 构建索引时报错

**解决：**
1. 检查文档格式（PDF/DOCX/TXT/MD）
2. 查看日志：`logs/app.log`
3. 尝试单个文档测试

### Embedding 模型加载失败

**症状：** `Failed to load embedding model`

**解决：**
1. 首次使用需下载模型（1-2GB）
2. 或改用 OpenAI Embedding：
   ```bash
   EMBEDDING_PROVIDER=openai
   EMBEDDING_API_KEY=your-key
   ```

### 答案质量不佳

**优化方法：**
1. 调整 `RETRIEVAL_TOP_K`（增加检索数）
2. 使用更清晰具体的问题
3. 检查文档质量

---

## 高级功能

### 历史轮数控制

多轮对话支持 1-50+ 轮历史：

```python
# 代码设置
agent = AcademicAgent(max_history_turns=10)

# 环境变量
MAX_HISTORY_TURNS=10
```

**推荐：**
- 快速问答：1-5 轮
- 一般对话：5-10 轮
- 深度讨论：20-30 轮

### 批量处理

```bash
for paper in *.pdf; do
    python cli_single_turn.py query "总结 $paper"
done
```

---

**更新时间：** 2025-12-21
