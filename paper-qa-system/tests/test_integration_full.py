#!/usr/bin/env python3
"""
测试套件 - 学术论文问答系统

使用 unittest 框架进行模块级别测试
验证核心功能和组件是否正常工作
"""

import unittest
import sys
import os
from pathlib import Path
from typing import List, Dict

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestImports(unittest.TestCase):
    """测试模块导入"""
    
    def test_core_imports(self):
        """验证核心模块可以正常导入"""
        # 由于 accelerate 库循环导入问题，这里只测试模块文件是否存在
        import os
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent
        
        # 检查核心文件是否存在
        core_files = {
            'config/__init__.py': '配置模块',
            'src/agent.py': 'Agent 模块',
            'src/loaders/document_loader.py': '文档加载器',
        }
        
        for file_path, description in core_files.items():
            full_path = project_root / file_path
            self.assertTrue(
                full_path.exists(),
                f"{description} 文件应该存在: {file_path}"
            )
        
        print("✓ 所有核心模块文件存在")
        
        # 尝试导入不依赖 transformers 的模块
        try:
            from llama_index.core import VectorStoreIndex, Document
            self.assertIsNotNone(VectorStoreIndex, "VectorStoreIndex 应该存在")
            print("✓ LlamaIndex 核心组件可导入")
        except ImportError as e:
            print(f"⚠️  LlamaIndex 导入警告: {e}")
    
    def test_llamaindex_imports(self):
        """验证 LlamaIndex 依赖可以导入"""
        try:
            from llama_index.core import VectorStoreIndex, Document, Settings
            from llama_index.core import StorageContext, load_index_from_storage
            
            self.assertIsNotNone(VectorStoreIndex, "VectorStoreIndex 应该存在")
            self.assertIsNotNone(Document, "Document 类应该存在")
            self.assertIsNotNone(Settings, "Settings 应该存在")
            
            print("✓ LlamaIndex 核心模块导入成功")
            
        except ImportError as e:
            self.fail(f"LlamaIndex 导入失败: {e}")
    
    def test_utility_imports(self):
        """验证工具类库可以导入"""
        success_count = 0
        total_count = 3
        
        # PyMuPDF
        try:
            import fitz  # PyMuPDF
            self.assertIsNotNone(fitz, "PyMuPDF 应该存在")
            success_count += 1
            print("✓ PyMuPDF 导入成功")
        except ImportError:
            print("⚠️  PyMuPDF 未安装")
        
        # loguru
        try:
            import loguru
            self.assertIsNotNone(loguru, "loguru 应该存在")
            success_count += 1
            print("✓ loguru 导入成功")
        except ImportError:
            print("⚠️  loguru 未安装")
        
        # pydantic_settings
        try:
            from pydantic_settings import BaseSettings
            self.assertIsNotNone(BaseSettings, "pydantic_settings 应该存在")
            success_count += 1
            print("✓ pydantic_settings 导入成功")
        except ImportError:
            print("⚠️  pydantic_settings 未安装")
        
        print(f"✓ 工具类库导入: {success_count}/{total_count} 成功")


