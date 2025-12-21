"""
Web UI - Gradio 界面
简洁美观的数据分析助手界面
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import gradio as gr
import pandas as pd
import json
import re
import plotly.express as px
import plotly.graph_objects as go

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入系统初始化
from init_system import initialize_system

# 初始化系统（必须在导入 Agent 之前）
initialize_system()

from src.agent import DataAnalystAgent
from src.utils.logger import logger
from src.utils.helpers import format_sql_for_display

# 全局变量
AGENT: Optional[DataAnalystAgent] = None
INITIALIZED = False
LAST_QUERY_RESULT: Optional[pd.DataFrame] = None  # 存储最后一次查询结果
LAST_QUERY_RESULT: Optional[pd.DataFrame] = None  # 存储最后一次查询结果


def initialize_agent():
    """初始化 Agent"""
    global AGENT, INITIALIZED
    
    try:
        logger.info("开始初始化 Agent...")
        
        # 从环境变量读取历史轮数配置（默认10轮）
        max_history_turns = int(os.getenv("MAX_HISTORY_TURNS", "10"))
        
        # 创建 Agent 实例
        AGENT = DataAnalystAgent(max_history_turns=max_history_turns)
        INITIALIZED = True
        
        logger.info(f"✅ Agent 初始化成功（历史轮数: {max_history_turns}）")
        
        result = f"""## ✅ 系统初始化成功！

### ⚙️ 系统配置

- **历史轮数**: {max_history_turns} 轮
- **LLM模型**: {os.getenv('LLM_MODEL', 'N/A')}
- **API地址**: {os.getenv('LLM_API_BASE', 'N/A')}
- **Embedding**: {os.getenv('EMBEDDING_PROVIDER', 'N/A')}

---

### 📋 下一步操作

1️⃣ **注册数据源**  
→ 切换到「🗄️ 数据源管理」标签页  
→ 注册数据库、文件、知识库或启用Web搜索

2️⃣ **开始分析**  
→ 切换到「💬 对话分析」标签页  
→ 选择数据源并开始提问

---

💡 **提示**: 您可以先创建示例数据库来体验功能：
```bash
python data/create_example_db.py
```
"""
        return True, result
        
    except Exception as e:
        logger.error(f"系统初始化失败: {e}", exc_info=True)
        error_msg = f"""## ❌ 初始化失败

**错误信息**: {str(e)}

---

### 🔧 排查建议

1. 检查 `.env` 文件配置是否正确
2. 确认 `LLM_API_KEY` 已配置
3. 验证网络连接是否正常
4. 查看日志文件: `logs/ai_data_analyst_*.log`

详细配置说明请查看: `API_KEY_SETUP.md`
"""
        return False, error_msg


def register_sqlite_db(db_name: str, db_path: str) -> str:
    """注册 SQLite 数据库"""
    if not INITIALIZED:
        return "❌ 请先初始化系统"
    
    if not db_name or not db_path:
        return "❌ 请填写数据库名称和路径"
    
    try:
        success = AGENT.register_sqlite_database(db_name, db_path)
        if success:
            # 获取schema信息
            schema = AGENT.get_data_source_schema(db_name)
            
            # 格式化输出
            result = f"""## ✅ 数据库注册成功

**数据库名称**: `{db_name}`  
**数据库路径**: `{db_path}`  
**数据源类型**: SQLite Database

---

### 📊 数据库结构

```text
{schema}
```

---

💡 **提示**: 现在可以在「对话分析」页面选择此数据源进行查询和分析了！
"""
            return result
        else:
            return f"❌ 数据库注册失败: {db_name}"
    except Exception as e:
        return f"❌ 注册失败: {str(e)}"


def register_file(file_name: str, file_path: str) -> str:
    """注册文件数据源"""
    if not INITIALIZED:
        return "❌ 请先初始化系统"
    
    if not file_name or not file_path:
        return "❌ 请填写文件名称和路径"
    
    try:
        success = AGENT.register_file(file_name, file_path)
        if success:
            schema = AGENT.get_data_source_schema(file_name)
            
            # 格式化输出
            result = f"""## ✅ 文件注册成功

**文件名称**: `{file_name}`  
**文件路径**: `{file_path}`  
**数据源类型**: File (CSV/Excel/JSON)

