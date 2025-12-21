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

# 面试类型
INTERVIEW_TYPES = {
    "technical": "技术面试",
    "behavioral": "行为面试",
    "comprehensive": "综合面试",
}
