# 🏗️ 架构设计文档

本文档详细说明英语学习助手系统的技术架构、设计决策和实现细节。

---

## 📋 目录

1. [系统概述](#系统概述)
2. [架构设计](#架构设计)
3. [技术选型](#技术选型)
4. [模块设计](#模块设计)
5. [数据流](#数据流)
6. [设计模式](#设计模式)
7. [性能优化](#性能优化)
8. [安全考虑](#安全考虑)

---

## 🎯 系统概述

### 项目目标

构建一个基于第三方LLM API的智能英语学习平台，提供：
- AI导师对话
- 翻译解析
- 写作批改
- 口语练习
- 多模态学习

### 核心设计原则

1. **API优先**: 所有AI能力通过第三方API实现
2. **模块化**: 清晰的模块划分，低耦合高内聚
3. **可扩展**: 易于添加新功能和支持新API
4. **用户友好**: 简洁的中文界面，流畅的交互体验
5. **可维护**: 详细的日志，规范的代码结构

---

## 🏛️ 架构设计

### 总体架构

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                       │
│                    (Gradio Web UI)                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                      │
│  ┌─────────────┬──────────────┬─────────────────────┐  │
│  │   Agent     │   Services   │   API Clients       │  │
│  │  (智能体)    │  (业务逻辑)   │   (API封装)         │  │
│  └─────────────┴──────────────┴─────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTPS
                     ↓
┌─────────────────────────────────────────────────────────┐
│                Third-Party LLM APIs                     │
│  ┌────────┬────────┬────────┬─────────┬────────────┐   │
│  │  LLM   │  TTS   │  STT   │ Vision  │   其他...   │   │
│  └────────┴────────┴────────┴─────────┴────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 分层架构

#### 1. 展示层 (Presentation Layer)

**职责**:
- 用户界面渲染
- 用户交互处理
- 输入验证
- 结果展示

**技术**: Gradio 4.0+

**特点**:
- 响应式设计，支持PC和移动端
- 全中文界面
- Markdown渲染
- 流式输出支持

#### 2. 业务逻辑层 (Business Logic Layer)

**职责**:
- 业务规则实现
- 数据处理和转换
- 功能编排

**模块**:
- `services/translation.py`: 翻译服务
- `services/writing.py`: 写作服务
- `services/speaking.py`: 口语服务
- `services/multimodal.py`: 多模态服务

**特点**:
- 单一职责
- 可复用
- 易于测试

#### 3. Agent层 (Agent Layer)

**职责**:
- 维护对话状态
- 上下文管理
- 学习档案管理
- 智能决策

**实现**: `agent/english_agent.py`

**特点**:
- 有状态服务
- 长期记忆能力
- 自适应行为

#### 4. API客户端层 (API Client Layer)

**职责**:
- 封装第三方API调用
- 请求/响应转换
- 错误处理和重试
- 流式输出处理

**模块**:
- `api/llm_client.py`: LLM调用
- `api/tts_client.py`: 语音合成
- `api/stt_client.py`: 语音识别
- `api/vision_client.py`: 多模态识别

**特点**:
- 统一接口
- 可插拔设计
- 易于切换API服务商

#### 5. 基础设施层 (Infrastructure Layer)

**职责**:
- 日志系统
- 配置管理
- 数据存储
- 工具函数

**模块**:
- `utils/logger.py`: 日志
- `utils/storage.py`: 存储
- `config/settings.py`: 配置
- `config/prompts.py`: Prompt管理

---

## 🔧 技术选型

### 核心技术栈

| 组件 | 技术 | 版本 | 选型理由 |
|------|------|------|---------|
| UI框架 | Gradio | 4.0+ | 快速构建ML界面，支持流式输出 |
| 后端语言 | Python | 3.8+ | AI/ML生态丰富，开发效率高 |
| 配置管理 | Pydantic | 2.0+ | 类型安全，自动验证 |
| 日志 | Loguru | 0.7+ | 简单易用，功能强大 |
| HTTP请求 | Requests | 2.31+ | 成熟稳定，文档完善 |
| 环境变量 | python-dotenv | 1.0+ | 标准的.env文件支持 |

### 第三方API

支持的API类型：
- **LLM**: 通义千问、OpenAI、其他兼容API
- **TTS**: 文字转语音
- **STT**: 语音转文字
- **Vision**: 图片/文档识别

---

## 🧩 模块设计

### 1. 配置管理模块

**目的**: 统一管理系统配置，支持环境变量和类型验证

**设计**:

```python
# config/settings.py
class Settings(BaseSettings):
    # 使用Pydantic进行类型验证
    LLM_API_KEY: str = Field(...)
    LLM_MODEL: str = Field(default="qwen-plus")
    
    class Config:
        env_file = ".env"  # 从.env加载
        case_sensitive = True

# 单例模式
settings = Settings()
```

**优点**:
- ✅ 类型安全
- ✅ 自动验证
- ✅ 环境变量支持
- ✅ 默认值处理

### 2. Prompt管理模块

**目的**: 集中管理所有Prompt模板，便于优化和调整

**设计**:

```python
# config/prompts.py
class PromptManager:
    # 所有Prompt定义在这里
    TRANSLATION_PROMPT = """..."""
    AGENT_SYSTEM_PROMPT = """..."""
    # ...

# 字典形式便于动态访问
PROMPT_TEMPLATES = {
    "translation": PROMPTS.TRANSLATION_PROMPT,
    # ...
}
```

**优点**:
- ✅ 集中管理
- ✅ 支持变量插值
- ✅ 便于版本控制
- ✅ 易于A/B测试

### 3. API客户端模块

**设计模式**: 策略模式 + 适配器模式

**基类设计**:

```python
class BaseLLMClient(ABC):
    """LLM客户端基类"""
    
    @abstractmethod
    def chat(self, messages, stream=True):
        """统一的chat接口"""
        pass
    
    @abstractmethod
    def _build_request(self, messages):
        """构建请求（子类实现）"""
        pass
    
    @abstractmethod
    def _parse_response(self, response):
        """解析响应（子类实现）"""
        pass
```

**具体实现**:

```python
class QwenLLMClient(BaseLLMClient):
    """通义千问客户端"""
    
    def _build_request(self, messages):
        # 通义千问特定的请求格式
        pass
    
    def _parse_response(self, response):
        # 通义千问特定的响应解析
        pass
```

**优点**:
- ✅ 易于扩展新API
- ✅ 统一接口
- ✅ 可测试性好

### 4. Agent模块

**设计**: 状态机 + 策略模式

**状态管理**:

```
┌─────────────────────────────────┐
│      EnglishLearningAgent       │
├─────────────────────────────────┤
│  State:                         │
│  - chat_history                 │
│  - student_profile              │
│  - difficulty                   │
│                                 │
│  Behaviors:                     │
│  - chat()                       │
│  - _build_messages()            │
│  - _update_profile()            │
│  - generate_summary()           │
└─────────────────────────────────┘
```

**对话流程**:

```
用户输入
   ↓
添加到历史
   ↓
构建完整消息列表
(系统提示 + 上下文 + 历史)
   ↓
调用LLM (流式输出)
   ↓
保存回复到历史
   ↓
更新学生档案
   ↓
持久化存储
```

**优点**:
- ✅ 有状态管理
- ✅ 上下文连贯
- ✅ 可扩展的决策逻辑

### 5. 服务层模块

**设计**: 门面模式 + 依赖注入

**服务接口**:

```python
class TranslationService:
    """翻译服务门面"""
    
    def __init__(self):
        # 依赖注入
        self.llm = llm_client
    
    def translate(self, text, task_type):
        """统一入口"""
        if task_type == "word":
            return self.analyze_word(text)
        # ...
    
    def analyze_word(self, word):
        """具体功能实现"""
        prompt = PROMPTS.WORD_ANALYSIS_PROMPT.format(word=word)
        return self.llm.chat_complete([{"role": "user", "content": prompt}])
```

**优点**:
- ✅ 简化接口
- ✅ 隐藏复杂性
- ✅ 易于组合

### 6. 工具模块

#### 日志系统

**设计**: 单例模式 + 装饰器模式

```python
# utils/logger.py
def setup_logger():
    """配置Loguru"""
    logger.add(
        sys.stdout,  # 控制台
        format="<green>{time}</green> | <level>{level}</level> | {message}",
        colorize=True
    )
    
    logger.add(
        "logs/app.log",  # 文件
        rotation="100 MB",
        retention="30 days"
    )

app_logger = setup_logger()

def log_api_call(api_name, prompt, model):
    """专用的API调用日志"""
    app_logger.info(f"API调用: {api_name}\n模型: {model}\nPrompt: {prompt}")
```

**日志级别**:
- `DEBUG`: 详细调试信息
- `INFO`: 一般信息（API调用、功能执行）
- `WARNING`: 警告信息
- `ERROR`: 错误信息（带堆栈跟踪）

#### 存储管理

**设计**: 仓储模式

```python
class StorageManager:
    """数据存储仓库"""
    
    def save_chat_history(self, session_id, messages, metadata):
        """保存对话历史"""
        # JSON格式存储
        pass
    
    def load_chat_history(self, session_id):
        """加载对话历史"""
        pass
    
    def get_user_statistics(self, user_id):
        """获取用户统计"""
        # 聚合分析
        pass
```

**存储结构**:

```
data/
├── history/
│   ├── user1/
│   │   ├── translation_20260101.json
│   │   ├── speaking_20260101.json
│   │   └── ...
│   └── chat_session_xxx.json
└── uploads/
    ├── image_xxx.jpg
    └── document_xxx.pdf
```

---

## 🔄 数据流

### 1. 普通对话流程

```
用户输入 → Web UI → Service → LLM Client → 第三方API
                                                  ↓
用户界面 ← Web UI ← Service ← LLM Client ← API响应
```

### 2. Agent对话流程

```
用户输入
   ↓
Agent.chat()
   ↓
添加到历史
   ↓
_build_messages()
   ├─ 系统提示词
   ├─ 上下文提示词
   └─ 对话历史
   ↓
LLM Client
   ↓
流式输出
   ├─ yield chunk → Web UI
   └─ 累积完整回复
   ↓
_update_profile()
   ├─ 分析薄弱项
   └─ 更新统计
   ↓
_save_history()
   └─ 持久化
```

### 3. 口语评估流程

```
用户录音 (Audio)
   ↓
Web UI
   ↓
SpeakingService.evaluate_speaking()
   ├─ STT Client
   │  └─ 语音识别 → 识别文本
   └─ LLM Client
      └─ 生成详细反馈
   ↓
合并结果
   ├─ 评分
   └─ 反馈
   ↓
返回 Web UI
```

### 4. 多模态解析流程

```
上传文件 (Image/PDF)
   ↓
MultimodalService
   ├─ 图片？
   │  └─ Vision Client
   │     └─ 图片识别 + 分析
   │
   └─ PDF？
      ├─ PDF文本提取
      └─ LLM Client
         └─ 内容分析
   ↓
返回结果 (Markdown)
```

---

## 🎨 设计模式

### 1. 单例模式 (Singleton)

**应用**: 配置对象、客户端实例

```python
# config/settings.py
settings = Settings()  # 全局单例

# src/api/llm_client.py
llm_client = LLMClient()  # 全局单例
```

**优点**:
- 全局访问点
- 节省资源
- 配置一致性

### 2. 策略模式 (Strategy)

**应用**: 不同的API客户端实现

```python
# 策略接口
class LLMStrategy(ABC):
    @abstractmethod
    def chat(self, messages):
        pass

# 具体策略
class QwenStrategy(LLMStrategy):
    def chat(self, messages):
        # 通义千问实现
        pass

class OpenAIStrategy(LLMStrategy):
    def chat(self, messages):
        # OpenAI实现
        pass
```

### 3. 门面模式 (Facade)

**应用**: Service层

```python
class TranslationService:
    """为复杂的翻译功能提供简单接口"""
    
    def translate(self, text, task_type):
        # 统一入口，内部路由到不同方法
        pass
```

### 4. 适配器模式 (Adapter)

**应用**: API客户端

```python
class APIAdapter:
    """将不同API的响应格式转换为统一格式"""
    
    def adapt_response(self, raw_response):
        # 转换为统一格式
        pass
```

### 5. 仓储模式 (Repository)

**应用**: 存储管理

```python
class StorageManager:
    """封装数据访问逻辑"""
    
    def save(self, data):
        # 抽象存储细节
        pass
```

---

## ⚡ 性能优化

### 1. 流式输出

**目的**: 减少首字节时间，提升用户体验

**实现**:

```python
def chat(self, messages, stream=True):
    """流式输出"""
    response = requests.post(..., stream=True)
    
    for line in response.iter_lines():
        # 逐块返回
        yield parse_chunk(line)
```

**效果**:
- ✅ 即时反馈
- ✅ 降低感知延迟
- ✅ 更流畅的体验

### 2. 日志异步写入

**实现**:

```python
# Loguru自动异步写入文件
logger.add(
    "logs/app.log",
    rotation="100 MB",
    enqueue=True  # 异步队列
)
```

### 3. 缓存机制

**潜在优化**: 缓存常见查询

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_word_analysis(word: str) -> str:
    """缓存单词解析结果"""
    return translation_service.analyze_word(word)
```

### 4. 批量处理

**潜在优化**: 批量API调用

```python
def translate_batch(texts: List[str]) -> List[str]:
    """批量翻译"""
    # 一次API调用处理多个文本
    pass
```

---

## 🔒 安全考虑

### 1. API密钥管理

**实践**:
- ✅ 使用`.env`文件存储
- ✅ 不提交到版本控制（`.gitignore`）
- ✅ 环境变量注入
- ❌ 避免硬编码

**示例**:

```bash
# .env
LLM_API_KEY=sk-xxxxx

# .gitignore
.env
```

### 2. 输入验证

**实践**:

```python
def translate(text: str) -> str:
    # 验证输入
    if not text or not text.strip():
        return "⚠️ 请输入内容"
    
    # 长度限制
    if len(text) > 10000:
        return "⚠️ 内容过长，请缩短"
    
    # 执行翻译
    return translation_service.translate(text)
```

### 3. 错误处理

**实践**:

```python
try:
    result = api_call()
except Timeout:
    # 具体错误
    return "请求超时"
except Exception as e:
    # 记录日志，返回友好提示
    app_logger.error(f"错误: {str(e)}", exc_info=True)
    return "系统错误，请稍后重试"
```

### 4. 日志脱敏

**实践**:

```python
def log_api_call(api_name, prompt, model):
    # 脱敏API密钥
    safe_key = api_key[:10] + "..." if api_key else "N/A"
    
    app_logger.info(f"API: {api_name}, Key: {safe_key}")
```

---

## 📊 数据模型

### 对话消息

```python
{
    "role": "user",  # user / assistant / system
    "content": "消息内容"
}
```

### 学生档案

```python
{
    "user_id": "user123",
    "level": "中级",
    "weak_points": ["语法", "词汇"],
    "practice_count": 42,
    "error_patterns": {
        "grammar": 15,
        "vocabulary": 10
    }
}
```

### 学习记录

```python
{
    "timestamp": "2026-01-01T10:00:00",
    "type": "translation",
    "content": {
        "input": "原文",
        "output": "结果",
        "duration": 1.5
    }
}
```

---

## 🔮 未来扩展

### 计划中的功能

1. **多用户系统**
   - 用户注册/登录
   - 个人学习数据隔离
   - 学习进度追踪

2. **学习计划**
   - AI生成个性化学习计划
   - 定时提醒
   - 目标管理

3. **社交功能**
   - 学习小组
   - 互相批改
   - 排行榜

4. **高级分析**
   - 学习曲线可视化
   - 薄弱项热图
   - 预测模型

### 技术演进

1. **数据库**
   - 从文件存储迁移到数据库（PostgreSQL/MongoDB）

2. **缓存**
   - 引入Redis缓存常用查询

3. **消息队列**
   - 异步任务处理（Celery）

4. **微服务**
   - 拆分为独立服务
   - API网关

---

## 📝 总结

### 架构优势

- ✅ **模块化**: 清晰的职责划分
- ✅ **可扩展**: 易于添加新功能
- ✅ **可维护**: 规范的代码结构
- ✅ **可测试**: 良好的解耦设计
- ✅ **用户友好**: 流畅的交互体验

### 技术亮点

- 🎯 100%基于API，无本地模型依赖
- 🎯 完整的日志系统，便于调试
- 🎯 统一的Prompt管理
- 🎯 流式输出优化体验
- 🎯 智能Agent记忆能力

---

**本架构文档持续更新中...**
