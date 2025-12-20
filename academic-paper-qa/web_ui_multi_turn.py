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
CHAT_CLEARED = False  # 标记对话是否被清空


def initialize():
    """初始化系统"""
    global AGENT, INITIALIZED
    
    try:
        logger.info("开始初始化 Agent...")
        
        # 从环境变量读取历史轮数配置（默认10轮）
        max_history_turns = int(os.getenv("MAX_HISTORY_TURNS", "10"))
        
        # 创建 Agent 实例
        AGENT = AcademicAgent(max_history_turns=max_history_turns)
        INITIALIZED = True
        
        logger.info(f"✅ Agent 初始化成功（历史轮数: {max_history_turns}）")
        return f"✅ 系统初始化成功！\n📝 历史轮数限制: {max_history_turns} 轮"
        
    except Exception as e:
        logger.error(f"系统初始化失败: {e}", exc_info=True)
        return f"❌ 初始化失败: {str(e)}"


def initialize_and_build():
    """初始化系统并构建索引（合并操作）"""
    global AGENT, INITIALIZED, INDEX_BUILT
    
    status_messages = []
    
    try:
        # 步骤 1: 初始化系统
        logger.info("=" * 70)
        logger.info("步骤 1/2: 初始化系统")
        logger.info("=" * 70)
        
        status_messages.append("🔄 [1/2] 正在初始化系统...")
        yield "\n".join(status_messages)
        
        start_init = time.time()
        # 创建 Agent 时不自动加载索引，避免重复生成 embeddings
        AGENT = AcademicAgent(auto_load=False)
        INITIALIZED = True
        elapsed_init = time.time() - start_init
        
        init_msg = f"✅ [1/2] 系统初始化成功！耗时: {elapsed_init:.2f}秒"
        status_messages.append(init_msg)
        logger.info(init_msg)
        yield "\n".join(status_messages)
        
        # 步骤 2: 构建索引
        logger.info("=" * 70)
        logger.info("步骤 2/2: 构建索引")
        logger.info("=" * 70)
        
        status_messages.append("\n🔄 [2/2] 正在构建索引...")
        yield "\n".join(status_messages)
        
        start_build = time.time()
        index = AGENT.rebuild_index()
        elapsed_build = time.time() - start_build
        
        INDEX_BUILT = True
        
        # 获取索引统计信息
        doc_count = len(AGENT.index.docstore.docs) if hasattr(AGENT, 'index') else 0
        
        build_msg = f"✅ [2/2] 索引构建成功！耗时: {elapsed_build:.2f}秒"
        status_messages.append(build_msg)
        status_messages.append(f"📚 文档块数: {doc_count}")
        status_messages.append(f"\n⏱️  总耗时: {elapsed_init + elapsed_build:.2f}秒")
        status_messages.append("\n🎉 系统已就绪，可以开始使用！")
        
        logger.info(build_msg)
        final_status = "\n".join(status_messages)
        yield final_status
        
        return final_status
        
    except Exception as e:
        error_msg = f"\n❌ 操作失败: {str(e)}"
        status_messages.append(error_msg)
        logger.error(f"初始化或构建失败: {e}", exc_info=True)
        yield "\n".join(status_messages)


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
    global AGENT, INDEX_BUILT, CHAT_CLEARED
    
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
        # 如果刚刚清空了历史，不要从 Gradio 的 history 恢复
        if CHAT_CLEARED:
            AGENT.clear_chat_history()
            CHAT_CLEARED = False  # 重置标志
        # 同步对话历史
        elif use_history and history:
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
        source_nodes = result.get('source_nodes', [])
        web_sources = result.get('web_sources', [])
        
        # 添加统计信息
        stats = f"\n\n---\n"
        stats += f"⏱️ 耗时: {metadata['elapsed_time']:.2f}秒 | "
        stats += f"📚 参考: {metadata['num_sources']}个"
        
        if use_history and metadata.get('history_turns', 0) > 0:
            stats += f" | 💬 对话: {metadata['history_turns']}轮"
        
        # 添加检索到的文档片段
        if source_nodes:
            stats += "\n\n<details><summary><b>📄 检索到的文档片段</b> (点击展开)</summary>\n\n"
            for i, node in enumerate(source_nodes[:3], 1):  # 只显示前3个
                file_name = node.metadata.get('file_name', 'Unknown')
                score = node.score if hasattr(node, 'score') else 'N/A'
                text_preview = node.text[:200].replace('\n', ' ') if hasattr(node, 'text') else 'N/A'
                stats += f"<small>\n\n**[{i}] {file_name}** (相似度: {score})\n\n"
                stats += f"{text_preview}...\n\n</small>"
            stats += "</details>"
        
        # 添加网络搜索结果
        if web_sources:
            stats += "\n\n<details><summary><b>🌐 网络搜索结果</b> (点击展开)</summary>\n\n"
            for i, source in enumerate(web_sources, 1):
                stats += f"<small>\n\n**[{i}] [{source['title']}]({source['url']})**\n\n"
                stats += f"{source['snippet'][:150]}...\n\n</small>"
            stats += "</details>"
        
        yield answer + stats
        
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        yield f"❌ 查询失败: {str(e)}"


