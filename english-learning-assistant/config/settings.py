"""系统配置文件"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


# 项目根目录
ROOT_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """系统配置类"""
    
    # 应用配置
    APP_NAME: str = "英语学习助手"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # LLM API 配置
    LLM_API_KEY: str = Field(default="", description="LLM API密钥")
    LLM_API_BASE: str = Field(default="https://dashscope.aliyuncs.com/api/v1", description="LLM API基础URL")
    LLM_MODEL: str = Field(default="qwen-plus", description="默认使用的模型")
    
    # 语音API配置
    TTS_API_KEY: str = Field(default="", description="文字转语音API密钥")
    TTS_API_BASE: str = Field(default="https://dashscope.aliyuncs.com/api/v1", description="TTS API基础URL")
    TTS_MODEL: str = Field(default="cosyvoice-v1", description="TTS模型")
    TTS_VOICE: str = Field(default="longxiaochun", description="TTS语音")
    
    STT_API_KEY: str = Field(default="", description="语音转文字API密钥")
    STT_API_BASE: str = Field(default="https://dashscope.aliyuncs.com/api/v1", description="STT API基础URL")
    STT_MODEL: str = Field(default="qwen-audio-turbo", description="STT模型")
    
    # 多模态API配置
    VISION_API_KEY: str = Field(default="", description="视觉API密钥")
    VISION_API_BASE: str = Field(default="https://dashscope.aliyuncs.com/api/v1", description="Vision API基础URL")
    VISION_MODEL: str = Field(default="qwen-vl-plus", description="视觉模型")
    
    # API请求配置
    API_TIMEOUT: int = Field(default=60, description="API请求超时时间(秒)")
    MAX_RETRIES: int = Field(default=3, description="API请求最大重试次数")
    STREAM_ENABLED: bool = Field(default=True, description="是否启用流式输出")
    
    # 模型参数
    TEMPERATURE: float = Field(default=0.7, description="温度参数")
    MAX_TOKENS: int = Field(default=2000, description="最大token数")
    TOP_P: float = Field(default=0.8, description="Top-p采样参数")
    
    # 路径配置
    DATA_DIR: Path = Field(default_factory=lambda: ROOT_DIR / "data", description="数据目录")
    LOG_DIR: Path = Field(default_factory=lambda: ROOT_DIR / "logs", description="日志目录")
    HISTORY_DIR: Path = Field(default_factory=lambda: ROOT_DIR / "data" / "history", description="学习记录目录")
    UPLOAD_DIR: Path = Field(default_factory=lambda: ROOT_DIR / "data" / "uploads", description="上传文件目录")
    
    # 学习配置
    DIFFICULTY_LEVELS: list = Field(
        default=["初级", "中级", "高级"],
        description="学习难度级别"
    )
    DEFAULT_DIFFICULTY: str = Field(default="中级", description="默认难度")
    
    # Gradio配置
    GRADIO_SERVER_NAME: str = Field(default="0.0.0.0", description="Gradio服务器地址")
    GRADIO_SERVER_PORT: int = Field(default=7860, description="Gradio服务器端口")
    GRADIO_SHARE: bool = Field(default=False, description="是否创建公开链接")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保目录存在
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# 全局配置实例
settings = Settings()
