"""LLM API配置类"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM配置模型"""
    
    api_key: str = Field(..., description="API密钥")
    api_base: str = Field(..., description="API基础URL")
    model: str = Field(..., description="模型名称")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=2000, ge=1, description="最大token数")
    top_p: float = Field(default=0.8, ge=0.0, le=1.0, description="Top-p采样")
    stream: bool = Field(default=True, description="是否流式输出")
    timeout: int = Field(default=60, description="请求超时时间")
    
    class Config:
        extra = "allow"


class TTSConfig(BaseModel):
    """文字转语音配置"""
    
    api_key: str = Field(..., description="API密钥")
    api_base: str = Field(..., description="API基础URL")
    model: str = Field(default="qwen3-tts-flash", description="TTS模型")
    voice: str = Field(default="Cherry", description="音色")
    format: str = Field(default="mp3", description="音频格式")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="语速")
    volume: int = Field(default=50, ge=0, le=100, description="音量")


class STTConfig(BaseModel):
    """语音转文字配置"""
    
    api_key: str = Field(..., description="API密钥")
    api_base: str = Field(..., description="API基础URL")
    model: str = Field(default="qwen3-asr-flash-filetrans", description="STT模型")
    language: str = Field(default="en", description="识别语言")
    format: str = Field(default="wav", description="音频格式")


class VisionConfig(BaseModel):
    """视觉API配置"""
    
    api_key: str = Field(..., description="API密钥")
    api_base: str = Field(..., description="API基础URL")
    model: str = Field(..., description="模型名称")
    temperature: float = Field(default=0.7, description="温度参数")
    max_tokens: int = Field(default=2000, description="最大token数")
