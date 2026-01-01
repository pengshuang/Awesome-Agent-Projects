# 🔧 开发者指南

本指南面向希望深入了解系统架构、进行二次开发或贡献代码的开发者。

---

## 📋 目录

1. [开发环境搭建](#开发环境搭建)
2. [项目结构详解](#项目结构详解)
3. [核心模块说明](#核心模块说明)
4. [API集成指南](#api集成指南)
5. [扩展开发](#扩展开发)
6. [调试技巧](#调试技巧)
7. [代码规范](#代码规范)

---

## 🛠️ 开发环境搭建

### 开发工具推荐

- **IDE**: PyCharm / VS Code
- **Python版本**: 3.8+
- **虚拟环境**: venv / conda
- **版本控制**: Git

### 开发环境配置

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果有开发依赖

# 3. 配置IDE
# PyCharm: 设置Python解释器为venv/bin/python
# VS Code: 选择venv作为Python解释器
```

### 调试配置

**VS Code** - `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Web UI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/web_ui.py",
            "console": "integratedTerminal",
            "env": {
                "DEBUG": "true"
            }
        }
    ]
}
```

---

## 📁 项目结构详解

### 整体架构

```
english-learning-assistant/
├── config/                 # 配置层
│   ├── __init__.py
│   ├── settings.py        # 全局配置
│   ├── llm_config.py      # API配置模型
│   └── prompts.py         # Prompt模板管理
├── src/                   # 源代码
│   ├── agent/            # Agent智能体
│   │   └── english_agent.py
│   ├── api/              # API客户端层
│   │   ├── llm_client.py     # LLM调用
│   │   ├── tts_client.py     # 文字转语音
│   │   ├── stt_client.py     # 语音转文字
│   │   └── vision_client.py  # 多模态
│   ├── services/         # 业务逻辑层
│   │   ├── translation.py    # 翻译服务
│   │   ├── writing.py        # 写作服务
│   │   ├── speaking.py       # 口语服务
│   │   └── multimodal.py     # 多模态服务
│   └── utils/            # 工具层
│       ├── logger.py         # 日志系统
│       └── storage.py        # 数据存储
├── data/                  # 数据目录
│   ├── history/          # 学习记录
│   └── uploads/          # 上传文件
├── logs/                  # 日志目录
├── docs/                  # 文档目录
├── web_ui.py             # Web界面入口
├── init_system.py        # 系统初始化
├── start.sh              # 启动脚本
└── requirements.txt      # 依赖清单
```

### 分层架构

```
┌─────────────────────────────────┐
│     Presentation Layer          │  Web UI (Gradio)
│         (web_ui.py)             │
├─────────────────────────────────┤
│      Service Layer              │  业务逻辑
│   (services/*)                  │  - translation
│                                 │  - writing
│                                 │  - speaking
│                                 │  - multimodal
├─────────────────────────────────┤
│       Agent Layer               │  智能Agent
│   (agent/english_agent.py)     │
├─────────────────────────────────┤
│       API Layer                 │  第三方API封装
│   (api/*)                       │  - llm_client
│                                 │  - tts_client
│                                 │  - stt_client
│                                 │  - vision_client
├─────────────────────────────────┤
│      Infrastructure             │  基础设施
│   (utils/*, config/*)           │  - logger
│                                 │  - storage
│                                 │  - settings
└─────────────────────────────────┘
```

---

## 🧩 核心模块说明

### 1. 配置模块 (config/)

#### settings.py - 全局配置

**作用**: 管理所有系统配置，使用Pydantic进行类型验证。

**核心类**:
```python
class Settings(BaseSettings):
    """系统配置类"""
    # API配置
    LLM_API_KEY: str
    LLM_API_BASE: str
    LLM_MODEL: str
    
    # 模型参数
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000
    
    # 路径配置
    DATA_DIR: Path
    LOG_DIR: Path
    
    class Config:
        env_file = ".env"  # 从.env文件加载
```

**使用方式**:
```python
from config.settings import settings

# 访问配置
api_key = settings.LLM_API_KEY
model = settings.LLM_MODEL
```

#### prompts.py - Prompt管理

**作用**: 集中管理所有功能模块的Prompt模板。

**设计特点**:
- 所有Prompt集中存储
- 支持变量插值
- 便于统一调整和优化

**使用方式**:
```python
from config.prompts import PROMPTS

# 使用Prompt模板
prompt = PROMPTS.TRANSLATION_PROMPT.format(text="Hello")
```

**添加新Prompt**:
```python
# 在PromptManager类中添加
NEW_FEATURE_PROMPT = """你的Prompt内容
支持变量: {var1}, {var2}
"""

# 在PROMPT_TEMPLATES字典中注册
PROMPT_TEMPLATES["new_feature"] = PROMPTS.NEW_FEATURE_PROMPT
```

---

### 2. API客户端层 (src/api/)

#### llm_client.py - LLM客户端

**核心功能**:
- 封装LLM API调用
- 支持流式和非流式输出
- 自动错误处理和重试

**核心方法**:

```python
class LLMClient:
    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True
    ) -> Generator[str, None, None]:
        """流式对话"""
        # 1. 记录API调用日志
        log_api_call("LLM Chat", prompt, model)
        
        # 2. 构建请求
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": stream
        }
        
        # 3. 发送请求并处理响应
        # 4. 异常处理
    
    def chat_complete(
        self,
        messages: List[Dict[str, str]]
    ) -> str:
        """非流式对话（返回完整结果）"""
```

**扩展支持新API**:

1. 继承LLMClient或创建新客户端类
2. 实现API特定的请求格式转换
3. 处理API特定的响应格式

示例:
```python
class CustomLLMClient(LLMClient):
    def _build_request(self, messages):
        """自定义请求格式"""
        # 转换为目标API的格式
        pass
    
    def _parse_response(self, response):
        """解析响应"""
        # 解析目标API的响应
        pass
```

#### tts_client.py - 语音合成

**核心功能**:
- 文字转语音
- 支持多种音色
- 可调节语速

**核心方法**:
```python
class TTSClient:
    def synthesize(
        self,
        text: str,
        voice: str = "samantha",
        speed: float = 1.0
    ) -> bytes:
        """合成语音，返回音频字节"""
```

#### stt_client.py - 语音识别

**核心功能**:
- 语音转文字
- 发音评估
- 多语言支持

**核心方法**:
```python
class STTClient:
    def transcribe(
        self,
        audio_data: bytes,
        language: str = "en"
    ) -> str:
        """识别语音"""
    
    def evaluate_pronunciation(
        self,
        audio_data: bytes,
        reference_text: str
    ) -> dict:
        """评估发音"""
```

#### vision_client.py - 多模态

**核心功能**:
- 图片内容识别
- PDF文本提取
- 多模态分析

**核心方法**:
```python
class VisionClient:
    def analyze_image(
        self,
        image_data: bytes,
        prompt: str
    ) -> str:
        """分析图片"""
    
    def extract_pdf_text(
        self,
        pdf_path: str
    ) -> str:
        """提取PDF文本"""
```

---

### 3. 业务服务层 (src/services/)

#### 服务层设计原则

- **单一职责**: 每个服务负责一类功能
- **依赖注入**: 通过构造函数注入API客户端
- **错误处理**: 统一的异常处理和用户友好提示
- **日志记录**: 记录关键操作

#### translation.py - 翻译服务

**功能**:
- 通用翻译
- 单词解析
- 长难句分析

**代码结构**:
```python
class TranslationService:
    def __init__(self):
        self.llm = llm_client
    
    def translate(self, text: str, task_type: str) -> str:
        """统一翻译入口"""
        if task_type == "word":
            return self.analyze_word(text)
        elif task_type == "sentence":
            return self.analyze_sentence(text)
        else:
            return self.translate_general(text)
    
    def translate_general(self, text: str) -> str:
        """通用翻译实现"""
        prompt = PROMPTS.TRANSLATION_PROMPT.format(text=text)
        messages = [{"role": "user", "content": prompt}]
        return self.llm.chat_complete(messages)
```

**添加新翻译功能**:
1. 在prompts.py中添加新的Prompt模板
2. 在TranslationService中添加新方法
3. 在web_ui.py中添加UI元素

#### writing.py - 写作服务

**功能**:
- 作文批改
- 写作润色

**核心逻辑**:
```python
class WritingService:
    def correct_writing(
        self,
        content: str,
        requirement: str = "通用写作"
    ) -> str:
        """批改作文"""
        # 1. 构建批改Prompt
        prompt = PROMPTS.WRITING_CORRECTION_PROMPT.format(
            content=content,
            requirement=requirement
        )
        
        # 2. 调用LLM
        messages = [{"role": "user", "content": prompt}]
        result = self.llm.chat_complete(messages)
        
        # 3. 记录日志
        app_logger.info("作文批改完成")
        
        return result
```

#### speaking.py - 口语服务

**功能**:
- 生成口语练习
- 评估发音
- TTS/STT集成

**关键实现**:
```python
class SpeakingService:
    def __init__(self):
        self.llm = llm_client
        self.stt = stt_client
        self.tts = tts_client
    
    def evaluate_speaking(
        self,
        audio_data: bytes,
        reference_text: str
    ) -> Dict:
        """评估口语"""
        # 1. STT识别
        result = self.stt.evaluate_pronunciation(
            audio_data, reference_text
        )
        
        # 2. LLM生成详细反馈
        prompt = PROMPTS.SPEAKING_CORRECTION_PROMPT.format(...)
        feedback = self.llm.chat_complete([...])
        
        # 3. 合并结果
        result["detailed_feedback"] = feedback
        return result
```

---

### 4. Agent模块 (src/agent/)

#### english_agent.py - 英语学习Agent

**核心设计**:

**状态管理**:
```python
class EnglishLearningAgent:
    def __init__(self, user_id: str, difficulty: str):
        # 对话历史
        self.chat_history: List[Dict[str, str]] = []
        
        # 学生档案
        self.student_profile = {
            "level": difficulty,
            "weak_points": [],
            "practice_count": 0,
            "error_patterns": {},
        }
```

**上下文管理**:
```python
def _build_messages(self) -> List[Dict[str, str]]:
    """构建发送给LLM的消息"""
    messages = []
    
    # 1. 系统提示词
    system_prompt = PROMPTS.AGENT_SYSTEM_PROMPT.format(
        difficulty=self.difficulty,
        level_description=...
    )
    messages.append({"role": "system", "content": system_prompt})
    
    # 2. 上下文提示（如有历史对话）
    if len(self.chat_history) > 2:
        context_prompt = PROMPTS.AGENT_CHAT_PROMPT.format(...)
        messages.append({"role": "system", "content": context_prompt})
    
    # 3. 对话历史（最近N轮）
    recent_history = self.chat_history[-20:]
    messages.extend(recent_history)
    
    return messages
```

**流式对话**:
```python
def chat(
    self,
    user_message: str,
    stream: bool = True
) -> Generator[str, None, None]:
    """流式对话"""
    # 1. 添加用户消息
    self.chat_history.append({
        "role": "user",
        "content": user_message
    })
    
    # 2. 构建消息列表
    messages = self._build_messages()
    
    # 3. 流式输出
    assistant_reply = ""
    for chunk in self.llm.chat(messages, stream=stream):
        assistant_reply += chunk
        yield chunk
    
    # 4. 保存回复
    self.chat_history.append({
        "role": "assistant",
        "content": assistant_reply
    })
    
    # 5. 更新档案
    self._update_profile(user_message, assistant_reply)
    
    # 6. 保存历史
    self._save_history()
```

**学习分析**:
```python
def _update_profile(self, user_message: str, assistant_reply: str):
    """更新学生档案"""
    self.student_profile["practice_count"] += 1
    
    # 分析回复中的关键词，识别薄弱项
    if "错误" in assistant_reply:
        # 提取薄弱项...
        pass
```

---

### 5. 工具模块 (src/utils/)

#### logger.py - 日志系统

**功能**:
- 多级别日志（DEBUG, INFO, WARNING, ERROR）
- 控制台彩色输出
- 文件日志（自动轮转）
- API调用专用日志

**配置**:
```python
def setup_logger():
    """配置日志系统"""
    # 控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time}</green> | <level>{level}</level> | {message}",
        colorize=True
    )
    
    # 文件输出
    logger.add(
        "logs/app.log",
        rotation="100 MB",
        retention="30 days"
    )
    
    # 错误日志
    logger.add(
        "logs/error.log",
        level="ERROR"
    )
```

**使用方式**:
```python
from src.utils.logger import app_logger, log_api_call

# 普通日志
app_logger.info("系统启动")
app_logger.error("发生错误", exc_info=True)

# API调用日志
log_api_call("LLM Chat", prompt_content, model_name)
```

#### storage.py - 数据存储

**功能**:
- 对话历史存储
- 学习记录管理
- 用户统计分析

**核心方法**:
```python
class StorageManager:
    def save_chat_history(
        self,
        session_id: str,
        messages: List[Dict],
        metadata: Dict
    ) -> bool:
        """保存对话历史"""
        # 构建数据结构
        data = {
            "session_id": session_id,
            "messages": messages,
            "metadata": metadata,
            "updated_at": datetime.now().isoformat()
        }
        
        # 保存为JSON
        file_path = self.history_dir / f"chat_{session_id}.json"
        with open(file_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_user_statistics(self, user_id: str) -> Dict:
        """获取用户统计"""
        # 遍历用户记录文件
        # 统计学习数据
        # 返回分析结果
```

---

## 🔌 API集成指南

### 添加新的LLM API支持

**步骤1: 创建配置类**

在 `config/llm_config.py` 中添加:
```python
class NewLLMConfig(BaseModel):
    api_key: str
    api_base: str
    model: str
    # 其他特定参数
```

**步骤2: 创建客户端类**

在 `src/api/` 中创建 `new_llm_client.py`:
```python
class NewLLMClient:
    def __init__(self, config: NewLLMConfig):
        self.config = config
    
    def chat(self, messages, stream=True):
        """实现chat方法"""
        # 1. 转换消息格式
        api_messages = self._convert_messages(messages)
        
        # 2. 构建请求
        payload = self._build_payload(api_messages, stream)
        
        # 3. 发送请求
        response = self._send_request(payload)
        
        # 4. 解析响应
        for chunk in self._parse_response(response, stream):
            yield chunk
    
    def _convert_messages(self, messages):
        """转换为API特定格式"""
        pass
    
    def _build_payload(self, messages, stream):
        """构建请求载荷"""
        pass
    
    def _send_request(self, payload):
        """发送HTTP请求"""
        pass
    
    def _parse_response(self, response, stream):
        """解析API响应"""
        pass
```

**步骤3: 集成到服务**

修改服务类使用新客户端:
```python
# 在services中
from src.api.new_llm_client import NewLLMClient

class TranslationService:
    def __init__(self, use_new_api=False):
        if use_new_api:
            self.llm = NewLLMClient(config)
        else:
            self.llm = llm_client
```

### 添加新的语音API

类似的，在 `src/api/` 中创建新的TTS/STT客户端。

---

## 🚀 扩展开发

### 添加新功能模块

**示例: 添加"语法检查"功能**

**步骤1: 添加Prompt**

在 `config/prompts.py`:
```python
class PromptManager:
    GRAMMAR_CHECK_PROMPT = """请检查以下英文句子的语法错误：

句子: {sentence}

请提供:
## 语法错误
[列出所有错误]

## 纠正建议
[提供正确的表达]

## 语法规则
[相关语法规则讲解]
"""

# 注册到字典
PROMPT_TEMPLATES["grammar_check"] = PROMPTS.GRAMMAR_CHECK_PROMPT
```

**步骤2: 创建服务**

在 `src/services/grammar.py`:
```python
class GrammarService:
    def __init__(self):
        self.llm = llm_client
    
    def check_grammar(self, sentence: str) -> str:
        """检查语法"""
        prompt = PROMPTS.GRAMMAR_CHECK_PROMPT.format(sentence=sentence)
        messages = [{"role": "user", "content": prompt}]
        result = self.llm.chat_complete(messages)
        app_logger.info("语法检查完成")
        return result
```

**步骤3: 添加到Web UI**

在 `web_ui.py`:
```python
from src.services.grammar import GrammarService
grammar_service = GrammarService()

def check_grammar(text):
    """语法检查处理函数"""
    if not text.strip():
        return "⚠️ 请输入要检查的句子"
    return grammar_service.check_grammar(text)

# 在create_ui()中添加Tab
with gr.Tab("📝 语法检查"):
    with gr.Row():
        with gr.Column():
            grammar_input = gr.Textbox(label="输入句子", lines=5)
            check_btn = gr.Button("检查语法", variant="primary")
        with gr.Column():
            grammar_output = gr.Markdown(label="检查结果")
    
    check_btn.click(
        check_grammar,
        inputs=grammar_input,
        outputs=grammar_output
    )
```

### 自定义Agent行为

**修改Agent的决策逻辑**:

在 `src/agent/english_agent.py`:
```python
class EnglishLearningAgent:
    def _should_provide_practice(self, user_message: str) -> bool:
        """判断是否应该主动提供练习"""
        # 自定义逻辑
        keywords = ["不懂", "不明白", "困难"]
        return any(kw in user_message for kw in keywords)
    
    def chat(self, user_message: str, stream: bool = True):
        """增强的对话逻辑"""
        # 原有逻辑...
        
        # 主动提供练习
        if self._should_provide_practice(user_message):
            practice_prompt = "看来你需要更多练习，让我给你一些建议..."
            # 生成练习内容
```

---

## 🐛 调试技巧

### 查看日志

**实时查看日志**:
```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log

# 查看API调用日志
tail -f logs/api.log
```

### 调试API调用

**在代码中添加断点**:
```python
def chat(self, messages, stream=True):
    # 打印请求信息
    print(f"发送请求: {messages}")
    
    # 设置断点
    import pdb; pdb.set_trace()
    
    # 调用API
    response = requests.post(...)
```

### 测试单个模块

**创建测试脚本**:
```python
# test_translation.py
from src.services.translation import translation_service

result = translation_service.translate("Hello", "word")
print(result)
```

### 使用Python调试器

**pdb调试**:
```python
import pdb

def my_function():
    x = 10
    pdb.set_trace()  # 设置断点
    y = x * 2
    return y
```

**常用pdb命令**:
- `n` (next): 下一行
- `s` (step): 进入函数
- `c` (continue): 继续执行
- `p variable`: 打印变量
- `l` (list): 查看代码
- `q` (quit): 退出

---

## 📏 代码规范

### Python风格指南

遵循 [PEP 8](https://pep8.org/)：

**命名规范**:
```python
# 类名: 大驼峰
class EnglishLearningAgent:
    pass

# 函数/变量: 小写+下划线
def translate_text(input_text):
    user_name = "张三"

# 常量: 大写+下划线
MAX_RETRY_COUNT = 3
API_TIMEOUT = 60
```

**注释规范**:
```python
def complex_function(param1: str, param2: int) -> dict:
    """函数简短描述
    
    详细说明函数的用途和行为。
    
    Args:
        param1: 参数1的说明
        param2: 参数2的说明
    
    Returns:
        返回值的说明
        
    Raises:
        ValueError: 什么情况下抛出
    """
    pass
```

### 类型注解

```python
from typing import List, Dict, Optional, Generator

def process_messages(
    messages: List[Dict[str, str]],
    options: Optional[Dict[str, Any]] = None
) -> Generator[str, None, None]:
    """使用类型注解提高代码可读性"""
    pass
```

### 错误处理

```python
def safe_api_call():
    """良好的错误处理"""
    try:
        # 尝试操作
        result = api_client.call()
        
    except requests.exceptions.Timeout:
        # 具体异常处理
        app_logger.error("API超时")
        return "请求超时，请重试"
        
    except requests.exceptions.RequestException as e:
        # 一般异常处理
        app_logger.error(f"请求失败: {str(e)}")
        return f"请求失败: {str(e)}"
        
    except Exception as e:
        # 兜底处理
        app_logger.error(f"未知错误: {str(e)}", exc_info=True)
        return "发生未知错误"
    
    finally:
        # 清理资源
        pass
```

### 文档字符串

使用详细的docstring：

```python
class TranslationService:
    """翻译服务类
    
    提供多种翻译和解析功能，包括：
    - 通用翻译
    - 单词解析
    - 长难句分析
    
    Attributes:
        llm: LLM客户端实例
    
    Example:
        >>> service = TranslationService()
        >>> result = service.translate("Hello", "word")
        >>> print(result)
    """
```

---

## 🧪 测试

### 单元测试

创建 `tests/` 目录:
```python
# tests/test_translation.py
import pytest
from src.services.translation import TranslationService

def test_translate_word():
    service = TranslationService()
    result = service.analyze_word("hello")
    assert "音标" in result
    assert "词性" in result
```

运行测试:
```bash
pytest tests/
```

### 集成测试

```python
# tests/test_integration.py
def test_full_workflow():
    # 测试完整流程
    agent = EnglishLearningAgent()
    response = agent.chat_complete("Hello")
    assert response
    assert len(response) > 0
```

---

## 📦 打包和部署

### 创建分发包

```bash
# 使用setuptools
python setup.py sdist bdist_wheel
```

### Docker部署

创建 `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "web_ui.py"]
```

构建和运行:
```bash
docker build -t english-assistant .
docker run -p 7860:7860 english-assistant
```

---

## 🤝 贡献代码

### 提交流程

1. Fork项目
2. 创建特性分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -m 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 创建Pull Request

### 代码审查清单

- [ ] 代码符合PEP 8规范
- [ ] 添加了必要的注释和docstring
- [ ] 更新了相关文档
- [ ] 添加了测试用例
- [ ] 所有测试通过
- [ ] 日志记录完善

---

## 📞 技术支持

遇到开发问题？

1. 查看[架构文档](ARCHITECTURE.md)
2. 查看代码中的注释
3. 搜索日志文件
4. 提交Issue

---

**Happy Coding! 🚀**
