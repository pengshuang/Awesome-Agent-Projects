# Pydantic Data Validation Guide

This project uses Pydantic v2 for data validation and configuration management.

## Quick Start

Already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Core Models

### 1. Resume Models

```python
from src.models.resume import ResumeData, ResumeMetadata

# Resume with auto-validation
resume = ResumeData(
    content="Resume text content...",
    metadata=ResumeMetadata(
        filename="resume.pdf",
        file_size=1024000,
        page_count=2
    )
)

# Auto-computed properties
print(resume.word_count)              # Computed field
print(resume.metadata.file_size_mb)   # 1.0 MB
```

### 2. Evaluation Models

```python
from src.models.evaluation import ScoreDetails, EvaluationResult

# Score with validation (0-10 range)
scores = ScoreDetails(
    basic_info=8,
    work_experience=9,
    project_quality=7,
    skills_match=8,
    education=9,
    overall_impression=8
)

# Auto-computed total score
print(scores.total_score)  # 81.7 (out of 100)
```

### 3. Interview Session

```python
from src.models.interview import InterviewSession, InterviewType, MessageRole

session = InterviewSession(
    interview_type=InterviewType.TECHNICAL
)

# Add messages with auto-timestamp
session.messages.append(InterviewMessage(
    role=MessageRole.USER,
    content="Tell me about your experience"
))
```

## Main Features

### Automatic Validation

```python
from pydantic import ValidationError

try:
    # Invalid score (must be 0-10)
    scores = ScoreDetails(basic_info=15)
except ValidationError as e:
    print(e.errors())
```

### Type Safety

```python
# IDE provides full type hints
resume: ResumeData = loader.load_pdf("resume.pdf")
content: str = resume.content
page_count: int = resume.metadata.page_count
```

### Serialization

```python
# Export to dict/JSON
resume_dict = resume.model_dump()
resume_json = resume.model_dump_json(indent=2)

# Load from dict/JSON
resume = ResumeData.model_validate(resume_dict)
resume = ResumeData.model_validate_json(resume_json)
```

## Configuration Management

### System Settings

```python
from config.settings import SystemConfig

# Auto-loads from .env with validation
config = SystemConfig()

# Type-safe access
api_key: str = config.llm_api_key
model: str = config.llm_model
temperature: float = config.temperature  # Validated [0.0, 2.0]
```

### Environment Variables

`.env` file:

```bash
LLM_API_KEY=sk-your-key
LLM_MODEL=gpt-3.5-turbo
LLM_API_BASE=https://api.openai.com/v1
TEMPERATURE=0.7
```

## Best Practices

### Use Type Hints

```python
from src.models.evaluation import EvaluationResult

def evaluate_resume(resume: ResumeData) -> EvaluationResult:
    # IDE knows all types
    return EvaluationResult(...)
```

### Error Handling

```python
from pydantic import ValidationError

try:
    resume = ResumeData(content="", metadata=metadata)
except ValidationError as e:
    for error in e.errors():
        field = error['loc'][0]
        message = error['msg']
        print(f"Error in {field}: {message}")
```

### Custom Validation

```python
from pydantic import BaseModel, field_validator

class CustomModel(BaseModel):
    score: int
    
    @field_validator('score')
    @classmethod
    def validate_score(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Score must be 0-100')
        return v
```

## Reference

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Developer Guide](DEVELOPER_GUIDE_EN.md)
- [User Guide](USER_GUIDE_EN.md)
