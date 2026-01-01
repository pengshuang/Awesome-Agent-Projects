# 🚀 快速启动指南

## 第一步：初始化系统

```bash
cd english-learning-assistant
python3 init_system.py
```

## 第二步：配置API密钥

编辑 `.env` 文件，填入你的API密钥：

```env
LLM_API_KEY=你的API密钥
```

**获取API密钥：**
- 通义千问：https://dashscope.aliyun.com/

## 第三步：启动应用

```bash
./start.sh
```

或者：

```bash
pip install -r requirements.txt
python3 web_ui.py
```

## 第四步：访问界面

在浏览器中打开：
```
http://localhost:7860
```

---

## 主要功能

### 1. 💬 AI智能对话
- 与AI英语导师对话练习
- 选择难度：初级/中级/高级
- 自动纠错和学习指导

### 2. 🔤 翻译解析
- 通用翻译（中英互译）
- 单词深度解析
- 长难句分析

### 3. ✍️ 写作批改
- 作文批改（语法、词汇、逻辑）
- 写作润色（学术/商务/日常）

### 4. 🎤 口语练习
- 跟读练习（英式/美式发音）
- 发音评估打分
- 语音识别

### 5. 📄 图片/PDF解析
- 上传图片识别英文内容
- PDF文档翻译讲解

### 6. ⚙️ Prompt管理
- 查看和调整系统Prompt
- 自定义AI回复风格

---

## 常见问题

**Q: 启动失败？**
- 检查Python版本（需要3.8+）
- 检查API密钥是否配置
- 查看 `logs/error.log` 日志

**Q: API调用失败？**
- 检查网络连接
- 确认API密钥有效
- 查看API余额

**Q: 语音功能无法使用？**
- 使用Chrome浏览器
- 允许麦克风权限
- 检查麦克风设备

---

## 文档

- 📖 [用户指南](docs/USER_GUIDE.md) - 详细功能说明
- 🔧 [开发指南](docs/DEVELOPER_GUIDE.md) - 二次开发文档
- 🏗️ [架构设计](docs/ARCHITECTURE.md) - 系统架构说明

---

## 技术支持

遇到问题？
1. 查看日志文件：`logs/`
2. 查阅文档
3. 提交Issue

---

**祝你学习愉快！🎓**
