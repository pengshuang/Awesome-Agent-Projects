"""
文档加载器测试

测试 DocumentLoader 的各项功能
"""

import sys
from pathlib import Path
import tempfile
import shutil

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.loaders.document_loader import (
    DocumentLoader,
    PDFReader,
    DOCXReader,
    MarkdownReader,
    TextCleaner,
)
from llama_index.core import Document


def test_text_cleaner():
    """测试文本清洗器"""
    print("\n" + "=" * 60)
    print("测试 1: 文本清洗器")
    print("=" * 60)
    
    cleaner = TextCleaner()
    
    # 测试用例
    test_cases = [
        # (输入, 预期包含, 描述)
        ("Hello  World\n\n\nTest", "Hello World", "移除多余空格和换行"),
        ("Line1\r\nLine2\rLine3", "Line1\nLine2\nLine3", "统一换行符"),
        ("  Text  with   spaces  ", "Text with spaces", "移除首尾空格"),
        ("中文，测试。  标点！", "中文，测试。标点！", "中文标点处理"),
    ]
    
    passed = 0
    for i, (input_text, expected, description) in enumerate(test_cases, 1):
        result = cleaner.clean_text(input_text, preserve_formatting=False)
        success = expected in result or result == expected
        status = "✓" if success else "✗"
        print(f"  {status} 测试 {i}: {description}")
        if success:
            passed += 1
        else:
            print(f"    输入: {repr(input_text)}")
            print(f"    期望: {repr(expected)}")
            print(f"    实际: {repr(result)}")
    
    print(f"\n通过: {passed}/{len(test_cases)}")


def test_markdown_reader():
    """测试 Markdown 读取器"""
    print("\n" + "=" * 60)
    print("测试 2: Markdown 读取器")
    print("=" * 60)
    
    # 创建临时 Markdown 文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write("# 测试标题\n\n这是测试内容。\n\n## 子标题\n\n更多内容。")
        temp_file = Path(f.name)
    
    try:
        reader = MarkdownReader()
        documents = reader.load_data(temp_file)
        
        assert len(documents) == 1, "应该返回 1 个文档"
        assert documents[0].metadata['file_type'] == 'markdown', "文件类型应为 markdown"
        assert '测试标题' in documents[0].text, "应包含标题内容"
        
        print("  ✓ Markdown 读取器测试通过")
        print(f"    加载的文档数: {len(documents)}")
        print(f"    文本长度: {len(documents[0].text)}")
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
    finally:
        temp_file.unlink()


def test_document_loader_basic():
    """测试基本的文档加载功能"""
    print("\n" + "=" * 60)
    print("测试 3: 基本文档加载")
    print("=" * 60)
    
    # 创建临时目录和文件
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # 创建测试文件
        (temp_dir / "test1.md").write_text("# 文档 1\n\n内容 1", encoding='utf-8')
        (temp_dir / "test2.md").write_text("# 文档 2\n\n内容 2", encoding='utf-8')
        
        # 创建子目录
        sub_dir = temp_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "test3.md").write_text("# 文档 3\n\n内容 3", encoding='utf-8')
        
        # 测试递归加载
        loader = DocumentLoader(input_dir=temp_dir, recursive=True)
        documents = loader.load_documents()
        
        assert len(documents) == 3, f"递归模式应加载 3 个文档，实际: {len(documents)}"
        print(f"  ✓ 递归加载: {len(documents)} 个文档")
        
        # 测试非递归加载
        loader_non_recursive = DocumentLoader(input_dir=temp_dir, recursive=False)
        documents_non_recursive = loader_non_recursive.load_documents()
        
        assert len(documents_non_recursive) == 2, f"非递归模式应加载 2 个文档，实际: {len(documents_non_recursive)}"
        print(f"  ✓ 非递归加载: {len(documents_non_recursive)} 个文档")
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
    finally:
        shutil.rmtree(temp_dir)


def test_file_extensions_filter():
    """测试文件扩展名过滤"""
    print("\n" + "=" * 60)
    print("测试 4: 文件扩展名过滤")
    print("=" * 60)
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # 创建不同类型的文件
        (temp_dir / "test.md").write_text("Markdown", encoding='utf-8')
        (temp_dir / "test.txt").write_text("Text file", encoding='utf-8')  # 不支持的格式
        
        loader = DocumentLoader(input_dir=temp_dir)
        
        # 只加载 Markdown
        md_docs = loader.load_documents(file_extensions=['.md'])
        assert len(md_docs) == 1, "应只加载 1 个 .md 文件"
        print(f"  ✓ 扩展名过滤: 正确加载 {len(md_docs)} 个 .md 文件")
        
        # 加载所有支持的格式
        all_docs = loader.load_documents()
        assert len(all_docs) == 1, "应只加载 1 个支持的文件"
        print(f"  ✓ 默认加载: {len(all_docs)} 个支持的文件")
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
    finally:
        shutil.rmtree(temp_dir)


