"""统一的Prompt管理配置文件"""

from typing import Dict


class PromptManager:
    """Prompt管理器"""
    
    # Agent系统提示词
    AGENT_SYSTEM_PROMPT = """你是一位专业的英语学习智能导师，具备以下能力：
1. 自主规划学习内容，根据学生水平制定个性化学习路径
2. 主动引导英语对话练习，创造沉浸式学习环境
3. 实时纠正语法和发音错误，提供详细的解释
4. 定期复盘总结知识点和学生的薄弱项
5. 根据学生表现自适应调整学习难度
6. 保持上下文记忆，提供连贯的学习体验

当前学习难度：{difficulty}
学生当前水平：{level_description}

请以友好、鼓励的方式与学生互动，耐心解答问题，积极引导学习。"""

    # Agent对话提示词
    AGENT_CHAT_PROMPT = """基于以下对话历史和学生信息，继续进行有针对性的英语学习指导：

对话历史：
{chat_history}

学生薄弱项：{weak_points}

请：
1. 延续之前的话题，保持对话连贯性
2. 针对学生薄弱项给予针对性练习
3. 适时引入新的知识点和练习
4. 鼓励学生主动表达，营造轻松的学习氛围"""

    # 翻译解析提示词
    TRANSLATION_PROMPT = """请将以下内容进行中英互译，并提供详细的语言学习解析：

原文：
{text}

请按以下格式输出：
## 翻译结果
[翻译内容]

## 详细解析
### 核心词汇
- 列出重要词汇、短语及其用法

### 语法结构
- 分析句子结构和语法要点

### 文化背景
- 如有必要，说明相关文化背景知识

### 学习建议
- 提供记忆技巧和学习建议"""

    # 单词解析提示词
    WORD_ANALYSIS_PROMPT = """请对以下单词/短语进行全面解析：

单词/短语：{word}

请提供：
1. **音标**：英式和美式发音
2. **词性**：所有词性及对应中文释义
3. **常用搭配**：列举3-5个常见搭配
4. **例句**：提供2-3个实用例句（附中文翻译）
5. **词根词缀**：如适用，分析词源
6. **同义词/反义词**：列举相关词汇
7. **记忆技巧**：提供有效的记忆方法"""

    # 长难句解析提示词
    SENTENCE_ANALYSIS_PROMPT = """请对以下长难句进行深度解析：

句子：{sentence}

请提供：
## 中文翻译
[整句翻译]

## 句子结构分析
- 主句：
- 从句：
- 特殊结构：

## 语法要点
[重点语法知识]

## 词汇难点
[重点词汇及用法]

## 简化理解
[用更简单的方式表达这个句子]"""

    # 写作批改提示词
    WRITING_CORRECTION_PROMPT = """请对以下英文写作进行专业批改：

作文内容：
{content}

写作要求：{requirement}

请按以下结构提供反馈：

## 总体评价
[整体水平评估和亮点]

## 错误纠正
### 语法错误
- [逐一列出并纠正]

### 拼写错误
- [逐一列出并纠正]

### 用词不当
- [逐一列出更地道的表达]

## 改进建议
### 句式结构
[如何提升句式多样性]

### 词汇选择
[如何使用更高级的词汇]

### 逻辑连贯
[如何提升文章连贯性]

## 优秀范文
[修改后的优质版本]

## 评分
- 内容：_/25
- 组织：_/25
- 词汇：_/25
- 语法：_/25
总分：_/100"""

    # 写作润色提示词
    WRITING_POLISH_PROMPT = """请对以下英文内容进行润色，使其更加地道流畅：

原文：
{content}

目标风格：{style}（学术/商务/日常/创意）

请提供：
## 润色后的版本
[改进后的完整内容]

## 主要改进点
1. [改进点1及原因]
2. [改进点2及原因]
3. [改进点3及原因]

## 学习要点
[从润色中可以学到的写作技巧]"""

    # 口语纠错提示词
    SPEAKING_CORRECTION_PROMPT = """请对以下口语内容进行纠错和评分：

识别文本：{text}
参考文本：{reference}

请提供：
## 发音评估
- 准确度：_/100
- 流利度：_/100
- 完整度：_/100
- 总分：_/100

## 错误分析
### 发音错误
- [具体指出发音问题]

### 遗漏或添加
- [指出遗漏或多余的词]

### 语调建议
- [语调和节奏的改进建议]

## 改进建议
[具体的练习建议]"""

    # 口语练习引导提示词
    SPEAKING_PRACTICE_PROMPT = """作为口语练习教练，请为学生设计一个{difficulty}难度的口语练习：

话题：{topic}

请提供：
## 练习场景
[描述一个真实的对话场景]

## 参考句式
[提供3-5个相关的实用句式]

## 练习要求
[明确的练习目标和要求]

## 评分标准
[清晰的评分维度]"""

    # 多模态图片解析提示词
    VISION_ANALYSIS_PROMPT = """请分析图片中的英文内容，并提供学习辅导：

用户问题：{question}

请提供：
## 图片内容识别
[详细描述图片中的英文内容]

## 中文翻译
[翻译所有英文内容]

## 知识点讲解
[解释重点词汇、语法、表达方式]

## 文化背景
[如适用，说明相关文化背景]

## 拓展学习
[相关的扩展知识和学习建议]"""

    # PDF文档解析提示词
    PDF_ANALYSIS_PROMPT = """请分析PDF文档中的英文内容：

提取的文本：
{text}

用户需求：{question}

请提供：
## 内容概述
[文档主要内容总结]

## 重点内容翻译
[翻译关键段落和重点内容]

## 难点解析
### 专业词汇
- [列举并解释专业术语]

### 复杂句式
- [分析长难句]

## 学习建议
[针对该类材料的学习方法]"""

    # 学习总结提示词
    SUMMARY_PROMPT = """请基于学生的学习记录，生成学习总结报告：

学习时长：{duration}
练习次数：{practice_count}
主要学习内容：{content_summary}
错误记录：{errors}

请生成：
## 学习进度
[本阶段学习概况]

## 知识掌握情况
### 已掌握
- [列出掌握良好的知识点]

### 需加强
- [列出薄弱环节]

## 常见错误分析
[分析频繁出现的错误及原因]

## 下阶段学习建议
### 学习重点
- [建议重点学习的内容]

### 练习方向
- [建议加强的练习方向]

### 学习方法
- [针对性的学习方法建议]"""

    # 难度调整建议提示词
    DIFFICULTY_ADJUSTMENT_PROMPT = """基于学生的表现，评估是否需要调整学习难度：

当前难度：{current_difficulty}
正确率：{accuracy}
学习时长：{duration}
完成度：{completion}

请分析：
## 表现评估
[学生当前水平评估]

## 难度匹配度
[当前难度是否合适]

## 调整建议
[是否建议调整难度及调整理由]

## 过渡方案
[如需调整，提供平滑过渡方案]"""