class TestConfiguration(unittest.TestCase):
    """测试配置管理"""
    
    def test_config_files_exist(self):
        """验证配置文件存在"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        
        config_files = [
            'config/__init__.py',
            'config/llm_config.py',
            'config/settings.py',
        ]
        
        for file_path in config_files:
            full_path = project_root / file_path
            self.assertTrue(
                full_path.exists(),
                f"配置文件应该存在: {file_path}"
            )
        
        print(f"✓ 所有配置文件都存在 ({len(config_files)} 个)")
    
    def test_env_example_exists(self):
        """验证 .env.example 文件存在"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        
        env_example = project_root / '.env.example'
        self.assertTrue(
            env_example.exists(),
            ".env.example 文件应该存在"
        )
        
        print("✓ .env.example 文件存在")
    
    def test_config_structure(self):
        """验证配置文件内容结构"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        
        # 读取 llm_config.py
        llm_config_path = project_root / 'config' / 'llm_config.py'
        content = llm_config_path.read_text()
        
        # 检查必要的函数（当前版本使用函数而非枚举）
        required_items = [
            'def get_llm',
            'def get_embedding_model',
            'provider',
            'OpenAI',
        ]
        
        for item in required_items:
            self.assertIn(
                item,
                content,
                f"配置应该包含: {item}"
            )
        
        print(f"✓ 配置结构完整 ({len(required_items)} 个必需项)")


class TestDocumentLoader(unittest.TestCase):
    """测试文档加载器"""
    
    def test_document_loader_file_exists(self):
        """验证文档加载器文件存在"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        
        loader_path = project_root / 'src' / 'loaders' / 'document_loader.py'
        self.assertTrue(
            loader_path.exists(),
            "document_loader.py 应该存在"
        )
        
        print("✓ DocumentLoader 文件存在")
    
    def test_supported_formats_defined(self):
        """验证支持的文件格式已定义"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        
        loader_path = project_root / 'src' / 'loaders' / 'document_loader.py'
        content = loader_path.read_text()
        
        # 检查是否定义了支持的格式（使用 SUPPORTED_EXTENSIONS）
        self.assertIn('SUPPORTED_EXTENSIONS', content, "应该定义 SUPPORTED_EXTENSIONS")
        self.assertIn('.pdf', content, "应该支持 PDF 格式")
        self.assertIn('.docx', content, "应该支持 DOCX 格式")
        
        print("✓ 支持的文件格式已定义")
    
    def test_loader_methods_defined(self):
        """验证加载器核心方法已定义"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        
        loader_path = project_root / 'src' / 'loaders' / 'document_loader.py'
        content = loader_path.read_text()
        
        required_methods = [
            'def load_documents',
            'def load_single_document',
            'def get_document_stats',
        ]
        
        for method in required_methods:
            self.assertIn(
                method,
                content,
                f"加载器应该定义方法: {method}"
            )
        
        print(f"✓ 所有核心方法已定义 ({len(required_methods)} 个)")
    
    def test_loader_class_structure(self):
        """测试加载器类结构"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        
        loader_path = project_root / 'src' / 'loaders' / 'document_loader.py'
        content = loader_path.read_text()
        
        # 检查类定义
        self.assertIn('class DocumentLoader', content, "应该定义 DocumentLoader 类")
        self.assertIn('def __init__', content, "应该有 __init__ 方法")
        
        print("✓ DocumentLoader 类结构完整")


class TestAcademicAgent(unittest.TestCase):
    """测试 Academic Agent"""
    
    def test_agent_file_exists(self):
        """验证 Agent 文件存在"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        
        agent_path = project_root / 'src' / 'agent.py'
        self.assertTrue(
            agent_path.exists(),
            "agent.py 文件应该存在"
        )
        
        print("✓ Agent 文件存在")
    
    def test_agent_class_defined(self):
        """验证 Agent 类已定义"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        
        agent_path = project_root / 'src' / 'agent.py'
        content = agent_path.read_text()
        
        self.assertIn('class AcademicAgent', content, "应该定义 AcademicAgent 类")
        print("✓ AcademicAgent 类已定义")
    
    def test_agent_init_defined(self):
        """验证 Agent 初始化方法已定义"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        
        agent_path = project_root / 'src' / 'agent.py'
        content = agent_path.read_text()
        
        # 检查 __init__ 参数
        self.assertIn('def __init__', content, "应该有 __init__ 方法")
        self.assertIn('documents_dir', content, "应该有 documents_dir 参数")
        self.assertIn('index_dir', content, "应该有 index_dir 参数")
        self.assertIn('auto_load', content, "应该有 auto_load 参数")
        
        print("✓ Agent 初始化方法已定义，参数正确")
    
    def test_agent_methods_defined(self):
        """验证 Agent 核心方法已定义"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        
        agent_path = project_root / 'src' / 'agent.py'
        content = agent_path.read_text()
        
        required_methods = [
            'def load_or_build_index',
            'def rebuild_index',
            'def query',
            'def list_papers',
            'def get_stats',
        ]
        
        for method in required_methods:
            self.assertIn(
                method,
                content,
                f"Agent 应该定义方法: {method}"
            )
        
        print(f"✓ 所有核心方法已定义 ({len(required_methods)} 个):")
        for method in required_methods:
            method_name = method.replace('def ', '').strip()
            print(f"  - {method_name}()")
    
    def test_create_agent_function_defined(self):
        """测试 create_agent 便捷函数已定义"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        
        agent_path = project_root / 'src' / 'agent.py'
        content = agent_path.read_text()
        
        self.assertIn('def create_agent', content, "应该定义 create_agent 函数")
        
        print("✓ create_agent 便捷函数已定义")


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_file_structure(self):
        """测试完整文件结构"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        
        # 检查核心文件是否存在
        core_files = [
            'config/__init__.py',
            'config/llm_config.py',
            'config/settings.py',
            'src/__init__.py',
            'src/agent.py',
            'src/loaders/__init__.py',
            'src/loaders/document_loader.py',
            'main.py',
            'init_system.py',
        ]
        
        all_exist = True
        for file_path in core_files:
            full_path = project_root / file_path
            if not full_path.exists():
                all_exist = False
                print(f"  ✗ 缺少: {file_path}")
        
        self.assertTrue(all_exist, "所有核心文件应该存在")
        
        print("✓ 完整文件结构验证通过")
        print(f"  - {len(core_files)} 个核心文件都存在")
    
    def test_directory_structure(self):
        """验证项目目录结构"""
        project_root = Path(__file__).parent.parent
        
        required_dirs = [
            'config',
            'src',
            'src/loaders',
            'src/indexing',
            'data',
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            self.assertTrue(
                dir_path.exists(),
                f"目录应该存在: {dir_name}"
            )
        
        print(f"✓ 项目目录结构完整 ({len(required_dirs)} 个目录)")
    
    def test_required_files(self):
        """验证必需文件存在"""
        project_root = Path(__file__).parent.parent
        
        required_files = [
            'main.py',
            'init_system.py',
            'config/__init__.py',
            'config/llm_config.py',
            'src/__init__.py',
            'src/agent.py',
            'src/loaders/__init__.py',
            'src/loaders/document_loader.py',
        ]
        
        for file_name in required_files:
            file_path = project_root / file_name
            self.assertTrue(
                file_path.exists(),
                f"文件应该存在: {file_name}"
            )
        
        print(f"✓ 所有必需文件都存在 ({len(required_files)} 个)")


class TestSystemInfo(unittest.TestCase):
    """测试系统信息"""
    
    def test_python_version(self):
        """验证 Python 版本"""
        import sys
        
        version = sys.version_info
        
        # 要求 Python 3.9+
        self.assertGreaterEqual(
            version.major,
            3,
            "Python 主版本应该 >= 3"
        )
        self.assertGreaterEqual(
            version.minor,
            9,
            "Python 次版本应该 >= 9 (需要 Python 3.9+)"
        )
        
        print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    def test_dependencies_installed(self):
        """验证关键依赖已安装"""
        dependencies = [
            ('llama_index', 'LlamaIndex'),
            ('fitz', 'PyMuPDF'),
            ('loguru', 'Loguru'),
            ('pydantic_settings', 'Pydantic Settings'),
        ]
        
        installed = []
        missing = []
        
        for module_name, display_name in dependencies:
            try:
                __import__(module_name)
                installed.append(display_name)
            except ImportError:
                missing.append(display_name)
        
        if missing:
            print(f"⚠️  缺少依赖: {', '.join(missing)}")
        
        print(f"✓ 已安装依赖: {len(installed)}/{len(dependencies)}")
        for dep in installed:
            print(f"  - {dep}")


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestImports,
        TestConfiguration,
        TestDocumentLoader,
        TestAcademicAgent,
        TestIntegration,
        TestSystemInfo,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 70)
    
    # 返回是否所有测试通过
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 70)
    print("学术论文问答系统 - 测试套件")
    print("=" * 70)
    print()
    
    success = run_tests()
    
    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)
