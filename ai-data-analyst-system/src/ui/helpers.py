"""
Web UI 辅助函数
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from loguru import logger

from .constants import CHART_TYPES, DEFAULT_CHART_HEIGHT


def format_success_message(title: str, content: str, tips: Optional[str] = None) -> str:
    """
    格式化成功消息
    
    Args:
        title: 标题
        content: 内容
        tips: 提示信息
        
    Returns:
        格式化的Markdown消息
    """
    message = f"## ✅ {title}\n\n{content}\n\n---\n"
    if tips:
        message += f"\n{tips}\n"
    return message


def format_error_message(error: str) -> str:
    """格式化错误消息"""
    return f"❌ {error}"


def format_datasource_info(name: str, path: str, source_type: str, schema: str, tips: str = "") -> str:
    """
    格式化数据源信息
    
    Args:
        name: 数据源名称
        path: 数据源路径
        source_type: 数据源类型
        schema: 数据源结构信息
        tips: 使用提示
        
    Returns:
        格式化的信息
    """
    info = f"""## ✅ {source_type}注册成功

**名称**: `{name}`  
**路径**: `{path}`  
**类型**: {source_type}

---

### 📊 结构信息

```text
{schema}
```

---

💡 **提示**: 现在可以在「对话分析」页面选择此数据源进行查询和分析了！

{tips}
"""
    return info


def create_chart_from_dataframe(
    df: pd.DataFrame,
    chart_type: str,
    x_col: str,
    y_col: str,
    color_col: Optional[str] = None,
    title: Optional[str] = None,
) -> Optional[go.Figure]:
    """
    从 DataFrame 创建图表
    
    Args:
        df: 数据框
        chart_type: 图表类型 (bar, line, scatter, pie, area)
        x_col: X轴列名
        y_col: Y轴列名
        color_col: 颜色分组列名
        title: 图表标题
        
    Returns:
        Plotly图表对象
    """
    try:
        # 验证列是否存在
        if x_col not in df.columns or y_col not in df.columns:
            logger.error(f"列不存在: {x_col} 或 {y_col}")
            return None
        
        if color_col and color_col not in df.columns and color_col != "无":
            logger.error(f"颜色列不存在: {color_col}")
            color_col = None
        
        # 处理颜色列
        if color_col == "无":
            color_col = None
        
        # 创建图表
        if chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title, height=DEFAULT_CHART_HEIGHT)
        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title, height=DEFAULT_CHART_HEIGHT)
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=title, height=DEFAULT_CHART_HEIGHT)
        elif chart_type == "pie":
            fig = px.pie(df, names=x_col, values=y_col, title=title, height=DEFAULT_CHART_HEIGHT)
        elif chart_type == "area":
            fig = px.area(df, x=x_col, y=y_col, color=color_col, title=title, height=DEFAULT_CHART_HEIGHT)
        else:
            logger.error(f"不支持的图表类型: {chart_type}")
            return None
        
        # 优化布局
        fig.update_layout(
            template="plotly_white",
            font=dict(size=12),
            margin=dict(l=50, r=50, t=50, b=50),
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"创建图表失败: {e}")
        return None


def extract_dataframe_from_response(response: str, result_data: Optional[pd.DataFrame] = None) -> Optional[pd.DataFrame]:
    """
    从响应中提取DataFrame
    
    Args:
        response: 响应文本
        result_data: 已有的结果数据
        
    Returns:
        DataFrame对象
    """
    if result_data is not None and isinstance(result_data, pd.DataFrame):
        return result_data
    
    return None


def format_datasource_list(sources: Dict[str, Any]) -> str:
    """
    格式化数据源列表
    
    Args:
        sources: 数据源字典
        
    Returns:
        格式化的列表
    """
    if not sources:
        return """### 📋 数据源列表

暂无已注册的数据源

---

**如何注册数据源？**

1. 切换到「🗄️ 数据源管理」标签页
2. 选择要注册的数据源类型
3. 填写相关信息并点击注册按钮
"""
    
    # 按类型分组
    sources_by_type = {}
    for name, info in sources.items():
        source_type = info['type']
        if source_type not in sources_by_type:
            sources_by_type[source_type] = []
        sources_by_type[source_type].append(name)
    
    # 生成列表
    result = "### 📋 已注册的数据源\n\n"
    
    type_icons = {
        "database": "🗄️",
        "file": "📄",
        "knowledge_base": "📚",
        "web_search": "🌐",
    }
    
    for source_type, names in sources_by_type.items():
        icon = type_icons.get(source_type, "📊")
        result += f"#### {icon} {source_type.upper()}\n\n"
        for name in names:
            result += f"- `{name}`\n"
        result += "\n"
    
    result += "---\n\n💡 **提示**: 可以在「对话分析」页面选择这些数据源进行查询。"
    
    return result
