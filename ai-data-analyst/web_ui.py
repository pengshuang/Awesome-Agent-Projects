"""
Web UI - Gradio 界面（重构版）
简洁美观的数据分析助手界面
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple, List
import gradio as gr
import pandas as pd

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入系统初始化
from init_system import initialize_system

# 初始化系统（必须在导入 Agent 之前）
initialize_system()

from src.agent import DataAnalystAgent
from src.utils.logger import logger
from src.ui import (
    CUSTOM_CSS,
    CHART_TYPES,
    MSG_ERROR_NOT_INITIALIZED,
    DataSourceManager,
    create_chart_from_dataframe,
)

# ============================================================================
# 全局状态管理
# ============================================================================

class AppState:
    """应用状态管理"""
    def __init__(self):
        self.agent: Optional[DataAnalystAgent] = None
        self.ds_manager: DataSourceManager = DataSourceManager()
        self.initialized: bool = False
        self.last_query_result: Optional[pd.DataFrame] = None
        self.query_history: List[dict] = []  # 查询历史缓存 [{"timestamp": str, "question": str, "data": DataFrame}]

# 全局状态实例
app_state = AppState()


# ============================================================================
# 系统初始化
# ============================================================================

def initialize_agent() -> Tuple[bool, str]:
    """初始化 Agent"""
    try:
        logger.info("开始初始化 Agent...")
        
        max_history_turns = int(os.getenv("MAX_HISTORY_TURNS", "10"))
        app_state.agent = DataAnalystAgent(max_history_turns=max_history_turns)
        app_state.ds_manager.set_agent(app_state.agent)
        app_state.initialized = True
        
        logger.info(f"✅ Agent 初始化成功（历史轮数: {max_history_turns}）")
        
        result = f"""## ✅ 系统初始化成功！

### ⚙️ 系统配置

- **历史轮数**: {max_history_turns} 轮
- **LLM模型**: {os.getenv('LLM_MODEL', 'N/A')}
- **API地址**: {os.getenv('LLM_API_BASE', 'N/A')}
- **Embedding**: {os.getenv('EMBEDDING_PROVIDER', 'N/A')}

---

### 📋 下一步操作

1️⃣ **注册数据源** → 切换到「🗄️ 数据源管理」标签页  
2️⃣ **开始分析** → 切换到「💬 对话分析」标签页

