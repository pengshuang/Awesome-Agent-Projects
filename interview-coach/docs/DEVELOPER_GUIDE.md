# AI 模拟面试系统 - 开发指南

本文档面向希望对系统进行二次开发、定制或扩展的开发者。

## 📋 目录

- [架构设计](#架构设计)
- [核心模块](#核心模块)
- [扩展开发](#扩展开发)
- [API 参考](#api-参考)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

## 🏗️ 架构设计

### 项目结构

详细的项目结构请参考：[项目概览 - 项目结构](PROJECT_OVERVIEW.md#-项目结构)

### 技术栈

- **Web 框架**: Gradio 4.0+
- **LLM 框架**: LlamaIndex 0.13+
- **PDF 解析**: PyMuPDF / PyPDF2
- **Web 搜索**: DuckDuckGo Search (ddgs)
- **日志**: Loguru
- **配置管理**: python-dotenv

### 设计原则

1. **模块化**：功能独立，低耦合
2. **可扩展**：易于添加新功能
3. **配置驱动**：通过环境变量灵活配置
4. **错误处理**：完善的异常捕获和降级
5. **日志记录**：详细的操作日志

## 🔧 核心模块

### 1. 配置模块 (config/)

#### settings.py

系统配置管理，包括路径、LLM 配置、系统参数等。

```python
from config import SystemConfig, initialize_settings

# 初始化系统配置
initialize_settings()

# 访问配置
print(SystemConfig.LLM_MODEL)
print(SystemConfig.RESUMES_DIR)
```

**关键配置**：
- `BASE_DIR`: 项目根目录
- `DATA_DIR`: 数据目录
- `RESUMES_DIR`: 简历存储目录
- `LLM_API_KEY`: LLM API Key
- `LLM_MODEL`: LLM 模型名称
- `ENABLE_WEB_SEARCH`: 是否启用联网搜索

#### llm_config.py

LLM 实例化和配置。

```python
from config import get_llm

# 获取 LLM 实例
llm = get_llm()

# 自定义参数
llm = get_llm(
    api_key="custom-key",
    api_base="https://custom-api.com",
    model="custom-model",
    temperature=0.5
)
```

**支持的 LLM**：
- OpenAI (官方)
- OpenAI-like (兼容接口)
- DeepSeek
- Qwen
- 其他兼容 OpenAI API 的服务

### 2. 简历加载器 (src/loaders/)

#### ResumeLoader

解析 PDF 格式简历，提取文本内容。

```python
from src import ResumeLoader

# 创建加载器
loader = ResumeLoader()

# 加载简历
result = loader.load_resume("path/to/resume.pdf")

# 访问内容
content = result["content"]
metadata = result["metadata"]

# 获取摘要
summary = loader.get_summary()
```

**API**：
- `load_resume(file_path)`: 加载简历文件
- `get_content()`: 获取简历内容
- `get_metadata()`: 获取元数据
- `get_summary()`: 获取简历摘要

**扩展支持其他格式**：

```python
# 在 ResumeLoader 中添加新方法
def _load_docx(self, file_path: Path) -> str:
    """加载 DOCX 文件"""
    import docx
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# 更新 load_resume 方法
def load_resume(self, file_path: str):
    file_path = Path(file_path)
    
    if file_path.suffix.lower() == ".pdf":
        content = self._load_pdf(file_path)
    elif file_path.suffix.lower() == ".docx":
        content = self._load_docx(file_path)
    else:
        raise ValueError(f"不支持的格式: {file_path.suffix}")
    
    # ... 其他处理
```

### 3. 简历评估器 (src/evaluator/)

#### ResumeEvaluator

基于 LLM 对简历进行多维度评估。

```python
from src import ResumeEvaluator

# 创建评估器
evaluator = ResumeEvaluator()

# 完整评估
result = evaluator.evaluate(
    resume_content=content,
    position="Python 开发工程师",
    requirements="3年以上经验..."
)

# 快速评分
score_result = evaluator.quick_score(content)

# 改进建议
suggestions = evaluator.suggest_improvements(content)
```

**API**：
- `evaluate(resume_content, position, requirements)`: 完整评估
- `quick_score(resume_content)`: 快速评分
- `suggest_improvements(resume_content)`: 改进建议

**自定义评估提示词**：

```python
custom_prompt = """
你是一位资深HR，请评估以下简历...
{resume_content}

评估维度：
1. ...
2. ...
"""

evaluator = ResumeEvaluator(custom_prompt=custom_prompt)
```

### 4. 面试 Agent (src/interview/)

#### InterviewAgent

多轮对话模拟面试。

```python
from src import InterviewAgent

# 创建 Agent
agent = InterviewAgent(
    resume_content=resume_content,
    interview_type="technical",  # technical, behavioral, comprehensive
    max_history_turns=20,
    enable_web_search=True,
)

# 开始面试
opening = agent.start_interview()
print(opening["opening"])

# 对话
response = agent.chat(
    user_message="我有3年Python开发经验...",
    use_web_search=True,
)
print(response["response"])

# 管理历史
agent.clear_history()
history = agent.get_history()
summary = agent.get_interview_summary()
```

**API**：
- `start_interview()`: 开始面试，生成开场白
- `chat(user_message, use_web_search)`: 进行一轮对话
- `clear_history()`: 清空对话历史
- `get_history()`: 获取对话历史
- `set_resume(resume_content)`: 更新简历内容
- `get_interview_summary()`: 获取面试总结

**自定义面试提示词**：

```python
custom_system_prompt = """
你是一位严格的技术面试官...
候选人简历：
{resume_summary}

面试要求：
1. ...
2. ...
"""

agent = InterviewAgent(
    resume_content=content,
    custom_system_prompt=custom_system_prompt,
)
```

### 5. Web 搜索工具 (src/tools/)

#### WebSearchTool

联网搜索功能。

```python
from src.tools import WebSearchTool

# 创建工具
tool = WebSearchTool(
    max_results=5,
    engine="duckduckgo",  # duckduckgo, searxng
)

# 搜索
results = tool.search("Python asyncio")

# 处理结果
for result in results:
    print(result["title"])
    print(result["url"])
    print(result["snippet"])
```

**API**：
- `search(query, max_results)`: 执行搜索

**添加新搜索引擎**：

```python
class WebSearchTool:
    def _search_custom_engine(self, query: str, max_results: int):
        """自定义搜索引擎"""
        # 实现搜索逻辑
        results = []
        # ...
        return results
    
    def search(self, query: str, max_results: Optional[int] = None):
        # 在引擎列表中添加新引擎
        engines_to_try = ["custom_engine", "duckduckgo", ...]
        
        for engine in engines_to_try:
            if engine == "custom_engine":
                results = self._search_custom_engine(query, max_results)
            # ...
```

## 🚀 扩展开发

### 添加新的面试类型

1. **更新常量定义** (src/constants.py)：

```python
INTERVIEW_TYPES = {
    "technical": "技术面试",
    "behavioral": "行为面试",
    "comprehensive": "综合面试",
    "case": "案例面试",  # 新增
}

CASE_INTERVIEW_PROMPT = """
你是一位咨询公司的案例面试官...
"""
```

2. **在 InterviewAgent 中支持新类型**：

```python
def _build_system_prompt(self, custom_prompt: Optional[str] = None):
    if custom_prompt:
        return custom_prompt
    
    if self.interview_type == "case":
        return CASE_INTERVIEW_PROMPT.format(...)
    # ... 其他类型
```

3. **在 Web UI 中添加选项**：

```python
interview_type = gr.Radio(
    label="面试类型",
    choices=[
        ("技术面试", "technical"),
        ("行为面试", "behavioral"),
        ("综合面试", "comprehensive"),
        ("案例面试", "case"),  # 新增
    ],
)
```

### 添加新的评估维度

修改 `src/constants.py`：

```python
EVALUATION_DIMENSIONS = [
    "基本信息完整性",
    "工作经验相关性",
    "项目经验质量",
    "技能匹配度",
    "教育背景",
    "整体印象",
    "软技能体现",  # 新增
    "职业规划清晰度",  # 新增
]

DEFAULT_EVALUATION_PROMPT = """
...
请按照以下维度进行评估：
1. 基本信息完整性
...
7. 软技能体现（沟通、协作、领导力等）
8. 职业规划清晰度
"""
```

### 集成新的 LLM

1. **安装 LlamaIndex 集成包**：

```bash
pip install llama-index-llms-anthropic  # 以 Anthropic 为例
```

2. **在 llm_config.py 中添加支持**：

```python
def get_llm(...):
    # 检测 API Base
    if "anthropic" in api_base:
        from llama_index.llms.anthropic import Anthropic
        return Anthropic(
            api_key=api_key,
            model=model,
        )
    # ... 其他 LLM
```

3. **更新 .env.example**：

```ini
# Anthropic Claude
# LLM_API_KEY=your-anthropic-key
# LLM_API_BASE=https://api.anthropic.com
# LLM_MODEL=claude-3-opus-20240229
```

### 添加新的工具

例如添加「简历优化」工具：

1. **创建新模块** (src/tools/resume_optimizer.py)：

```python
from typing import Dict, Any
from llama_index.core import Settings

class ResumeOptimizer:
    """简历优化工具"""
    
    def __init__(self):
        self.llm = Settings.llm
    
    def optimize(self, resume_content: str, target: str) -> Dict[str, Any]:
        """
        优化简历
        
        Args:
            resume_content: 原始简历
            target: 优化目标
        """
        prompt = f"""
        请优化以下简历，优化目标：{target}
        
        原始简历：
        {resume_content}
        
        请提供优化后的简历内容。
        """
        
        response = self.llm.complete(prompt)
        
        return {
            "optimized_content": response.text,
        }
```

2. **在 Web UI 中集成**：

```python
from src.tools.resume_optimizer import ResumeOptimizer

optimizer = ResumeOptimizer()

def optimize_resume(target: str):
    global current_resume_content
    
    result = optimizer.optimize(
        resume_content=current_resume_content,
        target=target,
    )
    
    return result["optimized_content"]

# 添加 UI 组件
with gr.Tab("📝 简历优化"):
    target_input = gr.Textbox(label="优化目标")
    optimize_btn = gr.Button("开始优化")
    optimized_output = gr.Textbox(label="优化结果")
    
    optimize_btn.click(
        fn=optimize_resume,
        inputs=[target_input],
        outputs=[optimized_output],
    )
```

### 数据持久化

添加数据库支持（以 SQLite 为例）：

1. **创建数据库模块** (src/database.py)：

```python
import sqlite3
from pathlib import Path
from typing import Dict, List

class Database:
    def __init__(self, db_path: str = "data/interview.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                content TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER,
                evaluation TEXT,
                score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resumes(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_resume(self, filename: str, content: str) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO resumes (filename, content) VALUES (?, ?)",
            (filename, content)
        )
        
        resume_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return resume_id
    
    def save_evaluation(self, resume_id: int, evaluation: str, score: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO evaluations (resume_id, evaluation, score) VALUES (?, ?, ?)",
            (resume_id, evaluation, score)
        )
        
        conn.commit()
        conn.close()
```

2. **在应用中使用**：

```python
from src.database import Database

db = Database()

# 保存简历
resume_id = db.save_resume(filename, content)

# 保存评估结果
db.save_evaluation(resume_id, evaluation_text, score)
```

## 📚 API 参考

### 完整 API 列表

#### ResumeLoader

```python
class ResumeLoader:
    def __init__(self) -> None
    def load_resume(self, file_path: str) -> Dict[str, Any]
    def get_content(self) -> Optional[str]
    def get_metadata(self) -> Dict[str, Any]
    def get_summary(self) -> str
```

#### ResumeEvaluator

```python
class ResumeEvaluator:
    def __init__(self, custom_prompt: Optional[str] = None) -> None
    def evaluate(
        self,
        resume_content: str,
        position: Optional[str] = None,
        requirements: Optional[str] = None,
    ) -> Dict[str, Any]
    def quick_score(self, resume_content: str) -> Dict[str, Any]
    def suggest_improvements(self, resume_content: str) -> Dict[str, Any]
```

#### InterviewAgent

```python
class InterviewAgent:
    def __init__(
        self,
        resume_content: Optional[str] = None,
        interview_type: str = "technical",
        max_history_turns: int = 20,
        enable_web_search: bool = True,
        custom_system_prompt: Optional[str] = None,
    ) -> None
    
    def start_interview(self) -> Dict[str, Any]
    def chat(self, user_message: str, use_web_search: bool = False) -> Dict[str, Any]
    def clear_history(self) -> None
    def get_history(self) -> List[Dict[str, str]]
    def set_resume(self, resume_content: str) -> None
    def get_interview_summary(self) -> Dict[str, Any]
```

#### WebSearchTool

```python
class WebSearchTool:
    def __init__(
        self,
        max_results: int = 5,
        engine: str = "duckduckgo",
        searxng_url: Optional[str] = None
    ) -> None
    
    def search(self, query: str, max_results: Optional[int] = None) -> List[Dict]
```

## 💡 最佳实践

### 代码风格

- 遵循 PEP 8 规范
- 使用类型注解
- 添加文档字符串
- 保持函数简洁（单一职责）

```python
def process_resume(
    file_path: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    处理简历文件
    
    Args:
        file_path: 简历文件路径
        options: 处理选项
        
    Returns:
        处理结果字典
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件格式不支持
    """
    # 实现
    pass
```

### 错误处理

```python
try:
    result = some_operation()
except SpecificError as e:
    logger.error(f"操作失败: {e}")
    # 降级或返回默认值
    result = default_value
except Exception as e:
    logger.exception(f"未预期的错误: {e}")
    raise
```

### 日志记录

```python
from loguru import logger

# 使用不同级别
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.exception("异常信息（包含堆栈）")

# 结构化日志
logger.info(f"处理完成 | 文件: {filename} | 耗时: {elapsed:.2f}秒")
```

### 配置管理

- 敏感信息放在 .env
- 默认值在代码中定义
- 支持环境变量覆盖

```python
SETTING = os.getenv("SETTING_NAME", "default_value")
```

### 测试

创建测试文件 (tests/test_loader.py)：

```python
import pytest
from src import ResumeLoader

def test_load_pdf():
    loader = ResumeLoader()
    result = loader.load_resume("tests/fixtures/sample.pdf")
    
    assert result["content"] is not None
    assert len(result["content"]) > 0
    assert "metadata" in result

def test_invalid_file():
    loader = ResumeLoader()
    
    with pytest.raises(ValueError):
        loader.load_resume("tests/fixtures/invalid.txt")
```

运行测试：

```bash
pytest tests/
```

## ❓ 常见问题

### Q1: 如何调试 LLM 调用？

启用详细日志：

```python
# 在 .env 中设置
LOG_LEVEL=DEBUG

# 或在代码中
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Q2: 如何优化响应速度？

1. 使用更快的模型
2. 减少上下文长度
3. 启用缓存
4. 异步处理

```python
import asyncio

async def async_evaluate(content):
    # 异步评估
    pass

# 并行处理
results = await asyncio.gather(
    async_evaluate(content1),
    async_evaluate(content2),
)
```

### Q3: 如何部署到服务器？

使用 Gunicorn + Nginx：

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动
gunicorn -w 4 -b 0.0.0.0:8000 web_ui:app
```

### Q4: 如何处理大文件？

- 分块读取
- 流式处理
- 限制文件大小

```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

if file_size > MAX_FILE_SIZE:
    raise ValueError("文件过大")
```

## 📞 支持

- GitHub Issues
- 邮件支持
- 技术文档

---

Happy Coding! 🚀
