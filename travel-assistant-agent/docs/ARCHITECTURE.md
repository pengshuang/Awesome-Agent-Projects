# 🏗️ 架构设计文档

> 智能旅游助手系统架构详解

## 📋 目录

- [系统概述](#系统概述)
- [架构设计原则](#架构设计原则)
- [系统架构图](#系统架构图)
- [核心组件](#核心组件)
- [数据流设计](#数据流设计)
- [技术选型](#技术选型)

---

## 🎯 系统概述

智能旅游助手是一个基于大模型的智能 Agent 系统,采用模块化架构设计,通过 Gradio 提供 Web 界面,调用阿里云千问 API 实现 AI 能力。

### 系统特点

- **轻量化**：纯 API 调用,无需本地模型,部署简单
- **模块化**：清晰的模块划分,易于维护和扩展
- **可靠性**：完善的错误处理、重试机制、日志记录
- **用户友好**：现代化 UI,响应式设计,多模态交互

---

## 📐 架构设计原则

### 1. 分层架构

```
┌─────────────────────────────────────┐
│         用户界面层 (UI Layer)         │  Gradio Web Interface
├─────────────────────────────────────┤
│      业务逻辑层 (Business Layer)      │  对话管理、场景识别
├─────────────────────────────────────┤
│        API 层 (API Layer)           │  文本/多模态 API 调用
├─────────────────────────────────────┤
│      配置层 (Config Layer)          │  Prompt、参数配置
└─────────────────────────────────────┘
```

### 2. 单一职责原则

每个模块/类只负责一个功能：
- `TravelAssistantAPI`: 专注 API 调用
- `ConversationManager`: 专注对话管理
- `create_ui()`: 专注界面构建

### 3. 配置化管理

所有配置集中在：
- `.env` 文件：环境变量配置
- `config/prompts.py`：Prompt 配置
- 全局常量：代码顶部统一定义

### 4. 错误处理策略

- API 调用：重试机制（最多 3 次）
- 超时处理：exponential backoff（5s、10s、15s）
- 友好提示：向用户返回清晰的错误信息

---

## 🗺️ 系统架构图

### 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                          用户浏览器                            │
│                    (http://localhost:7860)                    │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                      Gradio Web Server                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Chatbot 组件  │  │ Image 组件   │  │ Button 组件   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                     业务逻辑层 (app.py)                        │
│  ┌────────────────────────────────────────────────────┐      │
│  │ ConversationManager - 对话历史管理                  │      │
│  │  ├─ add_message()      : 添加消息                   │      │
│  │  ├─ get_context()      : 获取上下文                 │      │
│  │  └─ detect_scenario()  : 场景识别                   │      │
│  └────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────┐      │
│  │ 业务处理函数                                         │      │
│  │  ├─ process_text_message()   : 处理文本消息         │      │
│  │  ├─ process_image_upload()   : 处理图片上传         │      │
│  │  ├─ save_itinerary()         : 保存行程             │      │
│  │  └─ export_itinerary()       : 导出行程             │      │
│  └────────────────────────────────────────────────────┘      │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                  API 调用层 (TravelAssistantAPI)              │
│  ┌────────────────────────────────────────────────────┐      │
│  │ call_text_api()       : 文本 API 调用               │      │
│  │  ├─ 构建 payload                                    │      │
│  │  ├─ 重试逻辑（3次）                                  │      │
│  │  └─ 错误处理                                        │      │
│  └────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────┐      │
│  │ call_multimodal_api() : 多模态 API 调用             │      │
│  │  ├─ 图片 base64 编码                                │      │
│  │  ├─ 构建 payload                                    │      │
│  │  └─ 重试逻辑                                        │      │
│  └────────────────────────────────────────────────────┘      │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   阿里云千问 API 服务                          │
│  ┌──────────────────┐      ┌──────────────────┐             │
│  │ qwen3-max        │      │ qwen-vl-plus     │             │
│  │ (文本模型)        │      │ (多模态模型)      │             │
│  └──────────────────┘      └──────────────────┘             │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔧 核心组件

### 1. TravelAssistantAPI 类

**职责：**封装所有 API 调用逻辑

**核心方法：**

```python
class TravelAssistantAPI:
    def __init__(self):
        """初始化 API 客户端"""
        self.api_key = API_KEY
        self.base_url = API_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def call_text_api(self, user_message, system_prompt, temperature, max_tokens):
        """调用文本 API,带重试和超时处理"""
    
    def call_multimodal_api(self, image_path, user_query, system_prompt):
        """调用多模态 API,处理图片 base64 编码"""
```

**设计要点：**
- 统一的 headers 管理
- 重试机制（exponential backoff）
- 详细的日志记录
- 友好的错误提示

---

### 2. ConversationManager 类

**职责：**管理对话历史和场景识别

**核心方法：**

```python
class ConversationManager:
    def __init__(self):
        self.history = []              # 对话历史
        self.current_scenario = None   # 当前场景
        self.user_requirements = {}    # 用户需求
    
    def add_message(self, role, content):
        """添加消息到历史（带时间戳）"""
    
    def get_context(self, last_n=5):
        """获取最近 N 轮对话上下文"""
    
    def detect_scenario(self, user_input):
        """基于关键词识别场景"""
    
    def clear(self):
        """清空历史和状态"""
```

---

### 3. Prompt 配置体系

**职责：**管理所有 Prompt 模板

**文件：**`config/prompts.py`

**核心组件：**

```python
# 1. 核心系统 Prompt（定义 Agent 能力）
AGENT_CORE_SYSTEM_PROMPT = """..."""

# 2. 多模态 Prompt（图片识别指令）
MULTIMODAL_IMAGE_PROMPT = """..."""

# 3. 场景化 Prompt（6 大场景）
SCENARIO_PROMPTS = {
    "亲子游": """...""",
    "老年游": """...""",
    ...
}

# 4. Prompt 组合函数
def get_combined_prompt(base_prompt, scenario, additional_context):
    """动态组合 Prompt"""
```

---

## 🌊 数据流设计

### 文本对话流程

```
[用户] 输入："帮我规划杭州3天行程"
    ↓
[UI] Gradio Textbox 捕获输入
    ↓
[Handler] process_text_message(user_input, history)
    ↓
[场景识别] detect_scenario("帮我规划杭州3天行程")
    ↓
[Prompt 组合] get_combined_prompt(AGENT_CORE_SYSTEM_PROMPT)
    ↓
[API 调用] call_text_api(...)
    ↓
[重试逻辑] 尝试 1 → 尝试 2 → 尝试 3
    ↓
[API 响应] 返回 JSON
    ↓
[解析响应] 提取 content
    ↓
[更新历史] 添加消息到历史
    ↓
[返回结果] 返回给 UI
    ↓
[UI 更新] Gradio Chatbot 显示
```

---

## 🛠️ 技术选型

### 1. 前端框架：Gradio 4.x

**选择理由：**
- ✅ 快速搭建 AI 应用界面
- ✅ 自动生成响应式布局
- ✅ 支持多种组件
- ✅ Python 原生

### 2. 大模型：阿里云千问

**选择理由：**
- ✅ 中文能力优秀
- ✅ 支持长文本生成
- ✅ 提供多模态模型
- ✅ API 稳定

**模型选择：**
- **qwen3-max**：文本对话
- **qwen-vl-plus**：图片识别

### 3. HTTP 客户端：requests

**选择理由：**
- ✅ 简单易用
- ✅ 支持超时设置
- ✅ 自动处理 JSON

### 4. 配置管理：python-dotenv

**选择理由：**
- ✅ 环境变量集中管理
- ✅ 敏感信息隔离
- ✅ 不同环境轻松切换

---

## 📊 性能特性

### 1. 重试机制

指数退避（exponential backoff）

```python
for attempt in range(MAX_RETRIES):  # 最多 3 次
    try:
        response = requests.post(...)
        return response
    except Timeout:
        wait_time = 5 * (attempt + 1)  # 5s, 10s, 15s
        time.sleep(wait_time)
```

### 2. 超时控制

```python
TEXT_API_TIMEOUT = 60        # 文本 60s
MULTIMODAL_API_TIMEOUT = 90  # 多模态 90s
```

### 3. Token 优化

```python
MAX_TOKENS = 1500  # 限制输出长度
TEMPERATURE = 0.85  # 平衡创意和准确性
```

---

## 🔐 安全设计

### 1. API Key 保护

```bash
# .env 文件不提交到 git
echo ".env" >> .gitignore
```

### 2. 输入验证

```python
# 检查图片大小
if os.path.getsize(image_path) > 5 * 1024 * 1024:
    return "图片过大（限制5MB）"
```

### 3. 错误信息脱敏

```python
except Exception as e:
    logger.error(f"API 调用失败: {e}")
    return "❌ 请求失败,请稍后重试"
```

---

## 📈 扩展性设计

### 1. 模型切换

```python
# 只需修改配置
TEXT_MODEL_NAME = "gpt-4-turbo"
```

### 2. 功能扩展

新增功能只需 3 步：
1. 添加处理函数
2. 添加 UI 组件
3. 绑定事件

### 3. 多语言支持

```python
PROMPTS = {
    "zh": AGENT_CORE_SYSTEM_PROMPT_ZH,
    "en": AGENT_CORE_SYSTEM_PROMPT_EN
}
```

---

## 📝 设计模式

### 1. 单例模式

```python
api_client = TravelAssistantAPI()
conversation_mgr = ConversationManager()
```

### 2. 策略模式

```python
SCENARIO_PROMPTS = {
    "亲子游": "...",
    "老年游": "...",
}
```

### 3. 模板方法模式

```python
def call_api_template(api_func, *args, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            return api_func(*args, **kwargs)
        except Timeout:
            retry_logic()
```

---

## 🎯 总结

### 架构优势

✅ **简单清晰**：三层架构,职责明确
✅ **易于维护**：模块化设计
✅ **高可靠性**：重试机制、错误处理
✅ **易于扩展**：新增功能简单
✅ **轻量部署**：纯 API 调用

### 改进空间

🔄 **缓存机制**：避免重复 API 调用
🔄 **异步处理**：提升并发性能
🔄 **数据库**：持久化对话历史
🔄 **用户认证**：多用户支持

---

**📚 本文档持续更新中...**
