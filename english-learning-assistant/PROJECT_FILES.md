# 📦 项目文件说明

## 🎯 核心启动文件

| 文件 | 说明 |
|------|------|
| `web_ui.py` | **主程序** - Gradio Web界面入口 |
| `start.sh` | **启动脚本** - 一键启动应用 |
| `init_system.py` | **初始化脚本** - 首次运行配置 |

## ⚙️ 配置文件

| 文件/目录 | 说明 |
|------|------|
| `.env` | 环境配置（需自己创建，参考.env.example） |
| `.env.example` | 配置模板 |
| `config/settings.py` | 系统配置类 |
| `config/llm_config.py` | LLM API配置模型 |
| `config/prompts.py` | **Prompt管理** - 所有AI提示词 |

## 🤖 核心代码

### Agent智能体
- `src/agent/english_agent.py` - 英语学习Agent，负责对话管理、学习档案、上下文记忆

### API客户端
- `src/api/llm_client.py` - LLM文本对话客户端
- `src/api/tts_client.py` - 文字转语音客户端
- `src/api/stt_client.py` - 语音转文字客户端
- `src/api/vision_client.py` - 图片/PDF多模态客户端

### 业务服务
- `src/services/translation.py` - 翻译解析服务（通用翻译、单词、句子）
- `src/services/writing.py` - 写作批改和润色服务
- `src/services/speaking.py` - 口语练习和评估服务
- `src/services/multimodal.py` - 多模态文件解析服务

### 工具模块
- `src/utils/logger.py` - 日志系统（控制台+文件）
- `src/utils/storage.py` - 数据存储管理

## 📚 文档

| 文件 | 目标读者 | 内容 |
|------|----------|------|
| `README.md` | 所有人 | 项目介绍、功能特性、快速开始 |
| `QUICKSTART.md` | 新用户 | 快速启动指南 |
| `docs/USER_GUIDE.md` | 普通用户 | 详细使用教程，每个功能的使用方法 |
| `docs/DEVELOPER_GUIDE.md` | 开发者 | 二次开发指南，代码结构讲解 |
| `docs/ARCHITECTURE.md` | 架构师/开发者 | 系统架构设计，技术选型说明 |

## 📁 数据目录

```
data/
├── history/        # 学习记录（对话历史、练习记录）
└── uploads/        # 用户上传的图片和PDF文件
```

## 📝 日志目录

```
logs/
├── app.log         # 应用日志（所有级别）
├── error.log       # 错误日志
└── api.log         # API调用日志（记录每次Prompt）
```

## 🔧 其他文件

| 文件 | 说明 |
|------|------|
| `requirements.txt` | Python依赖清单 |
| `LICENSE` | MIT开源协议 |
| `.gitignore` | Git忽略文件配置 |

---

## 🎯 关键代码位置速查

### 想修改AI的回复风格？
👉 编辑 `config/prompts.py` 中的相应Prompt模板

### 想添加新功能？
👉 参考 `docs/DEVELOPER_GUIDE.md` 的"扩展开发"章节

### 想更换API服务商？
👉 修改 `.env` 中的 `LLM_API_BASE` 和 `LLM_MODEL`

### 想调整学习难度定义？
👉 编辑 `src/agent/english_agent.py` 中的 `level_descriptions`

### 想修改界面布局？
👉 编辑 `web_ui.py` 中的 `create_ui()` 函数

### 想查看API调用日志？
👉 查看 `logs/api.log` 文件

---

## 📊 项目统计

- **总代码文件**: 约20个Python文件
- **代码行数**: 约5000+ 行
- **核心功能模块**: 6个
- **文档页数**: 3个主要文档
- **配置项**: 20+ 个可配置参数

---

## 🚀 从零到运行只需3步

1. **初始化**: `python3 init_system.py`
2. **配置**: 编辑 `.env` 填入API密钥
3. **启动**: `./start.sh`

就这么简单！🎉