def clear_chat_history():
    """清空对话历史"""
    global AGENT, CHAT_CLEARED
    
    if AGENT:
        AGENT.clear_chat_history()
        CHAT_CLEARED = True  # 设置标志，表示用户手动清空了历史
        logger.info("✅ 对话历史已清空")
    
    return []  # 返回空列表来清空 chatbot 显示


def update_history_setting(max_turns: int):
    """更新历史轮数设置"""
    global AGENT
    
    if not INITIALIZED or not AGENT:
        return "❌ 系统未初始化"
    
    try:
        AGENT.set_max_history_turns(max_turns)
        info = AGENT.get_chat_history_info()
        status = f"✅ 已更新\n当前: {info['current_turns']}/{info['max_turns']} 轮"
        logger.info(f"历史轮数已更新为: {max_turns}")
        return status
    except Exception as e:
        logger.error(f"更新历史设置失败: {e}")
        return f"❌ 更新失败: {str(e)}"


def get_history_status():
    """获取历史状态"""
    global AGENT
    
    if not INITIALIZED or not AGENT:
        return "系统未初始化"
    
    try:
        info = AGENT.get_chat_history_info()
        return f"当前: {info['current_turns']}/{info['max_turns']} 轮"
    except:
        return "无法获取状态"


def chat_direct(message: str, history: List, enable_web: bool, selected_docs: List[str]):
    """直接 LLM 对话（支持文档附件）"""
    global AGENT, INITIALIZED, CHAT_CLEARED
    
    if not INITIALIZED:
        yield "❌ 系统未初始化，请先点击 '初始化系统' 按钮"
        return
    
    if not message or not message.strip():
        yield "⚠️ 请输入问题"
        return
    
    try:
        # 如果刚刚清空了历史，忽略 Gradio 传来的 history
        if CHAT_CLEARED:
            history = []
            CHAT_CLEARED = False  # 重置标志
        
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
        
        # 执行查询（带文档附件）
        result = AGENT.query_direct(
            question=context, 
            enable_web_search=enable_web,
            document_files=selected_docs if selected_docs else None
        )
        
        answer = result['answer']
        metadata = result['metadata']
        web_sources = result.get('web_sources', [])
        
        stats = f"\n\n---\n⏱️ 耗时: {metadata['elapsed_time']:.2f}秒"
        
        # 添加文档附件信息
        if result.get('document_sources'):
            stats += f" | 📎 附件: {len(result['document_sources'])}个"
            stats += "\n\n<details><summary><b>📄 使用的文档</b> (点击展开)</summary>\n\n"
            for doc in result['document_sources']:
                stats += f"<small>- 📄 {doc}</small>\n\n"
            stats += "</details>"
        
        # 添加网络搜索结果
        if web_sources:
            stats += "\n\n<details><summary><b>🌐 网络搜索结果</b> (点击展开)</summary>\n\n"
            for i, source in enumerate(web_sources, 1):
                stats += f"<small>\n\n**[{i}] [{source['title']}]({source['url']})**\n\n"
                stats += f"{source['snippet'][:150]}...\n\n</small>"
            stats += "</details>"
        
        yield answer + stats
        
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        yield f"❌ 查询失败: {str(e)}"


def get_available_documents():
    """获取可用文档列表"""
    global AGENT, INITIALIZED
    
    if not INITIALIZED or not AGENT:
        return []
    
    try:
        return AGENT.list_available_documents()
    except Exception as e:
        logger.error(f"获取文档列表失败: {e}")
        return []


