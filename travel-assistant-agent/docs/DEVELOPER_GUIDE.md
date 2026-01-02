# 🛠️ 开发者指南

> 二次开发、模块说明、代码结构详解

## 📋 目录

- [项目结构](#项目结构)
- [核心模块说明](#核心模块说明)
- [Prompt 体系](#prompt-体系)
- [API 调用机制](#api-调用机制)
- [二次开发指南](#二次开发指南)
- [测试指南](#测试指南)

---

## 📁 项目结构

```
travel-assistant-agent/
├── app.py                      # 主程序入口（683行）
├── requirements.txt            # 依赖清单
├── .env                        # 环境配置（不提交到 git）
├── .env.example                # 环境配置示例
├── start.sh                    # 启动脚本
│
├── config/                     # 配置模块
│   ├── __init__.py
│   ├── prompts.py             # Prompt 配置（核心灵魂,270行）
│   ├── llm_config.py          # LLM 配置
│   └── settings.py            # 其他设置
│
├── data/                       # 数据目录
│   └── saved_itineraries/     # 保存的行程
│
├── docs/                       # 文档目录
│   ├── USER_GUIDE.md          # 用户使用指南
│   ├── DEVELOPER_GUIDE.md     # 本文档
│   └── ARCHITECTURE.md        # 架构设计文档
│
├── logs/                       # 日志目录（自动生成）
│
├── tests/                      # 测试文件
│   ├── test_text_api.py       # 文本 API 测试
│   └── test_multimodal_api.py # 多模态 API 测试
│
└── README.md                   # 项目介绍
```

---

## 🔧 核心模块说明

### 1. app.py - 主程序

**代码结构：**

```python
# ========== 1. 配置和导入（50行）==========
import os, base64, logging, gradio as gr, requests
from config.prompts import *

# 配置参数
API_KEY = os.getenv("API_KEY")
TEXT_MODEL_NAME = os.getenv("TEXT_MODEL_NAME", "qwen3-max")
MULTIMODAL_MODEL_NAME = os.getenv("MULTIMODAL_MODEL_NAME", "qwen-vl-plus")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1500"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.85"))
TEXT_API_TIMEOUT = int(os.getenv("TEXT_API_TIMEOUT", "60"))
MULTIMODAL_API_TIMEOUT = int(os.getenv("MULTIMODAL_API_TIMEOUT", "90"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# ========== 2. API 调用类（180行）==========
class TravelAssistantAPI:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = API_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def call_text_api(self, user_message: str, system_prompt: str = None, 
                     temperature: float = None, max_tokens: int = None) -> str:
        """调用文本 API"""
        # 实现重试逻辑、超时处理、错误处理
    
    def call_multimodal_api(self, image_path: str, user_query: str, 
                           system_prompt: str = None) -> str:
        """调用多模态 API"""
        # 实现图片 base64 编码、API 调用、错误处理

# ========== 3. 对话管理类（80行）==========
class ConversationManager:
    def __init__(self):
        self.history = []
        self.current_scenario = None
        self.user_requirements = {}
    
    def add_message(self, role: str, content: str):
        """添加消息到历史"""
    
    def get_context(self, last_n: int = 5) -> str:
        """获取最近 N 轮对话上下文"""
    
    def detect_scenario(self, user_input: str) -> Optional[str]:
        """检测用户需求场景"""

# ========== 4. 核心处理函数（150行）==========
def process_text_message(user_input: str, history: List) -> Tuple[List, str]:
    """处理文本消息"""
    
def process_image_upload(image_path: str, user_query: str, history: List) -> Tuple[List, str]:
    """处理图片上传"""

def save_itinerary(history: List) -> str:
    """保存行程"""

def export_itinerary(history: List) -> str:
    """导出行程"""

def clear_conversation() -> Tuple[List, str]:
    """清空对话"""

# ========== 5. UI 界面构建（200行）==========
def create_ui():
    """创建 Gradio 界面"""
    with gr.Blocks(css=custom_css) as demo:
        # 标题
        # Chatbot 组件
        # 文本输入
        # 图片上传
        # 快速建议按钮
        # 行程管理按钮

# ========== 6. 主程序启动（10行）==========
if __name__ == "__main__":
    demo = create_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860)
```

---

### 2. config/prompts.py - Prompt 配置

**这是整个系统的灵魂！**

```python
# ========== 1. 核心系统 Prompt ==========
AGENT_CORE_SYSTEM_PROMPT = """
你是一位具备自主思考能力的资深旅游管家 AI 助手...
【你的核心能力】
1. 主动需求挖掘
2. 多方案最优规划
3. 专业旅游分析
4. 任务拆解执行
5. 动态调整优化
6. 人群智能适配
7. 全局要素协同
"""

# ========== 2. 多模态识别 Prompt ==========
MULTIMODAL_IMAGE_PROMPT = """
请仔细分析用户上传的图片...
【识别重点】景点/酒店/美食/地图/票据
【返回格式】结构化、分点呈现
"""

# ========== 3. 场景化 Prompt ==========
SCENARIO_PROMPTS = {
    "亲子游": "优先儿童友好景点、低强度行程...",
    "老年游": "低强度景点、舒适度优先...",
    "学生穷游": "免费/低价景点、青旅...",
    "情侣游": "浪漫景点、情侣酒店...",
    "轻奢游": "高品质景点、五星酒店...",
    "境外游": "签证、货币、语言、应急..."
}

# ========== 4. Prompt 组合函数 ==========
def get_combined_prompt(
    base_prompt: str,
    scenario: Optional[str] = None,
    additional_context: Optional[str] = None
) -> str:
    """组合多个 Prompt"""
    combined = base_prompt
    if scenario and scenario in SCENARIO_PROMPTS:
        combined += "\n\n" + SCENARIO_PROMPTS[scenario]
    if additional_context:
        combined += "\n\n" + additional_context
    return combined
```

---

## 📝 Prompt 体系

### Prompt 设计原则

1. **清晰的角色定位**
   - "你是一位资深旅游管家 AI 助手"
   - 明确能力边界和专业领域

2. **结构化能力描述**
   - 7 大核心能力
   - 每个能力有具体说明

3. **明确的输出规范**
   - 简洁为先（800-1200字）
   - 结构化分点
   - 重点突出

4. **场景化适配**
   - 6 大场景 Prompt
   - 自动识别和组合

### Prompt 组合逻辑

```python
# 基础对话
prompt = AGENT_CORE_SYSTEM_PROMPT

# 检测到亲子游场景
if "亲子" in user_input:
    prompt = get_combined_prompt(
        AGENT_CORE_SYSTEM_PROMPT,
        scenario="亲子游"
    )

# 图片识别
if image_upload:
    prompt = get_combined_prompt(
        AGENT_CORE_SYSTEM_PROMPT,
        additional_context=MULTIMODAL_IMAGE_PROMPT
    )
```

---

## 🌐 API 调用机制

### 1. 文本 API 调用流程

```python
def call_text_api(self, user_message, system_prompt, temperature, max_tokens):
    """文本 API 调用"""
    
    # 1. 构建请求 payload
    payload = {
        "model": TEXT_MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": temperature or TEMPERATURE,
        "max_tokens": max_tokens or MAX_TOKENS
    }
    
    # 2. 重试逻辑（最多 3 次）
    for attempt in range(MAX_RETRIES):
        try:
            # 3. 发送 POST 请求
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=TEXT_API_TIMEOUT
            )
            
            # 4. 解析响应
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            
        except requests.exceptions.Timeout:
            # 超时重试
            time.sleep(5 * (attempt + 1))
            continue
            
        except Exception as e:
            logger.error(f"API 调用失败: {e}")
            return f"❌ 请求失败: {e}"
    
    return "❌ 请求超时,请稍后重试"
```

### 2. 多模态 API 调用流程

```python
def call_multimodal_api(self, image_path, user_query, system_prompt):
    """多模态 API 调用"""
    
    # 1. 读取图片并转 base64
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    # 2. 构建 payload
    payload = {
        "model": MULTIMODAL_MODEL_NAME,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": user_query},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
            ]
        }]
    }
    
    # 3. 发送请求（带重试）
    # ...类似文本 API 调用逻辑
```

### 3. 重试机制

```python
# 指数退避重试
for attempt in range(MAX_RETRIES):
    try:
        response = requests.post(...)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.Timeout:
        wait_time = 5 * (attempt + 1)  # 5s, 10s, 15s
        time.sleep(wait_time)
        continue
```

---

## 🔨 二次开发指南

### 1. 添加新的场景适配

**步骤：**

1. 在 `config/prompts.py` 的 `SCENARIO_PROMPTS` 中添加新场景：

```python
SCENARIO_PROMPTS = {
    ...
    "商务出差": """【商务出差专属优化】
- 优先选择交通便利的酒店（地铁站/机场附近）
- 推荐商务型酒店（会议室、商务中心、快速 WiFi）
- 行程高效紧凑,充分利用碎片时间
- 补充贴士：会议设施、打印服务、商务餐厅"""
}
```

2. 在 `ConversationManager.detect_scenario()` 中添加检测逻辑：

```python
def detect_scenario(self, user_input: str) -> Optional[str]:
    scenarios = {
        ...
        "商务出差": ["出差", "商务", "会议", "公司", "差旅"]
    }
    # ...检测逻辑
```

### 2. 支持新的大模型

**步骤：**

1. 在 `.env` 中添加新模型配置：

```env
# OpenAI API
OPENAI_API_KEY=sk-xxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-4-turbo
```

2. 修改 `TravelAssistantAPI` 类,添加模型选择逻辑：

```python
class TravelAssistantAPI:
    def __init__(self, provider="qwen"):
        self.provider = provider
        if provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.base_url = os.getenv("OPENAI_BASE_URL")
        elif provider == "qwen":
            self.api_key = os.getenv("API_KEY")
            self.base_url = os.getenv("API_BASE_URL")
```

### 3. 添加新功能模块

**示例：添加实时天气查询**

1. 创建新模块 `src/weather.py`：

```python
import requests

def get_weather(city: str) -> dict:
    """查询城市天气"""
    api_url = f"https://api.weather.com/v1/city/{city}"
    response = requests.get(api_url)
    return response.json()
```

2. 在 `app.py` 中集成：

```python
from src.weather import get_weather

def process_text_message(user_input, history):
    # ...原有逻辑
    
    # 检测是否需要查询天气
    if "天气" in user_input:
        city = extract_city(user_input)  # 提取城市名
        weather_info = get_weather(city)
        response = f"当前{city}天气：{weather_info['temperature']}℃,{weather_info['condition']}"
```

### 4. 自定义 UI 风格

修改 `create_ui()` 中的 CSS：

```python
custom_css = """
.gradio-container {
    font-family: 'YourFont', sans-serif !important;
    max-width: 1600px !important;
}
.primary-btn {
    background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%) !important;
}
"""
```

---

## 🧪 测试指南

### 1. API 测试

**文本 API 测试：**

```bash
python tests/test_text_api.py
```

**多模态 API 测试：**

```bash
python tests/test_multimodal_api.py
```

**一键测试：**

```bash
bash tests/test_all_apis.sh
```

### 2. 单元测试

创建 `tests/test_conversation.py`：

```python
import unittest
from app import ConversationManager

class TestConversationManager(unittest.TestCase):
    def setUp(self):
        self.mgr = ConversationManager()
    
    def test_add_message(self):
        self.mgr.add_message("user", "测试消息")
        self.assertEqual(len(self.mgr.history), 1)
    
    def test_detect_scenario(self):
        result = self.mgr.detect_scenario("带孩子去旅游")
        self.assertEqual(result, "亲子游")

if __name__ == "__main__":
    unittest.main()
```

运行测试：

```bash
python -m unittest tests/test_conversation.py
```

---

## 📊 性能优化建议

### 1. 减少 API 调用次数

```python
# 使用缓存避免重复调用
from functools import lru_cache

@lru_cache(maxsize=100)
def call_text_api_cached(user_message, system_prompt):
    return call_text_api(user_message, system_prompt)
```

### 2. 控制 token 消耗

```python
# 动态调整 max_tokens
def get_optimal_max_tokens(user_input):
    if len(user_input) < 50:
        return 800  # 简单问题
    elif len(user_input) < 200:
        return 1500  # 中等复杂度
    else:
        return 2000  # 复杂规划
```

### 3. 优化图片处理

```python
from PIL import Image

def optimize_image(image_path, max_size_mb=2):
    """压缩图片到指定大小"""
    img = Image.open(image_path)
    # 压缩逻辑
    img.save(image_path, optimize=True, quality=85)
```

---

## 🐛 常见开发问题

### 1. 依赖安装失败

```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. Gradio 界面不显示

```bash
# 检查端口占用
lsof -i :7860

# 更换端口
demo.launch(server_port=7861)
```

### 3. API 调用频繁失败

```bash
# 增加重试次数
MAX_RETRIES=5

# 增加超时时间
TEXT_API_TIMEOUT=120
```

---

## 📚 参考资源

- [Gradio 官方文档](https://gradio.app/docs/)
- [阿里云千问 API 文档](https://help.aliyun.com/zh/dashscope/)
- [Python requests 文档](https://requests.readthedocs.io/)
- [项目 GitHub 仓库](https://github.com/your-repo/travel-assistant-agent)

---

**🎉 祝开发顺利！**

如有问题,欢迎提交 Issue 或 Pull Request。
