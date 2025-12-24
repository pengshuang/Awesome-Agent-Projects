# 快速开始指南

欢迎使用 Multi-Agent 数据合成系统！

## 🚀 5 分钟快速上手

### 步骤 1: 配置环境

```bash
# 复制环境变量模板
cp .env.example .env
```

编辑 `.env` 文件，配置你的 API Key：

```bash
# 使用 OpenAI
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1

# 使用 Qwen（通义千问）
# OPENAI_API_KEY=your-qwen-api-key
# OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

# 使用 Kimi（月之暗面）
# OPENAI_API_KEY=your-kimi-api-key
# OPENAI_API_BASE=https://api.moonshot.cn/v1
```

### 步骤 2: 启动系统

```bash
# 赋予执行权限（首次运行）
chmod +x start.sh

# 启动系统
./start.sh
```

系统会自动：
- ✅ 创建虚拟环境
- ✅ 安装所有依赖
- ✅ 初始化目录结构
- ✅ 启动 Web UI

### 步骤 3: 访问界面

浏览器会自动打开，或手动访问：

```
http://localhost:7860
```

### 步骤 4: 生成第一个数据集

#### 方式一：使用示例文档

1. 点击"上传文档文件"
2. 选择 `data/example_document.md`
3. 选择任务类型："逻辑推理类"
4. 设置迭代次数：5
5. 点击"🚀 开始合成"

#### 方式二：输入自己的文本

1. 在文本框中粘贴你的文档内容（至少500字）
2. 选择合适的任务类型
3. 设置迭代次数：5-10
4. 点击"🚀 开始合成"

### 步骤 5: 下载结果

生成完成后：
1. 查看右侧展示的问答对
2. 点击"下载结果"按钮
3. 获取 JSON 格式的数据集

## 📋 任务类型说明

选择最适合你文档的类型：

| 任务类型 | 适用场景 | 示例 |
|---------|---------|------|
| 逻辑推理类 | 观点论证、因果分析 | "为什么作者认为深度学习优于传统方法？" |
| 数值计算类 | 数据分析、统计计算 | "根据文档数据，计算增长率" |
| 信息查询类 | 信息检索、事实查询 | "文档中提到了哪些AI应用领域？" |
| 总结摘要类 | 内容概括、要点提炼 | "总结人工智能发展的三个阶段" |

## ⚙️ 参数调优建议

### 迭代次数选择

- **3-5 次**：快速测试，生成 2-4 个问答对
- **5-10 次**：标准使用，生成 4-8 个问答对（推荐）
- **10-15 次**：大量数据，生成 8-12 个问答对
- **15-20 次**：极限模式，生成 12-18 个问答对

### 文档长度建议

- **500-1000 字**：设置 3-5 次迭代
- **1000-3000 字**：设置 5-10 次迭代（最佳）
- **3000-5000 字**：设置 10-15 次迭代
- **5000+ 字**：设置 15-20 次迭代

## 📊 输出格式

生成的 JSON 文件格式：

```json
[
  {
    "question": "为什么1980年代的专家系统最终失败了？",
    "answer": "专家系统失败的主要原因包括：1) 知识获取困难...",
    "reasoning": "这个问题需要理解专家系统的局限性...",
    "task_type": "逻辑推理类",
    "iteration": 1,
    "timestamp": "2024-12-24T10:30:00"
  }
]
```

## 🔍 查看日志

如果遇到问题，查看日志文件：

```bash
# 查看最新日志
tail -f logs/system_*.log

# 或查看 Web UI 日志
tail -f logs/web_ui_*.log
```

## ❓ 常见问题

### Q: API 调用失败？

**检查清单：**
- ✅ `.env` 文件中的 API Key 是否正确
- ✅ `OPENAI_API_BASE` 是否配置正确
- ✅ 网络连接是否正常
- ✅ API Key 是否有足够余额

### Q: 生成速度慢？

**正常现象！** 每次迭代需要：
- 提议者生成问题（1次LLM调用）
- 求解者尝试回答（1次LLM调用）
- 验证者检查质量（1次LLM调用）

**预计时间：**
- 5次迭代 ≈ 3-5分钟
- 10次迭代 ≈ 6-10分钟

### Q: 生成的数据质量不好？

**优化建议：**
1. 确保文档内容充分、结构清晰
2. 选择匹配的任务类型
3. 增加迭代次数（后续问题会更好）
4. 使用更强的模型（如 GPT-4）
5. 调整 Prompt（参考开发指南）

## 🎯 最佳实践

### 1. 文档准备

✅ **好的文档：**
```
人工智能的发展经历了多个阶段。1950年代，艾伦·图灵提出了
图灵测试...（内容充实、逻辑清晰）
```

❌ **不好的文档：**
```
AI很重要。
深度学习很厉害。
（过于简单、信息不足）
```

### 2. 批量生成策略

```bash
# 为多个文档批量生成数据
for doc in data/documents/*.md; do
    # 使用 API 或 CLI 模式处理
    python cli_generate.py --input "$doc" --iterations 10
done
```

### 3. 数据后处理

```python
import json

# 读取生成的数据
with open('data/outputs/qa_pairs_xxx.json', 'r') as f:
    data = json.load(f)

# 筛选高质量数据（示例）
filtered = [
    qa for qa in data 
    if len(qa['question']) > 20 and len(qa['answer']) > 50
]

# 保存筛选结果
with open('filtered_qa_pairs.json', 'w') as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)
```

## 📖 更多资源

- 📘 [用户使用指南](docs/USER_GUIDE.md) - 详细使用说明
- 🛠️ [开发指南](docs/DEVELOPER_GUIDE.md) - 二次开发文档
- 📝 [README](README.md) - 项目总览

## 🎉 开始你的数据合成之旅！

现在你已经准备好了！开始生成高质量的训练数据吧！

```bash
./start.sh
```

---

**提示：** 首次使用建议从示例文档开始测试，熟悉流程后再处理自己的文档。

祝使用愉快！🚀
