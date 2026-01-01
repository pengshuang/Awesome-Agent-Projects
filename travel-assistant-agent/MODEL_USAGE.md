# 🤖 模型使用说明 - 智能旅游助手Agent

## 📋 模型分离架构

本系统支持**文本模型**和**多模态模型**分离配置，让您可以根据实际需求和预算灵活选择。

---

## 🎯 模型使用场景

### 📝 文本模型（TEXT_MODEL_NAME）

**使用场景**：所有纯文本任务
- ✅ 普通对话问答
- ✅ 旅游需求挖掘和追问
- ✅ 多方案行程规划生成
- ✅ 行程动态调整优化
- ✅ 应急方案建议
- ✅ 语音对讲的文本处理（语义理解部分）

**代码位置**：
```python
# app.py 中调用文本模型的函数
api_client.call_text_api()  # 使用 self.text_model
```

---

### 🖼️ 多模态模型（MULTIMODAL_MODEL_NAME）

**使用场景**：所有需要处理图片/视频的任务
- ✅ 景点图片识别
- ✅ 美食照片识别
- ✅ 酒店图片识别
- ✅ 地图截图分析
- ✅ 机票/高铁票识别
- ✅ 视频内容识别（如扩展）

**代码位置**：
```python
# app.py 中调用多模态模型的函数
api_client.call_multimodal_api()  # 使用 self.multimodal_model
```

---

## ⚙️ 配置方式

### 方案1：统一模型（推荐，简单）

适合Claude等原生支持多模态的模型：

```env
# .env 配置
TEXT_MODEL_NAME=claude-3-5-sonnet-20241022
MULTIMODAL_MODEL_NAME=claude-3-5-sonnet-20241022
```

**优点**：
- ✅ 配置简单，一个API密钥搞定
- ✅ Claude同一模型支持文本和多模态
- ✅ 无需切换模型，体验一致

**成本**：中等（Claude统一定价）

---

### 方案2：分离模型（成本优化）

文本用便宜的模型，图片识别用强大的模型：

```env
# .env 配置
TEXT_MODEL_NAME=gpt-3.5-turbo              # 文本便宜
MULTIMODAL_MODEL_NAME=gpt-4-vision-preview  # 图片强大
```

**优点**：
- ✅ 成本最优：文本用便宜的GPT-3.5（$0.001/1K tokens）
- ✅ 效果保证：图片识别用强大的GPT-4 Vision
- ✅ 灵活调整：根据预算随时切换

**成本**：最低（大部分是文本任务）

**估算**：
- 每次文本对话（500 tokens）：~$0.0005
- 每次图片识别（1000 tokens）：~$0.01
- 日常使用（80%文本 + 20%图片）：约节省60%成本

---

### 方案3：全用高端模型（最强效果）

```env
# .env 配置
TEXT_MODEL_NAME=gpt-4-turbo-preview
MULTIMODAL_MODEL_NAME=gpt-4-vision-preview
```

**优点**：
- ✅ 文本回答最优质
- ✅ 图片识别最准确
- ✅ 适合商业场景

**成本**：最高

---

### 方案4：混合模型（平衡）

```env
# .env 配置
TEXT_MODEL_NAME=claude-3-5-sonnet-20241022   # Claude文本
MULTIMODAL_MODEL_NAME=gpt-4-vision-preview   # OpenAI视觉
```

**优点**：
- ✅ 结合两家优势
- ✅ Claude文本性价比高
- ✅ GPT-4V图片识别准确

**注意**：需要两个API密钥

---

## 🔍 代码实现验证

### 核心类实现

```python
class TravelAssistantAPI:
    def __init__(self):
        self.text_model = TEXT_MODEL_NAME        # 文本模型
        self.multimodal_model = MULTIMODAL_MODEL_NAME  # 多模态模型
    
    def call_text_api(self, ...):
        # ✅ 使用文本模型
        payload = {"model": self.text_model, ...}
    
    def call_multimodal_api(self, ...):
        # ✅ 使用多模态模型
        payload = {"model": self.multimodal_model, ...}
```

### 任务分配验证

| 功能 | 调用函数 | 使用模型 | 验证状态 |
|------|---------|---------|---------|
| 文本对话 | `process_text_message()` → `call_text_api()` | `TEXT_MODEL_NAME` | ✅ |
| 图片识别 | `process_image_upload()` → `call_multimodal_api()` | `MULTIMODAL_MODEL_NAME` | ✅ |
| 语音处理 | `process_voice_input()` → `call_text_api()` | `TEXT_MODEL_NAME` | ✅ |
| 行程规划 | `process_text_message()` → `call_text_api()` | `TEXT_MODEL_NAME` | ✅ |

