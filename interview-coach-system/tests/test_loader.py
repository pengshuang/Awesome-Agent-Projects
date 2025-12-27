"""
简历加载器单元测试
"""

import pytest
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.loaders import ResumeLoader
from src.models.resume import ResumeData
from src.exceptions import (
    FileNotFoundError,
    UnsupportedFileFormatError,
    EmptyResumeError,
)


class TestResumeLoader:
    """简历加载器测试类"""
    
    @pytest.fixture
    def loader(self):
        """创建加载器实例"""
        return ResumeLoader()
    
    def test_loader_initialization(self, loader):
        """测试加载器初始化"""
        assert loader is not None
        assert loader.resume_content is None
        assert loader.resume_path is None
    
    def test_supported_formats(self, loader):
        """测试支持的格式"""
        assert ".pdf" in loader.SUPPORTED_FORMATS
    
    def test_load_nonexistent_file(self, loader):
        """测试加载不存在的文件"""
        with pytest.raises(FileNotFoundError):
            loader.load_resume("nonexistent_file.pdf")
    
    def test_load_unsupported_format(self, loader):
        """测试加载不支持的格式"""
        # 创建一个临时的.txt文件
        temp_file = Path("tests/fixtures/temp.txt")
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file.write_text("test content")
        
        try:
            with pytest.raises(UnsupportedFileFormatError):
                loader.load_resume(str(temp_file))
        finally:
            if temp_file.exists():
                temp_file.unlink()
    
    @pytest.mark.skipif(
        not Path("tests/fixtures/sample.pdf").exists(),
        reason="需要测试用的PDF文件"
    )
    def test_load_valid_resume(self, loader):
        """测试加载有效的简历"""
        result = loader.load_resume("tests/fixtures/sample.pdf")
        
        assert isinstance(result, ResumeData)
        assert result.content != ""
        assert result.metadata.file_name == "sample.pdf"
        assert result.metadata.content_length > 0
        assert result.metadata.load_time > 0
    
    @pytest.mark.skipif(
        not Path("tests/fixtures/sample.pdf").exists(),
        reason="需要测试用的PDF文件"
    )
    def test_resume_metadata(self, loader):
        """测试简历元数据"""
        result = loader.load_resume("tests/fixtures/sample.pdf")
        metadata = result.metadata
        
        assert metadata.file_name is not None
        assert metadata.file_path is not None
        assert metadata.file_size > 0
        assert metadata.content_length > 0
        assert metadata.load_time >= 0
    
    @pytest.mark.skipif(
        not Path("tests/fixtures/sample.pdf").exists(),
        reason="需要测试用的PDF文件"
    )
    def test_resume_preview(self, loader):
        """测试简历预览功能"""
        result = loader.load_resume("tests/fixtures/sample.pdf")
        preview = result.get_preview()
        
        assert isinstance(preview, str)
        assert len(preview) <= 203  # 200 + "..."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
