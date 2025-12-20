"""
简化版多轮对话 Web UI
使用 Gradio ChatInterface 组件，更稳定可靠
"""
import os
import sys
import time
from typing import List, Dict, Optional
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入系统初始化
from init_system import initialize_system

# 初始化系统（必须在导入 Agent 之前）
initialize_system()

from src.agent import AcademicAgent
from src.utils.logger import setup_logger, logger
import gradio as gr

# 设置日志
setup_logger()

# 全局变量
AGENT: Optional[AcademicAgent] = None
INITIALIZED = False
INDEX_BUILT = False


def initialize():
    """初始化系统"""
    global AGENT, INITIALIZED
    
    try:
        logger.info("开始初始化 Agent...")
        
        # 创建 Agent 实例
        AGENT = AcademicAgent()
        INITIALIZED = True
        
        logger.info("✅ Agent 初始化成功")
        return "✅ 系统初始化成功！"
        
    except Exception as e:
        logger.error(f"系统初始化失败: {e}", exc_info=True)
        return f"❌ 初始化失败: {str(e)}"


def build_index():
    """构建索引"""
    global AGENT, INDEX_BUILT
    
    if not INITIALIZED or not AGENT:
        return "❌ 请先初始化系统"
    
    try:
        logger.info("开始构建索引...")
        start = time.time()
        
        # 构建索引（使用 rebuild_index 方法）
        index = AGENT.rebuild_index()
        elapsed = time.time() - start
        
        INDEX_BUILT = True
        
        # 获取索引统计信息
        doc_count = len(AGENT.index.docstore.docs) if hasattr(AGENT, 'index') else 0
        
        msg = f"✅ 索引构建成功！\n"
        msg += f"📊 耗时: {elapsed:.2f}秒\n"
        msg += f"📚 文档块数: {doc_count}\n"
        
        logger.info(msg)
        return msg
        
    except Exception as e:
        logger.error(f"索引构建失败: {e}", exc_info=True)
        return f"❌ 构建失败: {str(e)}"


def chat_rag(message: str, history: List, enable_web: bool, top_k: int, use_history: bool):
    """RAG 多轮对话"""
    global AGENT, INDEX_BUILT
    
    if not INITIALIZED:
        yield "❌ 系统未初始化，请先点击 '初始化系统' 按钮"
        return
    
    if not INDEX_BUILT:
        yield "❌ 索引未构建，请先点击 '构建索引' 按钮"
        return
    
    if not message or not message.strip():
        yield "⚠️ 请输入问题"
        return
    
    try:
        # 同步对话历史
        if use_history and history:
            AGENT.chat_history = []
            for h in history:
                if isinstance(h, (list, tuple)) and len(h) >= 2:
                    AGENT.chat_history.append({"role": "user", "content": h[0]})
                    AGENT.chat_history.append({"role": "assistant", "content": h[1]})
        elif not use_history:
            AGENT.clear_chat_history()
        
        # 执行查询
        result = AGENT.query(
            message,
            verbose=False,
            enable_web_search=enable_web,
            top_k=int(top_k),
            use_history=use_history
        )
        
        # 构建回复
        answer = result['answer']
        metadata = result['metadata']
        
        # 添加统计信息
        stats = f"\n\n---\n"
        stats += f"⏱️ 耗时: {metadata['elapsed_time']:.2f}秒 | "
        stats += f"📚 参考: {metadata['num_sources']}个"
        
        if use_history and metadata.get('history_turns', 0) > 0:
            stats += f" | 💬 对话: {metadata['history_turns']}轮"
        
        yield answer + stats
        
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        yield f"❌ 查询失败: {str(e)}"


def chat_direct(message: str, history: List, enable_web: bool):
    """直接 LLM 对话"""
    global AGENT, INITIALIZED
    
    if not INITIALIZED:
        yield "❌ 系统未初始化，请先点击 '初始化系统' 按钮"
        return
    
    if not message or not message.strip():
        yield "⚠️ 请输入问题"
        return
    
    try:
        # 构建带历史的上下文
        context = message
        if history:
            context_parts = ["对话历史:"]
            for h in history[-(5*2):]:
                if isinstance(h, (list, tuple)) and len(h) >= 2:
                    context_parts.append(f"用户: {h[0]}")
                    context_parts.append(f"助手: {h[1]}")
            context_parts.append(f"\n当前问题: {message}")
            context = "\n".join(context_parts)
        
        # 执行查询
        result = AGENT.query_direct(context, enable_web_search=enable_web)
        
        answer = result['answer']
        metadata = result['metadata']
        
        stats = f"\n\n---\n⏱️ 耗时: {metadata['elapsed_time']:.2f}秒"
        yield answer + stats
        
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        yield f"❌ 查询失败: {str(e)}"