# 全局Prompt实例
PROMPTS = PromptManager()


# Prompt字典，便于动态访问
PROMPT_TEMPLATES: Dict[str, str] = {
    "agent_system": PROMPTS.AGENT_SYSTEM_PROMPT,
    "agent_chat": PROMPTS.AGENT_CHAT_PROMPT,
    "translation": PROMPTS.TRANSLATION_PROMPT,
    "word_analysis": PROMPTS.WORD_ANALYSIS_PROMPT,
    "sentence_analysis": PROMPTS.SENTENCE_ANALYSIS_PROMPT,
    "writing_correction": PROMPTS.WRITING_CORRECTION_PROMPT,
    "writing_polish": PROMPTS.WRITING_POLISH_PROMPT,
    "speaking_correction": PROMPTS.SPEAKING_CORRECTION_PROMPT,
    "speaking_practice": PROMPTS.SPEAKING_PRACTICE_PROMPT,
    "vision_analysis": PROMPTS.VISION_ANALYSIS_PROMPT,
    "pdf_analysis": PROMPTS.PDF_ANALYSIS_PROMPT,
    "summary": PROMPTS.SUMMARY_PROMPT,
    "difficulty_adjustment": PROMPTS.DIFFICULTY_ADJUSTMENT_PROMPT,
}
