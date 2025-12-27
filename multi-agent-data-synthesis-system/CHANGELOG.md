# 更新日志

所有重要的项目变更都会记录在此文档中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

## [2.0.0] - 2025-12-25

### 新增功能

#### Web UI 增强
- ✨ **Prompts 配置界面**：新增"⚙️ Prompts 配置"标签页，支持实时修改三个 Agent 的提示词
  - Proposer: system prompt、user_first prompt、user_iterative prompt
  - Solver: system prompt、user prompt
  - Validator: system prompt、user prompt
- 🎛️ **参数控制**：新增 Temperature 和评分阈值滑块配置
  - Temperature: 0.0-2.0（控制生成随机性）
  - 评分阈值: 1.0-10.0（控制质量筛选标准）
- ⏹️ **停止控制**：新增停止按钮，支持随时中断生成流程
- 🎨 **视觉优化**：
  - 三个 Agent 输出使用不同颜色背景块区分（红/蓝/绿）
  - 实时迭代内容显示在可滚动框中（最大高度 600px）
  - 实时日志字体大小优化
  - 推理步骤自动去除重复序号

#### 验证机制改进
- 📊 **评分制度**：从布尔判断（通过/不通过）改为 1-10 分精细评分
  - ValidatorOutput 模型：`is_valid: bool` → `score: float`
  - 新增 `score_threshold` 配置参数（默认 7.0）
  - 生成的 QA pair 包含 score 字段
- 📈 **评分标准**：
  - 9-10分：完美答案
  - 7-8分：正确答案
  - 5-6分：基本正确
  - 3-4分：部分正确
  - 1-2分：严重错误

#### 错误处理增强
- 🛡️ **JSON 解析容错**：三个 Agent 都添加了 JSON 解析错误处理
  - 格式错误时返回默认值而非抛出异常
  - 记录详细错误日志便于调试
- 🔄 **优雅降级**：Agent 执行失败时不再中断整个流程
  - Proposer/Solver/Validator 失败时使用默认值
  - 失败迭代计入 `failed_attempts` 而非终止
- 🔗 **兼容性改进**：history_buffer 支持 dict 和对象两种格式

### 修改

#### 配置文件
- `config/settings.py`：
  - 新增 `score_threshold: float = 7.0` 配置
- `config/prompts.py`：
  - 更新 validator prompt 为评分制
  - 添加详细的评分标准说明

#### 核心代码
- `src/models.py`：
  - ValidatorOutput: `is_valid` → `score`（1-10 分制）
- `src/agents.py`：
  - 所有 Agent 添加 JSON 解析错误处理
  - ProposerAgent: 支持 dict/对象混合格式的 history_buffer
  - ValidatorAgent: 输出评分而非布尔值
- `src/graph.py`：
  - 导入 settings 模块
  - 验证逻辑基于 score 和 threshold
  - 移除节点错误时的流程中断逻辑
  - QA pair 添加 score 字段

#### Web UI
- `web_ui.py`：
  - 添加全局 `stop_flag` 支持停止控制
  - 新增 Prompts 配置 UI（三个 accordion）
  - 新增 Temperature 和评分阈值滑块
  - 新增停止按钮和处理函数
  - 添加彩色样式类（proposer-block、solver-block、validator-block）
  - 迭代显示框添加滚动和样式
  - 优化 `format_iteration_detail` 函数
  - 推理步骤自动去除重复序号
  - 停止时保存已生成的有效问答对

### 文档更新
- 📚 **STRUCTURE.md**：更新项目结构说明，详细描述 v2.0 新功能
- 📚 **README.md**：
  - 添加 v2.0 新特性说明
  - 更新配置说明（包含评分阈值）
  - 更新 Prompt 定制说明（Web UI + 配置文件）
  - 更新输出格式（包含 score 字段）
  - 添加验证评分标准说明
- 📚 **CHANGELOG.md**：新增本文档

### 技术改进
- 🔧 更好的错误恢复机制
- 📊 更精细的质量控制
- 🎨 更好的用户体验
- 🛡️ 更健壮的容错能力

---

## [1.0.0] - 2024-12-24

### 初始版本

#### 核心功能
- 🤖 三智能体协作系统（Proposer/Solver/Validator）
- 🔄 Iterative Curriculum Learning 机制
- 📊 四种任务类型支持
- 🎨 Gradio Web UI
- 📝 完整的日志系统
- 🛠️ CLI 命令行工具

#### 基础架构
- LangGraph 工作流编排
- Pydantic 数据模型
- 配置化设计
- 模块化代码结构

---

## 待办事项

### 计划功能
- [ ] 支持更多任务类型
- [ ] 批量文档处理
- [ ] 数据质量统计报告
- [ ] 导出多种格式（CSV、Excel）
- [ ] Agent 性能监控面板
- [ ] 支持更多 LLM 提供商
- [ ] 问答对相似度检测（去重）
- [ ] 自定义评分权重配置

### 优化方向
- [ ] 提升生成速度
- [ ] 降低 API 成本
- [ ] 改进 Prompt 工程
- [ ] 增强错误提示
- [ ] 优化内存使用
