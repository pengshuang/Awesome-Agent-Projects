"""多模态解析服务模块"""

from typing import Optional
from pathlib import Path
from config.prompts import PROMPTS
from src.api.vision_client import vision_client
from src.utils.logger import app_logger


class MultimodalService:
    """多模态解析服务"""
    
    def __init__(self):
        self.vision = vision_client
    
    def analyze_image(
        self,
        image_path: str,
        question: str = "请分析这张图片中的英文内容，并提供详细的翻译和讲解。"
    ) -> str:
        """分析图片中的英文内容
        
        Args:
            image_path: 图片路径
            question: 用户问题
            
        Returns:
            分析结果
        """
        try:
            prompt = PROMPTS.VISION_ANALYSIS_PROMPT.format(
                question=question
            )
            
            result = self.vision.analyze_image_file(image_path, prompt)
            
            if result:
                app_logger.info(f"图片分析完成: {image_path}")
            
            return result or "❌ 图片分析失败"
        
        except Exception as e:
            app_logger.error(f"图片分析失败: {str(e)}")
            return f"❌ 图片分析失败: {str(e)}"
    
    def analyze_pdf(
        self,
        pdf_path: str,
        question: str = "请分析这份PDF文档的英文内容，提供翻译和重点讲解。"
    ) -> str:
        """分析PDF文档
        
        Args:
            pdf_path: PDF路径
            question: 用户问题
            
        Returns:
            分析结果
        """
        try:
            # 提取PDF文本
            pdf_text = self.vision.extract_pdf_text(pdf_path)
            
            if not pdf_text:
                return "❌ 无法提取PDF文本，请确保PDF包含可提取的文字内容"
            
            # 构建分析提示词
            prompt = PROMPTS.PDF_ANALYSIS_PROMPT.format(
                text=pdf_text[:8000],  # 限制长度避免超token
                question=question
            )
            
            # 使用LLM分析
            from src.api.llm_client import llm_client
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            result = llm_client.chat_complete(messages)
            
            app_logger.info(f"PDF分析完成: {pdf_path}")
            return result
        
        except Exception as e:
            app_logger.error(f"PDF分析失败: {str(e)}")
            return f"❌ PDF分析失败: {str(e)}"
    
    def process_upload(
        self,
        file_path: str,
        question: Optional[str] = None
    ) -> str:
        """处理上传的文件
        
        Args:
            file_path: 文件路径
            question: 用户问题
            
        Returns:
            处理结果
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                return self.analyze_image(
                    file_path,
                    question or "请分析这张图片中的英文内容，并提供详细的翻译和讲解。"
                )
            elif file_ext == '.pdf':
                return self.analyze_pdf(
                    file_path,
                    question or "请分析这份PDF文档的英文内容，提供翻译和重点讲解。"
                )
            else:
                return f"❌ 不支持的文件格式: {file_ext}\n\n支持的格式: 图片(jpg/png/gif等)、PDF"
        
        except Exception as e:
            app_logger.error(f"文件处理失败: {str(e)}")
            return f"❌ 文件处理失败: {str(e)}"


# 全局多模态服务实例
multimodal_service = MultimodalService()
