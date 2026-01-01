"""语音转文字API客户端"""

import dashscope
from http import HTTPStatus
from typing import Optional
import os
from pathlib import Path
from config.settings import settings, ROOT_DIR
from config.llm_config import STTConfig
from src.utils.logger import app_logger, log_api_call


class STTClient:
    """语音转文字客户端"""
    
    def __init__(self, config: Optional[STTConfig] = None):
        """初始化STT客户端
        
        Args:
            config: STT配置
        """
        if config:
            self.config = config
        else:
            self.config = STTConfig(
                api_key=settings.STT_API_KEY or settings.LLM_API_KEY,
                api_base=settings.STT_API_BASE,
                model=settings.STT_MODEL,
                language="en",
                format="wav"
            )
        
        # 设置 dashscope API 基础 URL
        # 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：https://dashscope-intl.aliyuncs.com/api/v1
        dashscope.base_http_api_url = self.config.api_base or 'https://dashscope.aliyuncs.com/api/v1'
        
        app_logger.info(f"STT客户端初始化完成，模型: {self.config.model}")
    
    def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        **kwargs
    ) -> Optional[str]:
        """识别语音
        
        Args:
            audio_data: 音频字节数据
            language: 语言代码（en/zh等）
            **kwargs: 其他参数
            
        Returns:
            识别的文本，失败返回None
        """
        try:
            # 记录API调用
            log_api_call("STT", f"音频大小: {len(audio_data)} bytes\n语言: {language or self.config.language}", "STT")
            
            # 创建临时文件保存音频
            temp_dir = ROOT_DIR / "data" / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成临时文件
            temp_file = temp_dir / f"audio_{os.getpid()}_{id(audio_data)}.wav"
            temp_file.write_bytes(audio_data)
            
            try:
                # 使用同步调用方式
                result = self._transcribe_sync(str(temp_file), language or self.config.language)
                
                return result
                
            finally:
                # 清理临时文件
                if temp_file.exists():
                    temp_file.unlink()
            
        except Exception as e:
            app_logger.error(f"STT识别失败: {str(e)}", exc_info=True)
            return None
    
    def _transcribe_sync(self, audio_path: str, language: str) -> Optional[str]:
        """同步识别音频文件
        
        Args:
            audio_path: 音频文件路径（本地文件路径或URL）
            language: 语言代码（en/zh等）
            
        Returns:
            识别的文本
        """
        try:
            # 准备消息
            messages = [
                {"role": "system", "content": [{"text": ""}]},  # 配置定制化识别的 Context
                {"role": "user", "content": [{"audio": audio_path}]}
            ]
            
            # 准备 ASR 选项
            asr_options = {
                "enable_itn": False  # 是否启用逆文本正则化
            }
            
            # 如果指定了语言，添加到选项中
            if language:
                asr_options["language"] = language
            
            # 调用 MultiModalConversation 进行同步识别
            response = dashscope.MultiModalConversation.call(
                api_key=self.config.api_key,
                model=self.config.model,
                messages=messages,
                result_format="message",
                asr_options=asr_options
            )
            
            app_logger.debug(f"STT响应: {response}")
            
            # 检查响应状态
            if response.status_code == HTTPStatus.OK:
                # 提取识别文本
                if hasattr(response, 'output') and response.output:
                    choices = response.output.get('choices', [])
                    if choices:
                        message = choices[0].get('message', {})
                        content = message.get('content', [])
                        if content:
                            # 提取文本内容
                            text_parts = []
                            for item in content:
                                if isinstance(item, dict) and 'text' in item:
                                    text_parts.append(item['text'])
                            
                            if text_parts:
                                result_text = ' '.join(text_parts).strip()
                                app_logger.info(f"STT识别成功: {result_text}")
                                return result_text
                
                app_logger.error(f"STT识别失败: 无法提取文本")
                return None
            else:
                app_logger.error(f"STT识别失败: {response}")
                return None
            
        except Exception as e:
            app_logger.error(f"同步转录失败: {str(e)}", exc_info=True)
            return None
    
    def transcribe_file(
        self,
        audio_path: str,
        language: Optional[str] = None,
        **kwargs
    ) -> Optional[str]:
        """识别音频文件
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码
            **kwargs: 其他参数
            
        Returns:
            识别的文本
        """
        try:
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            return self.transcribe(audio_data, language, **kwargs)
        
        except Exception as e:
            app_logger.error(f"读取音频文件失败: {str(e)}")
            return None
    
    def evaluate_pronunciation(
        self,
        audio_data: bytes,
        reference_text: str,
        **kwargs
    ) -> Optional[dict]:
        """评估发音
        
        Args:
            audio_data: 音频字节数据
            reference_text: 参考文本
            **kwargs: 其他参数
            
        Returns:
            评估结果字典
        """
        try:
            # 记录API调用
            log_api_call("发音评估", f"参考文本: {reference_text}", "STT")
            
            # 先识别语音
            recognized_text = self.transcribe(audio_data, **kwargs)
            if not recognized_text:
                return None
            
            # 计算相似度评分（这里可以调用更专业的发音评估API）
            # 简单实现：基于文本匹配
            score = self._calculate_similarity(reference_text, recognized_text)
            
            result = {
                "recognized_text": recognized_text,
                "reference_text": reference_text,
                "accuracy_score": score,
                "pronunciation_score": score,
                "fluency_score": score,
                "completeness_score": score,
                "overall_score": score,
                "feedback": self._generate_feedback(reference_text, recognized_text, score)
            }
            
            app_logger.info(f"发音评估完成，总分: {score}")
            return result
        
        except Exception as e:
            app_logger.error(f"发音评估失败: {str(e)}")
            return None
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简化版）"""
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        if text1 == text2:
            return 100.0
        
        # 简单的字符级相似度
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        similarity = len(intersection) / len(union) * 100
        return round(similarity, 2)
    
    def _generate_feedback(self, reference: str, recognized: str, score: float) -> str:
        """生成反馈信息"""
        if score >= 90:
            return "优秀！发音非常标准，继续保持！"
        elif score >= 75:
            return "良好！发音基本准确，稍加练习会更完美。"
        elif score >= 60:
            return "一般。有些词语发音不够准确，建议多听多练。"
        else:
            return "需要加强。建议仔细聆听标准发音，多加练习。"


# 全局STT客户端实例
stt_client = STTClient()
