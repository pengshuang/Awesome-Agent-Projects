"""
辅助工具函数
"""

import re
from typing import Optional


def format_sql_for_display(sql: str) -> str:
    """
    格式化SQL语句用于显示（带语法高亮的Markdown）
    
    Args:
        sql: SQL查询语句
        
    Returns:
        格式化后的Markdown字符串
    """
    # 清理SQL语句
    sql = sql.strip()
    
    # 移除可能的markdown代码块标记
    sql = re.sub(r'^```sql\n', '', sql)
    sql = re.sub(r'^```\n', '', sql)
    sql = re.sub(r'\n```$', '', sql)
    sql = sql.strip()
    
    # 返回带语法高亮的markdown格式
    return f"```sql\n{sql}\n```"


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后添加的后缀
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix


def format_data_for_display(data: any, max_rows: int = 10) -> str:
    """
    格式化数据用于显示
    
    Args:
        data: 数据（可以是DataFrame、list、dict等）
        max_rows: 最大显示行数
        
    Returns:
        格式化后的字符串
    """
    try:
        # 如果是pandas DataFrame
        if hasattr(data, 'to_markdown'):
            if len(data) > max_rows:
                return f"{data.head(max_rows).to_markdown()}\n\n... (显示前{max_rows}行，共{len(data)}行)"
            return data.to_markdown()
        
        # 如果是list或tuple
        elif isinstance(data, (list, tuple)):
            if len(data) > max_rows:
                preview = data[:max_rows]
                return f"{preview}\n\n... (显示前{max_rows}项，共{len(data)}项)"
            return str(data)
        
        # 其他类型直接转字符串
        else:
            return str(data)
    except Exception as e:
        return f"数据格式化失败: {str(e)}"


def extract_sql_from_response(response: str) -> Optional[str]:
    """
    从LLM响应中提取SQL语句
    
    Args:
        response: LLM的响应文本
        
    Returns:
        提取的SQL语句，如果没找到则返回None
    """
    # 尝试提取代码块中的SQL
    sql_pattern = r'```sql\n(.*?)\n```'
    match = re.search(sql_pattern, response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # 尝试提取普通代码块
    code_pattern = r'```\n(.*?)\n```'
    match = re.search(code_pattern, response, re.DOTALL)
    if match:
        sql = match.group(1).strip()
        # 简单验证是否像SQL语句
        if any(keyword in sql.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE']):
            return sql
    
    # 如果响应本身就是SQL（以SELECT等开头）
    response_stripped = response.strip()
    if any(response_stripped.upper().startswith(keyword) for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE']):
        return response_stripped
    
    return None


def format_chat_history_for_display(history: list, max_messages: int = 10) -> str:
    """
    格式化对话历史用于显示
    
    Args:
        history: 对话历史列表
        max_messages: 最大显示消息数
        
    Returns:
        格式化后的字符串
    """
    if not history:
        return "暂无对话历史"
    
    # 只显示最近的消息
    recent_history = history[-max_messages:] if len(history) > max_messages else history
    
    formatted = []
    for msg in recent_history:
        role = "👤 用户" if msg["role"] == "user" else "🤖 助手"
        content = truncate_text(msg["content"], max_length=200)
        formatted.append(f"{role}: {content}")
    
    result = "\n\n".join(formatted)
    
    if len(history) > max_messages:
        result = f"... (省略{len(history) - max_messages}条历史消息)\n\n{result}"
    
    return result
