"""
API 客户端模块
负责与第三方 LLM API 交互
"""

import os
import logging
import requests
import time
from typing import Optional

logger = logging.getLogger(__name__)


class TravelAssistantAPI:
    """
    旅游助手 API 调用封装类
    仅支持阿里云 DashScope qwen 模型
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        text_model: str,
        multimodal_model: str,
        text_timeout: int = 60,
        multimodal_timeout: int = 90,
        max_retries: int = 3
    ):
        """
        初始化 API 客户端
        
        Args:
            api_key: API 密钥
            base_url: API 基础 URL
            text_model: 文本模型名称
            multimodal_model: 多模态模型名称
            text_timeout: 文本 API 超时时间（秒）
            multimodal_timeout: 多模态 API 超时时间（秒）
            max_retries: 最大重试次数
        """
        self.api_key = api_key
        self.base_url = base_url
        self.text_model = text_model
        self.multimodal_model = multimodal_model
        self.text_timeout = text_timeout
        self.multimodal_timeout = multimodal_timeout
        self.max_retries = max_retries
        
        # OpenAI 兼容格式的 Headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(
            f"🚀 API 客户端初始化 | 文本模型: {self.text_model} | "
            f"视觉模型: {self.multimodal_model}"
        )
    
    def call_text_api(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.85,
        max_tokens: int = 1500
    ) -> str:
        """
        调用文本对话 API
        
        Args:
            user_message: 用户输入的消息
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大 token 数
        
        Returns:
            API 返回的文本内容
        """
        # 构建消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})
        
        payload = {
            "model": self.text_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        logger.info(
            f"📤 发送文本请求 | 模型: {self.text_model} | "
            f"超时: {self.text_timeout}s"
        )
        logger.debug(f"📝 输入: {user_message[:100]}...")
        
        # 带重试的请求
        return self._request_with_retry(
            payload=payload,
            timeout=self.text_timeout,
            api_type="文本"
        )
    
    def call_multimodal_api(
        self,
        user_message: str,
        image_data: str,
        media_type: str = "image/jpeg",
        system_prompt: Optional[str] = None,
        temperature: float = 0.85,
        max_tokens: int = 1500
    ) -> str:
        """
        调用多模态 API（图片识别）
        
        Args:
            user_message: 用户消息
            image_data: Base64 编码的图片数据
            media_type: 媒体类型
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大 token 数
        
        Returns:
            API 返回的识别结果
        """
        # 构建消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{image_data}"
                    }
                },
                {
                    "type": "text",
                    "text": user_message
                }
            ]
        })
        
        payload = {
            "model": self.multimodal_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        logger.info(
            f"📤 发送图片识别请求 | 模型: {self.multimodal_model} | "
            f"格式: {media_type} | 超时: {self.multimodal_timeout}s"
        )
        logger.debug(f"📝 识别要求: {user_message[:100]}...")
        
        # 带重试的请求
        return self._request_with_retry(
            payload=payload,
            timeout=self.multimodal_timeout,
            api_type="图片识别"
        )
    
    def _request_with_retry(
        self,
        payload: dict,
        timeout: int,
        api_type: str
    ) -> str:
        """
        带重试机制的 API 请求
        
        Args:
            payload: 请求负载
            timeout: 超时时间
            api_type: API 类型（用于日志）
        
        Returns:
            API 响应文本
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result["choices"][0]["message"]["content"]
                    
                    logger.info(
                        f"📥 收到{api_type}响应 | 状态码: 200 | "
                        f"长度: {len(response_text)} 字符"
                    )
                    logger.debug(f"💭 回复: {response_text[:100]}...")
                    
                    return response_text
                else:
                    error_msg = (
                        f"❌ {api_type} API 调用失败（状态码: {response.status_code}）\n"
                        f"提示：请检查 API 密钥和 URL 配置"
                    )
                    logger.error(
                        f"❌ {api_type}请求失败 | 状态码: {response.status_code} | "
                        f"响应: {response.text[:200]}"
                    )
                    return error_msg
                    
            except requests.exceptions.Timeout:
                attempt_info = f"（第 {attempt + 1}/{self.max_retries} 次尝试）"
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    logger.warning(
                        f"⏱️  {api_type}请求超时 {attempt_info}，{wait_time}秒后重试..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"⏱️  {api_type}请求超时 {attempt_info}，已达最大重试次数"
                    )
                    return f"❌ {api_type}超时，请检查网络连接后重试"
                    
            except requests.exceptions.ConnectionError as e:
                attempt_info = f"（第 {attempt + 1}/{self.max_retries} 次尝试）"
                logger.error(f"🔌 {api_type}连接错误 {attempt_info}: {str(e)}")
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    logger.warning(f"将在 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    return f"❌ {api_type}网络连接失败：{str(e)}"
                    
            except Exception as e:
                logger.error(f"⚠️  {api_type}异常: {str(e)}")
                return f"❌ {api_type}出错：{str(e)}"
        
        return f"❌ {api_type} API 调用失败，请稍后重试"
    
    def call_with_retry(self, func, *args, **kwargs):
        """
        兼容旧版本的重试方法（保留接口）
        
        Args:
            func: 要调用的函数
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            函数返回结果
        """
        return func(*args, **kwargs)
