"""口语练习服务模块"""

from typing import Optional, Dict
from config.prompts import PROMPTS
from src.api.llm_client import llm_client
from src.api.stt_client import stt_client
from src.api.tts_client import tts_client
from src.utils.logger import app_logger


class SpeakingService:
    """口语练习服务"""
    
    def __init__(self):
        self.llm = llm_client
        self.stt = stt_client
        self.tts = tts_client
    
    def generate_practice(
        self,
        topic: str,
        difficulty: str = "中级"
    ) -> str:
        """生成口语练习内容
        
        Args:
            topic: 练习话题
            difficulty: 难度级别
            
        Returns:
            练习内容
        """
        try:
            prompt = PROMPTS.SPEAKING_PRACTICE_PROMPT.format(
                difficulty=difficulty,
                topic=topic
            )
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            result = self.llm.chat_complete(messages)
            app_logger.info(f"生成口语练习: {topic}")
            return result
        
        except Exception as e:
            app_logger.error(f"生成口语练习失败: {str(e)}")
            return f"❌ 生成练习失败: {str(e)}"
    
    def evaluate_speaking(
        self,
        audio_data: bytes,
        reference_text: str
    ) -> Dict:
        """评估口语发音
        
        Args:
            audio_data: 录音数据
            reference_text: 参考文本
            
        Returns:
            评估结果字典
        """
        try:
            # 使用STT识别语音
            result = self.stt.evaluate_pronunciation(audio_data, reference_text)
            
            if not result:
                return {
                    "success": False,
                    "message": "❌ 语音识别失败，请重试"
                }
            
            # 使用LLM生成详细反馈
            prompt = PROMPTS.SPEAKING_CORRECTION_PROMPT.format(
                text=result["recognized_text"],
                reference=reference_text
            )
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            feedback = self.llm.chat_complete(messages)
            
            result["detailed_feedback"] = feedback
            result["success"] = True
            
            app_logger.info(f"口语评估完成，得分: {result['overall_score']}")
            return result
        
        except Exception as e:
            app_logger.error(f"口语评估失败: {str(e)}")
            return {
                "success": False,
                "message": f"❌ 评估失败: {str(e)}"
            }
    
    def text_to_speech(
        self,
        text: str,
        voice: str = "Cherry",
        speed: float = 1.0
    ) -> Optional[bytes]:
        """文本转语音
        
        Args:
            text: 要转换的文本
            voice: 音色（例如 Cherry）
            speed: 语速
            
        Returns:
            音频字节数据
        """
        try:
            audio_data = self.tts.synthesize(text, voice=voice, speed=speed)
            
            if audio_data:
                app_logger.info(f"TTS转换成功，文本长度: {len(text)}")
            
            return audio_data
        
        except Exception as e:
            app_logger.error(f"TTS转换失败: {str(e)}")
            return None
    
    def speech_to_text(
        self,
        audio_data: bytes,
        language: str = "en"
    ) -> Optional[str]:
        """语音转文本
        
        Args:
            audio_data: 音频数据
            language: 语言
            
        Returns:
            识别的文本
        """
        try:
            text = self.stt.transcribe(audio_data, language=language)
            
            if text:
                app_logger.info(f"STT识别成功: {text}")
            
            return text
        
        except Exception as e:
            app_logger.error(f"STT识别失败: {str(e)}")
            return None


# 全局口语服务实例
speaking_service = SpeakingService()