---

### 📄 文件信息

```text
{schema}
```

---

💡 **提示**: 现在可以在「对话分析」页面选择此数据源进行查询和分析了！
"""
            return result
        else:
            return f"❌ 文件注册失败: {file_name}"
    except Exception as e:
        return f"❌ 注册失败: {str(e)}"


def register_knowledge_base(kb_name: str, kb_dir: Optional[str] = None) -> str:
    """注册知识库"""
    if not INITIALIZED:
        return "❌ 请先初始化系统"
    
    if not kb_name:
        return "❌ 请填写知识库名称"
    
    try:
        success = AGENT.register_knowledge_base(kb_name, kb_dir)
        if success:
            schema = AGENT.get_data_source_schema(kb_name)
            
            # 格式化输出
            kb_dir_display = kb_dir if kb_dir else "默认目录 (data/knowledge_base/)"
            result = f"""## ✅ 知识库注册成功

**知识库名称**: `{kb_name}`  
**知识库目录**: `{kb_dir_display}`  
**数据源类型**: Vector Knowledge Base

---

### 📚 知识库信息

```text
{schema}
```

---

💡 **提示**: 现在可以在「对话分析」页面选择此数据源进行知识问答了！

📝 **使用建议**:
- 提问方式: "根据知识库，XXX是什么？"
- 支持语义检索，可以用自然语言提问
- 系统会自动检索相关文档并生成答案
"""
            return result
        else:
            return f"❌ 知识库注册失败: {kb_name}"
    except Exception as e:
        return f"❌ 注册失败: {str(e)}"


def register_web_search() -> str:
    """注册 Web 搜索"""
    if not INITIALIZED:
        return "❌ 请先初始化系统"
    
    try:
        success = AGENT.register_web_search()
        if success:
            result = """## ✅ Web搜索已启用

**数据源名称**: `web_search`  
**数据源类型**: Web Search Engine

---

### 🌐 Web搜索功能

Web搜索可以帮助您获取实时的互联网信息，适用于：
- 📰 获取最新资讯和动态
- 🔍 验证事实和数据
- 📊 补充分析所需的外部信息
- 🌍 了解行业趋势和市场动态

---

💡 **提示**: 现在可以在「对话分析」页面选择此数据源进行联网查询了！

📝 **使用建议**:
- 提问方式: "搜索XXX的最新信息"
- 系统会自动搜索并整理相关结果
- 可以与其他数据源配合使用
"""
            return result
        else:
            return """❌ Web搜索启用失败

请检查配置：
1. 确保在 `.env` 文件中设置了 `ENABLE_WEB_SEARCH=true`
2. 配置 `WEB_SEARCH_API_KEY`（如使用SerpAPI等服务）
3. 重启服务使配置生效
"""
    except Exception as e:
        return f"❌ 启用失败: {str(e)}"


def list_data_sources() -> str:
    """列出所有数据源"""
    if not INITIALIZED:
        return "❌ 请先初始化系统"
    
    sources = AGENT.list_data_sources()
    
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
    
    # 类型图标映射
    type_icons = {
        'sqlite': '🗄️',
        'file': '📄',
        'knowledge_base': '📚',
        'web': '🌐'
    }
    
    # 类型名称映射
    type_names = {
        'sqlite': 'SQLite 数据库',
        'file': '文件数据源',
        'knowledge_base': '知识库',
        'web': 'Web 搜索'
    }
    
    result = "## 📋 已注册的数据源\n\n"
    result += f"**总数**: {len(sources)} 个数据源\n\n---\n\n"
    
    for source_type, names in sorted(sources_by_type.items()):
        icon = type_icons.get(source_type, '📦')
        type_name = type_names.get(source_type, source_type)
        result += f"### {icon} {type_name}\n\n"
        for name in sorted(names):
            result += f"- `{name}`\n"
        result += "\n"
    
    result += """---

