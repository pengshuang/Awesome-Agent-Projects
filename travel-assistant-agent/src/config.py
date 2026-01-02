"""
配置管理模块
负责加载和管理环境变量配置
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """配置管理类"""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            env_file: .env 文件路径，默认从当前目录加载
        """
        # 加载环境变量
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # ==================== API 配置 ====================
        self.API_KEY = os.getenv("API_KEY", "")
        self.API_BASE_URL = os.getenv(
            "API_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # ==================== 模型配置 ====================
        self.TEXT_MODEL_NAME = os.getenv("TEXT_MODEL_NAME", "qwen3-max")
        self.MULTIMODAL_MODEL_NAME = os.getenv(
            "MULTIMODAL_MODEL_NAME",
            "qwen-vl-plus"
        )
        
        # ==================== 参数配置 ====================
        self.MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1500"))
        self.TEMPERATURE = float(os.getenv("TEMPERATURE", "0.85"))
        
        # ==================== 网络配置 ====================
        self.TEXT_API_TIMEOUT = int(os.getenv("TEXT_API_TIMEOUT", "60"))
        self.MULTIMODAL_API_TIMEOUT = int(os.getenv("MULTIMODAL_API_TIMEOUT", "90"))
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
        
        # ==================== 应用配置 ====================
        self.SAVE_DIR = Path("data/saved_itineraries")
        self.SAVE_DIR.mkdir(parents=True, exist_ok=True)
        
        self.SERVER_NAME = os.getenv("SERVER_NAME", "0.0.0.0")
        self.SERVER_PORT = int(os.getenv("SERVER_PORT", "7860"))
        self.SHARE = os.getenv("SHARE", "false").lower() == "true"
        self.INBROWSER = os.getenv("INBROWSER", "true").lower() == "true"
    
    def validate(self) -> bool:
        """
        验证配置是否有效
        
        Returns:
            配置是否有效
        """
        if not self.API_KEY:
            print("⚠️  警告：未检测到 API 密钥配置")
            print("请在 .env 文件中配置 API_KEY")
            return False
        
        return True
    
    def get_summary(self) -> dict:
        """
        获取配置摘要
        
        Returns:
            配置信息字典
        """
        return {
            "API配置": {
                "密钥": "✅ 已配置" if self.API_KEY else "❌ 未配置",
                "密钥长度": len(self.API_KEY) if self.API_KEY else 0,
                "API地址": self.API_BASE_URL
            },
            "模型配置": {
                "文本模型": self.TEXT_MODEL_NAME,
                "视觉模型": self.MULTIMODAL_MODEL_NAME
            },
            "参数配置": {
                "Max Tokens": self.MAX_TOKENS,
                "温度": self.TEMPERATURE
            },
            "网络配置": {
                "文本API超时": f"{self.TEXT_API_TIMEOUT}s",
                "多模态API超时": f"{self.MULTIMODAL_API_TIMEOUT}s",
                "最大重试": f"{self.MAX_RETRIES}次"
            },
            "应用配置": {
                "保存目录": str(self.SAVE_DIR.absolute()),
                "服务地址": f"{self.SERVER_NAME}:{self.SERVER_PORT}",
                "分享链接": "启用" if self.SHARE else "禁用",
                "自动打开浏览器": "是" if self.INBROWSER else "否"
            }
        }
    
    def print_summary(self):
        """打印配置摘要"""
        import logging
        logger = logging.getLogger(__name__)
        
        summary = self.get_summary()
        logger.info("=" * 80)
        logger.info("📝 配置信息:")
        
        for category, items in summary.items():
            logger.info(f"  {category}:")
            for key, value in items.items():
                logger.info(f"    • {key}: {value}")
        
        logger.info("=" * 80)


# 创建全局配置实例
config = Config()
