# AI 模拟面试系统 - 项目概览

## 📊 项目信息

- **项目名称**: AI 模拟面试系统 (AI Interview Coach)
- **版本**: 1.0.0
- **开发语言**: Python 3.9+
- **主要框架**: OpenAI API, Gradio
- **项目类型**: AI Agent 应用

## 🎯 项目目标

帮助求职者通过 AI 技术：
1. 优化和改进简历
2. 准备和练习面试
3. 提升求职竞争力

## ✨ 核心功能

### 1. 简历智能管理
- ✅ PDF 简历自动解析
- ✅ 简历内容提取和预览
- ✅ 支持中英文简历

### 2. 多维度简历评估
- ✅ 6 大维度专业评估
- ✅ 0-100 分量化评分
- ✅ 优缺点详细分析
- ✅ 可操作的改进建议
- ✅ 针对岗位的定制评估

### 3. 智能模拟面试
- ✅ 技术面试模式
- ✅ 行为面试模式
- ✅ 综合面试模式
- ✅ 基于简历的针对性提问
- ✅ 多轮对话深度追问
- ✅ 历史记录管理

### 4. 联网搜索增强
- ✅ DuckDuckGo 搜索集成
- ✅ SearXNG 搜索支持
- ✅ 自动降级和容错
- ✅ 搜索结果上下文增强

### 5. 多模型支持
- ✅ OpenAI (GPT-3.5, GPT-4)
- ✅ DeepSeek
- ✅ Qwen (通义千问)
- ✅ 其他 OpenAI 兼容 API

## 🏗️ 技术架构

### 核心技术栈
- **LLM 客户端**: OpenAI 官方库 (openai >= 1.0.0)
- **Web 框架**: Gradio 4.0+
- **PDF 解析**: PyMuPDF
- **Web 搜索**: ddgs (DuckDuckGo)
- **日志系统**: Loguru
- **配置管理**: python-dotenv

### 架构特点
- 模块化设计，低耦合高内聚
- 配置驱动，灵活可扩展
- 完善的错误处理和日志
- 直接使用 OpenAI API，无需额外框架
- 支持多种 LLM 后端

## 📁 项目结构

```
interview-coach/
├── config/                    # 配置模块
│   ├── llm_config.py         # LLM 配置
│   └── settings.py           # 系统配置
│
├── src/                       # 核心代码
│   ├── loaders/              # 简历加载器
│   │   └── resume_loader.py
│   ├── evaluator/            # 简历评估器
│   │   └── resume_evaluator.py
│   ├── interview/            # 面试 Agent
│   │   └── interview_agent.py
│   ├── tools/                # 工具集
│   │   └── web_search.py
│   └── utils/                # 工具函数
│       ├── logger.py
│       └── helpers.py
│
├── data/                      # 数据目录
│   ├── resumes/              # 简历存储
│   └── cache/                # 缓存
│
├── docs/                      # 文档
│   ├── FEATURES.md           # 功能介绍
│   ├── USER_GUIDE.md         # 用户指南
│   └── DEVELOPER_GUIDE.md    # 开发指南
│
├── logs/                      # 日志
├── output/                    # 输出
│
├── web_ui.py                 # Web UI 主程序
├── init_system.py            # 系统初始化
├── quick_start.py            # 快速入门示例
├── requirements.txt          # 依赖列表
├── .env.example              # 配置模板
├── start.sh                  # 启动脚本
└── README.md                 # 项目说明
```

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境
```bash
cp .env.example .env
# 编辑 .env，填写 API Key
```

### 3. 启动系统
```bash
./start.sh
# 或
python3 web_ui.py
```

### 4. 访问系统
打开浏览器访问: http://localhost:7860

## 📚 文档导航

### 面向不同用户群体

1. **普通用户** → [用户使用指南](docs/USER_GUIDE.md)
   - 如何上传简历
   - 如何评估简历
   - 如何进行模拟面试
   - 常见问题解答

2. **产品了解** → [功能介绍](docs/FEATURES.md)
   - 详细功能说明
   - 应用场景
   - 技术优势
   - 未来规划

3. **开发者** → [开发指南](docs/DEVELOPER_GUIDE.md)
   - 架构设计
   - 核心模块
   - 扩展开发
   - API 参考

## 💻 开发指南

### 代码规范
- 遵循 PEP 8
- 使用类型注解
- 添加文档字符串
- 完善的错误处理

### 扩展功能
- 添加新的面试类型
- 集成新的 LLM
- 支持更多简历格式
- 添加新的评估维度

### 测试
```bash
pytest tests/
```

## 🔧 配置说明

### LLM 配置
```ini
LLM_API_KEY=your-api-key
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
TEMPERATURE=0.7
```

### Web 搜索配置
```ini
ENABLE_WEB_SEARCH=true
WEB_SEARCH_ENGINE=duckduckgo
MAX_SEARCH_RESULTS=5
```

### 面试配置
```ini
MAX_HISTORY_TURNS=20
INTERVIEW_MODE=technical
```

## 📈 性能指标

### 响应时间（参考值）
- 简历加载: 1-3 秒
- 快速评分: 5-10 秒
- 完整评估: 10-30 秒
- 面试对话: 3-8 秒
- 联网搜索: +2-5 秒

### 支持规模
- 简历大小: < 10MB
- 简历页数: < 20 页
- 对话历史: 20 轮（可配置）
- 并发用户: 取决于部署方式

## 🔒 隐私和安全

- 简历在本地解析，不上传到第三方
- 仅与配置的 LLM API 通信
- 不存储用户数据到数据库
- 建议本地部署使用

## 🤝 贡献指南

欢迎贡献代码、报告问题、提出建议：

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 开源协议

MIT License

## 🙏 致谢

感谢以下开源项目：
- [OpenAI](https://github.com/openai/openai-python) - OpenAI Python 客户端
- [Gradio](https://github.com/gradio-app/gradio) - Web UI 框架
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - PDF 解析库
- [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) - 搜索工具

## 📞 联系方式

- GitHub Issues: 问题反馈和功能建议
- Email: 技术支持
- 文档: docs/ 目录

## 🗺️ 未来规划

### v1.1 (计划中)
- [ ] 支持 Word (DOCX) 格式
- [ ] 添加简历模板库
- [ ] 优化评估算法
- [ ] 增加更多面试类型

### v1.2 (计划中)
- [ ] 语音面试支持
- [ ] 面试录像分析
- [ ] 多语言支持
- [ ] 移动端适配

### v2.0 (规划中)
- [ ] 用户系统
- [ ] 数据持久化
- [ ] 团队协作功能
- [ ] HR 管理后台

## 📊 更新日志

### v1.0.0 (2025-12-20)
- ✨ 首次发布
- ✅ 简历 PDF 解析
- ✅ 多维度评估
- ✅ 模拟面试
- ✅ 联网搜索
- ✅ 多模型支持
- 📚 完整文档

---

**让 AI 助力你的职业发展！** 🎯
