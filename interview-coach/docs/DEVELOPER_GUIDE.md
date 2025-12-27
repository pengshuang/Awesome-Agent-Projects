# 开发指南

> 📘 **面向人群**：开发者、贡献者  
> 📌 **文档目的**：二次开发、模块扩展、代码说明

---

## 📋 快速导航

- [开发环境](#开发环境搭建) - 环境配置与依赖安装
- [项目结构](#项目结构) - 目录组织与模块说明
- [核心模块](#核心模块详解) - 代码实现详解
- [扩展开发](#扩展指南) - 自定义功能开发
- [测试调试](#测试与调试) - 单元测试与调试技巧
- [部署上线](#部署指南) - 生产环境部署方案

---

## 开发环境搭建

### 系统要求

| 项目 | 要求 |
|------|------|
| **操作系统** | macOS / Linux / Windows (WSL2) |
| **Python** | 3.10+ |
| **内存** | 最小 4GB，推荐 8GB+ |
| **磁盘** | 500MB+ |

### 快速开始

\`\`\`bash
# 1. 克隆项目
git clone https://github.com/pengshuang/Awesome-Agent-Projects.git
cd Awesome-Agent-Projects/interview-coach

# 2. 创建虚拟环境（推荐 conda）
conda create -n interview-coach python=3.10
conda activate interview-coach

# 3. 安装依赖
pip install -r requirements.txt        # 生产依赖
pip install -r requirements-dev.txt    # 开发工具

# 4. 配置环境
cp .env.example .env
# 编辑 .env 填写 LLM_API_KEY 等配置

# 5. 验证安装
pytest -v                              # 运行测试
python web_ui.py                       # 启动应用
\`\`\`

### 开发工具配置

**推荐 VS Code 插件**：
- Python (Pylance)
- Black Formatter
- isort
- GitLens

**代码质量工具**：
\`\`\`bash
# 代码格式化
black .
isort .

# 代码检查
flake8 src/ tests/
mypy src/

# 运行测试
pytest --cov=src --cov-report=html
\`\`\`

---

## 项目结构

\`\`\`
interview-coach/
├── config/                 # 配置管理
│   ├── settings.py        # SystemConfig (Pydantic Settings)
│   ├── llm_config.py      # LLM 客户端工厂
│   └── prompts.py         # Prompt 模板管理
│
├── src/                    # 核心业务逻辑
│   ├── models/            # Pydantic 数据模型
│   │   ├── resume.py      # 简历数据模型
│   │   ├── evaluation.py  # 评估结果模型
│   │   └── interview.py   # 面试会话模型
│   │
│   ├── loaders/           # 文件加载器
│   │   └── resume_loader.py  # PDF 解析
│   │
│   ├── evaluator/         # 简历评估引擎
│   │   └── resume_evaluator.py
│   │
│   ├── interview/         # 面试代理
│   │   └── interview_agent.py
│   │
│   ├── tools/             # 外部工具
│   │   └── web_search.py  # DuckDuckGo 搜索
│   │
│   └── utils/             # 通用工具
│       ├── logger.py      # Loguru 日志
│       └── helpers.py     # 辅助函数
│
├── tests/                 # 单元测试
├── docs/                  # 文档
├── web_ui.py              # Gradio UI 入口
└── requirements.txt       # 依赖清单
\`\`\`

### 模块职责划分

| 模块 | 职责 | 核心类/函数 |
|------|------|------------|
| `config` | 配置管理 | `SystemConfig`, `get_config()` |
| `src/models` | 数据建模 | `ResumeData`, `EvaluationResult` |
| `src/loaders` | 文件解析 | `ResumeLoader` |
| `src/evaluator` | 简历评估 | `ResumeEvaluator` |
| `src/interview` | 面试对话 | `InterviewAgent` |
| `src/tools` | 外部工具 | `WebSearchTool` |

---

## 核心模块详解

### 1. 配置管理 (config/)

#### SystemConfig - 配置类

使用 **Pydantic Settings** 实现类型安全配置，自动从 `.env` 加载。

\`\`\`python
# config/settings.py
from pydantic import Field
from pydantic_settings import BaseSettings

class SystemConfig(BaseSettings):
    \"\"\"系统配置\"\"\"
    model_config = SettingsConfigDict(env_file=".env")
    
    # LLM 配置
    llm_api_key: str = Field(..., alias="LLM_API_KEY")
    llm_api_base: str = Field(default="https://api.openai.com/v1")
    llm_model: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    
    # 面试配置
    max_history_turns: int = Field(default=20, ge=1, le=100)
    
# 单例模式
def get_config() -> SystemConfig:
    global _config
    if _config is None:
        _config = SystemConfig()
    return _config
\`\`\`

**扩展配置**：在 `SystemConfig` 类中添加新字段即可。

#### LLM 客户端工厂

\`\`\`python
# config/llm_config.py
from openai import OpenAI

def get_llm_client(api_key: str, api_base: str, model: str, temperature: float):
    client = OpenAI(api_key=api_key, base_url=api_base)
    return client, model, temperature
\`\`\`

---

### 2. 数据模型 (src/models/)

#### resume.py - 简历数据

\`\`\`python
from pydantic import BaseModel, Field, field_validator

class ResumeMetadata(BaseModel):
    \"\"\"简历元数据\"\"\"
    file_name: str
    file_size: int = Field(ge=0)
    content_length: int = Field(ge=0)
    load_time: float = Field(ge=0)
    
    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        if v > 100 * 1024 * 1024:  # 100MB
            raise ValueError("文件不能超过 100MB")
        return v

class ResumeData(BaseModel):
    \"\"\"简历完整数据\"\"\"
    content: str = Field(min_length=1)
    metadata: ResumeMetadata
\`\`\`

**扩展示例**：添加章节解析
\`\`\`python
class ResumeData(BaseModel):
    content: str
    metadata: ResumeMetadata
    parsed_sections: dict[str, str] = Field(default_factory=dict)  # 新增
\`\`\`

#### evaluation.py - 评估结果

\`\`\`python
class ScoreDetails(BaseModel):
    \"\"\"6 维度评分\"\"\"
    basic_info: int = Field(ge=0, le=10)
    work_experience: int = Field(ge=0, le=10)
    project_quality: int = Field(ge=0, le=10)
    skills_match: int = Field(ge=0, le=10)
    education: int = Field(ge=0, le=10)
    overall_impression: int = Field(ge=0, le=10)
    
    def get_total_score(self) -> float:
        \"\"\"总分（0-100）\"\"\"
        scores = [self.basic_info, self.work_experience, ...]
        return round(sum(scores) / len(scores) * 10, 1)
\`\`\`

---

### 3. 简历加载器 (src/loaders/)

#### ResumeLoader - PDF 解析

\`\`\`python
import pymupdf
from pathlib import Path
from src.models.resume import ResumeData, ResumeMetadata

class ResumeLoader:
    SUPPORTED_FORMATS = [".pdf"]
    
    def load_resume(self, file_path: str) -> ResumeData:
        \"\"\"加载简历\"\"\"
        path_obj = Path(file_path)
        
        # 验证文件
        if not path_obj.exists():
            raise FileNotFoundError(file_path)
        if path_obj.suffix not in self.SUPPORTED_FORMATS:
            raise UnsupportedFileFormatError(path_obj.suffix)
        
        # 解析 PDF
        content = self._load_pdf_pymupdf(path_obj)
        
        # 构建元数据
        metadata = ResumeMetadata(
            file_name=path_obj.name,
            file_size=path_obj.stat().st_size,
            content_length=len(content),
            load_time=elapsed_time,
        )
        
        return ResumeData(content=content, metadata=metadata)
    
    def _load_pdf_pymupdf(self, file_path: Path) -> str:
        \"\"\"使用 PyMuPDF 解析\"\"\"
        text_content = []
        with pymupdf.open(file_path) as doc:
            for page in doc:
                text_content.append(page.get_text())
        return "\\n\\n".join(text_content)
\`\`\`

**扩展支持 Word**：
\`\`\`python
import docx

def _load_docx(self, file_path: Path) -> str:
    doc = docx.Document(file_path)
    return "\\n\\n".join([p.text for p in doc.paragraphs if p.text.strip()])
\`\`\`

---

### 4. 简历评估器 (src/evaluator/)

#### ResumeEvaluator - 评估引擎

\`\`\`python
from config import get_config, get_llm_client
from config.prompts import PromptTemplates

class ResumeEvaluator:
    def __init__(self):
        config = get_config()
        self.client, self.model, self.temperature = get_llm_client(
            api_key=config.llm_api_key,
            api_base=config.llm_api_base,
            model=config.llm_model,
            temperature=config.temperature,
        )
    
    def evaluate(self, resume_content: str, position: str = None) -> dict:
        \"\"\"完整评估\"\"\"
        # 构建 Prompt
        prompt = PromptTemplates.get_evaluation_prompt(
            resume_content=resume_content,
            position=position or "通用岗位",
        )
        
        # 调用 LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )
        
        return {
            "evaluation": response.choices[0].message.content,
            "metadata": {"model": self.model}
        }
\`\`\`

---

### 5. 面试代理 (src/interview/)

#### InterviewAgent - 对话管理

\`\`\`python
class InterviewAgent:
    def __init__(self, resume_content: str, interview_type: str, max_history_turns: int):
        config = get_config()
        self.client, self.model, self.temperature = get_llm_client(...)
        self.chat_history = []
        self.max_history_turns = max_history_turns
    
    def start_interview(self) -> dict:
        \"\"\"生成开场白\"\"\"
        prompt = f"{self.system_prompt}\\n\\n请给出开场白并提出第一个问题。"
        response = self.client.chat.completions.create(...)
        opening = response.choices[0].message.content
        self.chat_history.append({"role": "assistant", "content": opening})
        return {"opening": opening}
    
    def chat(self, user_message: str) -> dict:
        \"\"\"处理用户消息\"\"\"
        self.chat_history.append({"role": "user", "content": user_message})
        
        # 构建消息（保留最近 N 轮）
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.chat_history[-self.max_history_turns:])
        
        # 调用 LLM
        response = self.client.chat.completions.create(...)
        assistant_message = response.choices[0].message.content
        
        self.chat_history.append({"role": "assistant", "content": assistant_message})
        return {"response": assistant_message}
\`\`\`

---

## 扩展指南

### 1. 添加新的 LLM 提供商

**需求**：支持 Anthropic Claude

**步骤**：
1. 在 `config/llm_config.py` 添加客户端工厂
2. 更新 `SystemConfig` 添加配置项
3. 更新 `.env.example`

\`\`\`python
# config/llm_config.py
def get_claude_client(api_key: str, model: str = "claude-3-opus"):
    from anthropic import Anthropic
    client = Anthropic(api_key=api_key)
    return client, model, 0.7

# config/settings.py
class SystemConfig(BaseSettings):
    llm_provider: Literal["openai", "claude"] = "openai"
    claude_api_key: Optional[str] = None
\`\`\`

### 2. 自定义评估维度

**需求**：添加"创新能力"评分维度

\`\`\`python
# src/models/evaluation.py
class ScoreDetails(BaseModel):
    basic_info: int = Field(ge=0, le=10)
    # ... 其他维度
    innovation: int = Field(ge=0, le=10, description="创新能力")  # 新增
    
    def get_total_score(self) -> float:
        scores = [self.basic_info, ..., self.innovation]  # 包含新维度
        return round(sum(scores) / len(scores) * 10, 1)

# config/prompts.py
RESUME_EVALUATION = \"\"\"
请从以下7个维度评分：
1. 基本信息完整性
...
7. 创新能力  # 新增
\"\"\"
\`\`\`

### 3. 添加新工具模块

**需求**：简历关键词提取

\`\`\`python
# src/tools/keyword_extractor.py
import jieba

class KeywordExtractor:
    def __init__(self, top_k: int = 20):
        self.top_k = top_k
    
    def extract(self, text: str) -> list[str]:
        words = jieba.cut(text)
        # 实现 TF-IDF 算法
        return list(words)[:self.top_k]

# src/tools/__init__.py
from .keyword_extractor import KeywordExtractor
__all__ = ["WebSearchTool", "KeywordExtractor"]
\`\`\`

---

## 测试与调试

### 单元测试

\`\`\`bash
# 运行所有测试
pytest

# 测试特定模块
pytest tests/test_loader.py

# 显示详细输出
pytest -v -s

# 代码覆盖率
pytest --cov=src --cov-report=html
\`\`\`

### 编写测试用例

\`\`\`python
# tests/test_loader.py
import pytest
from src.loaders import ResumeLoader

@pytest.fixture
def loader():
    return ResumeLoader()

def test_load_pdf(loader, sample_pdf_path):
    result = loader.load_resume(sample_pdf_path)
    assert result.content
    assert result.metadata.file_size > 0

def test_load_nonexistent_file(loader):
    with pytest.raises(FileNotFoundError):
        loader.load_resume("nonexistent.pdf")
\`\`\`

### 调试技巧

**1. 日志调试**：
\`\`\`python
from loguru import logger
logger.debug("调试信息: {}", variable)
logger.info("正常信息")
\`\`\`

**2. IPython 断点**：
\`\`\`python
from IPython import embed
embed()  # 在此处暂停，进入交互式 shell
\`\`\`

**3. VS Code 调试配置**：
\`\`\`json
// .vscode/launch.json
{
    "configurations": [
        {
            "name": "Python: Web UI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/web_ui.py"
        }
    ]
}
\`\`\`

---

## 部署指南

### 本地部署

\`\`\`bash
python web_ui.py
# 或
./start.sh
\`\`\`

### Docker 部署

\`\`\`dockerfile
# Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["python", "web_ui.py"]
\`\`\`

\`\`\`bash
docker build -t interview-coach .
docker run -p 7860:7860 --env-file .env interview-coach
\`\`\`

### 生产环境部署

**使用 Gunicorn**：
\`\`\`bash
pip install gunicorn uvicorn
gunicorn web_ui:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:7860
\`\`\`

**Nginx 反向代理**：
\`\`\`nginx
server {
    listen 80;
    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
\`\`\`

---

## 贡献规范

### 代码风格

\`\`\`bash
# 格式化代码
black .
isort .

# 代码检查
flake8 src/ tests/
mypy src/
\`\`\`

### Commit Message 规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**：
\`\`\`
feat: add Word document support
fix: handle empty PDF files
docs: update developer guide
\`\`\`

### Pull Request 检查清单

- [ ] 代码已格式化（Black + isort）
- [ ] 通过所有测试（pytest）
- [ ] 添加必要的测试用例
- [ ] 更新相关文档
- [ ] Commit message 符合规范

---

## 常见问题

**Q: Pydantic 与 Gradio 兼容性问题？**  
A: 在 `gr.Blocks()` 中设置 `show_api=False`，或将 computed_field 改为普通方法。

**Q: 如何调试 LLM API 调用？**  
A: 在调用前后添加 logger.info() 打印 Prompt 和 Response。

**Q: 如何优化 LLM 响应速度？**  
A: 使用更快的模型、实现缓存、异步处理、流式输出。

---

**文档版本**: v1.0  
**最后更新**: 2025-12-27  
**相关文档**: [用户指南](USER_GUIDE.md) | [架构文档](../ARCHITECTURE.md)