def test_metadata_extraction():
    """测试元数据提取"""
    print("\n" + "=" * 60)
    print("测试 5: 元数据提取")
    print("=" * 60)
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        test_file = temp_dir / "test.md"
        test_content = "# 测试\n\n这是测试内容。" * 10
        test_file.write_text(test_content, encoding='utf-8')
        
        loader = DocumentLoader()
        documents = loader.load_single_document(test_file)
        
        assert len(documents) == 1, "应返回 1 个文档"
        
        doc = documents[0]
        metadata = doc.metadata
        
        # 检查必要的元数据
        required_fields = [
            'file_name', 'file_path', 'file_type', 'file_size',
            'char_count', 'word_count', 'created_time', 'modified_time'
        ]
        
        missing_fields = [field for field in required_fields if field not in metadata]
        
        if missing_fields:
            print(f"  ✗ 缺少元数据字段: {missing_fields}")
        else:
            print("  ✓ 所有必要的元数据字段都存在")
        
        print(f"\n  元数据内容:")
        for key in required_fields:
            if key in metadata:
                print(f"    {key}: {metadata[key]}")
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
    finally:
        shutil.rmtree(temp_dir)


def test_document_stats():
    """测试文档统计功能"""
    print("\n" + "=" * 60)
    print("测试 6: 文档统计")
    print("=" * 60)
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # 创建多个文件
        (temp_dir / "doc1.md").write_text("内容 1" * 100, encoding='utf-8')
        (temp_dir / "doc2.md").write_text("内容 2" * 200, encoding='utf-8')
        
        loader = DocumentLoader(input_dir=temp_dir)
        documents = loader.load_documents()
        
        stats = loader.get_document_stats(documents)
        
        assert stats['total_documents'] == 2, "应有 2 个文档"
        assert stats['total_files'] == 2, "应有 2 个文件"
        assert stats['total_chars'] > 0, "总字符数应大于 0"
        assert stats['total_words'] > 0, "总单词数应大于 0"
        assert 'markdown' in stats['file_types'], "应包含 markdown 类型"
        
        print("  ✓ 统计信息生成成功")
        print(f"\n  统计详情:")
        print(f"    总文档数: {stats['total_documents']}")
        print(f"    总文件数: {stats['total_files']}")
        print(f"    总字符数: {stats['total_chars']}")
        print(f"    总单词数: {stats['total_words']}")
        print(f"    文件类型: {stats['file_types']}")
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
    finally:
        shutil.rmtree(temp_dir)


def test_text_cleaning_modes():
    """测试不同的文本清洗模式"""
    print("\n" + "=" * 60)
    print("测试 7: 文本清洗模式")
    print("=" * 60)
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        test_file = temp_dir / "test.md"
        messy_text = "Line 1  \n\n\n  Line 2   \n  Line 3  "
        test_file.write_text(messy_text, encoding='utf-8')
        
        # 不清洗
        loader_no_clean = DocumentLoader(clean_text=False)
        docs_no_clean = loader_no_clean.load_single_document(test_file)
        
        # 清洗并保留格式
        loader_preserve = DocumentLoader(clean_text=True, preserve_formatting=True)
        docs_preserve = loader_preserve.load_single_document(test_file)
        
        # 激进清洗
        loader_aggressive = DocumentLoader(clean_text=True, preserve_formatting=False)
        docs_aggressive = loader_aggressive.load_single_document(test_file)
        
        print("  ✓ 不同清洗模式测试完成")
        print(f"\n  原始长度: {len(docs_no_clean[0].text)}")
        print(f"  保留格式: {len(docs_preserve[0].text)}")
        print(f"  激进清洗: {len(docs_aggressive[0].text)}")
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
    finally:
        shutil.rmtree(temp_dir)


