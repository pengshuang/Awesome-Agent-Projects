# AI 模拟面试系统 - 开发指南

本指南面向开发者，介绍如何进行二次开发、功能扩展和系统定制。

## 📋 目录

- [开发环境搭建](#开发环境搭建)
- [项目架构](#项目架构)
- [核心模块详解](#核心模块详解)
- [扩展开发](#扩展开发)
- [调试与测试](#调试与测试)
- [部署指南](#部署指南)
- [常见问题](#常见问题)

---

## 开发环境搭建

### 环境要求

- Python 3.9+
- pip 20.0+
- Git
- 代码编辑器（推荐 VS Code）

### 开发环境配置

1. **克隆项目**
```bash
git clone https://github.com/yourusername/interview-coach.git
cd interview-coach
```

2. **创建虚拟环境**（推荐）
```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 或使用 conda
conda create -n interview-coach python=3.9
conda activate interview-coach
```

3. **安装依赖**
```bash
# 安装核心依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install pytest black flake8 mypy
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填写开发用的API密钥
```

5. **验证安装**
```bash
python -c "import gradio; import openai; print('Environment OK')"
```

---

## 项目架构

### 整体架构

```
interview-coach/
├── config/                    # 配置层
│   ├── __init__.py
│   ├── llm_config.py         # LLM客户端配置
│   ├── prompts.py            # Prompt模板管理
│   └── settings.py           # 系统配置
│
├── src/                       # 业务逻辑层
│   ├── __init__.py
│   ├── constants.py          # 常量定义
│   │
│   ├── loaders/              # 数据加载模块
│   │   ├── __init__.py
│   │   └── resume_loader.py
│   │
│   ├── evaluator/            # 评估模块
│   │   ├── __init__.py
│   │   └── resume_evaluator.py
│   │
│   ├── interview/            # 面试模块
│   │   ├── __init__.py
│   │   └── interview_agent.py
│   │
│   ├── tools/                # 工具模块
│   │   ├── __init__.py
│   │   └── web_search.py
│   │
│   └── utils/                # 工具函数
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
│
├── data/                      # 数据层
│   ├── resumes/              # 简历存储
│   └── cache/                # 缓存文件
│
├── logs/                      # 日志文件
├── docs/                      # 文档
│
├── web_ui.py                 # UI层（Gradio）
├── init_system.py            # 系统初始化
└── requirements.txt          # 依赖管理
```

### 架构设计原则

1. **模块化**：每个模块职责单一，低耦合
2. **配置驱动**：核心配置集中管理，易于修改
3. **可扩展**：预留扩展接口，方便添加新功能
4. **简洁性**：直接使用OpenAI SDK，不引入复杂框架
5. **可维护**：完善的日志和错误处理

---

## 核心模块详解

### 1. 配置模块 (config/)

#### llm_config.py - LLM配置

**核心功能**：
- 从环境变量读取LLM配置
- 创建OpenAI客户端实例
- 支持多种LLM服务商

**关键函数**：
```python
def get_llm_client() -> Tuple[OpenAI, str, float]:
    """
    获取LLM客户端实例
    
    Returns:
        (client, model, temperature)
    """
```

**扩展示例**：添加新的LLM服务商
```python
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
