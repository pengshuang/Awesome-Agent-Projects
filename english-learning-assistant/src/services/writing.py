"""写作批改服务模块"""

from typing import Optional
from config.prompts import PROMPTS
from src.api.llm_client import llm_client
from src.utils.logger import app_logger


class WritingService:
    """写作批改服务"""
    
    def __init__(self):
        self.llm = llm_client
    
    def correct_writing(
        self,
        content: str,
        requirement: str = "通用写作"
    ) -> str:
        """批改作文
        
        Args:
            content: 作文内容
            requirement: 写作要求
            
        Returns:
            批改结果
        """
        try:
            prompt = PROMPTS.WRITING_CORRECTION_PROMPT.format(
                content=content,
                requirement=requirement
            )
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            result = self.llm.chat_complete(messages)
            app_logger.info("作文批改完成")
            return result
        
        except Exception as e:
            app_logger.error(f"作文批改失败: {str(e)}")
            return f"❌ 批改失败: {str(e)}"
    
    def polish_writing(
        self,
        content: str,
        style: str = "日常"
    ) -> str:
        """润色写作
        
        Args:
            content: 原文内容
            style: 目标风格（学术/商务/日常/创意）
            
        Returns:
            润色结果
        """
        try:
            prompt = PROMPTS.WRITING_POLISH_PROMPT.format(
                content=content,
                style=style
            )
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            result = self.llm.chat_complete(messages)
            app_logger.info("写作润色完成")
            return result
        
        except Exception as e:
            app_logger.error(f"写作润色失败: {str(e)}")
            return f"❌ 润色失败: {str(e)}"


# 全局写作服务实例
writing_service = WritingService()