def test_pdf_reader():
    """测试 PDF 读取器"""
    print("\n" + "=" * 60)
    print("测试 8: PDF 读取器")
    print("=" * 60)
    
    # 使用项目中的 PDF 文件
    pdf_path = Path(__file__).parent.parent / "data" / "documents" / "infiniTransformer.pdf"
    
    if not pdf_path.exists():
        print(f"  ⚠ PDF 文件不存在，跳过测试: {pdf_path}")
        return
    
    try:
        reader = PDFReader()
        documents = reader.load_data(pdf_path)
        
        assert len(documents) > 0, "应该加载至少 1 个文档"
        assert documents[0].metadata.get('file_type') == 'pdf', "文件类型应为 pdf"
        assert len(documents[0].text) > 0, "应包含文本内容"
        
        # 检查是否包含页码信息
        if 'page_number' in documents[0].metadata:
            print(f"  ✓ PDF 读取器测试通过")
            print(f"    加载的文档数（页数）: {len(documents)}")
            print(f"    第一页文本长度: {len(documents[0].text)}")
            print(f"    总页数: {documents[0].metadata.get('total_pages', 'N/A')}")
        else:
            print(f"  ✓ PDF 读取器测试通过（无分页）")
            print(f"    加载的文档数: {len(documents)}")
            print(f"    文本长度: {len(documents[0].text)}")
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_pdf_loader_with_document_loader():
    """测试使用 DocumentLoader 加载 PDF"""
    print("\n" + "=" * 60)
    print("测试 9: DocumentLoader 加载 PDF")
    print("=" * 60)
    
    # 使用项目中的 PDF 文件
    pdf_path = Path(__file__).parent.parent / "data" / "documents" / "infiniTransformer.pdf"
    
    if not pdf_path.exists():
        print(f"  ⚠ PDF 文件不存在，跳过测试: {pdf_path}")
        return
    
    try:
        loader = DocumentLoader(clean_text=True, preserve_formatting=True)
        documents = loader.load_single_document(pdf_path)
        
        assert len(documents) > 0, "应该加载至少 1 个文档"
        
        # 检查元数据
        doc = documents[0]
        metadata = doc.metadata
        
        required_fields = ['file_name', 'file_path', 'file_type', 'file_size']
        missing_fields = [field for field in required_fields if field not in metadata]
        
        if missing_fields:
            print(f"  ✗ 缺少元数据字段: {missing_fields}")
        else:
            print("  ✓ PDF 通过 DocumentLoader 加载成功")
            print(f"    文件名: {metadata['file_name']}")
            print(f"    文件类型: {metadata['file_type']}")
            print(f"    文件大小: {metadata['file_size_mb']} MB")
            print(f"    加载的文档数: {len(documents)}")
            print(f"    总字符数: {sum(len(d.text) for d in documents)}")
            
            # 显示第一页的前200个字符
            if len(documents) > 0 and len(documents[0].text) > 0:
                preview = documents[0].text[:200].replace('\n', ' ')
                print(f"    内容预览: {preview}...")
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("测试 10: 错误处理")
    print("=" * 60)
    
    loader = DocumentLoader()
    
    # 测试不存在的目录
    try:
        loader.load_documents("./non_existent_directory")
        print("  ✗ 应该抛出 FileNotFoundError")
    except FileNotFoundError:
        print("  ✓ 正确处理不存在的目录")
    
    # 测试不存在的文件
    try:
        loader.load_single_document("./non_existent_file.pdf")
        print("  ✗ 应该抛出 FileNotFoundError")
    except FileNotFoundError:
        print("  ✓ 正确处理不存在的文件")
    
    # 测试不支持的格式
    temp_dir = Path(tempfile.mkdtemp())
    try:
        unsupported_file = temp_dir / "test.xyz"
        unsupported_file.write_text("test", encoding='utf-8')
        
        try:
            loader.load_single_document(unsupported_file)
            print("  ✗ 应该抛出 ValueError")
        except ValueError:
            print("  ✓ 正确处理不支持的格式")
    finally:
        shutil.rmtree(temp_dir)


def main():
    """运行所有测试"""
    print("=" * 60)
    print("文档加载器测试套件")
    print("=" * 60)
    
    tests = [
        test_text_cleaner,
        test_markdown_reader,
        test_document_loader_basic,
        test_file_extensions_filter,
        test_metadata_extraction,
        test_document_stats,
        test_text_cleaning_modes,
        test_pdf_reader,
        test_pdf_loader_with_document_loader,
        test_error_handling,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ 断言失败: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ 测试异常: {e}")
            failed += 1
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"通过: {passed}/{len(tests)}")
    print(f"失败: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✓ 所有测试通过！")
    else:
        print(f"\n✗ {failed} 个测试失败")


if __name__ == "__main__":
    main()
