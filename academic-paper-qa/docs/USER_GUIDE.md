# 📖 使用指南

## 目录
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [Web UI 使用](#web-ui-使用)
- [命令行使用](#命令行使用)
- [常见场景](#常见场景)
- [历史轮数控制](#历史轮数控制)
- [问题排查](#问题排查)

---

## 快速开始

### 系统要求
- Python 3.9+
- 4GB+ RAM
- 2GB+ 磁盘空间

### 三步上手

#### 1. 安装依赖
```bash
cd academic-paper-qa
pip install -r requirements.txt
```

#### 2. 配置 API
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
vim .env
```

**最小配置（必填）：**
```bash
LLM_API_BASE=https://api.moonshot.cn/v1  # API 端点
LLM_API_KEY=your-api-key-here             # 从 Moonshot 获取
LLM_MODEL=moonshot-v1-8k                  # 模型名称
```

#### 3. 启动使用
```bash
# Web UI 多轮对话（推荐）
./start_web_multi.sh

# 命令行多轮对话
./start_cli_multi.sh

# Web UI 单轮问答
./start_web_single.sh

# 命令行单轮问答
./start_cli_single.sh
```

---

## 配置说明

### 必须配置

#### 1. LLM API 配置
创建 `.env` 文件（可从 `.env.example` 复制）：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# ========== LLM 配置 ==========
# API 提供商：openai, moonshot, deepseek
LLM_PROVIDER=moonshot

# API 端点（必须包含 /v1 后缀）
LLM_API_BASE=https://api.moonshot.cn/v1

# API 密钥（从服务商获取）
LLM_API_KEY=your-api-key-here

# 模型名称
LLM_MODEL=moonshot-v1-8k

# 温度参数（0-1，越高越随机）
LLM_TEMPERATURE=0.7
```

**支持的 LLM 提供商：**

| 提供商 | API Base | 推荐模型 | 获取密钥 |
|--------|----------|----------|----------|
| **Moonshot** | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` | [Moonshot AI](https://platform.moonshot.cn/) |
| **OpenAI** | `https://api.openai.com/v1` | `gpt-3.5-turbo` | [OpenAI](https://platform.openai.com/) |
| **DeepSeek** | `https://api.deepseek.com/v1` | `deepseek-chat` | [DeepSeek](https://platform.deepseek.com/) |

**⚠️ 重要提示：**
- API Base 必须包含 `/v1` 后缀
- API Key 需要有足够的余额
- 不同模型的 context 长度不同，影响处理文档的大小

#### 2. Embedding 模型配置

```bash
# ========== Embedding 配置 ==========
# 模型路径（本地模型）
EMBEDDING_MODEL_NAME=BAAI/bge-small-zh-v1.5

# HuggingFace 缓存目录（可选）
HF_HOME=./models/huggingface
```

**首次运行会自动下载模型（约 100MB）：**
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-zh-v1.5')"
```

**国内加速下载（可选）：**
```bash
# 使用镜像源
export HF_ENDPOINT=https://hf-mirror.com
pip install -U huggingface_hub
```

### 可选配置

#### 3. 搜索引擎配置

```bash
# ========== 搜索配置 ==========
# 搜索提供商（目前仅支持 duckduckgo）
SEARCH_PROVIDER=duckduckgo

# 搜索结果数量
SEARCH_MAX_RESULTS=5
```

安装搜索依赖：
```bash
pip install duckduckgo-search
```

#### 4. 系统配置

```bash
# ========== 系统配置 ==========
# 文档目录
DOCUMENTS_DIR=./data/documents

# 向量存储目录
VECTOR_STORE_DIR=./data/vector_store

# 日志级别（DEBUG, INFO, WARNING, ERROR）
LOG_LEVEL=INFO

# 日志文件路径
LOG_FILE=./logs/app.log
```

#### 5. 检索参数配置

```bash
# ========== 检索配置 ==========
# Top-K 检索数量（返回最相关的 K 个文本块）
TOP_K=5

# 相似度阈值（0-1，越高越严格）
SIMILARITY_THRESHOLD=0.7

# 文本块大小（字符数）
CHUNK_SIZE=512

# 文本块重叠大小
CHUNK_OVERLAP=50
```

### 配置文件结构

```
academic-paper-qa/
├── .env                  # 主配置文件（不提交到 Git）
├── .env.example          # 配置模板
├── config/
│   ├── llm_config.py     # LLM 配置类
│   ├── embedding_config.py  # Embedding 配置类
│   └── search_config.py  # 搜索配置类
```

### 验证配置

运行配置检查脚本：
```bash
python init_system.py
```

**输出示例：**
```
✅ 环境配置检查通过
✅ LLM API 连接成功
✅ Embedding 模型加载成功
✅ 向量存储目录已创建
⚠️  未找到文档，请添加文档到 ./data/documents/
```

---

## Web UI 使用

### 启动 Web UI

```bash
# 方式 1：直接启动
python web_ui.py

# 方式 2：使用启动脚本
bash start_web_ui.sh

# 方式 3：后台运行
nohup python web_ui.py > logs/webui.log 2>&1 &
```

**启动成功后会显示：**
```
Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://xxxxx.gradio.live (如果开启了分享)
```

### Web UI 界面说明

#### 标签页 1：问答系统

```
┌─────────────────────────────────────────┐
│  问答模式:  ◉ RAG 模式  ○ LLM 模式     │
│  联网搜索:  ☐ 启用联网搜索             │
│  Top-K:     [====|====] 5              │
├─────────────────────────────────────────┤
│  请输入您的问题:                         │
│  ┌───────────────────────────────────┐  │
│  │ 这篇论文的主要贡献是什么？        │  │
│  └───────────────────────────────────┘  │
│              [提交问题]                  │
├─────────────────────────────────────────┤
│  📝 答案:                               │
│  本文的主要贡献包括...                  │
│                                         │
│  📌 参考来源 1:                         │
│  文件: transformer.pdf                  │
│  相似度: 0.89                           │
│  内容: "我们提出了..."                  │
└─────────────────────────────────────────┘
```

**使用步骤：**

1. **选择模式**
   - **RAG 模式**：基于本地文档回答（推荐）
   - **LLM 模式**：直接使用大模型回答

2. **配置参数**
   - **联网搜索**：勾选后可获取最新信息
   - **Top-K**：调整检索数量（1-10）
     - 值越大，检索范围越广
     - 建议初始值：5

3. **输入问题**
   - 支持中英文
   - 可以多轮对话
   - 支持上下文引用

4. **查看答案**
   - 答案：模型生成的回答
   - 来源：显示原文出处（RAG 模式）
   - 相似度：相关性评分

#### 标签页 2：索引构建

```
┌─────────────────────────────────────────┐
│  文档目录路径:                           │
│  ┌───────────────────────────────────┐  │
│  │ ./data/documents                  │  │
│  └───────────────────────────────────┘  │
│                                         │
│  强制重建: ☐ 重建索引（删除旧数据）     │
│                                         │
│              [构建索引]                  │
├─────────────────────────────────────────┤
│  📊 构建状态:                           │
│  ✅ 索引构建成功！                      │
│                                         │
│  总文档数量: 35 个文本块                │
│  源文件数量: 3 个                       │
│                                         │
│  各文件详情:                            │
│  • transformer.pdf: 15 个文本块         │
│  • attention.pdf: 12 个文本块           │
│  • bert.pdf: 8 个文本块                 │
└─────────────────────────────────────────┘
```

**使用步骤：**

1. **准备文档**
   ```bash
   # 将论文放到文档目录
   cp your_paper.pdf ./data/documents/
   
   # 支持子目录
   mkdir -p ./data/documents/nlp/
   cp papers/*.pdf ./data/documents/nlp/
   ```

2. **构建索引**
   - 输入文档目录路径（默认：`./data/documents`）
   - 首次构建或文档更新时，勾选「强制重建」
   - 点击「构建索引」按钮
   - 等待构建完成（大约 5-10 秒/文档）

3. **查看统计**
   - 总文本块数：文档被分割成的片段数
   - 源文件数：实际的文档文件数
   - 各文件详情：每个文件的文本块分布

**⚠️ 注意事项：**
- 构建过程中保持页面打开，不要刷新
- 大量文档建议使用命令行方式
- 索引会自动保存，下次启动自动加载

### 实际操作示例

#### 示例 1：快速问答
```
1. 启动 Web UI
2. 确认已有索引（底部状态栏显示）
3. 输入问题："Transformer 模型的核心创新是什么？"
4. 选择 RAG 模式
5. 点击提交
6. 查看答案和来源
```

#### 示例 2：联网增强
```
1. 输入问题："GPT-4 相比 GPT-3 有什么改进？"
2. 勾选「启用联网搜索」
3. 选择 LLM 模式
4. 提交问题
5. 获得最新信息
```

#### 示例 3：深度检索
```
1. 输入复杂问题："论文中的多头注意力机制是如何实现的？"
2. 调整 Top-K 为 8（增加检索范围）
3. 选择 RAG 模式
4. 查看多个来源的综合答案
```

---

## 命令行使用

### 基础命令

#### 1. 构建索引
```bash
# 基础构建
python main.py build

# 指定文档目录
python main.py build --input-dir ./data/documents

# 强制重建（删除旧索引）
python main.py build --force-rebuild

# 完整参数示例
python main.py build \
  --input-dir ./data/documents \
  --force-rebuild \
  --chunk-size 512 \
  --chunk-overlap 50
```

**参数说明：**
- `--input-dir`: 文档目录路径
- `--force-rebuild`: 强制重建索引
- `--chunk-size`: 文本块大小（字符数）
- `--chunk-overlap`: 文本块重叠大小

**输出示例：**
```
📚 开始加载文档...
✅ 已加载 3 个文档，共 35 个文本块

📊 统计信息:
  • transformer.pdf: 15 个文本块
  • attention.pdf: 12 个文本块
  • bert.pdf: 8 个文本块

🔨 开始构建索引...
✅ 索引构建完成！
💾 索引已保存到: ./data/vector_store/
```

#### 2. RAG 问答
```bash
# 基础问答
python main.py query "这篇论文的主要贡献是什么？"

# 带参数问答
python main.py query "Transformer 如何工作？" \
  --top-k 5 \
  --similarity-threshold 0.7

# 联网搜索增强
python main.py query "最新的 NLP 进展" \
  --web-search \
  --max-results 5
```

**参数说明：**
- `--top-k`: 检索数量（默认：5）
- `--similarity-threshold`: 相似度阈值（默认：0.7）
- `--web-search`: 启用联网搜索
- `--max-results`: 搜索结果数（默认：5）

**输出示例：**
```
🤔 问题: 这篇论文的主要贡献是什么？

💬 答案:
本文的主要贡献包括:
1. 提出了完全基于注意力机制的 Transformer 架构
2. 证明了自注意力机制在序列建模中的有效性
3. 在多个任务上取得了 SOTA 性能

📌 参考来源 1:
   文件: transformer.pdf
   相似度: 0.89
   页码: 1
   内容: "我们提出了 Transformer，一个完全基于注意力机制的模型架构..."

📌 参考来源 2:
   文件: transformer.pdf
   相似度: 0.85
   页码: 8
   内容: "实验结果表明，Transformer 在机器翻译任务上..."
```

#### 3. LLM 直接对话
```bash
# 基础对话
python main.py llm "解释一下什么是注意力机制"

# 联网对话
python main.py llm "2024年有哪些重要的 AI 论文？" \
  --web-search

# 调整温度参数
python main.py llm "给我一些研究建议" \
  --temperature 0.9
```

**参数说明：**
- `--web-search`: 启用联网搜索
- `--temperature`: 温度参数（0-1）
- `--max-tokens`: 最大生成长度

### 高级用法

#### 批量处理
```bash
# 批量问题文件（每行一个问题）
cat questions.txt | while read question; do
  python main.py query "$question" >> answers.txt
done
```

#### 导出结果
```bash
# 导出为 JSON
python main.py query "问题" --output-format json > result.json

# 导出为 Markdown
python main.py query "问题" --output-format markdown > result.md
```

#### 性能监控
```bash
# 启用详细日志
python main.py query "问题" --log-level DEBUG

# 显示性能统计
python main.py query "问题" --show-stats
```

---

## 常见场景

### 场景 1：新手上手（5分钟）

**目标**：快速体验系统功能

```bash
# 1. 配置 API
cp .env.example .env
vim .env  # 填入你的 API Key

# 2. 准备示例文档
mkdir -p ./data/documents
cp ~/Downloads/paper.pdf ./data/documents/

# 3. 启动 Web UI
python web_ui.py

# 4. 浏览器访问 http://localhost:7860
# 5. 在「索引构建」标签页构建索引
# 6. 在「问答」标签页提问
```

### 场景 2：日常使用

**目标**：高效阅读多篇论文

```bash
# 1. 批量添加论文
cp ~/Downloads/*.pdf ./data/documents/nlp/

# 2. 构建索引（命令行更快）
python main.py build --force-rebuild

# 3. 使用 Web UI 进行交互式问答
python web_ui.py

# 4. 典型问题流程：
#    a. 总体了解："这些论文的主要研究方向是什么？"
#    b. 深入细节："Transformer 的实现细节"
#    c. 对比分析："BERT 和 GPT 的区别"
#    d. 拓展思考："未来可能的研究方向"
```

### 场景 3：文献综述

**目标**：系统整理某个领域的文献

```bash
# 1. 准备文献（按主题分类）
./data/documents/
├── attention/       # 注意力机制相关
├── transformer/     # Transformer 相关
└── applications/    # 应用相关

# 2. 分别构建索引
python main.py build --input-dir ./data/documents/attention
python main.py build --input-dir ./data/documents/transformer

# 3. 使用脚本批量提问
cat << EOF > review_questions.txt
这个领域的发展历程是怎样的？
主要的技术方法有哪些？
各种方法的优缺点是什么？
未来的研究方向有哪些？
EOF

# 4. 批量生成答案
while read q; do
  echo "## $q" >> review.md
  python main.py query "$q" >> review.md
  echo "" >> review.md
done < review_questions.txt
```

### 场景 4：实时跟踪

**目标**：了解领域最新进展

```bash
# 使用 LLM 模式 + 联网搜索
python main.py llm "2024年 Transformer 有哪些新进展？" \
  --web-search \
  --max-results 10

# 定期执行（cron 任务）
# 每天 9:00 获取最新进展
0 9 * * * cd /path/to/project && \
  python main.py llm "最新的 NLP 研究" --web-search \
  >> ./logs/daily_updates.log
```

---

## 问题排查

### 常见问题

#### 1. API 连接失败

**错误信息：**
```
❌ Error: Connection timeout
❌ Error: Invalid API key
```

**解决方案：**
```bash
# 检查配置
cat .env | grep LLM

# 测试连接
python -c "
from src.config.llm_config import LLMConfig
config = LLMConfig()
print(f'API Base: {config.api_base}')
print(f'API Key: {config.api_key[:8]}...')
"

# 测试 API 调用
curl -X POST "https://api.moonshot.cn/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "moonshot-v1-8k",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

#### 2. Embedding 模型加载失败

**错误信息：**
```
❌ Error: Failed to load model BAAI/bge-small-zh-v1.5
```

**解决方案：**
```bash
# 手动下载模型
pip install -U huggingface_hub
export HF_ENDPOINT=https://hf-mirror.com  # 国内镜像
huggingface-cli download BAAI/bge-small-zh-v1.5

# 指定缓存目录
export HF_HOME=./models/huggingface
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-zh-v1.5')"
```

#### 3. 构建索引失败

**错误信息：**
```
❌ 构建索引失败: [Errno 32] Broken pipe
```

**解决方案：**
```bash
# 方法 1: 使用命令行构建（更稳定）
python main.py build --input-dir ./data/documents

# 方法 2: 减少文档数量
# 先测试单个文档
mkdir -p ./data/documents/test
cp your_paper.pdf ./data/documents/test/
python main.py build --input-dir ./data/documents/test

# 方法 3: 检查文档格式
file ./data/documents/*.pdf  # 确认是有效的 PDF

# 方法 4: 清理缓存重试
rm -rf ./data/vector_store/*
python main.py build --force-rebuild
```

#### 4. Web UI 无法访问

**错误信息：**
```
Connection refused
Port 7860 already in use
```

**解决方案：**
```bash
# 检查端口占用
lsof -i :7860

# 杀死占用进程
pkill -f "python web_ui.py"

# 使用其他端口
python web_ui.py --server-port 7861

# 检查防火墙
# Mac
sudo pfctl -s rules | grep 7860

# Linux
sudo iptables -L | grep 7860
```

#### 5. 内存不足

**错误信息：**
```
❌ Error: Out of memory
```

**解决方案：**
```bash
# 减小批次大小
export BATCH_SIZE=1

# 减小文本块大小
vim .env
# 修改: CHUNK_SIZE=256  (默认 512)

# 分批构建索引
python main.py build --input-dir ./data/documents/batch1
python main.py build --input-dir ./data/documents/batch2

# 使用更小的 Embedding 模型
# 修改 .env: EMBEDDING_MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

### 日志分析

#### 查看日志
```bash
# 实时查看
tail -f ./logs/app.log

# 查看错误
grep ERROR ./logs/app.log

# 查看最近 100 行
tail -n 100 ./logs/app.log

# 按时间筛选
grep "2024-12-20" ./logs/app.log
```

#### 启用调试模式
```bash
# 修改配置
vim .env
# 添加: LOG_LEVEL=DEBUG

# 或临时启用
python main.py query "问题" --log-level DEBUG
```

### 性能优化

#### 1. 加速索引构建
```bash
# 使用更快的 Embedding 模型
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# 减小文本块大小
CHUNK_SIZE=256

# 禁用文本清理（如果不需要）
python main.py build --no-clean-text
```

#### 2. 加速检索
```bash
# 减小 Top-K
python main.py query "问题" --top-k 3

# 提高相似度阈值
python main.py query "问题" --similarity-threshold 0.8
```

#### 3. 减少 API 调用
```bash
# 使用更短的 prompt
# 减小 max_tokens
# 使用更便宜的模型
```

### 获取帮助

- 📖 查看详细文档：`docs/`
- 🐛 报告问题：GitHub Issues
- 💬 社区讨论：GitHub Discussions
- 📧 邮件联系：your-email@example.com

---

## 历史轮数控制

### 功能说明

多轮对话模式支持灵活控制保留的历史对话轮数，避免 Token 消耗过大。

**核心概念：**
- 1轮对话 = 1条用户消息 + 1条助手回复 = 2条消息
- 默认保留最近10轮对话（20条消息）
- 可配置范围：1-50+轮

### 使用方式

#### 方式1: 初始化时设置（推荐）

```python
from src.agent import AcademicAgent

# 只保留最近5轮对话
agent = AcademicAgent(max_history_turns=5)

# 保留50轮对话（长对话场景）
agent = AcademicAgent(max_history_turns=50)

# 使用默认值（10轮）
agent = AcademicAgent()
```

#### 方式2: 运行时动态修改

```python
# 创建agent
agent = AcademicAgent()

# 查看当前设置
print(f"最大轮数: {agent.max_history_turns}")

# 动态修改为20轮
agent.set_max_history_turns(20)

# 修改为50轮
agent.set_max_history_turns(50)

# 查看当前状态
info = agent.get_chat_history_info()
print(f"当前: {info['current_turns']}/{info['max_turns']} 轮")
print(f"消息数: {info['total_messages']} 条")
print(f"已满: {info['is_full']}")
```

#### 方式3: Web UI 可视化控制

**步骤：**

1. **启动 Web UI**
```bash
python web_ui_multi_turn.py
# 或
./start_web_multi.sh
```

2. **在界面中调整**
   - 进入「RAG 对话」标签页
   - 在右侧设置栏找到「📊 对话历史控制」
   - 使用滑块调整「最大历史轮数」（1-50轮）
   - 点击「✅ 更新历史设置」按钮
   - 查看「历史状态」显示当前轮数

3. **查看系统状态**
   - 进入「ℹ️ 系统信息」标签页
   - 点击「🔄 刷新信息」
   - 查看详细的对话历史信息

#### 方式4: 环境变量配置

在 `.env` 文件中设置：

```bash
# 设置默认历史轮数为50
MAX_HISTORY_TURNS=50
```

系统启动时会自动读取此配置。

### 查看和管理

#### 查看历史状态

```python
# 获取详细信息
info = agent.get_chat_history_info()

print(f"当前轮数: {info['current_turns']}")
print(f"最大限制: {info['max_turns']}")
print(f"总消息数: {info['total_messages']}")
print(f"是否已满: {info['is_full']}")
```

**返回字段说明：**
- `current_turns`: 当前对话轮数
- `max_turns`: 最大限制轮数
- `total_messages`: 总消息数（轮数 × 2）
- `is_full`: 是否已达上限

#### 清空历史

```python
# 清空所有历史
agent.clear_chat_history()
```

在 Web UI 中点击「🗑️ 清空对话历史」按钮。

### 使用场景推荐

| 场景 | 推荐轮数 | Token估算 | 适用情况 |
|------|---------|-----------|---------|
| 快速问答 | 1-5轮 | 最少 | 独立问题，节省成本 |
| 一般对话 | 5-10轮 | 适中 | 默认配置，平衡体验 |
| 深度讨论 | 20-30轮 | 较多 | 学术讨论，连续推理 |
| 长期对话 | 50+轮 | 很多 | 完整记忆，特殊场景 |

### 实际应用示例

#### 示例1: 根据用户级别配置

```python
def create_agent_for_user(user_level: str):
    """根据用户等级创建不同配置的agent"""
    config = {
        "free": 5,       # 免费用户：5轮
        "basic": 15,     # 基础用户：15轮
        "premium": 50    # 高级用户：50轮
    }
    
    turns = config.get(user_level, 10)
    return AcademicAgent(max_history_turns=turns)

# 使用
free_agent = create_agent_for_user("free")      # 5轮
basic_agent = create_agent_for_user("basic")    # 15轮
premium_agent = create_agent_for_user("premium") # 50轮
```

#### 示例2: 动态调整策略

```python
# 根据对话复杂度调整
def adjust_history_by_complexity(agent, conversation_depth):
    if conversation_depth == "simple":
        agent.set_max_history_turns(5)
    elif conversation_depth == "medium":
        agent.set_max_history_turns(15)
    else:  # complex
        agent.set_max_history_turns(30)

# 根据Token使用量调整
def adjust_history_by_tokens(agent, total_tokens_used):
    if total_tokens_used > 50000:
        agent.set_max_history_turns(5)   # 降低消耗
    elif total_tokens_used > 20000:
        agent.set_max_history_turns(10)
    else:
        agent.set_max_history_turns(20)
```

#### 示例3: 定期清理策略

```python
# 切换话题时清空
if user_says("换个话题"):
    agent.clear_chat_history()
    print("✅ 已切换到新话题")

# 定期清空（避免上下文污染）
if message_count % 50 == 0:
    agent.clear_chat_history()
    print("✅ 已自动清理历史")

# 用户主动清空
if user_command == "/clear":
    agent.clear_chat_history()
    print("✅ 历史已清空")
```

### Token 消耗计算

```
每轮Token ≈ 问题Token + 回答Token
总Token = 当前问题 + Σ(历史轮次Token)

示例（假设每轮500 Token）：
- 5轮：  5 × 500 = 2,500 Token
- 10轮：10 × 500 = 5,000 Token
- 50轮：50 × 500 = 25,000 Token
```

### 最佳实践

#### 1. 根据场景选择轮数

```python
# ❌ 不推荐：历史太长，Token浪费
agent = AcademicAgent(max_history_turns=100)

# ✅ 推荐：根据场景选择
# 快速问答
agent = AcademicAgent(max_history_turns=5)

# 深度讨论
agent = AcademicAgent(max_history_turns=20)

# 特殊场景才使用大历史
if need_long_memory:
    agent = AcademicAgent(max_history_turns=50)
```

#### 2. 监控历史使用情况

```python
# 定期检查
info = agent.get_chat_history_info()
if info['is_full']:
    print(f"⚠️  历史已满 ({info['current_turns']}/{info['max_turns']})")
    print("提示：考虑清空历史或增加限制")
```

#### 3. 自适应调整

```python
# 根据实际使用动态调整
def smart_adjust(agent):
    info = agent.get_chat_history_info()
    
    # 历史快满时提醒
    if info['current_turns'] >= info['max_turns'] * 0.8:
        print("💡 提示：历史接近上限，可考虑清理")
    
    # 长时间未使用时重置
    if idle_time > 3600:  # 1小时
        agent.clear_chat_history()
```

### 常见问题

**Q: 修改轮数后，现有历史会丢失吗？**  
A: 如果减小轮数，会自动裁剪，只保留最近N轮。如果增大轮数，现有历史完全保留。

**Q: 如何选择合适的轮数？**  
A: 根据场景选择：简单问答用5轮，深度讨论用20-30轮，特殊场景用50+轮。

**Q: 轮数对性能有什么影响？**  
A: 轮数越多，每次请求的Token越多，响应时间和API成本都会增加。

**Q: 1轮对话等于多少条消息？**  
A: 1轮 = 1条用户消息 + 1条助手回复 = 2条消息。

---

## 下一步

- 👨‍💻 阅读 [开发者文档](DEVELOPER_GUIDE.md) 进行二次开发
- 📋 查看 [功能介绍](FEATURES.md) 了解更多特性
- 🚀 开始使用：`python web_ui_multi_turn.py`
