"""
业务处理模块
负责文本消息、图片识别、保存导出等业务逻辑
"""

import logging
from typing import List, Tuple
from pathlib import Path

from config.prompts import (
    AGENT_CORE_SYSTEM_PROMPT,
    MULTIMODAL_IMAGE_PROMPT,
    get_combined_prompt
)
from src.utils import (
    encode_image_to_base64,
    get_image_info,
    format_file_size,
    save_json_file,
    generate_timestamp_filename,
    format_conversation_history,
    Timer
)

logger = logging.getLogger(__name__)


class BusinessProcessor:
    """业务处理器"""
    
    def __init__(self, api_client, conversation_mgr, save_dir: Path):
        """
        初始化业务处理器
        
        Args:
            api_client: API 客户端实例
            conversation_mgr: 对话管理器实例
            save_dir: 行程保存目录
        """
        self.api_client = api_client
        self.conversation_mgr = conversation_mgr
        self.save_dir = save_dir
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("📦 业务处理器初始化完成")
    
    def process_text_message(
        self,
        user_input: str,
        history: List
    ) -> Tuple[List, str]:
        """
        处理文本消息
        
        Args:
            user_input: 用户输入
            history: 对话历史
        
        Returns:
            (更新后的历史记录, 清空的输入框)
        """
        if not user_input or not user_input.strip():
            return history if history else [], ""
        
        try:
            # 确保历史记录是列表
            if history is None:
                history = []
            
            logger.info(f"👤 用户输入: {user_input[:100]}...")
            
            # 检测场景
            scenario = self.conversation_mgr.detect_scenario(user_input)
            
            # 构建系统提示词
            system_prompt = get_combined_prompt(
                AGENT_CORE_SYSTEM_PROMPT,
                scenario=scenario,
                additional_context=self.conversation_mgr.get_context()
            )
            
            # 添加用户消息到历史
            self.conversation_mgr.add_message("user", user_input)
            
            # 调用 API
            logger.info("⏳ 正在调用大模型...")
            response = self.api_client.call_text_api(
                user_message=user_input,
                system_prompt=system_prompt
            )
            
            # 添加助手回复到历史
            self.conversation_mgr.add_message("assistant", response)
            history.append([user_input, response])
            
            logger.info(f"✅ 处理完成 | 响应长度: {len(response)} 字符")
            return history, ""
            
        except Exception as e:
            # 错误处理
            error_response = f"❌ 处理出错：{str(e)}"
            logger.error(f"❌ 处理文本消息失败: {str(e)}")
            
            if history and len(history) > 0 and history[-1][1] is None:
                history[-1][1] = error_response
            else:
                history.append([user_input, error_response])
            
            return history, ""
    
    def process_image_upload(
        self,
        image_path: str,
        history: List
    ) -> List:
        """
        处理图片上传和识别
        
        Args:
            image_path: 图片路径
            history: 对话历史
        
        Returns:
            更新后的历史记录
        """
        if not image_path:
            return history if history else []
        
        try:
            # 确保历史记录是列表
            if history is None:
                history = []
            
            logger.info(f"📷 收到图片上传: {image_path}")
            
            # 获取图片信息
            img_info = get_image_info(image_path)
            logger.info(
                f"  图片格式: {img_info['format']}, "
                f"尺寸: {img_info['width']}x{img_info['height']}, "
                f"大小: {format_file_size(img_info['file_size'])}"
            )
            
            # 编码图片
            image_data = encode_image_to_base64(image_path)
            if not image_data:
                raise ValueError("图片编码失败")
            
            # 判断图片格式
            img_format = img_info['format'].lower()
            media_type = (
                f"image/{img_format}" 
                if img_format in ["jpeg", "jpg", "png", "webp"] 
                else "image/jpeg"
            )
            
            # 添加用户消息
            user_msg = "📷 [用户上传了一张图片，请识别图片中的旅游相关内容]"
            
            # 调用多模态 API
            logger.info("⏳ 正在调用多模态模型识别图片...")
            response = self.api_client.call_multimodal_api(
                user_message="请识别这张图片中的旅游相关内容，并给出详细的攻略建议。",
                image_data=image_data,
                media_type=media_type,
                system_prompt=MULTIMODAL_IMAGE_PROMPT
            )
            
            # 更新历史
            self.conversation_mgr.add_message("user", user_msg)
            self.conversation_mgr.add_message("assistant", response)
            history.append([user_msg, response])
            
            logger.info(f"✅ 图片识别完成 | 响应长度: {len(response)} 字符")
            
        except Exception as e:
            # 错误处理
            error_msg = f"❌ 图片处理失败：{str(e)}"
            logger.error(f"❌ 处理图片上传失败: {str(e)}")
            user_msg = "📷 [用户上传了一张图片，请识别图片中的旅游相关内容]"
            history.append([user_msg, error_msg])
        
        return history if history else []
    
    def save_itinerary(self, history: List) -> str:
        """
        保存当前行程到本地文件
        
        Args:
            history: 对话历史
        
        Returns:
            保存结果提示
        """
        if not history:
            return "⚠️ 当前没有可保存的行程"
        
        try:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"itinerary_{timestamp}.md"
            filepath = self.save_dir / filename
            
            # 生成 Markdown 内容
            content = "# 我的旅游行程\n\n"
            content += f"**保存时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n"
            content += "---\n\n"
            
            for i, (user_msg, bot_msg) in enumerate(history, 1):
                if user_msg:
                    content += f"## 第 {i} 轮对话\n\n"
                    content += f"**我的需求**:\n{user_msg}\n\n"
                if bot_msg:
                    content += f"**智能助手回复**:\n{bot_msg}\n\n"
                    content += "---\n\n"
            
            # 保存文件
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info(f"💾 行程已保存: {filepath.name}")
            return f"✅ 行程已保存至：{filepath.name}"
        
        except Exception as e:
            logger.error(f"❌ 保存行程失败: {str(e)}")
            return f"❌ 保存失败：{str(e)}"
    
    def export_itinerary(self, history: List) -> str:
        """
        导出行程为文本格式
        
        Args:
            history: 对话历史
        
        Returns:
            文本格式的行程内容
        """
        if not history:
            return "当前没有可导出的行程"
        
        content = "=" * 50 + "\n"
        content += "我的旅游行程\n"
        content += f"导出时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n"
        content += "=" * 50 + "\n\n"
        
        for i, (user_msg, bot_msg) in enumerate(history, 1):
            if user_msg:
                content += f"【第 {i} 轮对话】\n"
                content += f"我的需求:\n{user_msg}\n\n"
            if bot_msg:
                content += f"智能助手回复:\n{bot_msg}\n\n"
                content += "-" * 50 + "\n\n"
        
        logger.info("📄 行程已导出为文本格式")
        return content
    
    def clear_conversation(self) -> Tuple[List, str]:
        """
        清空对话历史
        
        Returns:
            (空的历史记录, 清空提示)
        """
        self.conversation_mgr.clear()
        logger.info("🗑️  对话已清空")
        return [], "✅ 对话已清空，开始新的旅游规划吧!"