💡 **提示**: 可以先创建示例数据库来体验功能：
```bash
python data/create_example_db.py
```
"""
        return True, result
        
    except Exception as e:
        logger.error(f"系统初始化失败: {e}", exc_info=True)
        return False, f"## ❌ 初始化失败\n\n**错误信息**: {str(e)}\n\n详细配置说明请查看: `API_KEY_SETUP.md`"


# ============================================================================
# 对话功能
# ============================================================================

def chat_response(message: str, history: List, source: str) -> List:
    """处理用户消息并返回回复"""
    if not app_state.initialized or not app_state.agent:
        history.append((message, MSG_ERROR_NOT_INITIALIZED))
        return history
    
    if not message.strip():
        return history
    
    try:
        # 解析数据源
        source_name = None if source == "无（直接对话）" else source
        
        # 调用Agent分析（需要获取原始结果）
        result = app_state.agent.analyzer.analyze_single_source(
            question=message,
            source_name=source_name,
            chat_history=app_state.agent._format_chat_history(),
        ) if source_name else app_state.agent._direct_chat(message)
        
        # 保存查询结果数据（用于可视化）
        if result.get("success") and result.get("data"):
            try:
                # 将字典列表转换为DataFrame
                df = pd.DataFrame(result["data"])
                app_state.last_query_result = df
                
                # 添加到历史记录（限制最多保留20条）
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                query_record = {
                    "timestamp": timestamp,
                    "question": message[:50] + "..." if len(message) > 50 else message,
                    "data": df.copy(),
                    "rows": len(df),
                    "cols": len(df.columns)
                }
                app_state.query_history.insert(0, query_record)  # 最新的放在前面
                if len(app_state.query_history) > 20:
                    app_state.query_history = app_state.query_history[:20]
                
                logger.info(f"✅ 已保存查询结果用于可视化: {len(df)} 行，历史记录数: {len(app_state.query_history)}")
            except Exception as e:
                logger.warning(f"保存查询结果失败: {e}")
        
        # 构建回复文本
        if result["success"]:
            response = result["answer"]
            # 如果有SQL，添加SQL展示
            if "sql" in result and result["sql"]:
                from src.utils.helpers import format_sql_for_display
                sql_display = format_sql_for_display(result["sql"])
                response = f"### 生成的SQL查询\n\n{sql_display}\n\n### 分析结果\n\n{response}"
        else:
            response = f"❌ 抱歉，处理您的请求时遇到了问题：\n\n{result['error']}"
        
        # 更新对话历史
        app_state.agent._add_to_history("user", message)
        app_state.agent._add_to_history("assistant", response)
        
        history.append((message, response))
        return history
        
    except Exception as e:
        error_msg = f"❌ 处理消息时出错: {str(e)}"
        logger.error(error_msg, exc_info=True)
        history.append((message, error_msg))
        return history


def clear_chat_history() -> List:
    """清空对话历史"""
    if app_state.initialized and app_state.agent:
        app_state.agent.clear_history()
    return []


# ============================================================================
# 数据源管理
# ============================================================================

def update_source_list():
    """更新数据源列表"""
    if not app_state.initialized or not app_state.agent:
        return gr.update(choices=["无（直接对话）"])
    
    sources = app_state.agent.list_data_sources()
    source_names = ["无（直接对话）"] + list(sources.keys())
    return gr.update(choices=source_names)


# ============================================================================
# 数据可视化
# ============================================================================

def get_history_choices():
    """获取历史查询选项列表"""
    if not app_state.query_history:
        return ["最新查询"]
    
    choices = []
    for i, record in enumerate(app_state.query_history):
        label = f"[{record['timestamp']}] {record['question']} ({record['rows']}行×{record['cols']}列)"
        choices.append(label)
    
    return choices


def load_data_for_viz(history_selection: str):
    """加载数据用于可视化"""
    if not app_state.query_history:
        status = "⚠️ 暂无查询结果数据\n\n请先在「对话分析」页面执行数据查询"
        return status, None, gr.update(choices=[]), gr.update(choices=[]), gr.update(choices=["无"]), gr.update(choices=["最新查询"])
    
    # 解析选择的历史记录索引
    try:
        # 从选择的文本中提取时间戳来匹配记录
        selected_timestamp = history_selection.split("]")[0][1:] if "[" in history_selection else None
        
        # 查找对应的记录
        df = None
        for record in app_state.query_history:
            if selected_timestamp and record["timestamp"] == selected_timestamp:
                df = record["data"]
                break
        
        # 如果没找到，使用最新的
        if df is None:
            df = app_state.query_history[0]["data"]
    except Exception as e:
        logger.warning(f"解析历史选择失败: {e}，使用最新数据")
        df = app_state.query_history[0]["data"]
    
    columns = list(df.columns)
    status = f"✅ 数据已加载\n\n- **行数**: {len(df)}\n- **列数**: {len(columns)}\n- **列名**: {', '.join(columns)}"
    
    # 更新当前可视化使用的数据
    app_state.last_query_result = df
    
    return (
        status,
        df,
        gr.update(choices=columns, value=columns[0] if columns else None),
        gr.update(choices=columns, value=columns[1] if len(columns) > 1 else columns[0] if columns else None),
        gr.update(choices=["无"] + columns, value="无"),
        gr.update(choices=get_history_choices())
    )


def update_chart_preview(chart_type: str, x_col: str, y_col: str, color_col: Optional[str]):
    """更新图表预览"""
    if app_state.last_query_result is None:
        return (
            None,
            None,
            gr.update(choices=[]),
            gr.update(choices=[]),
            gr.update(choices=["无"])
        )
    
    df = app_state.last_query_result
    
    # 映射中文图表类型到英文
    chart_type_map = {
        "柱状图": "bar",
        "折线图": "line",
        "散点图": "scatter",
        "饼图": "pie",
        "面积图": "area",
        "箱线图": "box",
    }
    
    chart_type_en = chart_type_map.get(chart_type, "bar")
    
    # 创建图表
    fig = create_chart_from_dataframe(
        df=df,
        chart_type=chart_type_en,
        x_col=x_col,
        y_col=y_col,
        color_col=color_col if color_col != "无" else None,
        title=f"{chart_type}: {y_col} vs {x_col}"
    )
    
    columns = list(df.columns)
    
    return (
        fig,
        df,
        gr.update(choices=columns, value=x_col),
        gr.update(choices=columns, value=y_col),
        gr.update(choices=["无"] + columns, value=color_col)
    )


# ============================================================================
# UI 构建
# ============================================================================

def create_ui():
    """创建Gradio界面"""
    
    with gr.Blocks(css=CUSTOM_CSS, title="AI 数据分析助手", theme=gr.themes.Soft()) as demo:
        # 标题
        gr.HTML("""
        <div style="text-align: center; padding: 20px;">
            <h1>🤖 AI 数据分析助手</h1>
            <p>基于大模型的智能数据分析工具 | 支持多数据源融合分析 | NL2SQL | 报告生成</p>
        </div>
        """)
        
        # 主界面
        with gr.Tabs() as tabs:
            # ======== Tab 1: 对话分析 ========
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
                            refresh_sources_btn = gr.Button("🔄 刷新数据源", scale=1)
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 📊 数据源列表")
                        sources_display = gr.Markdown("暂无数据源")
                        list_sources_btn = gr.Button("📋 查看所有数据源")
            
            # ======== Tab 2: 数据源管理 ========
            with gr.Tab("🗄️ 数据源管理"):
                with gr.Row():
                    # SQLite 数据库
                    with gr.Column():
                        gr.Markdown("### 📁 SQLite 数据库")
                        db_name_input = gr.Textbox(label="数据库名称", placeholder="例如：sales_db")
                        db_path_input = gr.Textbox(
                            label="数据库路径",
                            placeholder="例如：data/databases/sales.db"
                        )
                        register_db_btn = gr.Button("➕ 注册数据库", variant="primary")
                        db_result = gr.Markdown()
                    
                    # 文件数据源
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
                    # 知识库
                    with gr.Column():
                        gr.Markdown("### 📚 知识库")
                        kb_name_input = gr.Textbox(label="知识库名称", placeholder="例如：business_kb")
                        kb_dir_input = gr.Textbox(
                            label="知识库目录（可选）",
                            placeholder="留空使用默认目录"
                        )
                        register_kb_btn = gr.Button("➕ 注册知识库", variant="primary")
                        kb_result = gr.Markdown()
                    
                    # Web 搜索
                    with gr.Column():
                        gr.Markdown("### 🌐 Web 搜索")
                        gr.Markdown("启用Web搜索以获取实时互联网信息")
                        register_web_btn = gr.Button("🔌 启用Web搜索", variant="primary")
                        web_result = gr.Markdown()
            
            # ======== Tab 3: 数据可视化 ========
            with gr.Tab("📊 数据可视化"):
                gr.Markdown("### 📈 将查询结果可视化\n在「对话分析」中执行数据查询后，可以在此处创建图表")
                
                with gr.Row():
                    # 左侧：配置面板
                    with gr.Column(scale=1):
                        gr.Markdown("### ⚙️ 图表配置")
                        history_selector = gr.Dropdown(
                            label="📜 选择历史查询",
                            choices=["最新查询"],
                            value="最新查询",
                            interactive=True
                        )
                        load_viz_btn = gr.Button("🔄 加载选中数据", variant="primary", size="lg")
                        viz_status = gr.Markdown("⚠️ 请先加载数据")
                        gr.Markdown("---")
                        
                        chart_type = gr.Dropdown(
                            label="图表类型",
                            choices=["柱状图", "折线图", "散点图", "饼图", "面积图"],
                            value="柱状图"
                        )
                        x_column = gr.Dropdown(label="X轴（分类/时间）", choices=[], value=None)
                        y_column = gr.Dropdown(label="Y轴（数值）", choices=[], value=None)
                        color_column = gr.Dropdown(label="颜色分组（可选）", choices=["无"], value="无")
                        
                        create_chart_btn = gr.Button("🎨 生成图表", variant="primary", size="lg")
                    
                    # 右侧：图表展示
                    with gr.Column(scale=3):
                        gr.Markdown("### 📊 图表展示")
                        viz_chart = gr.Plot(label="图表", show_label=False)
                        gr.Markdown("### 📋 数据表格")
                        viz_dataframe = gr.Dataframe(label="查询结果", wrap=True, interactive=False)
            
            # ======== Tab 4: 系统设置 ========
            with gr.Tab("⚙️ 系统设置"):
                gr.Markdown("### 🚀 系统初始化")
                init_btn = gr.Button("🔄 初始化系统", variant="primary", size="lg")
                init_result = gr.Markdown()
                
                gr.Markdown("---")
                gr.Markdown("""
                ### 📖 使用说明
                
                **1. 初始化系统** - 点击"初始化系统"按钮启动 AI 助手  
                **2. 注册数据源** - 在"数据源管理"标签页注册数据库、文件等  
                **3. 开始分析** - 在"对话分析"标签页选择数据源并提问  
                **4. 数据可视化** - 查询后在"数据可视化"标签页创建图表  
                **5. 配置环境** - 编辑 `.env` 文件配置 LLM API Key  
                **6. 查看文档** - 详细文档请查看 `docs/` 目录
                """)
        
        # ======================================================================
        # 事件绑定
        # ======================================================================
        
        # 初始化
        init_btn.click(
            fn=lambda: (initialize_agent()[1], update_source_list()),
            outputs=[init_result, source_dropdown]
        )
        
        # 注册数据源
        register_db_btn.click(
            fn=app_state.ds_manager.register_sqlite,
            inputs=[db_name_input, db_path_input],
            outputs=db_result
        ).then(fn=update_source_list, outputs=source_dropdown)
        
        register_file_btn.click(
            fn=app_state.ds_manager.register_file,
            inputs=[file_name_input, file_path_input],
            outputs=file_result
        ).then(fn=update_source_list, outputs=source_dropdown)
        
        register_kb_btn.click(
            fn=app_state.ds_manager.register_knowledge_base,
            inputs=[kb_name_input, kb_dir_input],
            outputs=kb_result
        ).then(fn=update_source_list, outputs=source_dropdown)
        
        register_web_btn.click(
            fn=app_state.ds_manager.register_web_search,
            outputs=web_result
        ).then(fn=update_source_list, outputs=source_dropdown)
        
        # 对话功能
        def submit_message(msg, hist, src):
            if not msg:
                return hist, ""
            new_hist = chat_response(msg, hist, src)
            return new_hist, ""
        
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
        
        clear_btn.click(fn=clear_chat_history, outputs=chatbot)
        refresh_sources_btn.click(fn=update_source_list, outputs=source_dropdown)
        list_sources_btn.click(fn=app_state.ds_manager.list_sources, outputs=sources_display)
        
        # 数据可视化
        load_viz_btn.click(
            fn=load_data_for_viz,
            inputs=[history_selector],
            outputs=[viz_status, viz_dataframe, x_column, y_column, color_column, history_selector]
        )
        
        create_chart_btn.click(
            fn=update_chart_preview,
            inputs=[chart_type, x_column, y_column, color_column],
            outputs=[viz_chart, viz_dataframe, x_column, y_column, color_column]
        )
    
    return demo


# ============================================================================
# 主程序入口
# ============================================================================

if __name__ == "__main__":
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
