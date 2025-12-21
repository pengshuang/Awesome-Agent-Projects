# 开发指南

面向开发者，介绍二次开发、功能扩展和系统定制。

## 📋 目录

- [环境搭建](#环境搭建)
- [架构概览](#架构概览)
- [核心模块](#核心模块)
- [扩展开发](#扩展开发)
- [测试与调试](#测试与调试)
- [部署指南](#部署指南)

---

## 环境搭建

### 环境要求

- Python 3.9+
- pip 20.0+
- Git

### 开发配置

```bash
# 1. 克隆并进入项目
git clone <repository-url>
cd interview-coach

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装开发工具（可选）
pip install pytest black isort mypy flake8

# 5. 配置环境
cp .env.example .env
# 编辑 .env，填写 API 密钥
```

---

## 架构概览

### 目录结构

```
interview-coach/
├── config/              # 配置管理
│   ├── llm_config.py   # LLM 客户端
│   ├── prompts.py      # Prompt 模板
│   └── settings.py     # Pydantic Settings
│
├── src/
│   ├── models/         # Pydantic 数据模型
│   │   ├── resume.py
│   │   ├── evaluation.py
│   │   └── interview.py
│   ├── loaders/        # 简历加载器
│   ├── evaluator/      # 评估引擎
│   ├── interview/      # 面试代理
│   ├── tools/          # 工具模块
│   ├── utils/          # 工具函数
│   └── exceptions.py   # 异常定义
│
├── tests/              # 测试
├── web_ui.py          # Gradio UI
└── quick_start.py     # CLI 示例
```

### 架构原则

1. **模块化**: 职责单一,低耦合
2. **类型安全**: Pydantic v2 数据验证
3. **配置驱动**: 集中配置管理
4. **可扩展**: 预留扩展接口
5. **可测试**: 完整测试覆盖

---

## 核心模块

### 1. 数据模型 (src/models/)

使用 **Pydantic v2** 实现类型安全的数据模型。

#### resume.py - 简历数据

```python
from pydantic import BaseModel, Field, computed_field

class ResumeMetadata(BaseModel):
    """简历元数据"""
    filename: str
    file_size: int
    page_count: int = 0
    
    @computed_field
    @property
    def file_size_mb(self) -> float:
        return round(self.file_size / (1024 * 1024), 2)

class ResumeData(BaseModel):
    """简历完整数据"""
    content: str = Field(..., description="简历文本内容")
    metadata: ResumeMetadata
    
    @computed_field
    @property
    def word_count(self) -> int:
        return len(self.content)
```

**扩展示例**: 添加新字段
```python
class ResumeData(BaseModel):
    # 新增字段
    parsed_sections: dict[str, str] = Field(
        default_factory=dict,
        description="解析的简历章节"
    )
```

#### evaluation.py - 评估结果

```python
class ScoreDetails(BaseModel):
    """评分详情"""
    basic_info: int = Field(ge=0, le=10)
    work_experience: int = Field(ge=0, le=10)
    project_quality: int = Field(ge=0, le=10)
    skills_match: int = Field(ge=0, le=10)
    education: int = Field(ge=0, le=10)
    overall_impression: int = Field(ge=0, le=10)
    
    @computed_field
    @property
    def total_score(self) -> float:
        return round(
            (self.basic_info + self.work_experience + 
             self.project_quality + self.skills_match + 
             self.education + self.overall_impression) / 6 * 10,
            1
        )
```

#### interview.py - 面试会话

```python
from enum import Enum

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class InterviewType(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    COMPREHENSIVE = "comprehensive"

class InterviewMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class InterviewSession(BaseModel):
    messages: list[InterviewMessage] = Field(default_factory=list)
    interview_type: InterviewType = InterviewType.COMPREHENSIVE
```

### 2. 配置管理 (config/settings.py)

使用 **Pydantic Settings** 管理配置。

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class SystemConfig(BaseSettings):
    """系统配置 - 自动从环境变量加载"""
    
    # LLM 配置
    llm_api_key: str = Field(..., description="LLM API密钥")
    llm_api_base: str = Field(
        default="https://api.openai.com/v1",
        description="API端点"
    )
    llm_model: str = Field(
        default="gpt-3.5-turbo",
        description="模型名称"
    )
    
    # 路径配置
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    
    @computed_field
    @property
    def data_dir(self) -> Path:
        return self.base_dir / "data"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

# 单例模式
_config_instance = None

def get_config() -> SystemConfig:
    global _config_instance
    if _config_instance is None:
        _config_instance = SystemConfig()
    return _config_instance
```

### 3. 异常处理 (src/exceptions.py)

```python
class InterviewCoachException(Exception):
    """基础异常"""
    pass

class ResumeLoadError(InterviewCoachException):
    """简历加载失败"""
    pass

class LLMAPIError(InterviewCoachException):
    """LLM API调用失败"""
    pass

class EvaluationError(InterviewCoachException):
    """评估处理失败"""
    pass
```

### 4. 简历加载器 (src/loaders/)

```python
import fitz  # PyMuPDF
from src.models.resume import ResumeData, ResumeMetadata
from src.exceptions import ResumeLoadError

class ResumeLoader:
    def load_pdf(self, file_path: str) -> ResumeData:
        """加载PDF简历"""
        try:
            doc = fitz.open(file_path)
            content = "\n".join(
                page.get_text() for page in doc
            )
            
            metadata = ResumeMetadata(
                filename=Path(file_path).name,
                file_size=Path(file_path).stat().st_size,
                page_count=doc.page_count
            )
            
            return ResumeData(
                content=content,
                metadata=metadata
            )
        except Exception as e:
            raise ResumeLoadError(f"加载失败: {e}")
```

### 5. 评估引擎 (src/evaluator/)

```python
from openai import OpenAI
from src.models.evaluation import EvaluationResult
from src.exceptions import EvaluationError

class ResumeEvaluator:
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model
    
    def evaluate(
        self, 
        resume: ResumeData,
        job_title: str = "",
        job_requirements: str = ""
    ) -> EvaluationResult:
        """评估简历"""
        try:
            prompt = self._build_prompt(
                resume, job_title, job_requirements
            )
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            # 解析为 Pydantic 模型
            result_dict = json.loads(
                response.choices[0].message.content
            )
            return EvaluationResult(**result_dict)
            
        except Exception as e:
            raise EvaluationError(f"评估失败: {e}")
```

---

## 扩展开发

### 添加新的评估维度

1. **修改数据模型** (`src/models/evaluation.py`):
```python
class ScoreDetails(BaseModel):
    # 原有字段...
    
    # 新增字段
    soft_skills: int = Field(
        ge=0, le=10,
        description="软技能评分"
    )
    
    @computed_field
    @property
    def total_score(self) -> float:
        # 更新计算逻辑
        return round(
            (self.basic_info + ... + self.soft_skills) / 7 * 10,
            1
        )
```

2. **更新 Prompt** (`config/prompts.py`):
```python
EVALUATION_PROMPT = """
评估维度：
...
7. 软技能（0-10分）：沟通、领导力等
"""
```

3. **测试新功能**:
```python
def test_new_dimension():
    result = evaluator.evaluate(resume)
    assert hasattr(result.scores, 'soft_skills')
    assert 0 <= result.scores.soft_skills <= 10
```

### 添加新的面试类型

1. **扩展枚举** (`src/models/interview.py`):
```python
class InterviewType(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    COMPREHENSIVE = "comprehensive"
    CASE_STUDY = "case_study"  # 新增
```

2. **更新 Prompt** (`config/prompts.py`):
```python
INTERVIEW_PROMPTS = {
    InterviewType.CASE_STUDY: """
    你是案例面试官，专注于业务分析能力...
    """
}
```

3. **UI 集成** (`web_ui.py`):
```python
interview_type = gr.Radio(
    choices=[
        "技术面试",
        "行为面试", 
        "综合面试",
        "案例分析"  # 新增
    ]
)
```

### 添加新的数据源

示例：支持 Word 文档

```python
# src/loaders/resume_loader.py
from docx import Document

class ResumeLoader:
    def load_docx(self, file_path: str) -> ResumeData:
        """加载Word简历"""
        try:
            doc = Document(file_path)
            content = "\n".join(
                para.text for para in doc.paragraphs
            )
            
            metadata = ResumeMetadata(
                filename=Path(file_path).name,
                file_size=Path(file_path).stat().st_size,
                page_count=len(doc.sections)
            )
            
            return ResumeData(
                content=content,
                metadata=metadata
            )
        except Exception as e:
            raise ResumeLoadError(f"加载Word失败: {e}")
```

---

## 测试与调试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_loader.py

# 查看覆盖率
pytest --cov=src tests/

# 详细输出
pytest -v -s
```

### 代码质量检查

```bash
# 格式化代码
black .
isort .

# 类型检查
mypy src/

# 代码风格
flake8 src/
```

### 调试技巧

**1. 日志调试**:
```python
from src.utils.logger import setup_logger

logger = setup_logger(__name__)
logger.debug(f"Resume content: {resume.content[:100]}")
```

**2. Pydantic 验证调试**:
```python
try:
    resume = ResumeData(**data)
except ValidationError as e:
    print(e.json())  # 查看详细错误
```

**3. LLM 响应调试**:
```python
# 打印完整响应
response = client.chat.completions.create(...)
print(response.model_dump_json(indent=2))
```

---

## 部署指南

### 本地部署

```bash
# 启动 Web UI
python web_ui.py

# 自定义端口
python web_ui.py --server-port 8080
```

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 7861

CMD ["python", "web_ui.py", "--server-name", "0.0.0.0"]
```

```bash
# 构建镜像
docker build -t interview-coach .

# 运行容器
docker run -p 7861:7861 \
  -e LLM_API_KEY=your_key \
  -e LLM_API_BASE=https://api.openai.com/v1 \
  interview-coach
```

### 生产环境建议

1. **安全**:
   - 使用密钥管理服务存储 API 密钥
   - 启用 HTTPS
   - 添加身份认证

2. **性能**:
   - 配置合适的并发数
   - 启用响应缓存
   - 使用负载均衡

3. **监控**:
   - 接入日志收集系统
   - 配置性能监控
   - 设置告警规则

---

## 常见问题

### Q: 如何切换 LLM 服务商?
**A**: 修改 `.env` 文件中的 `LLM_API_BASE` 和 `LLM_MODEL`。

### Q: 如何自定义 Prompt?
**A**: 编辑 `config/prompts.py`,所有 Prompt 模板集中管理。

### Q: Pydantic 验证失败怎么办?
**A**: 检查输入数据格式,查看 `ValidationError` 详细信息。

### Q: 如何添加新的配置项?
**A**: 在 `config/settings.py` 的 `SystemConfig` 中添加字段,支持从环境变量自动加载。

---

## 参考资源

- [Pydantic 文档](https://docs.pydantic.dev/)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Gradio 文档](https://gradio.app/docs/)
- [PyMuPDF 文档](https://pymupdf.readthedocs.io/)

---

如需更多帮助,欢迎提交 Issue!
# 在 get_llm_client 中添加
if api_base.endswith("your-llm-service.com"):
    # 添加特定配置
    client = OpenAI(
        api_key=api_key,
        base_url=api_base,
        # 添加特定参数
    )
```

#### prompts.py - Prompt管理

**核心功能**：
- 统一管理所有Prompt模板
- 提供Prompt构建工具类

**类结构**：
```python
class PromptTemplates:
    """Prompt模板集合"""
    RESUME_EVALUATION = """..."""      # 简历评估
    QUICK_SCORE = """..."""           # 快速评分
    IMPROVEMENT_SUGGESTIONS = """...""" # 改进建议
    JOB_ANALYSIS = """..."""          # 岗位解读
    INTERVIEW_TECHNICAL = """..."""    # 技术面试
    INTERVIEW_BEHAVIORAL = """..."""   # 行为面试
    INTERVIEW_COMPREHENSIVE = """...""" # 综合面试

class PromptManager:
    """Prompt管理器"""
    @staticmethod
    def get_resume_evaluation_prompt(...) -> str:
        """构建简历评估Prompt"""
```

**扩展示例**：添加新的Prompt模板
```python
# 1. 在 PromptTemplates 中添加模板
class PromptTemplates:
    NEW_FEATURE = """你的Prompt模板..."""

# 2. 在 PromptManager 中添加构建方法
class PromptManager:
    @staticmethod
    def get_new_feature_prompt(param1, param2) -> str:
        return PromptTemplates.NEW_FEATURE.format(
            param1=param1,
            param2=param2
        )
```

#### settings.py - 系统配置

**核心功能**：
- 管理系统级配置参数
- 提供配置类

**配置类**：
```python
class SystemConfig:
    # Web搜索配置
    ENABLE_WEB_SEARCH: bool
    WEB_SEARCH_ENGINE: str
    MAX_SEARCH_RESULTS: int
    
    # 面试配置
    MAX_HISTORY_TURNS: int
    
    # 日志配置
    LOG_LEVEL: str
```

---

### 2. 业务逻辑模块 (src/)

#### loaders/resume_loader.py - 简历加载器

**核心类**：`ResumeLoader`

**主要方法**：
```python
def load_resume(self, file_path: str) -> Dict[str, Any]:
    """
    加载并解析PDF简历
    
    Args:
        file_path: 简历文件路径
        
    Returns:
        {
            "content": str,      # 简历文本内容
            "metadata": {        # 元数据
                "file_name": str,
                "file_size": int,
                "content_length": int,
                "load_time": float
            }
        }
    """
```

**扩展示例**：支持DOCX格式
```python
import docx

def load_resume(self, file_path: str) -> Dict[str, Any]:
    # 添加格式检测
    if file_path.endswith('.docx'):
        return self._load_docx(file_path)
    elif file_path.endswith('.pdf'):
        return self._load_pdf(file_path)
    
def _load_docx(self, file_path: str) -> Dict[str, Any]:
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    # 构建返回结果...
```

#### evaluator/resume_evaluator.py - 简历评估器

**核心类**：`ResumeEvaluator`

**主要方法**：
```python
def evaluate(self, resume_content: str, 
             position: Optional[str] = None,
             requirements: Optional[str] = None) -> Dict[str, Any]:
    """完整评估"""

def quick_score(self, resume_content: str) -> Dict[str, Any]:
    """快速评分"""

def suggest_improvements(self, resume_content: str) -> Dict[str, Any]:
    """改进建议"""
```

**扩展示例**：添加新的评估维度
```python
def evaluate_with_custom_dimensions(
    self, 
    resume_content: str,
    custom_dimensions: List[str]
) -> Dict[str, Any]:
    """使用自定义评估维度"""
    
    # 构建自定义Prompt
    dimensions_text = "\n".join([
        f"- {dim}" for dim in custom_dimensions
    ])
    
    prompt = f"""请从以下维度评估简历：
{dimensions_text}

简历内容：
{resume_content}
"""
    
    # 调用LLM
    response = self.client.chat.completions.create(...)
    return result
```

#### interview/interview_agent.py - 面试Agent

**核心类**：`InterviewAgent`

**主要方法**：
```python
def start_interview(self) -> Dict[str, Any]:
    """开始面试，生成开场白"""

def chat(self, user_message: str, 
         use_web_search: bool = False) -> Dict[str, Any]:
    """处理用户回答，生成面试官回复"""

def get_interview_summary(self) -> Dict[str, Any]:
    """获取面试总结"""

def clear_history(self):
    """清空对话历史"""
```

**对话管理**：
```python
# 对话历史结构
self.chat_history: List[Dict[str, str]] = [
    {"role": "system", "content": "系统提示"},
    {"role": "assistant", "content": "面试官消息"},
    {"role": "user", "content": "用户消息"},
    ...
]
```

**扩展示例**：添加面试评分功能
```python
def score_answer(self, answer: str, question: str) -> Dict[str, Any]:
    """评估回答质量"""
    
    prompt = f"""作为面试官，请评估以下回答：

问题：{question}
回答：{answer}

请给出：
1. 评分（0-10分）
2. 评价
3. 改进建议
"""
    
    response = self.client.chat.completions.create(...)
    return {
        "score": ...,
        "evaluation": ...,
        "suggestions": ...
    }
```

#### tools/web_search.py - Web搜索工具

**核心类**：`WebSearchTool`

**主要方法**：
```python
def search(self, query: str) -> List[Dict[str, str]]:
    """
    执行搜索
    
    Returns:
        [
            {
                "title": "标题",
                "url": "链接",
                "snippet": "摘要"
            },
            ...
        ]
    """
```

**扩展示例**：添加Google搜索支持
```python
from googlesearch import search as google_search

class WebSearchTool:
    def _google_search(self, query: str) -> List[Dict[str, str]]:
        """Google搜索实现"""
        results = []
        for url in google_search(query, num_results=self.max_results):
            # 获取页面内容
            results.append({
                "title": ...,
                "url": url,
                "snippet": ...
            })
        return results
```

---

### 3. UI层 (web_ui.py)

**核心结构**：
```python
# 全局变量
resume_loader: Optional[ResumeLoader] = None
resume_evaluator: Optional[ResumeEvaluator] = None
interview_agent: Optional[InterviewAgent] = None
current_resume_content: Optional[str] = None

# 初始化函数
def initialize_components():
    """初始化系统组件"""

# 功能函数
def upload_resume(file) -> str:
    """上传简历"""

def evaluate_resume(position: str, requirements: str) -> str:
    """评估简历"""

def analyze_job_position(job_input: str, question_count: int) -> str:
    """岗位解读"""

def start_interview(interview_type: str, enable_web: bool) -> List:
    """开始面试"""

def chat_with_interviewer(message: str, history: List, 
                          enable_web: bool) -> Tuple[str, List]:
    """面试对话"""

# UI创建函数
def create_ui():
    """创建Gradio UI"""
```

**扩展示例**：添加新的Tab页
```python
def create_ui():
    with gr.Blocks() as app:
        # 现有Tab页...
        
        # 新增Tab页
        with gr.Tab("🆕 新功能"):
            gr.Markdown("## 新功能说明")
            
            with gr.Row():
                input_box = gr.Textbox(label="输入")
                output_box = gr.Markdown(value="输出")
            
            submit_btn = gr.Button("提交")
            
            # 绑定事件
            submit_btn.click(
                fn=your_new_function,
                inputs=[input_box],
                outputs=[output_box]
            )
    
    return app
```

---

## 扩展开发

### 1. 添加新的评估维度

**步骤**：

1. **修改Prompt模板** (`config/prompts.py`)
```python
RESUME_EVALUATION = """
...现有维度...

7. **你的新维度**（0-10分）
   评估标准...
"""
```

2. **无需修改代码**，Prompt变更会自动生效

### 2. 添加新的面试类型

**步骤**：

1. **添加Prompt模板** (`config/prompts.py`)
```python
class PromptTemplates:
    INTERVIEW_NEW_TYPE = """你是一位XX面试官..."""

class PromptManager:
    @staticmethod
    def get_interview_prompt_new_type(resume_summary: str) -> str:
        return PromptTemplates.INTERVIEW_NEW_TYPE.format(
            resume_summary=resume_summary
        )
```

2. **修改面试Agent** (`src/interview/interview_agent.py`)
```python
def _build_system_prompt(self) -> str:
    if self.interview_type == "new_type":
        return PromptManager.get_interview_prompt_new_type(
            self._extract_resume_summary()
        )
    # 现有代码...
```

3. **修改UI** (`web_ui.py`)
```python
interview_type = gr.Radio(
    choices=[
        ("技术面试", "technical"),
        ("行为面试", "behavioral"),
        ("综合面试", "comprehensive"),
        ("新类型面试", "new_type"),  # 添加
    ]
)
```

### 3. 集成新的LLM服务商

**步骤**：

1. **修改配置** (`config/llm_config.py`)
```python
def get_llm_client() -> Tuple[OpenAI, str, float]:
    # 读取配置
    api_base = os.getenv("LLM_API_BASE")
    
    # 添加新服务商判断
    if "new-llm-service.com" in api_base:
        client = OpenAI(
            api_key=api_key,
            base_url=api_base,
            # 新服务商特定配置
            timeout=60.0,
            max_retries=3,
        )
    
    return client, model, temperature
```

2. **更新环境变量模板** (`.env.example`)
```ini
# 新LLM服务商
LLM_API_KEY=your-api-key
LLM_API_BASE=https://api.new-llm-service.com/v1
LLM_MODEL=new-model-name
```

### 4. 添加简历导出功能

**实现示例**：
```python
# 在 web_ui.py 中添加
def export_evaluation_report(evaluation_result: str) -> str:
    """导出评估报告为PDF"""
    import markdown
    from weasyprint import HTML
    
    # Markdown转HTML
    html_content = markdown.markdown(evaluation_result)
    
    # HTML转PDF
    output_path = f"output/evaluation_{int(time.time())}.pdf"
    HTML(string=html_content).write_pdf(output_path)
    
    return output_path

# UI中添加导出按钮
export_btn = gr.Button("📥 导出PDF")
export_btn.click(
    fn=export_evaluation_report,
    inputs=[evaluation_output],
    outputs=[gr.File()]
)
```

---

## 调试与测试

### 日志系统

**配置日志级别** (`.env`)
```ini
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

**日志位置**
- 日志文件：`logs/app_{日期}.log`
- 控制台输出：实时显示

**关键日志点**：
```python
from loguru import logger

# 功能入口
logger.info("开始XXX功能...")

# LLM调用（已内置）
logger.info(f"[LLM API] XXX - Prompt:\n{prompt}")

# 错误处理
logger.error(f"XXX失败: {e}")

# 调试信息
logger.debug(f"中间结果: {data}")
```

### 单元测试

**测试结构**：
```
tests/
├── test_loaders.py
├── test_evaluator.py
├── test_interview.py
└── test_tools.py
```

**编写测试**：
```python
# tests/test_evaluator.py
import pytest
from src.evaluator import ResumeEvaluator

def test_quick_score():
    evaluator = ResumeEvaluator()
    resume = "测试简历内容..."
    
    result = evaluator.quick_score(resume)
    
    assert "score_text" in result
    assert "metadata" in result
    assert result["metadata"]["elapsed_time"] > 0
```

**运行测试**：
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_evaluator.py

# 显示详细输出
pytest -v

# 生成覆盖率报告
pytest --cov=src tests/
```

### 调试技巧

1. **Prompt调试**
   - 所有LLM调用都会打印Prompt日志
   - 设置 `LOG_LEVEL=INFO` 查看完整Prompt
   - 复制Prompt到LLM平台测试

2. **断点调试**
   - VS Code: 添加断点后按F5启动调试
   - PyCharm: 右键 -> Debug 'web_ui'

3. **Gradio调试**
   - 在 `web_ui.py` 的 `launch()` 中添加 `debug=True`
   - 查看浏览器控制台的网络请求

---

## 部署指南

### 本地部署

参考[快速开始](#快速开始)部分。

### Docker部署

1. **创建Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7861

CMD ["python", "web_ui.py"]
```

2. **构建镜像**
```bash
docker build -t interview-coach .
```

3. **运行容器**
```bash
docker run -d \
  -p 7861:7861 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  --name interview-coach \
  interview-coach
```

### 云服务器部署

1. **使用systemd服务**

创建 `/etc/systemd/system/interview-coach.service`：
```ini
[Unit]
Description=AI Interview Coach
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/interview-coach
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python web_ui.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable interview-coach
sudo systemctl start interview-coach
sudo systemctl status interview-coach
```

2. **使用Nginx反向代理**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:7861;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 性能优化

1. **API调用优化**
   - 使用更快的模型（如GPT-3.5-turbo）
   - 减少temperature降低随机性
   - 限制max_tokens减少响应时间

2. **缓存优化**
   - 缓存常用的评估结果
   - 使用Redis缓存Prompt结果

3. **并发处理**
   - Gradio默认支持多用户并发
   - 注意LLM API的并发限制

---

## 常见问题

### Q1: 如何修改UI端口？

**A**: 修改 `web_ui.py` 中的 `launch()` 参数：
```python
app.launch(
    server_name="127.0.0.1",
    server_port=7862,  # 修改端口
    share=False,
)
```

### Q2: 如何添加用户认证？

**A**: Gradio支持认证：
```python
app.launch(
    server_name="127.0.0.1",
    server_port=7861,
    auth=("username", "password"),  # 添加认证
)
```

### Q3: 如何优化LLM响应速度？

**A**: 
- 使用更快的模型
- 减少Prompt长度
- 使用streaming模式（需修改代码）
- 增加API并发限制

### Q4: 如何支持多语言？

**A**: 修改Prompt模板，添加语言参数：
```python
def get_resume_evaluation_prompt(resume_content, language="zh"):
    if language == "en":
        prompt = """You are a senior HR..."""
    else:
        prompt = """你是一位资深HR..."""
    return prompt
```

### Q5: 如何监控系统运行状态？

**A**: 
- 查看日志文件：`tail -f logs/app_*.log`
- 添加监控接口（需开发）
- 使用系统监控工具（如Prometheus）

---

## 代码规范

### Python代码规范

遵循 PEP 8 规范：

```python
# 命名规范
class ResumeEvaluator:  # 类名：大驼峰
    def evaluate_resume(self):  # 函数名：小写+下划线
        max_score = 100  # 变量名：小写+下划线
        API_KEY = "xxx"  # 常量：大写+下划线

# 注释规范
def process_data(data: List[str]) -> Dict[str, Any]:
    """
    处理数据的简短描述
    
    Args:
        data: 输入数据说明
        
    Returns:
        返回值说明
        
    Raises:
        ValueError: 异常情况说明
    """
    pass

# 类型注解
from typing import Optional, List, Dict, Any

def func(param: str) -> Optional[Dict[str, Any]]:
    pass
```

### 格式化工具

```bash
# 使用black格式化
black web_ui.py

# 使用flake8检查
flake8 web_ui.py

# 使用mypy类型检查
mypy web_ui.py
```

---

## 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

---

## 技术支持

- 📧 Email: support@example.com
- 💬 Discussion: GitHub Discussions
- 🐛 Bug Report: GitHub Issues

---

祝开发顺利！如有问题欢迎反馈。
