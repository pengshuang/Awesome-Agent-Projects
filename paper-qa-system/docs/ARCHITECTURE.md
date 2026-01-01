# 架构设计文档

> 面向架构师和高级开发者，详细介绍系统的整体架构设计和技术选型

## 目录

- [系统架构概览](#系统架构概览)
- [技术栈选型](#技术栈选型)
- [核心模块设计](#核心模块设计)
- [数据流设计](#数据流设计)
- [扩展性设计](#扩展性设计)

---

## 系统架构概览

### 整体架构

本系统采用 **RAG (Retrieval-Augmented Generation)** 架构，结合向量检索和大语言模型，实现学术论文的智能问答。

```
┌─────────────────────────────────────────────────────────────┐
│                        用户交互层                             │
│                  (Gradio Web UI - 多轮对话)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                      Agent 层                                 │
│              (AcademicAgent - 对话管理)                       │
│  • 对话历史管理                                               │
│  • 查询路由                                                   │
│  • 上下文维护                                                 │
└─────────────┬──────────────────────┬────────────────────────┘
              │                      │
    ┌─────────▼─────────┐  ┌────────▼──────────┐
    │   RAG Pipeline    │  │   工具层           │
    │  (查询与检索)      │  │  (Web Search)     │
    │  • 向量检索        │  │                   │
    │  • 重排序          │  │                   │
    └─────────┬─────────┘  └───────────────────┘
              │
    ┌─────────▼─────────┐
    │  索引与存储层      │
    │  • VectorStore    │
    │  • Document Store │
    └─────────┬─────────┘
              │
    ┌─────────▼─────────┐
    │   文档加载层       │
    │  • PDF Loader     │
    │  • DOCX Loader    │
    │  • TXT Loader     │
    └───────────────────┘
```

### 架构特点

1. **分层设计**：清晰的分层架构，各层职责明确
2. **模块化**：高内聚、低耦合的模块设计
3. **可扩展**：易于添加新的文档格式、新的检索策略
4. **可配置**：基于 Pydantic 的配置管理，灵活且类型安全

---

## 技术栈选型

### 核心框架

| 技术 | 版本 | 用途 | 选型理由 |
|-----|------|------|---------|
| **LlamaIndex** | 最新 | RAG 框架 | • 成熟的 RAG 解决方案<br>• 丰富的集成生态<br>• 活跃的社区支持 |
| **Pydantic** | 2.0+ | 配置管理 | • 类型安全<br>• 自动验证<br>• 易于维护 |
| **Gradio** | 4.0+ | Web UI | • 快速搭建界面<br>• 交互友好<br>• 支持多轮对话 |

### 模型支持

| 类型 | 支持的提供商 | 说明 |
|-----|-------------|------|
| **LLM** | OpenAI, DeepSeek, Moonshot, Qwen 等 | 通过 OpenAI 兼容接口统一调用 |
| **Embedding** | HuggingFace, OpenAI, FastEmbed, DashScope | 支持本地和云端多种方案 |

### 向量存储

- **Chroma**: 默认向量数据库，轻量级、易部署

---

## 核心模块设计

### 1. Agent 层 (`src/agent.py`)

**职责**：对话管理、查询路由、上下文维护

**核心类**：`AcademicAgent`

```python
class AcademicAgent:
    """学术论文智能问答 Agent"""
    
    def __init__(
        self,
        documents_dir: str,
        index_dir: str,
        max_history_turns: int = 10
    ):
        self.chat_history = []  # 对话历史
        self.query_engine = None  # 查询引擎
        self.web_search_tool = None  # 网络搜索工具
```

**关键方法**：
- `build_index()`: 构建文档索引
- `chat()`: 多轮对话核心方法
- `query()`: 单次查询（无上下文）
- `clear_history()`: 清空对话历史

**设计亮点**：
1. **历史管理**：自动维护最近 N 轮对话，支持上下文理解
2. **查询路由**：根据问题特征决定是否启用网络搜索
3. **流式输出**：支持打字机效果，提升用户体验

### 2. RAG Pipeline (`src/query/`)

**职责**：文档检索、相似度计算、答案生成

**核心组件**：
- `qa_engine.py`: 问答引擎封装
- `rag_pipeline.py`: RAG 流程编排

**检索流程**：
```
问题 → Embedding → 向量检索 → 相似度过滤 → 重排序 → 上下文构建 → LLM 生成
```

### 3. 索引层 (`src/indexing/`)

**职责**：文档索引、向量存储

**核心类**：
- `Indexer`: 索引构建器
- `VectorStoreManager`: 向量存储管理

**索引策略**：
- **分块**: 固定大小分块（可配置 chunk_size 和 overlap）
- **向量化**: 使用 Embedding 模型将文本转为向量
- **存储**: 持久化到 Chroma 向量数据库

### 4. 文档加载层 (`src/loaders/`)

**职责**：支持多种文档格式的加载和解析

**支持格式**：
- PDF: PyMuPDF / PyPDF2
- DOCX: python-docx
- TXT/MD: 直接读取

**设计模式**：策略模式，每种格式对应一个 Reader

### 5. 配置层 (`config/`)

**职责**：集中管理系统配置

**核心文件**：
- `models.py`: Pydantic 配置模型
- `llm_config.py`: LLM 和 Embedding 配置
- `settings.py`: 全局设置

**配置来源**：
1. `.env` 文件（优先级最高）
2. 环境变量
3. 默认值

---

## 数据流设计

### 1. 索引构建流程

```
文档文件
  ↓
文档加载器 (DocumentLoader)
  ↓
文本清洗 & 分块 (TextCleaner + TextSplitter)
  ↓
向量化 (Embedding Model)
  ↓
向量存储 (VectorStore)
```

### 2. 查询流程

```
用户问题
  ↓
[可选] 添加对话历史上下文
  ↓
问题向量化 (Embedding)
  ↓
向量检索 (相似度搜索)
  ↓
文档召回 & 重排序
  ↓
上下文构建
  ↓
LLM 生成答案
  ↓
[可选] 流式输出
```

### 3. 多轮对话流程

```
第1轮: Q1 → A1
         ↓ (保存到历史)
第2轮: Q2 + [Q1, A1] → A2
         ↓ (保存到历史)
第3轮: Q3 + [Q1, A1, Q2, A2] → A3
```

---

## 扩展性设计

### 1. 新增 Embedding 提供商

在 `config/llm_config.py` 的 `get_embedding_model()` 中添加新的分支：

```python
elif provider == "new_provider":
    # 实现新的 Embedding 逻辑
    return NewEmbedding(...)
```

同时更新 `config/models.py` 中的 `Literal` 类型定义。

### 2. 新增文档格式支持

1. 在 `src/loaders/document_loader.py` 中创建新的 Reader 类
2. 在 `DocumentLoader._initialize_readers()` 中注册
3. 添加对应的文件扩展名映射

### 3. 新增工具（Tool）

在 `src/tools/` 目录下添加新工具，并在 Agent 中注册：

```python
from src.tools.new_tool import NewTool

class AcademicAgent:
    def __init__(self, ...):
        self.new_tool = NewTool()
```

### 4. 自定义 Prompt

修改 `config/prompts.py` 中的模板：

```python
CHAT_PROMPT = """
你是一个专业的...
[自定义你的 Prompt]
"""
```

---

## 性能优化建议

### 1. 索引优化

- **增量索引**: 只对新增文档建索引
- **批量处理**: 批量向量化减少 API 调用
- **缓存**: 缓存常见问题的结果

### 2. 检索优化

- **混合检索**: 结合关键词和向量检索
- **重排序**: 使用 reranker 模型提升召回精度
- **筛选**: 设置相似度阈值过滤低质量结果

### 3. 部署优化

- **Docker 化**: 容器化部署便于管理
- **GPU 加速**: 本地 Embedding 模型使用 GPU
- **负载均衡**: 多实例部署应对高并发

---

## 安全性考虑

1. **API Key 管理**: 使用环境变量，不提交到代码库
2. **输入验证**: Pydantic 自动验证所有配置
3. **错误处理**: 完善的异常捕获和日志记录
4. **访问控制**: 可集成身份认证（暂未实现）

---

## 未来规划

- [ ] 支持更多文档格式（PPT, Excel 等）
- [ ] 图表识别和理解
- [ ] 多语言支持
- [ ] 分布式部署方案
- [ ] 性能监控和分析

---

**最后更新**: 2026-01-01
