"""
UI 模块
负责所有 Gradio UI 组件的创建和管理
"""

import gradio as gr
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class TravelAssistantUI:
    """旅行助手 UI 管理器"""
    
    def __init__(self):
        """初始化 UI 组件"""
        self.chatbot = None
        self.user_input = None
        self.image_input = None
        self.send_btn = None
        self.clear_btn = None
        self.save_btn = None
        self.export_btn = None
        
        # 快速建议按钮
        self.quick_btns = []
        
        logger.info("UI 组件已初始化")
    
    def create_interface(self) -> gr.Blocks:
        """
        创建 Gradio 界面
        
        Returns:
            Gradio Blocks 对象
        """
        logger.info("开始创建 Gradio UI...")
        
        with gr.Blocks(
            title="🧳 智能旅行助手",
            theme=gr.themes.Soft(),
            css=self._get_custom_css()
        ) as demo:
            
            # 标题和描述
            gr.Markdown(self._get_header_html())
            
            # 主对话区域
            with gr.Row():
                with gr.Column(scale=4):
                    # 聊天机器人
                    self.chatbot = gr.Chatbot(
                        value=[],
                        height=500,
                        show_label=False,
                        avatar_images=(
                            None,  # 用户头像
                            "🧳"   # AI 头像
                        ),
                        bubble_full_width=False,
                        render_markdown=True
                    )
                    
                    # 输入区域
                    with gr.Row():
                        self.user_input = gr.Textbox(
                            show_label=False,
                            placeholder="输入你的旅行问题或需求...",
                            container=False,
                            scale=8
                        )
                        self.send_btn = gr.Button(
                            "发送 📤",
                            variant="primary",
                            scale=1
                        )
                    
                    # 图片上传
                    self.image_input = gr.Image(
                        label="📸 上传图片（可选）",
                        type="filepath",
                        height=150
                    )
                    
                    # 操作按钮
                    with gr.Row():
                        self.clear_btn = gr.Button("清空对话 🗑️", size="sm")
                        self.save_btn = gr.Button("保存行程 💾", size="sm")
                        self.export_btn = gr.Button("导出行程 📄", size="sm")
                
                # 侧边栏
                with gr.Column(scale=1):
                    self._create_sidebar()
            
            # 状态栏
            gr.Markdown(self._get_footer_html())
        
        logger.info("✅ Gradio UI 创建完成")
        return demo
    
    def _create_sidebar(self):
        """创建侧边栏"""
        gr.Markdown("### 💡 快速开始")
        
        # 快速建议
        quick_suggestions = [
            "📍 推荐旅行目的地",
            "🗺️ 规划行程路线",
            "🏨 酒店住宿建议",
            "🍜 美食推荐",
            "🚌 交通出行方案",
            "💰 预算规划建议"
        ]
        
        for suggestion in quick_suggestions:
            btn = gr.Button(suggestion, size="sm", elem_classes="quick-btn")
            self.quick_btns.append(btn)
        
        # 使用说明
        gr.Markdown("### 📖 使用说明")
        gr.Markdown("""
        **功能特性：**
        - 💬 智能对话：输入问题即可获得建议
        - 📸 图片识别：上传图片识别景点和场景
        - 💾 保存行程：保存重要的行程安排
        - 📄 导出行程：导出完整对话记录
        
        **操作提示：**
        1. 直接输入问题或点击快速建议
        2. 可上传图片进行识别和咨询
        3. 支持多轮连续对话
        """)
    
    def _get_custom_css(self) -> str:
        """获取自定义 CSS 样式"""
        return """
        .quick-btn {
            margin: 5px 0 !important;
            text-align: left !important;
        }
        
        .gradio-container {
            max-width: 1400px !important;
            margin: auto !important;
        }
        
        #component-0 {
            padding: 20px !important;
        }
        
        .message {
            border-radius: 12px !important;
            padding: 12px 16px !important;
        }
        
        .user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
        }
        
        .bot {
            background: #f7fafc !important;
            border: 1px solid #e2e8f0 !important;
        }
        """
    
    def _get_header_html(self) -> str:
        """获取页面头部 HTML"""
        return """
        # 🧳 智能旅行助手
        
        > 你的私人旅行规划专家，为你提供个性化的旅行建议和行程规划
        """
    
    def _get_footer_html(self) -> str:
        """获取页面底部 HTML"""
        return """
        ---
        <div style="text-align: center; color: #718096; font-size: 12px;">
            <p>💡 提示：支持文本和图片多模态交互 | 🔒 数据本地存储，保护隐私</p>
        </div>
        """
    
    def bind_events(
        self,
        on_send_text,
        on_upload_image,
        on_clear,
        on_save,
        on_export,
        on_quick_suggestion
    ):
        """
        绑定所有事件处理器
        
        Args:
            on_send_text: 发送文本消息的处理函数
            on_upload_image: 上传图片的处理函数
            on_clear: 清空对话的处理函数
            on_save: 保存行程的处理函数
            on_export: 导出行程的处理函数
            on_quick_suggestion: 快速建议的处理函数
        """
        logger.info("开始绑定 UI 事件...")
        
        # 发送按钮
        self.send_btn.click(
            fn=on_send_text,
            inputs=[self.user_input, self.chatbot],
            outputs=[self.chatbot, self.user_input]
        )
        
        # 回车发送
        self.user_input.submit(
            fn=on_send_text,
            inputs=[self.user_input, self.chatbot],
            outputs=[self.chatbot, self.user_input]
        )
        
        # 图片上传
        self.image_input.change(
            fn=on_upload_image,
            inputs=[self.image_input, self.chatbot],
            outputs=[self.chatbot, self.image_input]
        )
        
        # 清空对话
        self.clear_btn.click(
            fn=on_clear,
            outputs=[self.chatbot, self.user_input, self.image_input]
        )
        
        # 保存行程
        self.save_btn.click(
            fn=on_save,
            inputs=[self.chatbot],
            outputs=[]
        )
        
        # 导出行程
        self.export_btn.click(
            fn=on_export,
            inputs=[self.chatbot],
            outputs=[]
        )
        
        # 快速建议按钮
        for btn in self.quick_btns:
            btn.click(
                fn=on_quick_suggestion,
                inputs=[btn, self.chatbot],
                outputs=[self.chatbot, self.user_input]
            )
        
        logger.info("✅ UI 事件绑定完成")


def create_app_ui() -> Tuple[gr.Blocks, TravelAssistantUI]:
    """
    创建应用 UI
    
    Returns:
        (Gradio Blocks, TravelAssistantUI) 元组
    """
    ui = TravelAssistantUI()
    demo = ui.create_interface()
    return demo, ui
