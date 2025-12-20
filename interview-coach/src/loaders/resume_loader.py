"""
简历加载器
支持 PDF 格式简历的解析
"""

from pathlib import Path
from typing import Optional, Dict, Any
import time

from loguru import logger

try:
    import pymupdf  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

from src.constants import (
    ERROR_FILE_NOT_FOUND,
    ERROR_INVALID_FILE,
    ERROR_NO_RESUME,
    WARNING_NO_CONTENT,
    SUCCESS_RESUME_LOADED,
    INFO_LOADING_RESUME,
)


class ResumeLoader:
    """
    简历加载器
    
    支持格式：
    - PDF (.pdf)
    
    优先使用 PyMuPDF (pymupdf)，更准确
    回退到 PyPDF2
    """
    
    SUPPORTED_FORMATS = [".pdf"]
    
    def __init__(self):
        """初始化简历加载器"""
        self.resume_content: Optional[str] = None
        self.resume_path: Optional[Path] = None
        self.metadata: Dict[str, Any] = {}
        
        # 检查依赖
        if not PYMUPDF_AVAILABLE and not PYPDF2_AVAILABLE:
            raise ImportError(
                "未安装 PDF 解析库，请安装：\n"
                "pip install pymupdf  # 推荐\n"
                "或\n"
                "pip install PyPDF2"
            )
        
        logger.info("简历加载器已初始化")
    
    def load_resume(self, file_path: str) -> Dict[str, Any]:
        """
        加载简历文件
        
        Args:
            file_path: 简历文件路径
            
        Returns:
            包含简历内容和元数据的字典
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式不支持
        """
        logger.info(f"{INFO_LOADING_RESUME} {file_path}")
        start_time = time.time()
        
        # 检查文件是否存在
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"{ERROR_FILE_NOT_FOUND}: {file_path}")
            raise FileNotFoundError(f"{ERROR_FILE_NOT_FOUND}: {file_path}")
        
        # 检查文件格式
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            logger.error(f"{ERROR_INVALID_FILE}: {file_path.suffix}")
            raise ValueError(
                f"{ERROR_INVALID_FILE}: {file_path.suffix}\n"
                f"支持的格式: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        # 加载文件
        self.resume_path = file_path
        self.resume_content = self._load_pdf(file_path)
        
        # 检查内容
        if not self.resume_content or not self.resume_content.strip():
            logger.warning(f"{WARNING_NO_CONTENT}: {file_path}")
            raise ValueError(f"{WARNING_NO_CONTENT}")
        
        # 构建元数据
        elapsed_time = time.time() - start_time
        self.metadata = {
            "file_name": file_path.name,
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "content_length": len(self.resume_content),
            "load_time": elapsed_time,
        }
        
        logger.info(f"{SUCCESS_RESUME_LOADED} | 耗时: {elapsed_time:.2f}秒 | 长度: {len(self.resume_content)}")
        
        return {
            "content": self.resume_content,
            "metadata": self.metadata,
        }
    
    def _load_pdf(self, file_path: Path) -> str:
        """
        加载 PDF 文件
        
        Args:
            file_path: PDF 文件路径
            
        Returns:
            PDF 文本内容
        """
        # 优先使用 PyMuPDF
        if PYMUPDF_AVAILABLE:
            try:
                return self._load_pdf_pymupdf(file_path)
            except Exception as e:
                logger.warning(f"PyMuPDF 加载失败: {e}")
                if PYPDF2_AVAILABLE:
                    logger.info("尝试使用 PyPDF2...")
                    return self._load_pdf_pypdf2(file_path)
                else:
                    raise
        
        # 回退到 PyPDF2
        elif PYPDF2_AVAILABLE:
            return self._load_pdf_pypdf2(file_path)
        
        else:
            raise ImportError("未安装 PDF 解析库")
    
    def _load_pdf_pymupdf(self, file_path: Path) -> str:
        """使用 PyMuPDF 加载 PDF"""
        import pymupdf
        
        text_content = []
        
        with pymupdf.open(file_path) as doc:
            for page_num, page in enumerate(doc, 1):
                text = page.get_text()
                if text.strip():
                    text_content.append(f"--- 第 {page_num} 页 ---\n{text}")
        
        return "\n\n".join(text_content)
    
    def _load_pdf_pypdf2(self, file_path: Path) -> str:
        """使用 PyPDF2 加载 PDF"""
        import PyPDF2
        
        text_content = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    text_content.append(f"--- 第 {page_num} 页 ---\n{text}")
        
        return "\n\n".join(text_content)
    
    def get_content(self) -> Optional[str]:
        """获取简历内容"""
        return self.resume_content
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取元数据"""
        return self.metadata
    
    def get_summary(self) -> str:
        """获取简历摘要（前500字符）"""
        if not self.resume_content:
            return ""
        
        content = self.resume_content[:500]
        if len(self.resume_content) > 500:
            content += "..."
        
        return content
