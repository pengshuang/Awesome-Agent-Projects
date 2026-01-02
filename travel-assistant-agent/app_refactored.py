"""
智能旅游助手Agent - 主程序（重构版）
基于 Gradio 4.x 的生产级旅游智能助手 Web 应用
"""

import logging
from pathlib import Path

import gradio as gr

# 导入重构后的模块
from src.config import config
from src.api_client import TravelAssistantAPI
from src.conversation import ConversationManager
from src.processor import BusinessProcessor
from src.ui import create_app_ui

# ==================== 日志配置 ====================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class TravelAssistantApp:
    """旅行助手应用主类"""
    
    def __init__(self):
        """初始化应用"""
        logger.info("=" * 80)
        logger.info("🧳 初始化旅行助手应用...")
        logger.info("=" * 80)
        
        # 验证配置
        if not config.validate():
            raise ValueError("配置验证失败，请检查 .env 文件")
        
        # 打印配置摘要
        config.print_summary()
        
        # 初始化各个组件
        self.api_client = TravelAssistantAPI(
            api_key=config.API_KEY,
            base_url=config.API_BASE_URL,
            text_model=config.TEXT_MODEL_NAME,
            multimodal_model=config.MULTIMODAL_MODEL_NAME,
            max_tokens=config.MAX_TOKENS,
            temperature=config.TEMPERATURE,
            text_timeout=config.TEXT_API_TIMEOUT,
            multimodal_timeout=config.MULTIMODAL_API_TIMEOUT,
            max_retries=config.MAX_RETRIES
        )
        
        self.conversation_manager = ConversationManager()
        
        self.processor = BusinessProcessor(
            api_client=self.api_client,
            conversation_mgr=self.conversation_manager,
            save_dir=config.SAVE_DIR
        )
        
        # 创建 UI
        self.demo, self.ui = create_app_ui()
        
        # 绑定事件
        self._bind_events()
        
        logger.info("✅ 应用初始化完成")
        logger.info("=" * 80)
    
    def _bind_events(self):
        """绑定所有 UI 事件到处理函数"""
        self.ui.bind_events(
            on_send_text=self._handle_send_text,
            on_upload_image=self._handle_upload_image,
            on_clear=self._handle_clear,
            on_save=self._handle_save,
            on_export=self._handle_export,
            on_quick_suggestion=self._handle_quick_suggestion
        )
    
    def _handle_send_text(self, user_input: str, history: list) -> tuple:
        """
        处理文本消息发送
        
        Args:
            user_input: 用户输入
            history: 对话历史
        
        Returns:
            (更新后的历史, 清空的输入框)
        """
        if not user_input or not user_input.strip():
            return history, ""
        
        logger.info(f"📥 用户输入: {user_input[:100]}...")
        
        # 使用处理器处理消息
        updated_history = self.processor.process_text_message(
            user_input=user_input,
            history=history
        )
        
        return updated_history, ""
    
    def _handle_upload_image(self, image_path: str, history: list) -> tuple:
        """
        处理图片上传
        
        Args:
            image_path: 图片路径
            history: 对话历史
        
        Returns:
            (更新后的历史, 清空的图片输入)
        """
        if not image_path:
            return history, None
        
        logger.info(f"📸 接收到图片: {image_path}")
        
        # 使用处理器处理图片
        updated_history = self.processor.process_image_upload(
            image_path=image_path,
            history=history
        )
        
        return updated_history, None
    
    def _handle_clear(self) -> tuple:
        """
        清空对话
        
        Returns:
            (清空的历史, 清空的输入, 清空的图片)
        """
        logger.info("🗑️  清空对话")
        self.conversation_manager.clear()
        return [], "", None
    
    def _handle_save(self, history: list):
        """
        保存行程
        
        Args:
            history: 对话历史
        """
        self.processor.save_itinerary(history)
    
    def _handle_export(self, history: list):
        """
        导出行程
        
        Args:
            history: 对话历史
        """
        self.processor.export_itinerary(history)
    
    def _handle_quick_suggestion(self, btn_text: gr.Button, history: list) -> tuple:
        """
        处理快速建议按钮点击
        
        Args:
            btn_text: 按钮文本
            history: 对话历史
        
        Returns:
            (更新后的历史, 清空的输入框)
        """
        # 提取建议文本（去掉 emoji）
        suggestion = btn_text.split(maxsplit=1)[-1] if btn_text else ""
        
        if not suggestion:
            return history, ""
        
        logger.info(f"💡 快速建议: {suggestion}")
        
        # 使用处理器处理消息
        updated_history = self.processor.process_text_message(
            user_input=suggestion,
            history=history
        )
        
        return updated_history, ""
    
    def launch(self):
        """启动应用"""
        logger.info("=" * 80)
        logger.info("🚀 启动 Gradio 服务器...")
        logger.info("=" * 80)
        
        try:
            self.demo.launch(
                server_name=config.SERVER_NAME,
                server_port=config.SERVER_PORT,
                share=config.SHARE,
                inbrowser=config.INBROWSER
            )
        except Exception as e:
            logger.error(f"❌ 启动失败: {e}")
            raise


def main():
    """主函数"""
    try:
        app = TravelAssistantApp()
        app.launch()
    except KeyboardInterrupt:
        logger.info("\n👋 用户中断，程序退出")
    except Exception as e:
        logger.error(f"❌ 程序异常: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