def main():
    """主函数"""
    logger.info("=" * 70)
    logger.info("启动简化版多轮对话 Web UI")
    logger.info("=" * 70)
    
    # 创建界面
    with gr.Blocks(title="学术论文问答系统 - 多轮对话") as demo:
        
        gr.Markdown("""
        # 🎓 学术论文问答系统 - 多轮对话版
        
        **支持多轮对话的智能问答系统**
        - 📚 基于文档的 RAG 问答
        - 💬 自动记忆对话历史
        - 🤖 直接 LLM 对话模式
        """)
        
        # 系统初始化
        with gr.Accordion("🔧 系统初始化与索引构建", open=True):
            gr.Markdown("""
            💡 **提示**: 首次使用或更新文档后，请点击下方按钮初始化系统并构建索引
            """)
            
            init_and_build_btn = gr.Button(
                "🚀 初始化系统并构建索引", 
                variant="primary",
                size="lg"
            )
            
            status_output = gr.Textbox(
                label="📊 系统状态", 
                interactive=False,
                lines=8,
                max_lines=15
            )
        
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
                        
                        gr.Markdown("---")
                        gr.Markdown("### 📊 对话历史控制")
                        
                        max_history_slider = gr.Slider(
                            minimum=1,
                            maximum=50,
                            value=10,
                            step=1,
                            label="📝 最大历史轮数",
                            info="限制保留的对话轮数"
                        )
                        
                        update_history_btn = gr.Button(
                            "✅ 更新历史设置",
                            size="sm"
                        )
                        
                        history_status = gr.Textbox(
                            label="历史状态",
                            value="未设置",
                            interactive=False,
                            max_lines=2
                        )
                        
                        gr.Markdown("---")
                        
                        clear_btn_rag = gr.Button(
                            "🗑️ 清空对话历史",
                            variant="secondary",
                            size="sm"
                        )
                
                # RAG 对话接口
                chat_interface_rag = gr.ChatInterface(
                    fn=chat_rag,
                    chatbot=chatbot_rag,
                    additional_inputs=[
                        enable_web_rag,
                        top_k_rag,
                        use_history_rag
                    ]
                )
            
            # 直接对话
            with gr.Tab("💬 直接对话"):
                
                gr.Markdown("""
                ### 🤖 纯 LLM 对话
                - 💬 不使用文档检索
                - 🧠 基于模型知识回答
                - 📎 支持附加文档作为上下文
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
                        
                        # 文档选择器
                        doc_selector = gr.CheckboxGroup(
                            choices=[],
                            label="📎 选择文档附件",
                            info="将文档内容发送给 LLM",
                            interactive=True
                        )
                        
                        refresh_docs_btn = gr.Button("🔄 刷新文档列表", size="sm")
                        
                        enable_web_direct = gr.Checkbox(
                            label="🌐 网络搜索",
                            value=False,
                            info="搜索网页增强"
                        )
                        
                        gr.Markdown("---")
                        
                        clear_btn_direct = gr.Button(
                            "🗑️ 清空对话历史",
                            variant="secondary",
                            size="sm"
                        )
                
                # 刷新文档列表
                def refresh_doc_list():
                    docs = get_available_documents()
                    return gr.CheckboxGroup(choices=docs, value=[])
                
                refresh_docs_btn.click(
                    fn=refresh_doc_list,
                    outputs=doc_selector
                )
                
                # 直接对话接口
                chat_interface_direct = gr.ChatInterface(
                    fn=chat_direct,
                    chatbot=chatbot_direct,
                    additional_inputs=[enable_web_direct, doc_selector]
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
                        hist_info = AGENT.get_chat_history_info()
                        info += f"- 💬 对话历史: {hist_info['current_turns']}/{hist_info['max_turns']} 轮\n"
                        info += f"- 📊 消息总数: {hist_info['total_messages']} 条\n"
                        info += f"- ⚠️  是否已满: {'是' if hist_info['is_full'] else '否'}\n"
                    
                    info += "\n## 🔧 配置信息\n\n"
                    info += f"- 🤖 LLM: {os.getenv('LLM_MODEL', 'kimi-k2-turbo-preview')}\n"
                    info += f"- 🧮 Embedding: {os.getenv('EMBEDDING_PROVIDER', 'huggingface')}\n"
                    
                    return info
                
                info_display = gr.Markdown("点击下方按钮刷新系统信息")
                refresh_btn = gr.Button("🔄 刷新信息", variant="secondary")
                refresh_btn.click(get_system_info, outputs=[info_display])
        
        # 事件绑定
        init_and_build_btn.click(
            initialize_and_build, 
            outputs=[status_output]
        )
        
        # 更新历史设置按钮绑定
        update_history_btn.click(
            update_history_setting,
            inputs=[max_history_slider],
            outputs=[history_status]
        )
        
        # 清空对话历史按钮绑定
        clear_btn_rag.click(
            clear_chat_history,
            outputs=[chatbot_rag]
        )
        
        clear_btn_direct.click(
            clear_chat_history,
            outputs=[chatbot_direct]
        )
    
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
