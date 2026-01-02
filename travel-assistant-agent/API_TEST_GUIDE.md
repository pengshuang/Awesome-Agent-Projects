# API 测试指南

本目录包含两个测试脚本，用于验证第三方 LLM API 是否可用。

## 文件说明

### 1. `test_text_api.py` - 文本 LLM API 测试
测试阿里云 DashScope qwen 文本模型的可用性。

**功能：**
- ✅ 检查 API 配置（密钥、URL、模型名称）
- ✅ 发送测试请求到文本 API
- ✅ 验证响应格式正确性
- ✅ 显示 Token 使用情况
- ✅ 记录详细的网络和性能信息

**使用方法：**
```bash
# 基础用法
python test_text_api.py

# 输出示例
[2026-01-02 10:30:00] INFO - 🧪 开始测试文本 LLM API
[2026-01-02 10:30:00] INFO - 📝 配置信息:
[2026-01-02 10:30:00] INFO -   • API 密钥: ✅ 已配置 (长度: 32)
[2026-01-02 10:30:00] INFO -   • API URL: https://dashscope.aliyuncs.com/compatible-mode/v1
[2026-01-02 10:30:00] INFO -   • 模型名称: qwen3-max
...
[2026-01-02 10:30:05] INFO - ✅ 文本 API 测试成功！
```

---

### 2. `test_multimodal_api.py` - 多模态 LLM API 测试
测试阿里云 DashScope qwen-vl 视觉模型的可用性。

**功能：**
- ✅ 检查 API 配置（密钥、URL、模型名称）
- ✅ 创建测试图片或使用指定的图片
- ✅ 对图片进行 Base64 编码
- ✅ 发送多模态请求到 Vision API
- ✅ 验证响应格式正确性
- ✅ 显示 Token 使用情况

**使用方法：**
```bash
# 使用内置测试图片
python test_multimodal_api.py

# 使用自定义图片
python test_multimodal_api.py --image /path/to/your/image.jpg

# 输出示例
[2026-01-02 10:35:00] INFO - 🧪 开始测试多模态 LLM API
[2026-01-02 10:35:00] INFO - 📝 配置信息:
[2026-01-02 10:35:00] INFO -   • API 密钥: ✅ 已配置 (长度: 32)
[2026-01-02 10:35:00] INFO -   • 模型名称: qwen-vl-plus
...
[2026-01-02 10:35:10] INFO - ✅ 多模态 API 测试成功！
```

---

## 环境配置

确保 `.env` 文件中已配置以下参数：

```dotenv
# API 密钥（必填）
API_KEY=your_api_key_here

# API 地址
API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 模型配置
TEXT_MODEL_NAME=qwen3-max
MULTIMODAL_MODEL_NAME=qwen-vl-plus

# 超时配置（秒）
TEXT_API_TIMEOUT=60
MULTIMODAL_API_TIMEOUT=90

# 其他参数
MAX_TOKENS=4096
TEMPERATURE=0.85
```

---

## 一键测试脚本

创建 `test_all_apis.sh` 快速测试所有 API：

```bash
#!/bin/bash
echo "🧪 开始 API 测试..."
echo ""

echo "1️⃣  测试文本 API..."
python test_text_api.py
TEXT_RESULT=$?

echo ""
echo "2️⃣  测试多模态 API..."
python test_multimodal_api.py
MULTIMODAL_RESULT=$?

echo ""
echo "=" 
if [ $TEXT_RESULT -eq 0 ] && [ $MULTIMODAL_RESULT -eq 0 ]; then
    echo "✅ 所有 API 测试通过！"
    exit 0
else
    echo "❌ 有 API 测试失败，请检查配置和网络"
    exit 1
fi
```

使用方法：
```bash
chmod +x test_all_apis.sh
./test_all_apis.sh
```

---

## 故障排查

### 问题 1: API 密钥未配置
**错误信息：** `❌ API 密钥未配置`

**解决方案：**
1. 打开 `.env` 文件
2. 在 `API_KEY=` 后添加您的 API 密钥
3. 保存文件重新运行

### 问题 2: 请求超时
**错误信息：** `❌ 请求超时 (超过 60s)`

**解决方案：**
1. 检查网络连接
2. 增加超时时间，在 `.env` 中修改：
   ```dotenv
   TEXT_API_TIMEOUT=120
   MULTIMODAL_API_TIMEOUT=150
   ```

### 问题 3: 连接错误
**错误信息：** `❌ 连接错误`

**解决方案：**
1. 检查 API_BASE_URL 是否正确
2. 检查网络连接
3. 尝试 ping API 服务器：
   ```bash
   curl -I https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
   ```

### 问题 4: HTTP 404 错误
**错误信息：** `❌ HTTP 错误 404`

**解决方案：**
1. 检查 API_BASE_URL 末尾是否有 `/v1`
2. 正确的 URL 应该是：`https://dashscope.aliyuncs.com/compatible-mode/v1`
3. 不要添加 `/chat/completions`

### 问题 5: API 密钥无效
**错误信息：** `❌ HTTP 错误 401`

**解决方案：**
1. 检查 API_KEY 是否正确复制（无多余空格）
2. 确认 API_KEY 未过期
3. 从 https://dashscope.console.aliyun.com 获取新的 API 密钥

---

## 日志详解

### 成功日志示例（文本 API）
```
✅ HTTP 状态码正常 (200 OK)
✅ 响应格式正确
📝 AI 回复 (45 字符):
────────────────────────────────────
旅游是对世界的探索，是心灵的放松...
────────────────────────────────────
📊 Token 使用情况:
  • 输入: 23 tokens
  • 输出: 45 tokens
  • 总计: 68 tokens
```

### 警告日志示例
```
⏳ 请求超时 (超过 60s)
💡 建议: 检查网络连接或增加超时时间
```

---

## 进阶用法

### 自定义测试消息（文本 API）
编辑 `test_text_api.py` 第 89 行：
```python
test_message = "你想测试的自定义消息"
```

### 自定义测试图片（多模态 API）
使用命令行参数：
```bash
python test_multimodal_api.py --image /path/to/custom/image.png
```

### 修改模型配置
在 `.env` 中修改：
```dotenv
# 文本模型选项: qwen3-max, qwen-max, qwen-turbo 等
TEXT_MODEL_NAME=qwen-max

# 视觉模型选项: qwen-vl-plus, qwen-vl-max 等
MULTIMODAL_MODEL_NAME=qwen-vl-max
```

---

## 预期输出

### ✅ 成功状态码
- `200 OK` - 请求成功
- 响应包含 `choices` 和有效的消息内容

### ❌ 常见错误状态码
- `400 Bad Request` - 请求格式有误
- `401 Unauthorized` - API 密钥无效
- `403 Forbidden` - 无访问权限
- `404 Not Found` - API 端点不存在
- `500 Internal Server Error` - 服务器错误
- `503 Service Unavailable` - 服务暂不可用

---

## 性能基准

基于正常网络条件的预期性能：

| 指标 | 文本 API | 多模态 API |
|------|---------|----------|
| 平均响应时间 | 3-8s | 5-15s |
| 超时设置 | 60s | 90s |
| 每次请求 Token | 20-50 | 100-200 |

---

## 相关文件

- `.env` - 环境变量配置文件
- `app.py` - 主应用程序
- `requirements.txt` - 依赖包列表

---

## 获取帮助

如遇到问题，请检查：
1. ✅ API 密钥是否正确
2. ✅ 网络连接是否正常
3. ✅ `.env` 配置是否完整
4. ✅ 查看详细日志信息
5. ✅ 检查 API 服务状态

---

**最后更新：2026-01-02**
