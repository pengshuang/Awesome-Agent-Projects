"""LLM API客户端模块"""

import json
from typing import Dict, List, Optional, Generator, Any
import requests
from config.settings import settings
from config.llm_config import LLMConfig
from src.utils.logger import app_logger, log_api_call


class LLMClient:
    """LLM API客户端"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """初始化客户端
        
        Args:
            config: LLM配置，如果不提供则使用默认配置
        """
        if config:
            self.config = config
        else:
            # 使用默认配置
            self.config = LLMConfig(
                api_key=settings.LLM_API_KEY,
                api_base=settings.LLM_API_BASE,
                model=settings.LLM_MODEL,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                top_p=settings.TOP_P,
                stream=settings.STREAM_ENABLED,
                timeout=settings.API_TIMEOUT
            )
        
        app_logger.info(f"LLM客户端初始化完成，模型: {self.config.model}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: Optional[bool] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """发送对话请求（流式输出）
        
        Args:
            messages: 消息列表，格式 [{"role": "user/assistant/system", "content": "..."}]
            stream: 是否流式输出，默认使用配置值
            **kwargs: 其他API参数
            
        Yields:
            生成的文本内容
        """
        try:
            # 记录API调用
            prompt_content = self._format_messages_for_log(messages)
            log_api_call("LLM Chat", prompt_content, self.config.model)
            
            # 准备请求参数
            use_stream = stream if stream is not None else self.config.stream
            payload = {
                "model": self.config.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "stream": use_stream,
            }
            
            # 添加其他参数
            for key, value in kwargs.items():
                if key not in payload:
                    payload[key] = value
            
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            # 发送请求
            url = f"{self.config.api_base}/chat/completions"
            
            if use_stream:
                # 流式请求
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            line = line[6:]  # 移除 'data: ' 前缀
                            if line == '[DONE]':
                                break
                            try:
                                data = json.loads(line)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
            else:
                # 非流式请求
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    yield content
        
        except requests.exceptions.Timeout:
            error_msg = "❌ API请求超时，请检查网络连接或稍后重试"
            app_logger.error(error_msg)
            yield error_msg
        
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ API请求失败: {str(e)}"
            app_logger.error(error_msg)
            yield error_msg
        
        except Exception as e:
            error_msg = f"❌ 发生未知错误: {str(e)}"
            app_logger.error(error_msg, exc_info=True)
            yield error_msg
    
    def chat_complete(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """发送对话请求（完整输出）
        
        Args:
            messages: 消息列表
            **kwargs: 其他API参数
            
        Returns:
            完整的回复文本
        """
        try:
            result = ""
            for chunk in self.chat(messages, stream=False, **kwargs):
                result += chunk
            return result
        
        except Exception as e:
            error_msg = f"❌ 获取完整回复失败: {str(e)}"
            app_logger.error(error_msg)
            return error_msg
    
    def _format_messages_for_log(self, messages: List[Dict[str, str]]) -> str:
        """格式化消息用于日志记录"""
        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"[{role.upper()}]\n{content}\n")
        return "\n".join(formatted)
    
    def validate_config(self) -> bool:
        """验证配置是否有效
        
        Returns:
            配置是否有效
        """
        if not self.config.api_key:
            app_logger.error("LLM API密钥未配置")
            return False
        
        if not self.config.api_base:
            app_logger.error("LLM API地址未配置")
            return False
        
        if not self.config.model:
            app_logger.error("LLM模型未配置")
            return False
        
        return True
    
    def test_connection(self) -> tuple[bool, str]:
        """测试API连接
        
        Returns:
            (是否成功, 消息)
        """
        try:
            if not self.validate_config():
                return False, "配置验证失败"
            
            test_messages = [
                {"role": "user", "content": "Hello"}
            ]
            
            response = self.chat_complete(test_messages)
            
            if "❌" in response:
                return False, response
            
            return True, "连接测试成功"
        
        except Exception as e:
            return False, f"连接测试失败: {str(e)}"


# 全局LLM客户端实例
llm_client = LLMClient()
