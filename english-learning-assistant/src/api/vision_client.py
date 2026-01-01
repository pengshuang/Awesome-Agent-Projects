"""多模态API客户端"""

import base64
from typing import Optional, List
from pathlib import Path
import requests
from config.settings import settings
from config.llm_config import VisionConfig
from src.utils.logger import app_logger, log_api_call


class VisionClient:
    """视觉API客户端（处理图片和PDF）"""
    
    def __init__(self, config: Optional[VisionConfig] = None):
        """初始化Vision客户端
        
        Args:
            config: Vision配置
        """
        if config:
            self.config = config
        else:
            self.config = VisionConfig(
                api_key=settings.VISION_API_KEY or settings.LLM_API_KEY,
                api_base=settings.VISION_API_BASE,
                model=settings.VISION_MODEL,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )
        
        app_logger.info(f"Vision客户端初始化完成，模型: {self.config.model}")
    
    def analyze_image(
        self,
        image_data: bytes,
        prompt: str,
        **kwargs
    ) -> Optional[str]:
        """分析图片
        
        Args:
            image_data: 图片字节数据
            prompt: 分析提示词
            **kwargs: 其他参数
            
        Returns:
            分析结果文本
        """
        try:
            # 记录API调用
            log_api_call("Vision分析图片", prompt, self.config.model)
            
            # Base64编码图片
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # 准备请求参数
            payload = {
                "model": self.config.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            }
            
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.config.api_base}/chat/completions"
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=90
            )
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                app_logger.info("图片分析成功")
                return content
            else:
                app_logger.error("Vision响应格式错误")
                return None
        
        except requests.exceptions.RequestException as e:
            app_logger.error(f"Vision API请求失败: {str(e)}")
            return f"❌ 图片分析失败: {str(e)}"
        
        except Exception as e:
            app_logger.error(f"图片分析失败: {str(e)}", exc_info=True)
            return f"❌ 发生错误: {str(e)}"
    
    def analyze_image_file(
        self,
        image_path: str,
        prompt: str,
        **kwargs
    ) -> Optional[str]:
        """分析图片文件
        
        Args:
            image_path: 图片文件路径
            prompt: 分析提示词
            **kwargs: 其他参数
            
        Returns:
            分析结果文本
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            return self.analyze_image(image_data, prompt, **kwargs)
        
        except Exception as e:
            app_logger.error(f"读取图片文件失败: {str(e)}")
            return f"❌ 读取图片失败: {str(e)}"
    
    def extract_pdf_text(self, pdf_path: str) -> Optional[str]:
        """从PDF提取文本
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            提取的文本
        """
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(pdf_path)
            text_parts = []
            
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    text_parts.append(f"--- 第 {page_num} 页 ---\n{text}")
            
            full_text = "\n\n".join(text_parts)
            app_logger.info(f"PDF文本提取成功，共 {len(reader.pages)} 页")
            
            return full_text
        
        except Exception as e:
            app_logger.error(f"PDF文本提取失败: {str(e)}")
            return None
    
    def analyze_pdf(
        self,
        pdf_path: str,
        prompt: str,
        **kwargs
    ) -> Optional[str]:
        """分析PDF文档
        
        Args:
            pdf_path: PDF文件路径
            prompt: 分析提示词
            **kwargs: 其他参数
            
        Returns:
            分析结果
        """
        try:
            # 提取PDF文本
            pdf_text = self.extract_pdf_text(pdf_path)
            if not pdf_text:
                return "❌ 无法提取PDF文本内容"
            
            # 使用LLM分析
            from src.api.llm_client import llm_client
            
            messages = [
                {
                    "role": "user",
                    "content": f"{prompt}\n\nPDF内容：\n{pdf_text[:10000]}"  # 限制长度
                }
            ]
            
            result = llm_client.chat_complete(messages, **kwargs)
            return result
        
        except Exception as e:
            app_logger.error(f"PDF分析失败: {str(e)}")
            return f"❌ PDF分析失败: {str(e)}"


# 全局Vision客户端实例
vision_client = VisionClient()
