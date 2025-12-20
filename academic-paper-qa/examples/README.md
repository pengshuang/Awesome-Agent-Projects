# Examples 示例文件说明

本目录包含各种使用示例，帮助你快速上手项目。

---

## 📚 示例列表

### 🚀 入门示例

#### 1. **quick_start.py** - 快速开始（推荐新手）
3 步快速上手，演示最基本的使用流程。

**适合**: 第一次使用的新手
**功能**: 初始化 → 加载索引 → 执行查询

```bash
python examples/quick_start.py
```

---

#### 2. **build_index.py** - 构建索引
首次使用前必须运行，用于构建文档索引。

**适合**: 首次安装或更新文档后
**功能**: 加载文档 → 构建向量索引 → 持久化

```bash
python examples/build_index.py
```

---

### 🎯 核心功能示例

#### 3. **agent_demo.py** - Agent 完整功能演示
演示 Agent 的所有功能，包含 6 个子示例。

**适合**: 想全面了解 Agent 功能的用户
**功能**: 
- 基础使用
- 执行查询
- 强制重建索引
- 自定义路径
- 交互式问答
- 高级查询选项

```bash
python examples/agent_demo.py
```

---

### 🌐 高级功能示例

#### 4. **web_search_demo.py** - 联网搜索功能
演示如何使用联网搜索增强问答能力。

**适合**: 需要查询本地文档以外信息的用户
**功能**:
- RAG 模式 + 联网搜索
- 对比启用/禁用联网搜索
- 查询新话题（本地文档不存在）

```bash
python examples/web_search_demo.py
```

**前置条件**: 在 `.env` 文件中设置 `ENABLE_WEB_SEARCH=true`

---

#### 5. **direct_llm_demo.py** - 直接 LLM 对话模式
演示不使用向量检索，直接与 LLM 对话。

**适合**: 想使用通用知识或进行开放对话的用户
**功能**:
- 基础 LLM 对话
- LLM + 联网搜索
- RAG vs LLM 对比
- 交互式对话

```bash
python examples/direct_llm_demo.py
```

---

#### 6. **advanced_query.py** - 高级查询选项
演示 Agent 的高级查询参数和性能优化。

**适合**: 需要调优查询效果的高级用户
**功能**:
- 自定义 top_k（检索文档数量）
- 查看源文档详细信息
- 查询性能分析

```bash
python examples/advanced_query.py
```

---

### 🔧 底层功能示例

#### 7. **document_loader_demo.py** - 文档加载器示例
演示如何直接使用文档加载器（简化版）。

**适合**: 需要自定义文档加载流程的开发者
**功能**:
- 加载目录下所有文档
- 只加载特定类型（如 PDF）
- 加载单个文件

```bash
python examples/document_loader_demo.py
```

---

## 🎓 推荐学习路径

### 新手路径
1. **build_index.py** - 构建索引（必须）
2. **quick_start.py** - 快速开始
3. **agent_demo.py** - 完整功能演示
4. **web_search_demo.py** - 联网搜索
5. **direct_llm_demo.py** - 直接对话模式

### 开发者路径
1. **build_index.py** - 构建索引
2. **document_loader_demo.py** - 了解文档加载
3. **agent_demo.py** - Agent 功能
4. **advanced_query.py** - 查询优化

---

## 📊 示例对比

| 示例文件 | 难度 | 功能完整度 | 适合场景 |
|---------|------|-----------|---------|
| quick_start.py | ⭐ | 基础 | 快速上手 |
| build_index.py | ⭐ | 工具 | 首次安装 |
| agent_demo.py | ⭐⭐ | 完整 | 全面学习 |
| web_search_demo.py | ⭐⭐ | 高级 | 联网增强 |
| direct_llm_demo.py | ⭐⭐ | 高级 | 开放对话 |
| advanced_query.py | ⭐⭐⭐ | 高级 | 性能调优 |
| document_loader_demo.py | ⭐⭐⭐ | 底层 | 自定义开发 |

---

## 🔍 功能索引

按功能查找示例：

### RAG 问答
- `quick_start.py` - 基础 RAG 查询
- `agent_demo.py` - 完整 RAG 功能
- `advanced_query.py` - 高级 RAG 选项

### 联网搜索
- `web_search_demo.py` - 联网搜索专项
- `direct_llm_demo.py` (示例 2) - LLM + 联网搜索

### LLM 对话
- `direct_llm_demo.py` - 直接 LLM 模式
- `agent_demo.py` (示例 5) - 交互式对话

### 文档管理
- `build_index.py` - 构建/重建索引
- `document_loader_demo.py` - 文档加载
- `agent_demo.py` (示例 1) - 列出论文

### 性能优化
- `advanced_query.py` - 查询参数调优
- `agent_demo.py` (示例 6) - 高级选项

---

## ⚙️ 运行前准备

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置 API Key
```

### 3. 准备文档
```bash
# 将 PDF、DOCX、Markdown 文档放入
mkdir -p data/documents
# 复制文档到 data/documents/
```

### 4. 构建索引
```bash
python examples/build_index.py
```

### 5. 运行示例
```bash
python examples/quick_start.py
```

---

## 💡 常见问题

### Q: 运行示例时提示"未找到索引"？
A: 请先运行 `python examples/build_index.py` 构建索引。

### Q: 联网搜索示例不工作？
A: 确保在 `.env` 文件中设置了 `ENABLE_WEB_SEARCH=true`。

### Q: 哪个示例最适合我？
A: 
- 新手 → `quick_start.py`
- 全面学习 → `agent_demo.py`
- 联网增强 → `web_search_demo.py`
- 开放对话 → `direct_llm_demo.py`

### Q: 如何自定义示例？
A: 所有示例代码都可以直接修改。建议复制一个示例文件，然后根据需求修改。

---

## 📚 更多资源

- **项目文档**: `README.md`
- **快速开始**: `QUICK_START.md`
- **开发指南**: `docs/DEVELOPER_GUIDE.md`
- **Agent 使用**: `docs/AGENT_USAGE.md`
- **配置指南**: `docs/CONFIG_GUIDE.md`

---

## 🎉 开始使用

最快的上手方式：

```bash
# 1. 构建索引
python examples/build_index.py

# 2. 快速开始
python examples/quick_start.py

# 3. 探索更多功能
python examples/agent_demo.py
```

祝你使用愉快！ 🚀
