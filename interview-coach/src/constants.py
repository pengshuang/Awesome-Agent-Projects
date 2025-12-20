"""
常量定义模块
"""

# 日志分隔符
LOG_SEPARATOR_FULL = "=" * 70
LOG_SEPARATOR_HALF = "-" * 70

# 成功信息
SUCCESS_RESUME_LOADED = "✅ 简历加载成功"
SUCCESS_EVALUATION_COMPLETED = "✅ 简历评估完成"
SUCCESS_INTERVIEW_STARTED = "✅ 面试开始"

# 错误信息
ERROR_NO_RESUME = "❌ 未加载简历"
ERROR_INVALID_FILE = "❌ 文件格式不支持"
ERROR_FILE_NOT_FOUND = "❌ 文件不存在"

# 警告信息
WARNING_NO_CONTENT = "⚠️ 简历内容为空"
WARNING_LARGE_FILE = "⚠️ 文件过大"

# 提示信息
INFO_LOADING_RESUME = "📄 正在加载简历..."
INFO_EVALUATING_RESUME = "🔍 正在评估简历..."
INFO_STARTING_INTERVIEW = "💼 正在准备面试..."
INFO_WEB_SEARCH_ENABLED = "🌐 联网搜索已启用"

# 简历评估维度
EVALUATION_DIMENSIONS = [
    "基本信息完整性",
    "工作经验相关性",
    "项目经验质量",
    "技能匹配度",
    "教育背景",
    "整体印象",
]

# 面试类型
INTERVIEW_TYPES = {
    "technical": "技术面试",
    "behavioral": "行为面试",
    "comprehensive": "综合面试",
}

# 默认提示词
DEFAULT_EVALUATION_PROMPT = """
你是一位资深的HR和技术面试官。请仔细分析以下简历，并从多个维度进行评估。

简历内容：
{resume_content}

请按照以下维度进行评估（每个维度0-10分）：
1. 基本信息完整性（联系方式、个人信息等）
2. 工作经验相关性（是否与目标岗位匹配）
3. 项目经验质量（项目深度、技术难度等）
4. 技能匹配度（技能栈是否符合要求）
5. 教育背景（学历、专业等）
6. 整体印象（简历排版、表达能力等）

请提供：
1. 各维度评分及理由
2. 总体评分（0-100分）
3. 优点总结（3-5条）
4. 需要改进的地方（3-5条）
5. 针对性建议

以结构化的方式输出评估结果。
"""

DEFAULT_INTERVIEW_SYSTEM_PROMPT = """
你是一位专业的面试官，正在对候选人进行{interview_type}。

候选人简历摘要：
{resume_summary}

面试要求：
1. 根据简历内容提出有针对性的问题
2. 问题要有深度，能够考察候选人的真实水平
3. 保持专业、友好的态度
4. 根据候选人的回答进行追问
5. 适当时候可以问一些场景题或行为题

请以自然、专业的方式进行面试，每次提出1-2个问题，等待候选人回答后再继续。
"""
