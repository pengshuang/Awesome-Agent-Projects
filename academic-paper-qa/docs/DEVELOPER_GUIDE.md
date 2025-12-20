# 👨‍💻 开发者指南

> 本文档面向需要进行二次开发、扩展功能或深入了解项目架构的开发者

## 目录
- [项目结构](#项目结构)
- [核心架构](#核心架构)
- [核心模块](#核心模块)
- [API 参考](#api-参考)
- [扩展开发](#扩展开发)
- [测试指南](#测试指南)
- [部署指南](#部署指南)
- [代码规范](#代码规范)

---

## 项目结构

### 📂 完整目录结构

```
academic-paper-qa/
├── 🚀 启动文件
│   ├── web_ui_multi_turn.py        # Web UI 多轮对话 ⭐
│   ├── web_ui_single_turn.py       # Web UI 单轮问答
│   ├── cli_multi_turn.py           # 命令行多轮对话 ⭐
│   ├── cli_single_turn.py          # 命令行单轮问答
│   └── init_system.py              # 系统初始化
│
├── 🛠️ 启动脚本
│   ├── start_web_multi.sh          # 启动 Web 多轮
│   ├── start_web_single.sh         # 启动 Web 单轮
│   ├── start_cli_multi.sh          # 启动命令行多轮
│   └── start_cli_single.sh         # 启动命令行单轮
│
├── 🔧 核心模块 (src/)
│   ├── agent.py                    # AcademicAgent 核心类
│   ├── constants.py                # 常量定义
│   │
│   ├── loaders/                    # 文档加载器
│   │   ├── __init__.py
│   │   └── document_loader.py      # 文档加载主类
│   │
│   ├── indexing/                   # 索引构建
│   │   ├── __init__.py
│   │   ├── indexer.py              # 索引构建器
│   │   └── vector_store.py         # 向量存储
│   │
│   ├── query/                      # 查询引擎
│   │   ├── __init__.py
│   │   ├── qa_engine.py            # 问答引擎
│   │   └── rag_pipeline.py         # RAG 流程
│   │
│   ├── tools/                      # 工具集
│   │   ├── __init__.py
│   │   └── web_search.py           # 网络搜索
│   │
│   └── utils/                      # 工具函数
│       ├── __init__.py
│       ├── logger.py               # 日志工具
│       └── helpers.py              # 辅助函数
│
├── ⚙️ 配置 (config/)
│   ├── __init__.py
│   ├── llm_config.py               # LLM 配置
│   └── settings.py                 # 全局设置
│
├── 📚 文档 (docs/)
│   ├── USER_GUIDE.md               # 用户使用指南
│   ├── FEATURES.md                 # 功能详细说明
│   └── DEVELOPER_GUIDE.md          # 开发者文档（本文件）
│
├── 📄 示例 (examples/)
│   ├── quick_start.py              # 快速入门
│   ├── advanced_query.py           # 高级查询
│   ├── agent_demo.py               # Agent 演示
│   └── README.md                   # 示例说明
│
├── 🧪 测试 (tests/)
│   ├── test_agent_core.py          # Agent 核心测试
│   ├── test_multi_turn_chat.py     # 多轮对话测试
│   ├── test_loader_documents.py    # 文档加载测试
│   ├── test_web_search.py          # Web 搜索测试
│   ├── test_ui_features.py         # UI 功能测试
│   └── README.md                   # 测试说明
│
├── 📦 数据 (data/)
│   ├── documents/                  # 文档存储（放置 PDF 等）
│   ├── vector_store/               # 向量索引
│   ├── cache/                      # 缓存文件
│   └── processed/                  # 处理后的文档
│
├── 📋 项目文档
│   ├── README.md                   # 项目主文档 ⭐
│   └── CODE_OPTIMIZATION_SUMMARY.md # 代码优化记录
│
└── ⚙️ 配置文件
    ├── .env                        # 环境变量（不提交）
    ├── .env.example                # 配置模板
    └── requirements.txt            # Python 依赖
```

### 📊 核心功能模块

| 功能模块 | 文件路径 | 说明 |
|---------|---------|------|
| **Agent 核心** | `src/agent.py` | AcademicAgent 主类，RAG 问答逻辑 |
| **文档加载** | `src/loaders/document_loader.py` | 支持 PDF、DOCX、MD、TXT |
| **索引构建** | `src/indexing/indexer.py` | 向量索引构建和管理 |
| **查询引擎** | `src/query/qa_engine.py` | 问答引擎，检索和生成 |
| **网络搜索** | `src/tools/web_search.py` | DuckDuckGo 搜索集成 |
| **多轮对话** | `src/agent.py` | 对话历史管理 |

---

## 核心架构

### 整体架构

```
┌─────────────────────────────────────────────────────┐
│                    User Layer                        │
│  ┌──────────────┐              ┌──────────────┐    │
│  │   Web UI     │              │   CLI        │    │
│  │  (Gradio)    │              │   (Typer)    │    │
│  └──────────────┘              └──────────────┘    │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                 Application Layer                    │
│  ┌──────────────────────────────────────────────┐  │
│  │              Agent (main.py)                  │  │
│  │  • Query Processing                          │  │
│  │  • Context Management                        │  │
│  │  • Response Generation                       │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌─────────────┐ ┌────────────┐
│   Document   │ │   Retrieval │ │    LLM     │
│   Loader     │ │   Engine    │ │  Service   │
│              │ │             │ │            │
│ • PDF        │ │ • Vector    │ │ • OpenAI   │
│ • DOCX       │ │   Store     │ │ • Moonshot │
│ • Markdown   │ │ • Semantic  │ │ • DeepSeek │
│ • TXT        │ │   Search    │ │            │
└──────────────┘ └─────────────┘ └────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│                  Storage Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │   Chroma     │  │   Config     │  │   Logs   │ │
│  │ Vector Store │  │    (.env)    │  │          │ │
│  └──────────────┘  └──────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## 核心模块

### 1. AcademicAgent - 核心 Agent 类

**位置**: `src/agent.py`

**职责**:
- 向量索引管理（构建、加载、持久化）
- RAG 问答（检索增强生成）
- 直接 LLM 对话（支持文档附件）
- 多轮对话历史管理
- 文档统计和管理

#### 核心方法

##### 1.1 索引管理

```python
from src.agent import AcademicAgent

# 创建 Agent 实例（自动加载索引）
agent = AcademicAgent()

# 创建 Agent 但不自动加载索引
agent = AcademicAgent(auto_load=False)

# 手动构建或加载索引
agent.load_or_build_index(force_rebuild=False)

# 强制重建索引
agent.rebuild_index()

# 检查索引是否存在
if agent._index_exists():
    print("索引已存在")
```

**方法详解**:

```python
def load_or_build_index(self, force_rebuild: bool = False) -> VectorStoreIndex:
    """
    加载或构建向量索引
    
    Args:
        force_rebuild: 是否强制重建索引
        
    Returns:
        VectorStoreIndex: 向量索引实例
        
    流程:
        1. 如果 force_rebuild=True，直接重建
        2. 否则检查索引是否存在
        3. 存在则加载，不存在则构建
    """
```

##### 1.2 RAG 问答

```python
# 基础 RAG 查询
result = agent.query(
    question="Transformer 的核心创新是什么？",
    mode="rag"
)

# 高级 RAG 查询（启用网络搜索）
result = agent.query(
    question="最新的大语言模型有哪些？",
    mode="rag",
    enable_web_search=True,
    top_k=5,
    similarity_threshold=0.7
)

# 处理结果
print(f"答案: {result['answer']}")
print(f"检索到的文档: {len(result.get('source_nodes', []))}")

# 查看来源文档
for i, node in enumerate(result.get('source_nodes', []), 1):
    print(f"\n来源 {i}:")
    print(f"  文件: {node.node.metadata.get('file_name')}")
    print(f"  相似度: {node.score:.2f}")
    print(f"  内容片段: {node.node.text[:100]}...")

# 查看网络搜索结果（如果启用）
if result.get('web_sources'):
    print("\n网络搜索结果:")
    for source in result['web_sources']:
        print(f"  - {source['title']}: {source['url']}")
```

**方法详解**:

```python
def query(
    self,
    question: str,
    mode: str = "rag",
    enable_web_search: bool = False,
    top_k: int = 5,
    similarity_threshold: float = 0.7,
    response_mode: str = "compact"
) -> Dict[str, Any]:
    """
    执行查询
    
    Args:
        question: 用户问题
        mode: 查询模式 ('rag' 或 'llm')
        enable_web_search: 是否启用网络搜索
        top_k: 检索文档数量
        similarity_threshold: 相似度阈值
        response_mode: 响应模式 (compact/tree_summarize/refine)
        
    Returns:
        {
            'answer': str,              # 生成的答案
            'source_nodes': List,       # 检索到的文档节点
            'web_sources': List[Dict],  # 网络搜索结果（如果启用）
            'query_time': float         # 查询耗时
        }
    """
```

##### 1.3 直接 LLM 对话（支持文档附件）

```python
# 基础 LLM 对话
result = agent.query_direct(
    question="解释一下机器学习的基本概念"
)

# 带文档附件的对话（Moonshot API）
result = agent.query_direct(
    question="请总结这篇论文的主要内容",
    document_paths=[
        "data/documents/paper1.pdf",
        "data/documents/paper2.pdf"
    ]
)

# 带网络搜索的对话
result = agent.query_direct(
    question="2024年AI领域有哪些重大突破？",
    enable_web_search=True
)

# 组合使用：文档附件 + 网络搜索
result = agent.query_direct(
    question="对比这篇论文和最新的研究进展",
    document_paths=["data/documents/paper.pdf"],
    enable_web_search=True
)

# 处理结果
print(f"答案: {result['answer']}")
print(f"使用的文档: {result.get('attached_documents', [])}")
print(f"网络来源: {len(result.get('web_sources', []))}")
```

**方法详解**:

```python
def query_direct(
    self,
    question: str,
    document_paths: Optional[List[str]] = None,
    enable_web_search: bool = False,
    temperature: float = 0.1
) -> Dict[str, Any]:
    """
    直接调用 LLM（不使用 RAG）
    
    Args:
        question: 用户问题
        document_paths: 文档路径列表（Moonshot 支持文件上传）
        enable_web_search: 是否启用网络搜索
        temperature: LLM 温度参数
        
    Returns:
        {
            'answer': str,
            'attached_documents': List[str],  # 使用的文档列表
            'web_sources': List[Dict],        # 网络搜索结果
            'mode': 'direct'
        }
        
    注意:
        - 文档上传功能需要 Moonshot API
        - 支持 PDF、DOCX、MD、TXT 格式
        - 文件会被缓存，避免重复上传
    """
```

##### 1.4 多轮对话管理

```python
# 多轮对话示例
agent = AcademicAgent()

# 第一轮对话
result1 = agent.query_direct("什么是 Transformer？")
print(result1['answer'])

# 第二轮（自动记忆上下文）
result2 = agent.query_direct("它有哪些应用？")  # "它"会自动理解为 Transformer
print(result2['answer'])

# 第三轮（继续深入）
result3 = agent.query_direct("在 NLP 领域的具体应用有哪些？")
print(result3['answer'])

# 查看对话历史
history = agent.get_chat_history()
for i, msg in enumerate(history, 1):
    print(f"\n[{i}] {msg['role']}: {msg['content'][:50]}...")

# 清空对话历史
agent.clear_chat_history()

# 设置历史保留轮数（默认10轮）
agent.set_max_history_turns(20)

# 构建上下文 Prompt（内部使用）
context_prompt = agent._build_context_prompt("当前问题")
```

**对话历史管理方法**:

```python
def _update_chat_history(self, user_message: str, assistant_message: str):
    """更新对话历史，自动管理历史长度"""
    
def clear_chat_history(self):
    """清空对话历史"""
    
def get_chat_history(self) -> List[Dict[str, str]]:
    """获取对话历史"""
    
def set_max_history_turns(self, max_turns: int):
    """设置最大保留历史轮数"""
    
def _build_context_prompt(self, question: str) -> str:
    """
    构建包含历史上下文的 Prompt
    
    格式:
        历史对话:
        用户: 问题1
        助手: 回答1
        用户: 问题2
        助手: 回答2
        
        当前问题: {question}
    """
```

##### 1.5 文档和统计管理

```python
# 列出所有可用文档
documents = agent.list_available_documents()
print(f"找到 {len(documents)} 个文档:")
for doc in documents:
    print(f"  - {doc}")

# 列出已索引的论文（简略）
papers = agent.list_papers(detailed=False)
for paper in papers:
    print(f"{paper['file_name']}: {paper['char_count']} 字符")

# 列出已索引的论文（详细）
papers = agent.list_papers(detailed=True)
for paper in papers:
    print(f"\n文件: {paper['file_name']}")
    print(f"  格式: {paper['format']}")
    print(f"  大小: {paper['size_mb']:.2f} MB")
    print(f"  字符数: {paper['char_count']}")
    print(f"  预览: {paper['preview']}")

# 获取系统统计信息
stats = agent.get_statistics()
print(f"文档总数: {stats['total_documents']}")
print(f"总字符数: {stats['total_chars']:,}")
print(f"总大小: {stats['total_size_mb']:.2f} MB")
print(f"索引状态: {stats['index_built']}")

# 清空文件上传缓存
agent.clear_file_cache()
```

#### 完整使用示例

```python
from src.agent import AcademicAgent
from pathlib import Path

def main():
    """完整的 Agent 使用示例"""
    
    # 1. 初始化 Agent
    print("=" * 70)
    print("初始化 Academic Agent")
    print("=" * 70)
    
    agent = AcademicAgent(
        documents_dir="./data/documents",
        index_dir="./data/vector_store",
        auto_load=True  # 自动加载或构建索引
    )
    
    # 2. 查看统计信息
    stats = agent.get_statistics()
    print(f"\n文档统计:")
    print(f"  总文档数: {stats['total_documents']}")
    print(f"  总字符数: {stats['total_chars']:,}")
    print(f"  索引状态: {'已构建' if stats['index_built'] else '未构建'}")
    
    # 3. RAG 问答示例
    print("\n" + "=" * 70)
    print("RAG 问答示例")
    print("=" * 70)
    
    result = agent.query(
        question="什么是注意力机制？",
        mode="rag",
        top_k=3
    )
    
    print(f"\n问题: 什么是注意力机制？")
    print(f"\n答案:\n{result['answer']}")
    print(f"\n来源文档: {len(result.get('source_nodes', []))} 个")
    
    # 4. 带网络搜索的 RAG
    print("\n" + "=" * 70)
    print("RAG + 网络搜索示例")
    print("=" * 70)
    
    result = agent.query(
        question="2024年大语言模型的最新进展",
        mode="rag",
        enable_web_search=True,
        top_k=3
    )
    
    print(f"\n问题: 2024年大语言模型的最新进展")
    print(f"\n答案:\n{result['answer']}")
    if result.get('web_sources'):
        print(f"\n网络来源: {len(result['web_sources'])} 个")
    
    # 5. 直接 LLM 对话
    print("\n" + "=" * 70)
    print("直接 LLM 对话示例")
    print("=" * 70)
    
    result = agent.query_direct(
        question="解释一下深度学习的基本原理"
    )
    
    print(f"\n问题: 解释一下深度学习的基本原理")
    print(f"\n答案:\n{result['answer']}")
    
    # 6. 多轮对话示例
    print("\n" + "=" * 70)
    print("多轮对话示例")
    print("=" * 70)
    
    # 第一轮
    result1 = agent.query_direct("什么是卷积神经网络？")
    print(f"\n[用户] 什么是卷积神经网络？")
    print(f"[助手] {result1['answer'][:200]}...")
    
    # 第二轮（有上下文记忆）
    result2 = agent.query_direct("它主要用在哪些领域？")
    print(f"\n[用户] 它主要用在哪些领域？")
    print(f"[助手] {result2['answer'][:200]}...")
    
    # 查看历史
    history = agent.get_chat_history()
    print(f"\n对话历史: {len(history)} 条消息")
    
    # 7. 文档附件示例（Moonshot API）
    print("\n" + "=" * 70)
    print("文档附件示例")
    print("=" * 70)
    
    # 检查是否有文档
    docs = agent.list_available_documents()
    if docs:
        result = agent.query_direct(
            question="请总结这篇文档的主要内容",
            document_paths=[docs[0]]  # 使用第一个文档
        )
        print(f"\n问题: 请总结这篇文档的主要内容")
        print(f"使用文档: {docs[0]}")
        print(f"\n答案:\n{result['answer'][:300]}...")
    else:
        print("\n没有可用文档，跳过文档附件示例")
    
    print("\n" + "=" * 70)
    print("示例完成")
    print("=" * 70)

if __name__ == "__main__":
    main()
```

---

### 2. DocumentLoader - 文档加载器

**位置**: `src/loaders/document_loader.py`

**职责**:
- 加载多种格式文档（PDF、DOCX、MD、TXT）
- 文本清洗和规范化
- 元数据提取
- 统计信息计算

#### 核心方法

```python
from src.loaders.document_loader import DocumentLoader

# 基础使用
loader = DocumentLoader(input_dir="./data/documents")
documents = loader.load_documents()

# 高级配置
loader = DocumentLoader(
    input_dir="./data/documents",
    recursive=True,           # 递归扫描子目录
    clean_text=True,          # 清洗文本
    preserve_formatting=False # 不保留格式
)
documents = loader.load_documents()

# 获取统计信息
stats = loader.get_statistics()
print(f"总文档数: {stats['total_documents']}")
print(f"总文件数: {stats['total_files']}")
print(f"文件类型: {stats['file_types']}")
print(f"总大小: {stats['total_size_mb']:.2f} MB")
print(f"总字符数: {stats['total_chars']:,}")
```

#### 支持的文档格式

```python
# PDF 文件
# - 优先使用 PyMuPDF（更快更准确）
# - 备选 pypdf
documents_pdf = loader._load_pdf("path/to/paper.pdf")

# DOCX 文件
documents_docx = loader._load_docx("path/to/document.docx")

# Markdown 文件
documents_md = loader._load_markdown("path/to/readme.md")

# 文本文件
documents_txt = loader._load_text("path/to/notes.txt")
```

#### 文本清洗功能

```python
# 清洗文本（去除控制字符、规范空白）
cleaned_text = loader._clean_text(raw_text)

# 清洗步骤:
# 1. 移除控制字符
# 2. 规范多余的换行符
# 3. 规范空格
# 4. 修正中文标点后的空格
# 5. 修正英文标点后的多余空格
```

#### 完整使用示例

```python
from src.loaders.document_loader import DocumentLoader
from pathlib import Path

def load_and_analyze_documents():
    """加载并分析文档"""
    
    # 1. 创建加载器
    loader = DocumentLoader(
        input_dir="./data/documents",
        recursive=True,
        clean_text=True
    )
    
    # 2. 加载文档
    print("正在加载文档...")
    documents = loader.load_documents()
    
    # 3. 查看统计
    stats = loader.get_statistics()
    print(f"\n文档统计:")
    print(f"  总文档块数: {stats['total_documents']}")
    print(f"  总文件数: {stats['total_files']}")
    print(f"  文件类型分布: {stats['file_types']}")
    print(f"  总大小: {stats['total_size_mb']:.2f} MB")
    print(f"  总字符数: {stats['total_chars']:,}")
    print(f"  总单词数: {stats['total_words']:,}")
    
    # 4. 查看文档详情
    print(f"\n文档详情:")
    for i, doc in enumerate(documents[:3], 1):  # 只显示前3个
        print(f"\n文档 {i}:")
        print(f"  文件名: {doc.metadata.get('file_name')}")
        print(f"  格式: {doc.metadata.get('format')}")
        print(f"  大小: {doc.metadata.get('file_size_mb', 0):.2f} MB")
        print(f"  字符数: {doc.metadata.get('char_count')}")
        print(f"  预览: {doc.text[:100]}...")
    
    return documents

if __name__ == "__main__":
    documents = load_and_analyze_documents()
```

---

### 3. WebSearchTool - 网络搜索工具

**位置**: `src/tools/web_search.py`

**职责**:
- DuckDuckGo 网络搜索
- 多搜索引擎支持（DuckDuckGo、SearXNG、SerpAPI）
- 自动故障转移
- 结果格式化

#### 核心方法

```python
from src.tools.web_search import WebSearchTool

# 基础搜索
tool = WebSearchTool(max_results=5)
results = tool.search("机器学习最新进展")

# 使用特定搜索引擎
tool = WebSearchTool(
    max_results=5,
    engine="duckduckgo"  # 或 "searxng", "serpapi"
)
results = tool.search("深度学习")

# 处理结果
for i, result in enumerate(results, 1):
    print(f"\n{i}. {result['title']}")
    print(f"   URL: {result['url']}")
    print(f"   摘要: {result['snippet'][:100]}...")
```

#### 多引擎支持

```python
# DuckDuckGo（默认，免费）
tool = WebSearchTool(engine="duckduckgo")

# SearXNG（需要自建实例）
tool = WebSearchTool(
    engine="searxng",
    searxng_base_url="http://localhost:8888"
)

# SerpAPI（需要 API Key）
tool = WebSearchTool(
    engine="serpapi",
    serpapi_api_key="your-api-key"
)
```

#### 完整使用示例

```python
from src.tools.web_search import WebSearchTool
import os

def search_with_fallback(query: str):
    """带故障转移的搜索"""
    
    # 尝试多个引擎
    engines = ["duckduckgo", "searxng"]
    
    for engine in engines:
        try:
            print(f"\n尝试使用 {engine}...")
            tool = WebSearchTool(max_results=3, engine=engine)
            results = tool.search(query)
            
            if results:
                print(f"✓ 使用 {engine} 找到 {len(results)} 个结果")
                return results
        except Exception as e:
            print(f"✗ {engine} 失败: {e}")
            continue
    
    print("所有搜索引擎都失败了")
    return []

# 使用
results = search_with_fallback("2024年AI领域突破")
for result in results:
    print(f"- {result['title']}: {result['url']}")
```

---

### 4. 配置模块

#### 4.1 SystemConfig - 系统配置

**位置**: `config/settings.py`

```python
from config import SystemConfig

# 访问配置
print(f"文档目录: {SystemConfig.DOCUMENTS_DIR}")
print(f"向量库目录: {SystemConfig.VECTOR_STORE_DIR}")
print(f"Chunk 大小: {SystemConfig.CHUNK_SIZE}")
print(f"Chunk 重叠: {SystemConfig.CHUNK_OVERLAP}")
print(f"检索 Top-K: {SystemConfig.RETRIEVAL_TOP_K}")

# 确保目录存在
SystemConfig.ensure_directories()
```

#### 4.2 LLM 配置

**位置**: `config/llm_config.py`

```python
from config.llm_config import get_llm, get_embedding_model

# 获取 LLM 实例
llm = get_llm()

# 获取 Embedding 模型
embed_model = get_embedding_model(provider="huggingface")

# 自定义配置
llm = get_llm(
    api_key="your-api-key",
    api_base="https://api.moonshot.cn/v1",
    model="moonshot-v1-8k"
)
```

---

## API 参考

### create_agent() - 快速创建 Agent

```python
from src.agent import create_agent

def create_agent(
    documents_dir: str = "./data/documents",
    index_dir: str = "./data/vector_store",
    force_rebuild: bool = False,
    auto_load: bool = True
) -> AcademicAgent:
    """
    快速创建 Academic Agent 实例
    
    Args:
        documents_dir: 文档目录路径
        index_dir: 索引存储目录
        force_rebuild: 是否强制重建索引
        auto_load: 是否自动加载索引
        
    Returns:
        AcademicAgent 实例
        
    示例:
        # 默认配置
        agent = create_agent()
        
        # 自定义目录
        agent = create_agent(
            documents_dir="./my_papers",
            force_rebuild=True
        )
    """
```

### AcademicAgent 类完整 API

```python
class AcademicAgent:
    """学术论文问答 Agent"""
    
    # 初始化
    def __init__(
        documents_dir: Optional[str] = None,
        index_dir: Optional[str] = None,
        auto_load: bool = True
    )
    
    # 索引管理
    def load_or_build_index(force_rebuild: bool = False) -> VectorStoreIndex
    def rebuild_index() -> VectorStoreIndex
    def _index_exists() -> bool
    
    # 查询方法
    def query(
        question: str,
        mode: str = "rag",
        enable_web_search: bool = False,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        response_mode: str = "compact"
    ) -> Dict[str, Any]
    
    def query_direct(
        question: str,
        document_paths: Optional[List[str]] = None,
        enable_web_search: bool = False,
        temperature: float = 0.1
    ) -> Dict[str, Any]
    
    # 对话历史
    def get_chat_history() -> List[Dict[str, str]]
    def clear_chat_history()
    def set_max_history_turns(max_turns: int)
    
    # 文档管理
    def list_papers(detailed: bool = False) -> List[Dict[str, Any]]
    def list_available_documents() -> List[str]
    def get_statistics() -> Dict[str, Any]
    
    # 缓存管理
    def clear_file_cache()
```

### DocumentLoader 类完整 API

```python
class DocumentLoader:
    """文档加载器"""
    
    def __init__(
        input_dir: str,
        recursive: bool = True,
        clean_text: bool = True,
        preserve_formatting: bool = False
    )
    
    def load_documents() -> List[Document]
    def get_statistics() -> Dict[str, Any]
    def _clean_text(text: str) -> str
```

### WebSearchTool 类完整 API

```python
class WebSearchTool:
    """网络搜索工具"""
    
    def __init__(
        max_results: int = 3,
        engine: str = "duckduckgo"
    )
    
    def search(query: str) -> List[Dict[str, str]]
```

---

## 扩展开发

### 1. 添加新的文档格式支持

#### 步骤 1: 创建自定义加载器

```python
# custom_loaders/epub_loader.py
from pathlib import Path
from typing import List
from llama_index.core import Document

class EPUBLoader:
    """EPUB 文档加载器示例"""
    
    def load(self, file_path: str) -> List[Document]:
        """加载 EPUB 文件"""
        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError("请安装: pip install ebooklib beautifulsoup4")
        
        # 读取 EPUB 文件
        book = epub.read_epub(file_path)
        
        # 提取文本内容
        texts = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text = soup.get_text()
                texts.append(text)
        
        # 合并文本
        full_text = '\n\n'.join(texts)
        
        # 创建 Document 对象
        doc = Document(
            text=full_text,
            metadata={
                'file_name': Path(file_path).name,
                'file_path': file_path,
                'format': 'epub',
                'title': book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else 'Unknown'
            }
        )
        
        return [doc]
```

#### 步骤 2: 集成到 DocumentLoader

```python
# 修改 src/loaders/document_loader.py
from custom_loaders.epub_loader import EPUBLoader

class DocumentLoader:
    def __init__(self, ...):
        # 添加 EPUB 支持
        self.supported_extensions.update({
            'epub': ['.epub']
        })
        self.epub_loader = EPUBLoader()
    
    def _load_single_file(self, file_path: str) -> List[Document]:
        # 添加 EPUB 处理
        if file_path.endswith('.epub'):
            return self.epub_loader.load(file_path)
        # ... 其他格式
```

### 2. 添加新的 LLM 提供商

#### 示例：集成 DeepSeek API

```python
# custom_llm/deepseek_llm.py
from typing import Optional, List, Dict, Any
from llama_index.core.llms import LLM, CompletionResponse
from llama_index.core.base.llms.types import ChatMessage
import requests

class DeepSeekLLM(LLM):
    """DeepSeek LLM 实现"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        api_base: str = "https://api.deepseek.com/v1",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.model = model
        self.api_base = api_base
    
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        """文本补全"""
        response = requests.post(
            f"{self.api_base}/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "prompt": prompt,
                **kwargs
            }
        )
        result = response.json()
        return CompletionResponse(text=result['choices'][0]['text'])
    
    def chat(self, messages: List[ChatMessage], **kwargs) -> CompletionResponse:
        """多轮对话"""
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                **kwargs
            }
        )
        result = response.json()
        return CompletionResponse(text=result['choices'][0]['message']['content'])
    
    @property
    def metadata(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "provider": "deepseek"
        }
```

#### 集成到配置

```python
# config/llm_config.py
def get_llm(provider: Optional[str] = None, **kwargs):
    """获取 LLM 实例"""
    provider = provider or os.getenv("LLM_PROVIDER", "openai")
    
    if provider == "deepseek":
        from custom_llm.deepseek_llm import DeepSeekLLM
        return DeepSeekLLM(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        )
    elif provider == "openai":
        # ... 现有代码
        pass
```

### 3. 自定义检索策略

#### 实现混合检索（关键词 + 语义）

```python
# custom_retrieval/hybrid_retriever.py
from typing import List
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import NodeWithScore
from rank_bm25 import BM25Okapi
import numpy as np

class HybridRetriever:
    """混合检索器：BM25 + 向量检索"""
    
    def __init__(
        self,
        index: VectorStoreIndex,
        bm25_weight: float = 0.3,
        vector_weight: float = 0.7
    ):
        self.index = index
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight
        
        # 构建 BM25 索引
        self._build_bm25_index()
    
    def _build_bm25_index(self):
        """构建 BM25 索引"""
        # 获取所有文档
        all_nodes = list(self.index.docstore.docs.values())
        
        # 分词（简单按空格分词，实际应使用分词器）
        corpus = [node.text.split() for node in all_nodes]
        
        # 创建 BM25 索引
        self.bm25 = BM25Okapi(corpus)
        self.nodes = all_nodes
    
    def retrieve(self, query: str, top_k: int = 5) -> List[NodeWithScore]:
        """混合检索"""
        # 1. BM25 检索
        query_tokens = query.split()
        bm25_scores = self.bm25.get_scores(query_tokens)
        
        # 2. 向量检索
        retriever = self.index.as_retriever(similarity_top_k=top_k * 2)
        vector_results = retriever.retrieve(query)
        
        # 3. 融合分数
        # 创建节点ID到分数的映射
        bm25_score_dict = {
            node.node_id: score 
            for node, score in zip(self.nodes, bm25_scores)
        }
        
        vector_score_dict = {
            result.node.node_id: result.score 
            for result in vector_results
        }
        
        # 合并分数（RRF - Reciprocal Rank Fusion）
        all_node_ids = set(bm25_score_dict.keys()) | set(vector_score_dict.keys())
        
        fused_scores = {}
        for node_id in all_node_ids:
            bm25_score = bm25_score_dict.get(node_id, 0)
            vector_score = vector_score_dict.get(node_id, 0)
            
            # 归一化并加权
            fused_scores[node_id] = (
                self.bm25_weight * bm25_score + 
                self.vector_weight * vector_score
            )
        
        # 4. 排序并返回 Top-K
        sorted_node_ids = sorted(
            fused_scores.keys(), 
            key=lambda x: fused_scores[x], 
            reverse=True
        )[:top_k]
        
        # 构建结果
        results = []
        for node_id in sorted_node_ids:
            node = next(n for n in self.nodes if n.node_id == node_id)
            results.append(NodeWithScore(
                node=node,
                score=fused_scores[node_id]
            ))
        
        return results
```

#### 使用混合检索

```python
from src.agent import AcademicAgent
from custom_retrieval.hybrid_retriever import HybridRetriever

# 创建 Agent
agent = AcademicAgent()

# 创建混合检索器
hybrid_retriever = HybridRetriever(
    index=agent.index,
    bm25_weight=0.3,
    vector_weight=0.7
)

# 使用混合检索
query = "Transformer 注意力机制"
results = hybrid_retriever.retrieve(query, top_k=5)

for i, result in enumerate(results, 1):
    print(f"\n{i}. 分数: {result.score:.4f}")
    print(f"   内容: {result.node.text[:100]}...")
```

### 4. 自定义 Prompt 模板

#### 创建 Prompt 管理器

```python
# custom_prompts/prompt_manager.py
from typing import Dict
import yaml

class PromptManager:
    """Prompt 模板管理器"""
    
    def __init__(self, config_file: str = "prompts.yaml"):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.prompts = yaml.safe_load(f)
    
    def get_prompt(self, name: str, **kwargs) -> str:
        """获取并格式化 Prompt"""
        template = self.prompts.get(name)
        if not template:
            raise ValueError(f"Prompt '{name}' not found")
        return template.format(**kwargs)
    
    def register_prompt(self, name: str, template: str):
        """注册新的 Prompt"""
        self.prompts[name] = template
```

#### Prompt 配置文件

```yaml
# prompts.yaml
rag_qa:
  system: |
    你是一个专业的学术论文分析助手。
    请基于提供的文档内容回答问题，确保答案准确、客观。
  
  user: |
    文档内容:
    {context}
    
    问题: {question}
    
    请提供详细的答案，并引用具体的段落。

analysis:
  system: |
    你是一个深度学术论文分析专家。
  
  user: |
    请深入分析以下论文:
    {paper_content}
    
    分析维度:
    1. 研究问题和动机
    2. 技术方法和创新点
    3. 实验设计和结果
    4. 结论和未来工作
    5. 优势和局限性

comparison:
  system: |
    你是一个论文对比分析专家。
  
  user: |
    论文 A:
    {paper_a}
    
    论文 B:
    {paper_b}
    
    请对比这两篇论文的:
    1. 研究方法差异
    2. 技术创新点
    3. 实验结果对比
    4. 各自优劣势
```

#### 使用自定义 Prompt

```python
from custom_prompts.prompt_manager import PromptManager

# 加载 Prompt 管理器
pm = PromptManager("prompts.yaml")

# 使用预定义 Prompt
rag_prompt = pm.get_prompt(
    "rag_qa",
    context="文档内容...",
    question="什么是注意力机制？"
)

# 注册新 Prompt
pm.register_prompt(
    "summary",
    "请总结以下内容:\n{content}\n\n要求:\n1. 简洁明了\n2. 保留关键信息"
)

# 使用新 Prompt
summary_prompt = pm.get_prompt("summary", content="要总结的内容...")
```

### 5. 添加后处理器

#### 答案质量评估器

```python
# custom_postprocessors/quality_evaluator.py
from typing import Dict, List
from llama_index.core.llms import LLM

class AnswerQualityEvaluator:
    """答案质量评估器"""
    
    def __init__(self, llm: LLM):
        self.llm = llm
    
    def evaluate(
        self,
        question: str,
        answer: str,
        sources: List[Dict]
    ) -> Dict[str, float]:
        """评估答案质量"""
        
        # 1. 相关性评分 (0-1)
        relevance = self._evaluate_relevance(question, answer)
        
        # 2. 完整性评分 (0-1)
        completeness = self._evaluate_completeness(answer, sources)
        
        # 3. 准确性评分 (0-1)
        accuracy = self._evaluate_accuracy(answer, sources)
        
        # 4. 清晰度评分 (0-1)
        clarity = self._evaluate_clarity(answer)
        
        # 总体评分
        overall = (relevance + completeness + accuracy + clarity) / 4
        
        return {
            'relevance': relevance,
            'completeness': completeness,
            'accuracy': accuracy,
            'clarity': clarity,
            'overall': overall
        }
    
    def _evaluate_relevance(self, question: str, answer: str) -> float:
        """评估相关性"""
        prompt = f"""
        问题: {question}
        答案: {answer}
        
        请评估答案与问题的相关性(0-1之间的分数):
        - 1.0: 完全相关，直接回答了问题
        - 0.5: 部分相关，回答了部分问题
        - 0.0: 完全不相关
        
        只返回分数，不要解释。
        """
        
        try:
            response = self.llm.complete(prompt)
            score = float(response.text.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.5  # 默认分数
    
    def _evaluate_completeness(self, answer: str, sources: List[Dict]) -> float:
        """评估完整性"""
        # 简单实现：检查答案长度和来源覆盖度
        answer_length = len(answer)
        sources_used = len(sources)
        
        length_score = min(answer_length / 500, 1.0)  # 500字符为满分
        sources_score = min(sources_used / 3, 1.0)     # 使用3个来源为满分
        
        return (length_score + sources_score) / 2
    
    def _evaluate_accuracy(self, answer: str, sources: List[Dict]) -> float:
        """评估准确性（通过来源一致性）"""
        if not sources:
            return 0.5
        
        # 检查答案中是否引用了来源内容
        matches = 0
        for source in sources:
            source_text = source.get('text', '')
            # 简单的文本匹配
            if any(chunk in answer for chunk in source_text.split()[:10]):
                matches += 1
        
        return matches / len(sources) if sources else 0.5
    
    def _evaluate_clarity(self, answer: str) -> float:
        """评估清晰度"""
        # 简单指标：句子数量、平均句子长度
        sentences = answer.split('。')
        num_sentences = len([s for s in sentences if s.strip()])
        
        if num_sentences == 0:
            return 0.0
        
        avg_length = len(answer) / num_sentences
        
        # 理想句子长度：20-50字
        if 20 <= avg_length <= 50:
            return 1.0
        elif avg_length < 20:
            return 0.7  # 太短
        else:
            return max(0.3, 1.0 - (avg_length - 50) / 100)  # 太长
```

#### 使用质量评估器

```python
from src.agent import AcademicAgent
from custom_postprocessors.quality_evaluator import AnswerQualityEvaluator
from config.llm_config import get_llm

# 创建 Agent
agent = AcademicAgent()

# 创建评估器
llm = get_llm()
evaluator = AnswerQualityEvaluator(llm)

# 执行查询
result = agent.query("什么是深度学习？")

# 评估答案质量
quality = evaluator.evaluate(
    question="什么是深度学习？",
    answer=result['answer'],
    sources=result.get('source_nodes', [])
)

print(f"答案质量评估:")
print(f"  相关性: {quality['relevance']:.2f}")
print(f"  完整性: {quality['completeness']:.2f}")
print(f"  准确性: {quality['accuracy']:.2f}")
print(f"  清晰度: {quality['clarity']:.2f}")
print(f"  总体评分: {quality['overall']:.2f}")
```

---
        self,
        input_dir: str,
        recursive: bool = True,
        clean_text: bool = True,
        preserve_formatting: bool = False,
        supported_formats: List[str] = None
    ):
        """
        参数:
            input_dir: 文档目录
            recursive: 是否递归扫描子目录
            clean_text: 是否清理文本
            preserve_formatting: 是否保留格式
            supported_formats: 支持的文件格式列表
        """
        pass
    
    def load_documents(self) -> List[Document]:
        """加载所有文档"""
        pass
    
    def _load_single_file(self, file_path: str) -> List[Document]:
        """加载单个文件"""
        pass
```

**使用示例：**

```python
from src.loaders import DocumentLoader

# 基础使用
loader = DocumentLoader(input_dir="./data/documents")
documents = loader.load_documents()

# 高级配置
loader = DocumentLoader(
    input_dir="./data/documents",
    recursive=True,
    clean_text=True,
    preserve_formatting=False,
    supported_formats=[".pdf", ".docx", ".md"]
)
documents = loader.load_documents()

# 统计信息
print(f"加载了 {len(documents)} 个文档块")
for doc in documents:
    print(f"文件: {doc.metadata['file_name']}, 长度: {len(doc.text)}")
```

**扩展开发：添加新的文档格式**

```python
from src.loaders.base import BaseLoader
from typing import List
from llama_index.core import Document

class CustomLoader(BaseLoader):
    """自定义加载器示例"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.supported_extensions = [".custom"]
    
    def load(self, file_path: str) -> List[Document]:
        """加载自定义格式文件"""
        # 实现你的加载逻辑
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 创建文档对象
        doc = Document(
            text=content,
            metadata={
                'file_name': os.path.basename(file_path),
                'file_path': file_path,
                'format': 'custom'
            }
        )
        return [doc]
```

### 2. Vector Store（向量存储）

**位置**：`src/retrieval/vector_store.py`

**职责**：
- 文档向量化
- 向量索引构建
- 语义检索
- 索引持久化

**核心类：**

```python
class VectorStore:
    """向量存储管理器"""
    
    def __init__(
        self,
        persist_dir: str,
        embedding_model: str = "BAAI/bge-small-zh-v1.5",
        collection_name: str = "documents"
    ):
        """
        参数:
            persist_dir: 持久化目录
            embedding_model: Embedding 模型名称
            collection_name: 集合名称
        """
        pass
    
    def build_index(
        self,
        documents: List[Document],
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ) -> VectorStoreIndex:
        """构建向量索引"""
        pass
    
    def query(
        self,
        query_text: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[NodeWithScore]:
        """查询相似文档"""
        pass
    
    def delete_index(self):
        """删除索引"""
        pass
```

**使用示例：**

```python
from src.retrieval import VectorStore
from src.loaders import DocumentLoader

# 1. 加载文档
loader = DocumentLoader(input_dir="./data/documents")
documents = loader.load_documents()

# 2. 构建索引
vector_store = VectorStore(
    persist_dir="./data/vector_store",
    embedding_model="BAAI/bge-small-zh-v1.5"
)
index = vector_store.build_index(
    documents=documents,
    chunk_size=512,
    chunk_overlap=50
)

# 3. 查询
results = vector_store.query(
    query_text="Transformer 模型的核心创新",
    top_k=5,
    similarity_threshold=0.7
)

# 4. 处理结果
for result in results:
    print(f"相似度: {result.score}")
    print(f"内容: {result.node.text[:100]}...")
    print(f"来源: {result.node.metadata['file_name']}")
```

### 3. RAG Agent（问答引擎）

**位置**：`src/agent/rag_agent.py`

**职责**：
- 问题理解
- 文档检索
- 上下文构建
- 答案生成
- 来源追溯

**核心类：**

```python
class RAGAgent:
    """RAG 问答 Agent"""
    
    def __init__(
        self,
        vector_store: VectorStore,
        llm: BaseLLM,
        prompt_template: str = None
    ):
        """
        参数:
            vector_store: 向量存储
            llm: 语言模型
            prompt_template: Prompt 模板
        """
        pass
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        return_sources: bool = True
    ) -> Dict[str, Any]:
        """
        RAG 问答
        
        返回:
            {
                'answer': str,              # 生成的答案
                'sources': List[Dict],      # 来源列表
                'confidence': float,        # 置信度
                'retrieval_time': float,    # 检索耗时
                'generation_time': float    # 生成耗时
            }
        """
        pass
    
    def _build_context(self, retrieved_nodes: List[NodeWithScore]) -> str:
        """构建上下文"""
        pass
    
    def _format_sources(self, nodes: List[NodeWithScore]) -> List[Dict]:
        """格式化来源信息"""
        pass
```

**使用示例：**

```python
from src.agent import RAGAgent
from src.retrieval import VectorStore
from src.llm import MoonshotLLM

# 1. 初始化组件
vector_store = VectorStore(persist_dir="./data/vector_store")
llm = MoonshotLLM()

# 2. 创建 Agent
agent = RAGAgent(
    vector_store=vector_store,
    llm=llm,
    prompt_template="基于以下内容回答问题:\n{context}\n\n问题: {question}"
)

# 3. 提问
result = agent.query(
    question="Transformer 的核心创新是什么？",
    top_k=5,
    return_sources=True
)

# 4. 获取结果
print(f"答案: {result['answer']}")
print(f"置信度: {result['confidence']}")
print(f"检索耗时: {result['retrieval_time']:.2f}s")
print(f"生成耗时: {result['generation_time']:.2f}s")

for i, source in enumerate(result['sources'], 1):
    print(f"\n来源 {i}:")
    print(f"  文件: {source['file_name']}")
    print(f"  相似度: {source['similarity']:.2f}")
    print(f"  内容: {source['text'][:100]}...")
```

### 4. LLM Service（语言模型服务）

**位置**：`src/llm/`

**职责**：
- 统一 LLM 接口
- 多提供商支持
- 请求管理
- 错误处理

**核心接口：**

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLM(ABC):
    """LLM 基类"""
    
    @abstractmethod
    def __init__(self, config: Dict[str, Any]):
        """初始化 LLM"""
        pass
    
    @abstractmethod
    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """文本补全"""
        pass
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """多轮对话"""
        pass
```

**实现示例：**

```python
from src.llm.base import BaseLLM
import requests

class CustomLLM(BaseLLM):
    """自定义 LLM 实现"""
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get('api_key')
        self.api_base = config.get('api_base')
        self.model = config.get('model')
    
    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """实现文本补全"""
        response = requests.post(
            f"{self.api_base}/completions",
            json={
                "model": self.model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()['choices'][0]['text']
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """实现多轮对话"""
        response = requests.post(
            f"{self.api_base}/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()['choices'][0]['message']['content']
```

---

## API 参考

### create_agent()

创建 RAG Agent 实例。

```python
def create_agent(
    documents_dir: str = "./data/documents",
    vector_store_dir: str = "./data/vector_store",
    force_rebuild: bool = False,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    embedding_model: str = "BAAI/bge-small-zh-v1.5",
    llm_provider: str = "moonshot",
    **kwargs
) -> RAGAgent:
    """
    创建 RAG Agent
    
    参数:
        documents_dir: 文档目录
        vector_store_dir: 向量存储目录
        force_rebuild: 是否强制重建索引
        chunk_size: 文本块大小
        chunk_overlap: 文本块重叠
        embedding_model: Embedding 模型
        llm_provider: LLM 提供商
        **kwargs: 其他参数
    
    返回:
        RAGAgent 实例
    
    异常:
        FileNotFoundError: 文档目录不存在
        ValueError: 配置参数无效
    """
```

**使用示例：**

```python
from src.agent import create_agent

# 基础使用
agent = create_agent()

# 自定义配置
agent = create_agent(
    documents_dir="./my_papers",
    force_rebuild=True,
    chunk_size=256,
    llm_provider="openai"
)
```

### query()

执行 RAG 查询。

```python
def query(
    agent: RAGAgent,
    question: str,
    mode: str = "rag",
    web_search: bool = False,
    top_k: int = 5,
    temperature: float = 0.7,
    **kwargs
) -> Dict[str, Any]:
    """
    执行查询
    
    参数:
        agent: RAG Agent 实例
        question: 用户问题
        mode: 查询模式 ('rag' 或 'llm')
        web_search: 是否启用联网搜索
        top_k: 检索数量
        temperature: 温度参数
        **kwargs: 其他参数
    
    返回:
        {
            'answer': str,
            'sources': List[Dict],
            'mode': str,
            'web_results': List[Dict]  # 如果启用联网搜索
        }
    """
```

---

## 扩展开发

### 1. 添加新的 LLM 提供商

**步骤：**

1. 创建新的 LLM 类：

```python
# src/llm/custom_llm.py
from src.llm.base import BaseLLM

class CustomLLM(BaseLLM):
    def __init__(self, config):
        self.api_key = config.get('api_key')
        # 初始化你的 LLM 客户端
    
    def complete(self, prompt, **kwargs):
        # 实现补全逻辑
        pass
    
    def chat(self, messages, **kwargs):
        # 实现对话逻辑
        pass
```

2. 注册到配置：

```python
# src/config/llm_config.py
LLM_PROVIDERS = {
    'openai': OpenAILLM,
    'moonshot': MoonshotLLM,
    'custom': CustomLLM,  # 添加新提供商
}
```

3. 更新 .env.example：

```bash
# 添加新的配置项
LLM_PROVIDER=custom
CUSTOM_API_KEY=your-key
CUSTOM_API_BASE=https://api.custom.com/v1
```

### 2. 自定义检索策略

**示例：实现混合检索（关键词 + 语义）**

```python
# src/retrieval/hybrid_retriever.py
from src.retrieval.vector_store import VectorStore
from typing import List
from llama_index.core import QueryBundle
from llama_index.core.schema import NodeWithScore

class HybridRetriever:
    """混合检索器：结合关键词和语义检索"""
    
    def __init__(
        self,
        vector_store: VectorStore,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7
    ):
        self.vector_store = vector_store
        self.keyword_weight = keyword_weight
        self.semantic_weight = semantic_weight
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> List[NodeWithScore]:
        """混合检索"""
        # 1. 语义检索
        semantic_results = self.vector_store.query(query, top_k=top_k)
        
        # 2. 关键词检索
        keyword_results = self._keyword_search(query, top_k=top_k)
        
        # 3. 融合结果
        merged_results = self._merge_results(
            semantic_results,
            keyword_results
        )
        
        return merged_results[:top_k]
    
    def _keyword_search(self, query: str, top_k: int) -> List[NodeWithScore]:
        """关键词搜索实现"""
        # 实现 BM25 或其他关键词检索算法
        pass
    
    def _merge_results(
        self,
        semantic: List[NodeWithScore],
        keyword: List[NodeWithScore]
    ) -> List[NodeWithScore]:
        """融合检索结果"""
        # 实现 RRF (Reciprocal Rank Fusion) 或其他融合策略
        pass
```

### 3. 自定义 Prompt 模板

**创建 Prompt 配置文件：**

```yaml
# config/prompts.yaml
rag_prompt: |
  你是一个专业的学术论文分析助手。
  
  基于以下文档内容回答用户问题：
  {context}
  
  问题: {question}
  
  要求:
  1. 答案必须基于提供的文档内容
  2. 如果文档中没有相关信息，请明确说明
  3. 引用具体的段落支持你的答案
  
  答案:

analysis_prompt: |
  请深度分析以下论文内容：
  {context}
  
  分析维度：
  1. 研究问题和动机
  2. 技术方法
  3. 实验设计
  4. 主要结论
  5. 创新点和局限性
  
  分析结果:
```

**使用自定义 Prompt：**

```python
from src.utils import load_prompts

# 加载 Prompt 模板
prompts = load_prompts("config/prompts.yaml")

# 创建 Agent 时指定
agent = RAGAgent(
    vector_store=vector_store,
    llm=llm,
    prompt_template=prompts['rag_prompt']
)
```

### 4. 添加后处理器

**示例：答案质量评估**

```python
# src/utils/postprocessor.py
class AnswerQualityEvaluator:
    """答案质量评估器"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def evaluate(self, question: str, answer: str, sources: List[Dict]) -> Dict:
        """评估答案质量"""
        # 1. 相关性评分
        relevance_score = self._evaluate_relevance(question, answer)
        
        # 2. 完整性评分
        completeness_score = self._evaluate_completeness(answer, sources)
        
        # 3. 准确性评分
        accuracy_score = self._evaluate_accuracy(answer, sources)
        
        return {
            'relevance': relevance_score,
            'completeness': completeness_score,
            'accuracy': accuracy_score,
            'overall': (relevance_score + completeness_score + accuracy_score) / 3
        }
    
    def _evaluate_relevance(self, question: str, answer: str) -> float:
        """评估相关性"""
        prompt = f"问题: {question}\n答案: {answer}\n\n请评估答案与问题的相关性(0-1):"
        # 使用 LLM 评估
        pass
```

---

## 测试指南

### 单元测试

**位置**：`tests/unit/`

**运行测试：**

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/unit/test_document_loader.py

# 运行并查看覆盖率
pytest --cov=src tests/

# 生成HTML报告
pytest --cov=src --cov-report=html tests/
```

**测试示例：**

```python
# tests/unit/test_document_loader.py
import pytest
from src.loaders import DocumentLoader

class TestDocumentLoader:
    """DocumentLoader 单元测试"""
    
    @pytest.fixture
    def loader(self):
        """测试fixture"""
        return DocumentLoader(
            input_dir="tests/fixtures/documents",
            recursive=True
        )
    
    def test_load_pdf(self, loader):
        """测试 PDF 加载"""
        documents = loader.load_documents()
        assert len(documents) > 0
        assert any(doc.metadata['format'] == 'pdf' for doc in documents)
    
    def test_metadata(self, loader):
        """测试元数据"""
        documents = loader.load_documents()
        for doc in documents:
            assert 'file_name' in doc.metadata
            assert 'file_path' in doc.metadata
            assert 'format' in doc.metadata
```

### 集成测试

**位置**：`tests/integration/`

```python
# tests/integration/test_rag_pipeline.py
import pytest
from src.agent import create_agent

class TestRAGPipeline:
    """RAG 管道集成测试"""
    
    @pytest.fixture(scope="class")
    def agent(self):
        """创建测试 Agent"""
        return create_agent(
            documents_dir="tests/fixtures/documents",
            force_rebuild=True
        )
    
    def test_end_to_end_query(self, agent):
        """端到端查询测试"""
        result = agent.query(
            question="测试问题",
            top_k=3
        )
        
        assert 'answer' in result
        assert 'sources' in result
        assert len(result['sources']) <= 3
    
    def test_query_performance(self, agent):
        """性能测试"""
        import time
        
        start = time.time()
        result = agent.query("测试问题")
        elapsed = time.time() - start
        
        assert elapsed < 10  # 10秒内完成
```

---

## 部署指南

### Docker 部署

**创建 Dockerfile：**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data/documents /app/data/vector_store /app/logs

# 暴露端口
EXPOSE 7860

# 启动应用
CMD ["python", "web_ui.py", "--server-port", "7860", "--server-name", "0.0.0.0"]
```

**创建 docker-compose.yml：**

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "7860:7860"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
      - LLM_API_BASE=${LLM_API_BASE}
      - LLM_MODEL=${LLM_MODEL}
    restart: unless-stopped
```

**部署命令：**

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 代码规范

### Python 代码规范

**遵循 PEP 8 标准：**

1. **Import 组织**
   ```python
   # 标准库
   import os
   from pathlib import Path
   from typing import Optional, List, Dict, Any
   
   # 第三方库
   from llama_index.core import VectorStoreIndex
   from loguru import logger
   
   # 本地模块
   from config import SystemConfig
   from src.loaders import DocumentLoader
   ```

2. **命名规范**
   - 类名：`PascalCase` (例如：`DocumentLoader`)
   - 函数名：`snake_case` (例如：`load_documents`)
   - 常量：`UPPER_CASE` (例如：`DEFAULT_CHUNK_SIZE`)
   - 私有方法：`_private_method`

3. **类型注解**
   ```python
   def query(
       self,
       question: str,
       top_k: int = 5,
       enable_web_search: bool = False
   ) -> Dict[str, Any]:
       """带完整类型注解的函数"""
       pass
   ```

4. **文档字符串（Google 风格）**
   ```python
   def build_index(self, documents: List[Document]) -> VectorStoreIndex:
       """构建向量索引
       
       Args:
           documents: 文档列表
           
       Returns:
           VectorStoreIndex: 构建的索引对象
           
       Raises:
           ValueError: 当文档列表为空时
       """
       pass
   ```

### 代码质量检查

```bash
# 格式化代码
black src/ tests/

# 排序 imports
isort src/ tests/

# 代码检查
flake8 src/ tests/

# 类型检查（可选）
mypy src/
```

### Git 提交规范

**提交消息格式：**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型（type）：**
- `feat`: 新功能
- `fix`: 修复 Bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构代码
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例：**
```
feat(agent): 添加多轮对话历史管理功能

- 实现对话历史存储
- 添加历史清空功能
- 支持上下文记忆

Closes #123
```

---

## 贡献指南

### 开发流程

1. **Fork 项目**
   ```bash
   # 在 GitHub 上 Fork 项目
   git clone https://github.com/your-username/academic-paper-qa.git
   cd academic-paper-qa
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **开发和测试**
   ```bash
   # 编写代码
   vim src/your_module.py
   
   # 编写测试
   vim tests/test_your_module.py
   
   # 运行测试
   pytest tests/test_your_module.py
   ```

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature-name
   # 在 GitHub 上创建 Pull Request
   ```

### Pull Request 检查清单

- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 测试全部通过
- [ ] 更新了相关文档
- [ ] 提交消息清晰明确
- [ ] 代码没有引入新的警告

---

## 二次开发实践案例

### 案例 1: 构建学科专用问答系统

**需求**: 为特定学科（如生物医学）构建专用问答系统

```python
# biology_qa_system.py
from src.agent import AcademicAgent
from typing import Dict, Any

class BiologyQASystem(AcademicAgent):
    """生物医学专用问答系统"""
    
    def __init__(self, **kwargs):
        super().__init__(
            documents_dir="./data/biology_papers",
            **kwargs
        )
        
        # 学科专用术语库
        self.terminology = self._load_terminology()
    
    def _load_terminology(self) -> Dict[str, str]:
        """加载学科术语"""
        return {
            "PCR": "Polymerase Chain Reaction (聚合酶链式反应)",
            "CRISPR": "Clustered Regularly Interspaced Short Palindromic Repeats",
            # ... 更多术语
        }
    
    def query(self, question: str, **kwargs) -> Dict[str, Any]:
        """增强查询：添加术语解释"""
        
        # 检测并解释专业术语
        detected_terms = self._detect_terms(question)
        
        # 执行标准查询
        result = super().query(question, **kwargs)
        
        # 在答案中添加术语解释
        if detected_terms:
            term_explanations = "\n\n**术语解释:**\n"
            for term in detected_terms:
                term_explanations += f"- {term}: {self.terminology[term]}\n"
            result['answer'] += term_explanations
        
        return result
    
    def _detect_terms(self, text: str) -> list:
        """检测文本中的专业术语"""
        return [term for term in self.terminology if term in text.upper()]

# 使用示例
bio_qa = BiologyQASystem()
result = bio_qa.query("PCR 技术的原理是什么？")
print(result['answer'])
```

### 案例 2: 添加批量处理功能

**需求**: 批量处理多个问题，生成报告

```python
# batch_processor.py
from src.agent import AcademicAgent
from typing import List, Dict
import pandas as pd
from datetime import datetime

class BatchProcessor:
    """批量问答处理器"""
    
    def __init__(self):
        self.agent = AcademicAgent()
    
    def process_questions(
        self,
        questions: List[str],
        output_file: str = "qa_results.xlsx"
    ) -> pd.DataFrame:
        """批量处理问题"""
        
        results = []
        
        for i, question in enumerate(questions, 1):
            print(f"处理问题 {i}/{len(questions)}: {question[:50]}...")
            
            try:
                result = self.agent.query(question)
                
                results.append({
                    'question': question,
                    'answer': result['answer'],
                    'sources_count': len(result.get('source_nodes', [])),
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                results.append({
                    'question': question,
                    'answer': '',
                    'sources_count': 0,
                    'status': f'error: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                })
        
        # 转换为 DataFrame
        df = pd.DataFrame(results)
        
        # 导出到 Excel
        df.to_excel(output_file, index=False)
        print(f"\n结果已保存到: {output_file}")
        
        return df

# 使用示例
processor = BatchProcessor()

questions = [
    "什么是深度学习？",
    "Transformer 的核心创新是什么？",
    "如何训练大语言模型？"
]

df = processor.process_questions(questions)
print(f"\n处理完成，成功: {len(df[df.status=='success'])} 条")
```

### 案例 3: 添加引用生成器

**需求**: 自动生成学术引用格式

```python
# citation_generator.py
from src.agent import AcademicAgent
from typing import Dict, List
import re

class CitationGenerator:
    """学术引用生成器"""
    
    def __init__(self):
        self.agent = AcademicAgent()
    
    def query_with_citations(
        self,
        question: str,
        citation_style: str = "apa"
    ) -> Dict:
        """带引用的查询"""
        
        # 执行查询
        result = self.agent.query(question)
        
        # 生成引用
        citations = self._generate_citations(
            result.get('source_nodes', []),
            style=citation_style
        )
        
        # 在答案中添加引用标记
        answer_with_citations = self._add_citation_marks(
            result['answer'],
            citations
        )
        
        return {
            'answer': answer_with_citations,
            'citations': citations,
            'original_answer': result['answer']
        }
    
    def _generate_citations(
        self,
        sources: List,
        style: str = "apa"
    ) -> List[str]:
        """生成引用列表"""
        citations = []
        
        for i, source in enumerate(sources, 1):
            metadata = source.node.metadata
            
            if style == "apa":
                # APA 格式
                citation = f"[{i}] {metadata.get('file_name', 'Unknown')}. Retrieved from {metadata.get('file_path', 'Unknown path')}."
            elif style == "mla":
                # MLA 格式
                citation = f"[{i}] {metadata.get('file_name', 'Unknown')}."
            else:
                citation = f"[{i}] {metadata.get('file_name', 'Unknown')}"
            
            citations.append(citation)
        
        return citations
    
    def _add_citation_marks(self, answer: str, citations: List[str]) -> str:
        """在答案中添加引用标记"""
        # 简单实现：在答案末尾添加引用列表
        if citations:
            answer += "\n\n**参考文献:**\n"
            for citation in citations:
                answer += f"{citation}\n"
        
        return answer

# 使用示例
cit_gen = CitationGenerator()
result = cit_gen.query_with_citations(
    "什么是注意力机制？",
    citation_style="apa"
)
print(result['answer'])
```

### 案例 4: 构建 API 服务

**需求**: 将系统封装为 REST API

```python
# api_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from src.agent import AcademicAgent
import uvicorn

app = FastAPI(title="Academic QA API")
agent = AcademicAgent()

class QueryRequest(BaseModel):
    question: str
    mode: str = "rag"
    enable_web_search: bool = False
    top_k: int = 5
    document_paths: Optional[List[str]] = None

class QueryResponse(BaseModel):
    answer: str
    sources_count: int
    mode: str

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """查询接口"""
    try:
        if request.mode == "rag":
            result = agent.query(
                question=request.question,
                enable_web_search=request.enable_web_search,
                top_k=request.top_k
            )
        else:
            result = agent.query_direct(
                question=request.question,
                document_paths=request.document_paths,
                enable_web_search=request.enable_web_search
            )
        
        return QueryResponse(
            answer=result['answer'],
            sources_count=len(result.get('source_nodes', [])),
            mode=request.mode
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_statistics():
    """获取统计信息"""
    return agent.get_statistics()

@app.post("/rebuild_index")
async def rebuild_index():
    """重建索引"""
    try:
        agent.rebuild_index()
        return {"status": "success", "message": "索引重建完成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 启动服务
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 使用示例（客户端）
"""
import requests

# 查询
response = requests.post(
    "http://localhost:8000/query",
    json={
        "question": "什么是深度学习？",
        "mode": "rag",
        "top_k": 3
    }
)
print(response.json())

# 获取统计
stats = requests.get("http://localhost:8000/stats")
print(stats.json())
"""
```

### 案例 5: 添加缓存层

**需求**: 为频繁查询添加缓存，提升性能

```python
# cached_agent.py
from src.agent import AcademicAgent
from typing import Dict, Any
import hashlib
import json
import redis
from functools import wraps

class CachedAgent(AcademicAgent):
    """带缓存的 Agent"""
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, **kwargs):
        super().__init__(**kwargs)
        
        # 连接 Redis
        self.cache = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )
        
        # 缓存过期时间（秒）
        self.cache_ttl = 3600  # 1小时
    
    def _get_cache_key(self, question: str, **kwargs) -> str:
        """生成缓存键"""
        # 将问题和参数组合成唯一键
        key_data = {
            'question': question,
            **kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def query(self, question: str, **kwargs) -> Dict[str, Any]:
        """带缓存的查询"""
        
        # 生成缓存键
        cache_key = f"query:{self._get_cache_key(question, **kwargs)}"
        
        # 尝试从缓存获取
        cached_result = self.cache.get(cache_key)
        if cached_result:
            print(f"✓ 缓存命中: {cache_key}")
            return json.loads(cached_result)
        
        # 缓存未命中，执行查询
        print(f"✗ 缓存未命中，执行查询...")
        result = super().query(question, **kwargs)
        
        # 存入缓存（不缓存 source_nodes，太大）
        cacheable_result = {
            'answer': result['answer'],
            'sources_count': len(result.get('source_nodes', [])),
            'cached': False
        }
        
        self.cache.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(cacheable_result)
        )
        
        return result
    
    def clear_cache(self):
        """清空缓存"""
        pattern = "query:*"
        keys = self.cache.keys(pattern)
        if keys:
            self.cache.delete(*keys)
            print(f"已清空 {len(keys)} 个缓存项")

# 使用示例
agent = CachedAgent()

# 第一次查询（无缓存）
result1 = agent.query("什么是深度学习？")  # 需要几秒

# 第二次相同查询（有缓存）
result2 = agent.query("什么是深度学习？")  # 毫秒级响应

# 清空缓存
agent.clear_cache()
```

---

## 常见开发任务

### 添加新的文档格式支持

**步骤**:
1. 在 `src/loaders/` 创建新的加载器类
2. 实现文档读取和文本提取逻辑
3. 在 `DocumentLoader` 中注册新格式
4. 添加测试用例验证功能
5. 更新文档说明支持的格式

**示例**: 参见 [扩展开发 - 添加新的文档格式支持](#1-添加新的文档格式支持)

### 优化检索性能

**策略**:
1. **调整分块参数**: 
   - 增大 `chunk_size` 可以保留更多上下文，但会降低检索精度
   - 增大 `chunk_overlap` 可以避免关键信息被切断
   
2. **尝试不同 Embedding 模型**:
   - `BAAI/bge-small-zh-v1.5`: 轻量级，速度快
   - `BAAI/bge-large-zh`: 效果更好，但更慢
   - `text-embedding-3-small`: OpenAI Embedding
   
3. **实现混合检索**:
   - 结合关键词检索（BM25）和语义检索
   - 参见 [扩展开发 - 自定义检索策略](#3-自定义检索策略)
   
4. **添加缓存机制**:
   - 缓存频繁查询的结果
   - 使用 Redis 或内存缓存
   - 参见 [案例 5 - 添加缓存层](#案例-5-添加缓存层)

### 集成新的 LLM 提供商

**步骤**:
1. 在 `config/llm_config.py` 中添加新的 LLM 类
2. 实现必要的接口方法（`complete`, `chat`）
3. 添加环境变量配置
4. 更新 `.env.example` 示例
5. 编写使用文档和示例

**示例**: 参见 [扩展开发 - 添加新的 LLM 提供商](#2-添加新的-llm-提供商)

### 添加新的输出格式

**示例**: 导出为 Markdown 报告

```python
def export_to_markdown(
    question: str,
    result: Dict[str, Any],
    output_file: str
):
    """导出查询结果为 Markdown 报告"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # 标题
        f.write(f"# 查询报告\n\n")
        f.write(f"**问题**: {question}\n\n")
        f.write(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 答案
        f.write(f"## 答案\n\n")
        f.write(f"{result['answer']}\n\n")
        
        # 来源
        if result.get('source_nodes'):
            f.write(f"## 参考来源\n\n")
            for i, node in enumerate(result['source_nodes'], 1):
                f.write(f"### 来源 {i}\n\n")
                f.write(f"- **文件**: {node.node.metadata.get('file_name')}\n")
                f.write(f"- **相似度**: {node.score:.2f}\n")
                f.write(f"- **内容**:\n\n```\n{node.node.text[:200]}...\n```\n\n")
```

---

## 下一步

- 📋 查看 [功能介绍](FEATURES.md) 了解系统能力
- 📖 阅读 [使用指南](USER_GUIDE.md) 开始使用
- 🚀 开始开发你的扩展功能
- 💬 加入讨论获取帮助

---

**更新日期**: 2025-12-20  
**版本**: v2.0  
**维护者**: Academic QA Team
