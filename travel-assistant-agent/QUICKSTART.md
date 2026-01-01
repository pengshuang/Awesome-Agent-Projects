# 🌏 智能旅游助手Agent - 快速开始指南

## 📦 安装步骤

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置API密钥
```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑.env文件，填入您的API密钥
# 将 your_api_key_here 替换为真实的API密钥
```

### 3. 启动应用
```bash
# 方式1：直接运行Python脚本
python app.py

# 方式2：使用启动脚本（推荐）
chmod +x start.sh
./start.sh
```

## 🎯 快速测试

启动成功后，尝试以下对话：

### 示例1：简单规划
```
输入：帮我规划一个3天的杭州行程
```

### 示例2：需求挖掘
```
输入：想去旅游，不知道去哪
（Agent会主动询问：目的地、天数、预算、偏好等信息）
```

### 示例3：场景适配
```
输入：带爸妈去成都玩5天
（Agent会自动识别为老年游，适配低强度行程）
```

### 示例4：动态调整
```
第1轮：帮我规划杭州3天行程
第2轮：行程太赶了，能不能放慢节奏？
（Agent会在原方案基础上优化调整）
```

## 🖼️ 图片识别测试

1. 点击"图片识别"标签
2. 上传景点/美食/酒店照片
3. 点击"识别图片"按钮
4. 查看AI返回的识别结果和攻略建议

## 🎤 语音交互测试（简化版）

1. 点击"语音对讲"标签
2. 点击麦克风按钮录制语音
3. 点击"处理语音"按钮
4. 查看语音识别结果和回答

## 💾 保存和导出

- **保存行程**：点击"保存行程"按钮，文件保存在 `data/saved_itineraries/` 目录
- **导出行程**：点击"行程导出"标签，然后点击"导出为文本"按钮

## ⚙️ 配置说明

### API配置（.env文件）
```env
API_KEY=your_api_key_here          # 必填
API_BASE_URL=https://api.anthropic.com
MODEL_NAME=claude-3-5-sonnet-20241022
MAX_TOKENS=4096
TEMPERATURE=0.85
```

### 支持的模型
- Claude: `claude-3-5-sonnet-20241022` (推荐)
- OpenAI: `gpt-4-turbo-preview`
- 其他兼容OpenAI API格式的模型

## 🐛 常见问题

### API调用失败
- 检查API密钥是否正确
- 检查网络连接
- 检查API余额

### 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 重新安装
pip install -r requirements.txt --force-reinstall
```

### 端口被占用
修改 `app.py` 中的端口号：
```python
app.launch(
    server_port=7861  # 改为其他端口
)
```

## 📚 更多文档

完整文档请查看 [README.md](README.md)

---

祝您使用愉快！🎉
