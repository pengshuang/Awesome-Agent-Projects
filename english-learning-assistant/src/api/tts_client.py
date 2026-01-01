"""文字转语音API客户端"""

import os
import base64
from typing import Optional
import dashscope
from config.settings import settings
from config.llm_config import TTSConfig
from src.utils.logger import app_logger, log_api_call


class TTSClient:
    """文字转语音客户端"""

    def _ensure_bytes(self, audio_obj: object) -> Optional[bytes]:
        """尝试将各种类型的音频对象转成 bytes"""
        if audio_obj is None:
            return None
        if isinstance(audio_obj, bytes):
            return audio_obj

        # 优先处理常见包装
        if hasattr(audio_obj, "data"):
            audio_obj = audio_obj.data
        if isinstance(audio_obj, dict):
            for key in ("data", "audio_data", "audio"):
                if key in audio_obj:
                    return self._ensure_bytes(audio_obj[key])

        if isinstance(audio_obj, str):
            try:
                return base64.b64decode(audio_obj)
            except Exception:
                return None

        for attr in ("to_bytes", "tobytes"):
            if hasattr(audio_obj, attr):
                try:
                    return getattr(audio_obj, attr)()
                except Exception:
                    pass

        return None
    
    def __init__(self, config: Optional[TTSConfig] = None):
        """初始化TTS客户端
        
        Args:
            config: TTS配置
        """
        if config:
            self.config = config
        else:
            self.config = TTSConfig(
                api_key=settings.TTS_API_KEY or settings.LLM_API_KEY,
                api_base=settings.TTS_API_BASE,
                model=settings.TTS_MODEL,
                voice=settings.TTS_VOICE,
                format="mp3",
                speed=1.0,
                volume=50
            )
        
        # 设置 dashscope API 基础 URL
        dashscope.base_http_api_url = self.config.api_base
        
        app_logger.info(f"TTS客户端初始化完成，模型: {self.config.model}")
    
    def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: Optional[float] = None,
        **kwargs
    ) -> Optional[bytes]:
        """合成语音
        
        Args:
            text: 要合成的文本
            voice: 音色
            speed: 语速（0.5-2.0）
            **kwargs: 其他参数
            
        Returns:
            音频字节数据，失败返回None
        """
        try:
            # 记录API调用
            log_api_call("TTS", f"文本: {text[:100]}...\n音色: {voice or self.config.voice}", "TTS")
            
            # 使用 dashscope MultiModalConversation 调用 TTS API
            # 参考文档: https://help.aliyun.com/zh/model-studio/qwen-tts
            response = dashscope.MultiModalConversation.call(
                model=self.config.model,
                text=text,
                voice=voice or self.config.voice,
                language_type="English",  # 英语学习场景，指定英文
                api_key=self.config.api_key,
                stream=False
            )
            
            if response is None:
                app_logger.error("TTS 返回响应为 None")
                return None

            app_logger.debug(f"TTS response type: {type(response)}, status_code: {getattr(response, 'status_code', 'N/A')}")

            # qwen3-tts-flash 返回结构: response.output.audio.url 或 response.output.audio_data
            audio_bytes = None
            
            if hasattr(response, 'output') and response.output is not None:
                output = response.output
                app_logger.debug(f"output: {output}")
                
                # 方式1: 从 audio 对象获取
                if hasattr(output, 'audio') and output.audio is not None:
                    audio = output.audio
                    # 优先使用 URL 下载
                    if hasattr(audio, 'url') and audio.url:
                        try:
                            import requests
                            resp = requests.get(audio.url, timeout=30)
                            resp.raise_for_status()
                            audio_bytes = resp.content
                            app_logger.debug(f"从 URL 下载音频成功")
                        except Exception as e:
                            app_logger.warning(f"从 URL 下载失败: {e}")
                    
                    # 如果有 data 字段（Base64编码）
                    if not audio_bytes and hasattr(audio, 'data') and audio.data:
                        audio_bytes = self._ensure_bytes(audio.data)
                        app_logger.debug(f"从 audio.data 获取音频")
                
                # 方式2: 从 audio_data 字段获取
                if not audio_bytes and hasattr(output, 'audio_data'):
                    audio_bytes = self._ensure_bytes(output.audio_data)
                    app_logger.debug(f"从 output.audio_data 获取音频")

            if audio_bytes and len(audio_bytes) > 0:
                app_logger.info(f"TTS合成成功，音频大小: {len(audio_bytes)} bytes")
                return audio_bytes

            status = getattr(response, "status_code", None)
            code = getattr(response, "code", None)
            message = getattr(response, "message", None)
            app_logger.error(f"TTS合成失败: status_code={status}, code={code}, message={message}")
            return None
        
        except Exception as e:
            app_logger.error(f"TTS合成失败: {str(e)}", exc_info=True)
            return None
    
    def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None,
        **kwargs
    ) -> bool:
        """合成语音并保存到文件
        
        Args:
            text: 要合成的文本
            output_path: 输出文件路径
            voice: 音色
            **kwargs: 其他参数
            
        Returns:
            是否成功
        """
        try:
            audio_bytes = self.synthesize(text, voice, **kwargs)
            if audio_bytes:
                with open(output_path, 'wb') as f:
                    f.write(audio_bytes)
                app_logger.info(f"语音已保存到: {output_path}")
                return True
            return False
        
        except Exception as e:
            app_logger.error(f"保存语音文件失败: {str(e)}")
            return False


# 全局TTS客户端实例
tts_client = TTSClient()