def main():
    """主函数"""
    logger.info("=" * 70)
    logger.info("启动简化版多轮对话 Web UI")
    logger.info("=" * 70)
    
    # 创建界面
    with gr.Blocks(title="学术论文问答系统 - 多轮对话", theme=gr.themes.Soft()) as demo:
        
        gr.Markdown("""
        # 🎓 学术论文问答系统 - 多轮对话版
        
        **支持多轮对话的智能问答系统**
        - 📚 基于文档的 RAG 问答
        - 💬 自动记忆对话历史
        - 🤖 直接 LLM 对话模式
        """)
        
        # 系统初始化
        with gr.Accordion("🔧 系统初始化", open=True):
            with gr.Row():
                init_btn = gr.Button("1️⃣ 初始化系统", variant="primary", scale=1)
                build_btn = gr.Button("2️⃣ 构建索引", variant="primary", scale=1)
            
            with gr.Row():
                init_output = gr.Textbox(label="初始化状态", interactive=False, scale=1)
                build_output = gr.Textbox(label="构建状态", interactive=False, scale=1)
        
        gr.Markdown("---")
        
        # 对话模式选择
        with gr.Tabs():
            
            # RAG 问答
            with gr.Tab("🔍 RAG 问答（推荐）"):
                
                gr.Markdown("""
                ### 📚 基于文档的智能问答
                - ✅ 支持多轮对话，自动记忆上下文
                - 📖 基于已加载的学术文献回答
                - 🎯 答案准确，有据可查
                """)
                
                with gr.Row():
                    with gr.Column(scale=3):
                        chatbot_rag = gr.Chatbot(
                            label="对话窗口",
                            height=450
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### ⚙️ 设置")
                        
                        use_history_rag = gr.Checkbox(
                            label="💬 启用对话历史",
                            value=True,
                            info="记忆之前的对话"
                        )
                        
                        top_k_rag = gr.Slider(
                            minimum=1,
                            maximum=10,
                            value=5,
                            step=1,
                            label="📚 检索文档数",
                            info="检索的文档数量"
                        )
                        
                        enable_web_rag = gr.Checkbox(
                            label="🌐 网络搜索",
                            value=False,
                            info="搜索网页增强"
                        )
                
                # RAG 对话接口
                chat_interface_rag = gr.ChatInterface(
                    fn=chat_rag,
                    chatbot=chatbot_rag,
                    additional_inputs=[
                        enable_web_rag,
                        top_k_rag,
                        use_history_rag
                    ],
                    retry_btn=None,
                    undo_btn=None
                )
            
            # 直接对话
            with gr.Tab("💬 直接对话"):
                
                gr.Markdown("""
                ### 🤖 纯 LLM 对话
                - 💬 不使用文档检索
                - 🧠 基于模型知识回答
                - ⚡ 响应速度快
                """)
                
                with gr.Row():
                    with gr.Column(scale=3):
                        chatbot_direct = gr.Chatbot(
                            label="对话窗口",
                            height=450
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### ⚙️ 设置")
                        
                        enable_web_direct = gr.Checkbox(
                            label="🌐 网络搜索",
                            value=False,
                            info="搜索网页增强"
                        )
                
                # 直接对话接口
                chat_interface_direct = gr.ChatInterface(
                    fn=chat_direct,
                    chatbot=chatbot_direct,
                    additional_inputs=[enable_web_direct],
                    retry_btn=None,
                    undo_btn=None
                )
            
            # 系统信息
            with gr.Tab("ℹ️ 系统信息"):
                
                def get_system_info():
                    if not INITIALIZED or not AGENT:
                        return "❌ 系统未初始化"
                    
                    info = "## 📊 系统状态\n\n"
                    info += f"- ✅ 系统状态: {'已初始化' if INITIALIZED else '未初始化'}\n"
                    info += f"- 📚 索引状态: {'已构建' if INDEX_BUILT else '未构建'}\n"
                    
                    if INDEX_BUILT:
                        info += f"- 💬 对话历史: {len(AGENT.chat_history) // 2} 轮\n"
                        info += f"- 📝 最大轮数: {AGENT.max_history_turns} 轮\n"
                    
                    info += "\n## 🔧 配置信息\n\n"
                    info += f"- 🤖 LLM: {os.getenv('LLM_MODEL', 'kimi-k2-turbo-preview')}\n"
                    info += f"- 🧮 Embedding: {os.getenv('EMBEDDING_PROVIDER', 'huggingface')}\n"
                    
                    return info
                
                info_display = gr.Markdown("点击下方按钮刷新系统信息")
                refresh_btn = gr.Button("🔄 刷新信息", variant="secondary")
                refresh_btn.click(get_system_info, outputs=[info_display])
        
        # 事件绑定
        init_btn.click(initialize, outputs=[init_output])
        build_btn.click(build_index, outputs=[build_output])
    
    # 启动
    logger.info("正在启动 Gradio 服务...")
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()
