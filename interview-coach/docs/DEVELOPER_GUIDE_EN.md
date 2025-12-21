# Developer Guide

For developers, covering secondary development, feature extensions, and system customization.

## 📋 Contents

- [Environment Setup](#environment-setup)
- [Architecture Overview](#architecture-overview)
- [Core Modules](#core-modules)
- [Extension Development](#extension-development)
- [Testing & Debugging](#testing--debugging)
- [Deployment Guide](#deployment-guide)

---

## Environment Setup

### Requirements

- Python 3.9+
- pip 20.0+
- Git

### Development Setup

```bash
# 1. Clone and enter project
git clone https://github.com/pengshuang/Awesome-Agent-Projects.git
cd Awesome-Agent-Projects/interview-coach

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development tools (optional)
pip install pytest black isort mypy flake8

# 5. Configure environment
cp .env.example .env
# Edit .env, fill in API keys
```

---

## Architecture Overview

### Directory Structure

```
interview-coach/
├── config/              # Configuration management
│   ├── llm_config.py   # LLM client
│   ├── prompts.py      # Prompt templates
│   └── settings.py     # Pydantic Settings
│
├── src/
│   ├── models/         # Pydantic data models
│   │   ├── resume.py
│   │   ├── evaluation.py
│   │   └── interview.py
│   ├── loaders/        # Resume loaders
│   ├── evaluator/      # Evaluation engine
│   ├── interview/      # Interview agent
│   ├── tools/          # Tool modules
│   ├── utils/          # Utilities
│   └── exceptions.py   # Exception definitions
│
├── tests/              # Tests
├── web_ui.py          # Gradio UI
└── quick_start.py     # CLI example
```

### Architecture Principles

1. **Modular**: Single responsibility, low coupling
2. **Type Safe**: Pydantic v2 data validation
3. **Config-Driven**: Centralized configuration management
4. **Extensible**: Reserved extension interfaces
5. **Testable**: Complete test coverage

---

## Core Modules

### 1. Data Models (src/models/)

Using **Pydantic v2** for type-safe data models.

#### resume.py - Resume Data

```python
from pydantic import BaseModel, Field, computed_field

class ResumeMetadata(BaseModel):
    """Resume metadata"""
    filename: str
    file_size: int
    page_count: int = 0
    
    @computed_field
    @property
    def file_size_mb(self) -> float:
        return round(self.file_size / (1024 * 1024), 2)

class ResumeData(BaseModel):
    """Complete resume data"""
    content: str = Field(..., description="Resume text content")
    metadata: ResumeMetadata
    
    @computed_field
    @property
    def word_count(self) -> int:
        return len(self.content)
```

**Extension Example**: Add new fields
```python
class ResumeData(BaseModel):
    # New field
    parsed_sections: dict[str, str] = Field(
        default_factory=dict,
        description="Parsed resume sections"
    )
```

#### evaluation.py - Evaluation Results

```python
class ScoreDetails(BaseModel):
    """Score details"""
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

#### interview.py - Interview Session

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

### 2. Configuration Management (config/settings.py)

Using **Pydantic Settings** for configuration management.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class SystemConfig(BaseSettings):
    """System config - auto-loads from environment variables"""
    
    # LLM config
    llm_api_key: str = Field(..., description="LLM API key")
    llm_api_base: str = Field(
        default="https://api.openai.com/v1",
        description="API endpoint"
    )
    llm_model: str = Field(
        default="gpt-3.5-turbo",
        description="Model name"
    )
    
    # Path config
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

# Singleton pattern
_config_instance = None

def get_config() -> SystemConfig:
    global _config_instance
    if _config_instance is None:
        _config_instance = SystemConfig()
    return _config_instance
```

### 3. Exception Handling (src/exceptions.py)

```python
class InterviewCoachException(Exception):
    """Base exception"""
    pass

class ResumeLoadError(InterviewCoachException):
    """Resume loading failed"""
    pass

class LLMAPIError(InterviewCoachException):
    """LLM API call failed"""
    pass

class EvaluationError(InterviewCoachException):
    """Evaluation processing failed"""
    pass
```

### 4. Resume Loader (src/loaders/)

```python
import fitz  # PyMuPDF
from src.models.resume import ResumeData, ResumeMetadata
from src.exceptions import ResumeLoadError

class ResumeLoader:
    def load_pdf(self, file_path: str) -> ResumeData:
        """Load PDF resume"""
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
            raise ResumeLoadError(f"Loading failed: {e}")
```

### 5. Evaluation Engine (src/evaluator/)

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
        """Evaluate resume"""
        try:
            prompt = self._build_prompt(
                resume, job_title, job_requirements
            )
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return self._parse_result(response)
        except Exception as e:
            raise EvaluationError(f"Evaluation failed: {e}")
```

### 6. Interview Agent (src/interview/)

```python
class InterviewAgent:
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model
        self.session = InterviewSession()
    
    def start_interview(
        self,
        resume: ResumeData,
        interview_type: InterviewType
    ) -> str:
        """Start interview"""
        system_prompt = self._get_system_prompt(
            interview_type, resume
        )
        self.session.messages.append(
            InterviewMessage(role=MessageRole.SYSTEM, content=system_prompt)
        )
        return self._generate_opening()
    
    def chat(self, user_message: str) -> str:
        """Continue conversation"""
        self.session.messages.append(
            InterviewMessage(role=MessageRole.USER, content=user_message)
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[m.model_dump() for m in self.session.messages]
        )
        
        assistant_message = response.choices[0].message.content
        self.session.messages.append(
            InterviewMessage(role=MessageRole.ASSISTANT, content=assistant_message)
        )
        
        return assistant_message
```

---

## Extension Development

### Custom Prompts

Edit `config/prompts.py`:

```python
CUSTOM_EVALUATION_PROMPT = """
You are a professional HR consultant...
[Your custom prompt]
"""
```

### Add New Evaluation Dimensions

```python
class ScoreDetails(BaseModel):
    # Existing dimensions
    basic_info: int
    # ... other dimensions
    
    # New dimension
    leadership: int = Field(ge=0, le=10, description="Leadership skills")
```

### Integrate New LLM Provider

```python
from typing import Protocol

class LLMClient(Protocol):
    def chat(self, messages: list[dict]) -> str:
        ...

class CustomLLMClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def chat(self, messages: list[dict]) -> str:
        # Implement your LLM call logic
        pass
```

### Add Web Search Tool

```python
from duckduckgo_search import DDGS

class WebSearchTool:
    def search(self, query: str, max_results: int = 3) -> list[dict]:
        """Search web"""
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
```

---

## Testing & Debugging

### Run Tests

```bash
# All tests
pytest tests/

# Specific test
pytest tests/test_loader.py

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Write Tests

```python
import pytest
from src.loaders import ResumeLoader
from src.exceptions import ResumeLoadError

def test_load_valid_pdf():
    loader = ResumeLoader()
    resume = loader.load_pdf("tests/fixtures/sample_resume.pdf")
    assert resume.content
    assert resume.metadata.page_count > 0

def test_load_invalid_file():
    loader = ResumeLoader()
    with pytest.raises(ResumeLoadError):
        loader.load_pdf("invalid.pdf")
```

### Debugging Tips

1. **Enable Debug Logging**
```python
from src.utils.logger import setup_logger
logger = setup_logger(level="DEBUG")
```

2. **Validate Data Models**
```python
try:
    resume = ResumeData(**data)
except ValidationError as e:
    print(e.json())
```

3. **Use Type Checker**
```bash
mypy src/
```

---

## Deployment Guide

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "web_ui.py"]
```

### Build and Run

```bash
docker build -t interview-coach .
docker run -p 7861:7861 -v $(pwd)/data:/app/data interview-coach
```

### Environment Variables

Production environment:

```bash
export LLM_API_KEY=your-key
export LLM_MODEL=gpt-4
export LOG_LEVEL=INFO
```

### Performance Optimization

1. **Enable Caching**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(param):
    ...
```

2. **Async Processing**
```python
import asyncio

async def async_evaluate(resume):
    ...
```

3. **Connection Pooling**
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    max_retries=3,
    timeout=30.0
)
```

---

## Development Standards

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings

```python
def function_name(param: str) -> int:
    """
    Function description
    
    Args:
        param: Parameter description
        
    Returns:
        Return value description
    """
    pass
```

### Git Workflow

```bash
# 1. Create branch
git checkout -b feature/new-feature

# 2. Develop and test

# 3. Commit
git commit -m "Add: feature description"

# 4. Push
git push origin feature/new-feature

# 5. Create Pull Request
```

### Commit Convention

- `Add:` New feature
- `Fix:` Bug fix
- `Update:` Feature update
- `Refactor:` Code refactoring
- `Docs:` Documentation update
- `Test:` Add tests

---

## Resources

- 📚 [Pydantic Documentation](https://docs.pydantic.dev/)
- 📚 [OpenAI API Reference](https://platform.openai.com/docs)
- 📚 [Gradio Documentation](https://www.gradio.app/docs/)
- 🐛 [Report Issues](https://github.com/your-repo/issues)

---

**Last Updated:** 2025-12-21
