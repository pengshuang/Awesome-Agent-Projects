"""
Web UI - Gradio 界面（优化版）
简洁友好的数据分析助手界面 - 减少操作步骤，提升用户体验
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
        self.auto_visualize: bool = True  # 自动生成可视化

# 全局状态实例
app_state = AppState()


# ============================================================================
# 系统初始化
# ============================================================================

def initialize_agent() -> Tuple[bool, str]:
    """初始化 Agent（自动在启动时调用）"""
    try:
        if app_state.initialized:
            return True, "✅ 系统已就绪"
        
        logger.info("开始初始化 Agent...")
        
        max_history_turns = int(os.getenv("MAX_HISTORY_TURNS", "10"))
        app_state.agent = DataAnalystAgent(max_history_turns=max_history_turns)
        app_state.ds_manager.set_agent(app_state.agent)
        app_state.initialized = True
        
        logger.info(f"✅ Agent 初始化成功（历史轮数: {max_history_turns}）")
        
        result = f"✅ 系统已就绪 | 模型: {os.getenv('LLM_MODEL', 'N/A')}"
        return True, result
        
    except Exception as e:
        logger.error(f"系统初始化失败: {e}", exc_info=True)
        return False, f"❌ 初始化失败: {str(e)}"


# ============================================================================
# 对话功能
# ============================================================================

def chat_response(message: str, history: List, source: str):
    """处理用户消息并返回回复，同时自动生成可视化"""
    if not app_state.initialized or not app_state.agent:
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": MSG_ERROR_NOT_INITIALIZED})
        return history, None, None, gr.update(), gr.update(), gr.update(), gr.update()
    
    if not message.strip():
        return history, None, None, gr.update(), gr.update(), gr.update(), gr.update()
    
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
        viz_chart = None
        viz_df = None
        if result.get("success") and result.get("data"):
            try:
                # 将字典列表转换为DataFrame
                df = pd.DataFrame(result["data"])
                app_state.last_query_result = df
                viz_df = df
                
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
                app_state.query_history.insert(0, query_record)
                if len(app_state.query_history) > 20:
                    app_state.query_history = app_state.query_history[:20]
                
                # 自动生成可视化（如果数据合适）
                if app_state.auto_visualize and len(df) > 0 and len(df.columns) >= 2:
                    try:
                        cols = list(df.columns)
                        x_col = cols[0]
                        y_col = cols[1] if len(cols) > 1 else cols[0]
                        
                        # 智能选择图表类型
                        chart_type = "bar"
                        if df[y_col].dtype in ['float64', 'int64'] and len(df) > 10:
                            chart_type = "line"
                        
                        viz_chart = create_chart_from_dataframe(
                            df=df,
                            chart_type=chart_type,
                            x_col=x_col,
                            y_col=y_col,
                            title=f"{y_col} vs {x_col}"
                        )
                        logger.info(f"✅ 自动生成可视化图表: {chart_type}")
                    except Exception as e:
                        logger.warning(f"自动可视化失败: {e}")
                
                logger.info(f"✅ 已保存查询结果: {len(df)} 行")
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
        
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        
        # 更新可视化选项
        cols = list(viz_df.columns) if viz_df is not None else []
        history_choices = get_history_choices()
        return (
            history,
            viz_chart,
            viz_df,
            gr.update(choices=cols, value=cols[0] if cols else None),
            gr.update(choices=cols, value=cols[1] if len(cols) > 1 else cols[0] if cols else None),
            gr.update(choices=["无"] + cols, value="无"),
            gr.update(choices=history_choices, value="当前查询")
        )
        
    except Exception as e:
        error_msg = f"❌ 处理消息时出错: {str(e)}"
        logger.error(error_msg, exc_info=True)
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": error_msg})
        return history, None, None, gr.update(), gr.update(), gr.update(), gr.update()


def clear_chat_history() -> List:
    """清空对话历史"""
    if app_state.initialized and app_state.agent:
        app_state.agent.clear_history()
    return []


# ============================================================================
# 数据源管理 - 快捷注册
# ============================================================================

def quick_register_datasource(ds_type: str, name: str, path: str):
    """快捷注册数据源（统一接口）"""
    if not name or not path:
        return "❌ 请填写完整的名称和路径", gr.update()
    
    try:
        if ds_type == "SQLite数据库":
            result = app_state.ds_manager.register_sqlite(name, path)
        elif ds_type == "文件(CSV/Excel)":
            result = app_state.ds_manager.register_file(name, path)
        elif ds_type == "知识库":
            result = app_state.ds_manager.register_knowledge_base(name, path if path.strip() else None)
        else:
            return "❌ 不支持的数据源类型", gr.update()
        
        # 更新数据源列表
        new_sources = update_source_list()
        return result, new_sources
    except Exception as e:
        logger.error(f"注册数据源失败: {e}")
        return f"❌ 注册失败: {str(e)}", gr.update()


def update_source_list():
    """更新数据源列表"""
    if not app_state.initialized or not app_state.agent:
        return gr.update(choices=["无（直接对话）"])
    
    sources = app_state.agent.list_data_sources()
    source_names = ["无（直接对话）"] + list(sources.keys())
    return gr.update(choices=source_names)


# ============================================================================
# 数据可视化 - 简化版
# ============================================================================

def get_history_choices():
    """获取历史查询选项列表"""
    if not app_state.query_history:
        return ["当前查询"]
    
    choices = ["当前查询"]
    for record in app_state.query_history:
        label = f"[{record['timestamp']}] {record['question']} ({record['rows']}行)"
        choices.append(label)
    
    return choices


def load_history_data(history_selection: str):
    """加载选中的历史查询数据"""
    if history_selection == "当前查询" or not app_state.query_history:
        # 使用当前数据
        if app_state.last_query_result is None:
            return None, None, gr.update(), gr.update(), gr.update()
        
        df = app_state.last_query_result
    else:
        # 解析选择的历史记录
        try:
            selected_timestamp = history_selection.split("]")[0][1:] if "[" in history_selection else None
            df = None
            
            for record in app_state.query_history:
                if selected_timestamp and record["timestamp"] == selected_timestamp:
                    df = record["data"]
                    break
            
            if df is None:
                df = app_state.query_history[0]["data"]
        except Exception as e:
            logger.warning(f"解析历史选择失败: {e}，使用最新数据")
            df = app_state.query_history[0]["data"] if app_state.query_history else app_state.last_query_result
    
    if df is None:
        return None, None, gr.update(), gr.update(), gr.update()
    
    # 更新当前可视化使用的数据
    app_state.last_query_result = df
    
    # 自动生成图表
    cols = list(df.columns)
    x_col = cols[0] if cols else None
    y_col = cols[1] if len(cols) > 1 else cols[0] if cols else None
    
    chart = None
    if x_col and y_col:
        chart = create_chart_from_dataframe(
            df=df,
            chart_type="bar",
            x_col=x_col,
            y_col=y_col,
            title=f"{y_col} vs {x_col}"
        )
    
    return (
        chart,
        df,
        gr.update(choices=cols, value=x_col),
        gr.update(choices=cols, value=y_col),
        gr.update(choices=["无"] + cols, value="无")
    )


def update_chart(chart_type: str, x_col: str, y_col: str, color_col: Optional[str]):
    """更新图表（实时预览）"""
    if app_state.last_query_result is None or x_col is None or y_col is None:
        return None
    
    df = app_state.last_query_result
    
    # 映射中文图表类型到英文
    chart_type_map = {
        "柱状图": "bar",
        "折线图": "line",
        "散点图": "scatter",
        "饼图": "pie",
        "面积图": "area",
    }
    
    chart_type_en = chart_type_map.get(chart_type, "bar")
    
    # 创建图表
    fig = create_chart_from_dataframe(
        df=df,
        chart_type=chart_type_en,
        x_col=x_col,
        y_col=y_col,
        color_col=color_col if color_col and color_col != "无" else None,
        title=f"{y_col} vs {x_col}"
    )
    
    return fig


# ============================================================================
# UI 构建 - 简化版
# ============================================================================

def create_ui():
    """创建Gradio界面 - 优化后的简洁版本"""
    
    with gr.Blocks(css=CUSTOM_CSS, title="AI 数据分析助手", theme=gr.themes.Soft()) as demo:
        # 顶部状态栏
        with gr.Row():
            gr.HTML("""
            <div style="text-align: center; padding: 15px;">
                <h2>🤖 AI 数据分析助手</h2>
                <p style="color: #666; margin: 5px 0;">快速分析 | 智能可视化 | 自然语言交互</p>
            </div>
            """)
            system_status = gr.Markdown("⏳ 正在初始化...", elem_classes=["system-status"])
        
        # 操作指引
        with gr.Row():
            gr.Markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; color: white; margin-bottom: 10px;">
                <h3 style="margin: 0 0 10px 0; color: white;">📖 快速开始</h3>
                <p style="margin: 5px 0; font-size: 14px;">① 点击底部<strong>「➕ 快速添加数据源」</strong>注册数据库/文件 → ② 在左侧<strong>选择数据源</strong> → ③ <strong>输入问题</strong>自动生成分析和图表</p>
                <p style="margin: 5px 0; font-size: 13px; opacity: 0.9;">💡 提示：查询后右侧自动显示可视化，可在「⚙️ 图表设置」中调整样式</p>
            </div>
            """)
        
        # 主界面 - 单屏设计
        with gr.Row():
            # 左侧：对话区 (60%)
            with gr.Column(scale=3):
                gr.Markdown("### 💬 智能对话")
                
                # 数据源选择（精简）
                with gr.Row():
                    source_dropdown = gr.Dropdown(
                        label="📊 数据源",
                        choices=["无（直接对话）"],
                        value="无（直接对话）",
                        scale=3,
                        container=False
                    )
                    refresh_btn = gr.Button("🔄", scale=0, size="sm")
                
                # 对话窗口
                chatbot = gr.Chatbot(
                    label="",
                    height=400,
                    show_copy_button=True,
                    render_markdown=True,
                    type='messages',
                    container=False
                )
                
                # 输入区（精简）
                with gr.Row():
                    message_input = gr.Textbox(
                        label="",
                        placeholder="💡 输入你的问题，例如：显示销售前10名的产品...",
                        lines=2,
                        scale=5,
                        container=False
                    )
                
                with gr.Row():
                    submit_btn = gr.Button("📤 发送", variant="primary", scale=2)
                    clear_btn = gr.Button("🗑️ 清空", scale=1, variant="secondary")
            
            # 右侧：可视化区 (40%)
            with gr.Column(scale=2):
                with gr.Row():
                    gr.Markdown("### 📊 数据可视化")
                    history_dropdown = gr.Dropdown(
                        label="",
                        choices=["当前查询"],
                        value="当前查询",
                        scale=1,
                        container=False,
                        interactive=True,
                        elem_classes=["history-selector"]
                    )
                
                # 图表显示（自动生成）
                viz_chart = gr.Plot(label="", show_label=False, container=False)
                
                # 图表控制（折叠式）
                with gr.Accordion("⚙️ 图表设置", open=False):
                    chart_type = gr.Radio(
                        choices=["柱状图", "折线图", "散点图", "饼图", "面积图"],
                        value="柱状图",
                        label="图表类型",
                        container=False
                    )
                    with gr.Row():
                        x_column = gr.Dropdown(label="X轴", choices=[], value=None, scale=1)
                        y_column = gr.Dropdown(label="Y轴", choices=[], value=None, scale=1)
                    color_column = gr.Dropdown(label="颜色分组（可选）", choices=["无"], value="无")
                
                # 数据表格（折叠式）
                with gr.Accordion("📋 数据详情", open=False):
                    viz_dataframe = gr.Dataframe(
                        label="",
                        wrap=True,
                        interactive=False,
                        max_height=300
                    )
        
        # 底部：快捷操作区
        with gr.Accordion("➕ 快速添加数据源", open=False):
            with gr.Row():
                ds_type = gr.Radio(
                    choices=["SQLite数据库", "文件(CSV/Excel)", "知识库"],
                    value="SQLite数据库",
                    label="类型",
                    scale=1
                )
                with gr.Column(scale=3):
                    with gr.Row():
                        ds_name = gr.Textbox(label="名称", placeholder="例如：sales_db", scale=1)
                        ds_path = gr.Textbox(label="路径", placeholder="例如：data/databases/sales.db", scale=2)
                    ds_result = gr.Markdown("")
                add_btn = gr.Button("➕ 添加", variant="primary", scale=1)
        
        # ======================================================================
        # 事件绑定 - 简化版
        # ======================================================================
        
        # 自动初始化（页面加载时）
        demo.load(
            fn=lambda: (initialize_agent()[1], update_source_list()),
            outputs=[system_status, source_dropdown]
        )
        
        # 对话功能
        def submit_message(msg, hist, src):
            if not msg:
                return hist, "", None, None, gr.update(), gr.update(), gr.update(), gr.update()
            new_hist, chart, df, x_upd, y_upd, c_upd, hist_upd = chat_response(msg, hist, src)
            return new_hist, "", chart, df, x_upd, y_upd, c_upd, hist_upd
        
        submit_btn.click(
            fn=submit_message,
            inputs=[message_input, chatbot, source_dropdown],
            outputs=[chatbot, message_input, viz_chart, viz_dataframe, x_column, y_column, color_column, history_dropdown]
        )
        
        message_input.submit(
            fn=submit_message,
            inputs=[message_input, chatbot, source_dropdown],
            outputs=[chatbot, message_input, viz_chart, viz_dataframe, x_column, y_column, color_column, history_dropdown]
        )
        
        clear_btn.click(fn=clear_chat_history, outputs=chatbot)
        refresh_btn.click(fn=update_source_list, outputs=source_dropdown)
        
        # 历史查询切换
        history_dropdown.change(
            fn=load_history_data,
            inputs=[history_dropdown],
            outputs=[viz_chart, viz_dataframe, x_column, y_column, color_column]
        )
        
        # 快速添加数据源
        add_btn.click(
            fn=quick_register_datasource,
            inputs=[ds_type, ds_name, ds_path],
            outputs=[ds_result, source_dropdown]
        )
        
        # 图表实时更新
        for component in [chart_type, x_column, y_column, color_column]:
            component.change(
                fn=update_chart,
                inputs=[chart_type, x_column, y_column, color_column],
                outputs=viz_chart
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
