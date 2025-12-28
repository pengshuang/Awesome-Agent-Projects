"""
Web UI 常量定义
"""

# UI 相关常量
MAX_CHAT_HISTORY_DISPLAY = 10
DEFAULT_CHART_HEIGHT = 500
DEFAULT_TABLE_MAX_ROWS = 100

# 消息前缀
MSG_ERROR_NOT_INITIALIZED = "❌ 请先初始化系统"
MSG_SUCCESS_PREFIX = "## ✅ "
MSG_ERROR_PREFIX = "❌ "
MSG_INFO_PREFIX = "💡 "

# Chart 类型
CHART_TYPES = {
    "bar": "柱状图",
    "line": "折线图",
    "scatter": "散点图",
    "pie": "饼图",
    "area": "面积图",
}

# 数据源类型图标
DATASOURCE_ICONS = {
    "database": "🗄️",
    "file": "📄",
    "knowledge_base": "📚",
    "web_search": "🌐",
}

# CSS 样式
CUSTOM_CSS = """
.chatbot {
    height: 600px !important;
}

.dataframe {
    font-size: 12px !important;
}

/* SQL 代码块样式 */
.markdown-body pre {
    background-color: #f6f8fa;
    border-radius: 6px;
    padding: 16px;
}

/* 表格样式 */
.markdown-body table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}

.markdown-body table th {
    background-color: #f0f0f0;
    font-weight: bold;
    padding: 10px;
}

.markdown-body table td {
    padding: 8px;
    border: 1px solid #ddd;
}

/* 图表容器样式 */
.plot-container {
    margin: 20px 0;
}
"""

# 提示消息模板
TIPS = {
    "database": """
💡 **数据库使用建议**:
- 支持复杂的SQL查询
- 可以进行数据分析和统计
- 自动生成可视化图表
""",
    "file": """
💡 **文件使用建议**:
- 支持 CSV、Excel、JSON 格式
- 可以进行数据分析和筛选
- 自动生成统计报告
""",
    "knowledge_base": """
💡 **知识库使用建议**:
- 提问方式: "根据知识库，XXX是什么？"
- 支持语义检索，可以用自然语言提问
- 系统会自动检索相关文档并生成答案
""",
    "web_search": """
💡 **Web搜索使用建议**:
- 提问方式: "搜索XXX的最新信息"
- 系统会自动搜索并整理相关结果
- 可以与其他数据源配合使用
""",
}