---

## 💰 成本估算对比

### 场景：日常使用（100次请求）
- 80次文本对话（平均500 tokens/次）
- 20次图片识别（平均1000 tokens/次）

| 方案 | 文本成本 | 图片成本 | 总成本 | 节省比例 |
|------|---------|---------|--------|---------|
| **方案1**：全用Claude Sonnet | $0.80 | $0.30 | **$1.10** | 基准 |
| **方案2**：GPT-3.5 + GPT-4V | $0.04 | $0.20 | **$0.24** | 节省78% |
| **方案3**：全用GPT-4 | $2.40 | $0.20 | **$2.60** | -136% |

💡 **推荐**：方案2最经济，方案1最简单

---

## 🛠️ 切换模型步骤

### 1️⃣ 修改配置文件

编辑 `.env` 文件：
```bash
vim .env
# 或
nano .env
```

### 2️⃣ 更新模型配置

```env
# 改为您想要的模型
TEXT_MODEL_NAME=your_text_model
MULTIMODAL_MODEL_NAME=your_multimodal_model
```

### 3️⃣ 重启应用

```bash
# 停止当前应用（Ctrl+C）
# 重新启动
python app.py
```

### 4️⃣ 验证配置

启动时会显示：
```
🚀 正在启动智能旅游助手Agent...
📝 文本模型：your_text_model
🖼️  多模态模型：your_multimodal_model
```

---

## 🔧 高级配置

### 自动回退机制

如果只配置了 `TEXT_MODEL_NAME`，系统会自动使用文本模型处理多模态任务：

```env
# 只配置文本模型
TEXT_MODEL_NAME=claude-3-5-sonnet-20241022
# MULTIMODAL_MODEL_NAME 留空或不配置

# 结果：两种任务都用 claude-3-5-sonnet-20241022
```

### 兼容旧配置

如果您之前使用的是 `MODEL_NAME`，系统会自动兼容：

```env
# 旧配置（仍然有效）
MODEL_NAME=claude-3-5-sonnet-20241022

# 系统会自动转换为
TEXT_MODEL_NAME=claude-3-5-sonnet-20241022
MULTIMODAL_MODEL_NAME=claude-3-5-sonnet-20241022
```

---

## 📊 支持的模型列表

### Claude系列（推荐）
```env
# 性价比之王（文本+多模态统一）
claude-3-5-sonnet-20241022

# 更强大的版本
claude-3-opus-20240229
```

### OpenAI系列
```env
# 文本模型
gpt-4-turbo-preview    # 强大但贵
gpt-4                  # 稳定版
gpt-3.5-turbo         # 经济版

# 多模态模型
gpt-4-vision-preview   # 专门的视觉模型
gpt-4-turbo           # 统一模型（含视觉）
```

### 其他兼容模型
只要支持OpenAI API格式的模型都可以使用

---

## ⚠️ 注意事项

### 1. API密钥要求
- 使用Claude：只需一个Anthropic API密钥
- 使用OpenAI：只需一个OpenAI API密钥
- 混合使用：需要对应服务商的API密钥

### 2. API地址配置
```env
# Claude
API_BASE_URL=https://api.anthropic.com

# OpenAI
API_BASE_URL=https://api.openai.com
```

### 3. 模型能力要求
- 文本模型：必须支持文本对话
- 多模态模型：必须支持图片输入（vision capability）

### 4. 调试建议
启动时查看日志确认使用的模型：
```
📝 文本模型：claude-3-5-sonnet-20241022
🖼️  多模态模型：claude-3-5-sonnet-20241022
   （使用统一模型处理文本和多模态任务）
```

---

## 🎯 最佳实践建议

### 个人使用
**推荐**：方案1（全用Claude统一模型）
- 配置简单，一个API密钥
- 性价比高，成本适中
- 体验一致

### 开发测试
**推荐**：方案2（GPT-3.5 + GPT-4V）
- 成本最低，节省预算
- 测试频繁，文本用便宜的
- 图片识别保证效果

### 商业部署
**推荐**：方案3（全用GPT-4）或 方案1（Claude Sonnet）
- 追求最佳效果
- 成本可接受
- 用户体验优先

---

## 📞 技术支持

如有疑问，请查看：
- [README.md](README.md) - 完整文档
- [.env.example](.env.example) - 配置示例

---

<div align="center">
  <p><strong>🤖 灵活配置，按需选择</strong></p>
  <p>文本和多模态任务分离，成本优化与效果兼顾</p>
</div>