💡 **使用方法**:
1. 在「对话分析」页面的下拉框中选择数据源
2. 输入您的问题并点击发送
3. 系统会自动分析并返回结果
"""
    
    return result


def chat_response(message: str, history: List, source_name: Optional[str] = None):
    """
    处理对话
    
    Args:
        message: 用户消息
        history: 对话历史（Gradio格式 - 列表的列表）
        source_name: 数据源名称（可选）
    """
    global LAST_QUERY_RESULT
    
    if not INITIALIZED:
        # 返回正确的Gradio格式：添加一条消息到历史
        history = history or []
        history.append([message, "❌ 请先初始化系统"])
        return history
    
    if not message:
        history = history or []
        history.append([message, "请输入您的问题"])
        return history
    
    try:
        # 调用 Agent
        reply = AGENT.chat(
            message=message,
            source_name=source_name if source_name and source_name != "无（直接对话）" else None,
        )
        
        # 尝试从回复中提取查询结果（如果是SQL查询）
        try:
            result_df = extract_query_result(reply, source_name)
            if result_df is not None and not result_df.empty:
                LAST_QUERY_RESULT = result_df
                logger.info(f"已提取查询结果: {len(result_df)} 行")
        except Exception as e:
            logger.warning(f"提取查询结果失败: {e}")
        
        # 添加到历史记录（Gradio Chatbot 格式：[[user_msg, bot_msg], ...]）
        history = history or []
        history.append([message, reply])
        return history
            
    except Exception as e:
        logger.error(f"对话处理失败: {e}", exc_info=True)
        error_msg = f"❌ 对话处理失败: {str(e)}"
        history = history or []
        history.append([message, error_msg])
        return history


def extract_query_result(reply: str, source_name: Optional[str]) -> Optional[pd.DataFrame]:
    """
    从Agent回复中提取查询结果
    
    Args:
        reply: Agent的回复文本
        source_name: 数据源名称
    
    Returns:
        查询结果DataFrame或None
    """
    global AGENT
    
    if not AGENT or not source_name or source_name == "无（直接对话）":
        return None
    
    # 尝试从回复中提取SQL查询结果
    try:
        # 检查数据源是否存在
        if hasattr(AGENT, 'analyzer') and hasattr(AGENT.analyzer, 'data_sources'):
            data_sources = AGENT.analyzer.data_sources
            
            if source_name in data_sources:
                source = data_sources[source_name]
                source_type = getattr(source, 'source_type', '')
                
                # 从回复中提取SQL语句
                sql_match = re.search(r'```sql\s+(.*?)\s+```', reply, re.DOTALL | re.IGNORECASE)
                if sql_match and source_type == 'sqlite':
                    sql = sql_match.group(1).strip()
                    # 执行查询
                    result = source.query(sql)
                    if isinstance(result, dict) and 'data' in result:
                        return pd.DataFrame(result['data'])
    except Exception as e:
        logger.warning(f"无法提取查询结果: {e}")
    
    return None


def get_visualization_data() -> Tuple[pd.DataFrame, str]:
    """
    获取可视化数据
    
    Returns:
        (DataFrame, status_message)
    """
    global LAST_QUERY_RESULT
    
    if LAST_QUERY_RESULT is not None and not LAST_QUERY_RESULT.empty:
        return LAST_QUERY_RESULT, f"✅ 数据已加载 ({len(LAST_QUERY_RESULT)} 行 × {len(LAST_QUERY_RESULT.columns)} 列)"
    
    return pd.DataFrame(), "⚠️ 暂无查询数据，请先在「对话分析」中执行查询"


def create_chart(df: pd.DataFrame, chart_type: str, x_col: str, y_col: str, color_col: Optional[str] = None):
    """
    创建图表
    
    Args:
        df: 数据DataFrame
        chart_type: 图表类型
        x_col: X轴列名
        y_col: Y轴列名
        color_col: 颜色分组列名
    
    Returns:
        Plotly图表对象
    """
    if df.empty:
        return None
    
    try:
        # 确保选择的列存在
        if x_col not in df.columns or y_col not in df.columns:
            return None
        
        if color_col and color_col not in df.columns:
            color_col = None
        
        # 根据图表类型创建图表
        if chart_type == "折线图":
            fig = px.line(df, x=x_col, y=y_col, color=color_col, markers=True)
        elif chart_type == "柱状图":
            fig = px.bar(df, x=x_col, y=y_col, color=color_col)
        elif chart_type == "散点图":
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, size=y_col if color_col else None)
        elif chart_type == "饼图":
            fig = px.pie(df, names=x_col, values=y_col)
        elif chart_type == "面积图":
            fig = px.area(df, x=x_col, y=y_col, color=color_col)
        elif chart_type == "箱线图":
            fig = px.box(df, x=x_col, y=y_col, color=color_col)
        else:
            fig = px.bar(df, x=x_col, y=y_col, color=color_col)
        
        # 美化图表
        fig.update_layout(
            template="plotly_white",
            hovermode='x unified',
            title_font_size=20,
            font=dict(size=12),
            showlegend=True,
            height=500
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"创建图表失败: {e}", exc_info=True)
        return None


def update_chart_preview(chart_type: str, x_col: str, y_col: str, color_col: Optional[str]):
    """
    更新图表预览
    
    Returns:
        (图表, 数据表, 列选择下拉框更新)
    """
    global LAST_QUERY_RESULT
    
    if LAST_QUERY_RESULT is None or LAST_QUERY_RESULT.empty:
        return None, None, gr.update(), gr.update(), gr.update()
    
    # 创建图表
    fig = create_chart(LAST_QUERY_RESULT, chart_type, x_col, y_col, color_col)
    
    # 准备列选择
    columns = list(LAST_QUERY_RESULT.columns)
    
    return (
        fig,
        LAST_QUERY_RESULT,
        gr.update(choices=columns, value=columns[0] if columns else None),
        gr.update(choices=columns, value=columns[1] if len(columns) > 1 else columns[0] if columns else None),
        gr.update(choices=["无"] + columns, value="无")
    )


def load_data_for_viz():
    """
    加载数据用于可视化
    
    Returns:
        (状态消息, 数据表, X轴选择, Y轴选择, 颜色选择)
    """
    global LAST_QUERY_RESULT
    
    if LAST_QUERY_RESULT is None or LAST_QUERY_RESULT.empty:
        return (
            "⚠️ 暂无查询数据，请先在「对话分析」中执行数据查询",
            None,
            gr.update(choices=[]),
            gr.update(choices=[]),
            gr.update(choices=["无"])
        )
    
    columns = list(LAST_QUERY_RESULT.columns)
    
    return (
        f"✅ 数据已加载 ({len(LAST_QUERY_RESULT)} 行 × {len(LAST_QUERY_RESULT.columns)} 列)",
        LAST_QUERY_RESULT,
        gr.update(choices=columns, value=columns[0] if columns else None),
        gr.update(choices=columns, value=columns[1] if len(columns) > 1 else columns[0] if columns else None),
        gr.update(choices=["无"] + columns, value="无")
    )


def clear_chat_history():
    """清空对话历史"""
    global LAST_QUERY_RESULT
    
    if INITIALIZED:
        AGENT.clear_history()
    
    LAST_QUERY_RESULT = None
    logger.info("对话历史和查询结果已清空")
    return []  # 返回空列表清空聊天界面


def create_ui():
    """创建 Gradio 界面"""
    
    # 自定义CSS
    custom_css = """
    .gradio-container {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    }
    .header {
        text-align: center;
        padding: 20px;
        background: white;
        color: #333;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    .header h1 {
        margin: 0;
        font-size: 2.5em;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .header p {
        margin: 10px 0 0 0;
        font-size: 1.1em;
        color: #666;
    }
    """
    
    with gr.Blocks(css=custom_css, title="AI 数据分析助手", theme=gr.themes.Soft()) as demo:
        # 标题
        gr.HTML("""
        <div class="header">
            <h1>🤖 AI 数据分析助手</h1>
            <p>基于大模型的智能数据分析工具 | 支持多数据源融合分析 | NL2SQL | 报告生成</p>
        </div>
        """)
        
        # 主界面
        with gr.Tabs() as tabs:
            # Tab 1: 对话分析
            with gr.Tab("💬 对话分析"):
                with gr.Row():
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(
                            label="对话窗口",
                            height=500,
                            show_copy_button=True,
                            render_markdown=True,
                            type='tuples'
                        )
                        
                        with gr.Row():
                            message_input = gr.Textbox(
                                label="输入您的问题",
                                placeholder="例如：分析销售数据的趋势...",
                                lines=2,
                                scale=4,
                            )
                            source_dropdown = gr.Dropdown(
                                label="选择数据源",
                                choices=["无（直接对话）"],
                                value="无（直接对话）",
                                scale=1,
                            )
                        
                        with gr.Row():
                            submit_btn = gr.Button("📤 发送", variant="primary", scale=2)
                            clear_btn = gr.Button("🗑️ 清空历史", scale=1)
                            refresh_sources_btn = gr.Button("🔄 刷新数据源列表", scale=1)
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 📊 数据源列表")
                        sources_display = gr.Markdown("暂无数据源")
                        list_sources_btn = gr.Button("📋 查看所有数据源")
            
            # Tab 2: 数据源管理
            with gr.Tab("🗄️ 数据源管理"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 📁 SQLite 数据库")
                        db_name_input = gr.Textbox(label="数据库名称", placeholder="例如：sales_db")
                        db_path_input = gr.Textbox(
                            label="数据库路径",
                            placeholder="例如：/path/to/database.db 或 data/databases/sales.db"
                        )
                        register_db_btn = gr.Button("➕ 注册数据库", variant="primary")
                        db_result = gr.Markdown()
                    
                    with gr.Column():
                        gr.Markdown("### 📄 文件数据源")
                        file_name_input = gr.Textbox(label="文件名称", placeholder="例如：sales_data")
                        file_path_input = gr.Textbox(
                            label="文件路径",
                            placeholder="例如：data/files/sales.csv"
                        )
                        register_file_btn = gr.Button("➕ 注册文件", variant="primary")
                        file_result = gr.Markdown()
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 📚 知识库")
                        kb_name_input = gr.Textbox(label="知识库名称", placeholder="例如：business_kb")
                        kb_dir_input = gr.Textbox(
                            label="知识库目录（可选）",
                            placeholder="留空使用默认目录"
                        )
                        register_kb_btn = gr.Button("➕ 注册知识库", variant="primary")
                        kb_result = gr.Markdown()
                    
                    with gr.Column():
                        gr.Markdown("### 🌐 Web 搜索")
                        gr.Markdown("启用Web搜索以获取实时互联网信息")
                        register_web_btn = gr.Button("🔌 启用Web搜索", variant="primary")
                        web_result = gr.Markdown()
            
            # Tab 3: 数据可视化
            with gr.Tab("📊 数据可视化"):
                gr.Markdown("""
                ### 📈 将查询结果可视化
                在「对话分析」中执行数据查询后，可以在此处创建图表
                """)
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### ⚙️ 图表配置")
                        
                        load_viz_btn = gr.Button("🔄 加载数据", variant="primary", size="lg")
                        viz_status = gr.Markdown("⚠️ 请先加载数据")
                        
                        gr.Markdown("---")
                        
                        chart_type = gr.Dropdown(
                            label="图表类型",
                            choices=["柱状图", "折线图", "散点图", "饼图", "面积图", "箱线图"],
                            value="柱状图"
                        )
                        
                        x_column = gr.Dropdown(
                            label="X轴（分类/时间）",
                            choices=[],
                            value=None
                        )
                        
                        y_column = gr.Dropdown(
                            label="Y轴（数值）",
                            choices=[],
                            value=None
                        )
                        
                        color_column = gr.Dropdown(
                            label="颜色分组（可选）",
                            choices=["无"],
                            value="无"
                        )
                        
                        create_chart_btn = gr.Button("🎨 生成图表", variant="primary", size="lg")
                        
                        gr.Markdown("""
                        ---
                        ### 💡 使用提示
                        
                        1. **加载数据**: 点击「🔄 加载数据」按钮
                        2. **选择列**: 为X轴和Y轴选择合适的列
                        3. **选择图表**: 根据数据特征选择图表类型
                        4. **生成图表**: 点击「🎨 生成图表」按钮
                        
                        **图表类型选择**:
                        - **柱状图**: 适合分类对比
                        - **折线图**: 适合趋势分析
                        - **散点图**: 适合相关性分析
                        - **饼图**: 适合占比分析
                        - **面积图**: 适合累积趋势
                        - **箱线图**: 适合分布分析
                        """)
                    
                    with gr.Column(scale=3):
                        gr.Markdown("### 📊 图表展示")
                        viz_chart = gr.Plot(label="图表", show_label=False)
                        
                        gr.Markdown("### 📋 数据表格")
                        viz_dataframe = gr.Dataframe(
                            label="查询结果",
                            wrap=True,
                            interactive=False
                        )
            
            # Tab 4: 系统设置
            with gr.Tab("⚙️ 系统设置"):
                gr.Markdown("### 🚀 系统初始化")
                init_btn = gr.Button("🔄 初始化系统", variant="primary", size="lg")
                init_result = gr.Markdown()
                
                gr.Markdown("---")
                gr.Markdown("""
                ### 📖 使用说明
                
                **1. 初始化系统**
                - 点击"初始化系统"按钮启动 AI 助手
                
                **2. 注册数据源**
                - 在"数据源管理"标签页注册数据库、文件、知识库或Web搜索
                
                **3. 开始分析**
                - 在"对话分析"标签页选择数据源并提问
                - 支持自然语言查询、SQL生成、数据分析等
                
                **4. 数据可视化**
                - 查询后在"数据可视化"标签页创建图表
                
                **5. 配置环境**
                - 编辑 `.env` 文件配置 LLM API Key 和其他参数
                
                **6. 查看文档**
                - 详细文档请查看 `docs/` 目录
                """)
        
        # 事件处理
        def update_source_list():
            """更新数据源列表"""
            if not INITIALIZED:
                return gr.update(choices=["无（直接对话）"])
            
            sources = AGENT.list_data_sources()
            source_names = ["无（直接对话）"] + list(sources.keys())
            return gr.update(choices=source_names)
        
        # 初始化按钮
        def on_init():
            success, msg = initialize_agent()
            if success:
                return msg, gr.update(choices=["无（直接对话）"])
            return msg, gr.update()
        
        init_btn.click(
            fn=on_init,
            outputs=[init_result, source_dropdown]
        )
        
        # 注册数据源
        register_db_btn.click(
            fn=register_sqlite_db,
            inputs=[db_name_input, db_path_input],
            outputs=db_result
        ).then(
            fn=update_source_list,
            outputs=source_dropdown
        )
        
        register_file_btn.click(
            fn=register_file,
            inputs=[file_name_input, file_path_input],
            outputs=file_result
        ).then(
            fn=update_source_list,
            outputs=source_dropdown
        )
        
        register_kb_btn.click(
            fn=register_knowledge_base,
            inputs=[kb_name_input, kb_dir_input],
            outputs=kb_result
        ).then(
            fn=update_source_list,
            outputs=source_dropdown
        )
        
        register_web_btn.click(
            fn=register_web_search,
            outputs=web_result
        ).then(
            fn=update_source_list,
            outputs=source_dropdown
        )
        
        # 对话功能
        def submit_message(message, history, source):
            """提交消息并清空输入框"""
            if not message:
                return history, ""
            new_history = chat_response(message, history, source)
            return new_history, ""  # 返回新历史和空字符串（清空输入框）
        
        submit_btn.click(
            fn=submit_message,
            inputs=[message_input, chatbot, source_dropdown],
            outputs=[chatbot, message_input]
        )
        
        message_input.submit(
            fn=submit_message,
            inputs=[message_input, chatbot, source_dropdown],
            outputs=[chatbot, message_input]
        )
        
        clear_btn.click(
            fn=clear_chat_history,
            outputs=chatbot
        )
        
        refresh_sources_btn.click(
            fn=update_source_list,
            outputs=source_dropdown
        )
        
        list_sources_btn.click(
            fn=list_data_sources,
            outputs=sources_display
        )
        
        # 数据可视化功能
        load_viz_btn.click(
            fn=load_data_for_viz,
            outputs=[viz_status, viz_dataframe, x_column, y_column, color_column]
        )
        
        create_chart_btn.click(
            fn=update_chart_preview,
            inputs=[chart_type, x_column, y_column, color_column],
            outputs=[viz_chart, viz_dataframe, x_column, y_column, color_column]
        )
    
    return demo


if __name__ == "__main__":
    demo = create_ui()
    
    # 启动服务
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
