"""
文档加载器示例

演示 DocumentLoader 的基本功能（简化版）
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.loaders.document_loader import DocumentLoader


def example_1_load_directory():
    """示例 1: 加载目录下所有文档"""
    
    print("\n" + "=" * 70)
    print("示例 1: 加载目录下所有文档")
    print("=" * 70 + "\n")
    
    # 创建加载器
    loader = DocumentLoader(
        input_dir="./data/documents",
        recursive=True,          # 递归加载子目录
        clean_text=True,         # 启用文本清洗
        preserve_formatting=True # 保留格式信息
    )
    
    # 加载所有文档
    documents = loader.load_documents()
    
    print(f"成功加载 {len(documents)} 个文档\n")
    
    # 显示前 3 个文档的信息
    for i, doc in enumerate(documents[:3], 1):
        print(f"文档 {i}:")
        print(f"  文件名: {doc.metadata.get('file_name')}")
        print(f"  类型: {doc.metadata.get('file_type')}")
        print(f"  大小: {doc.metadata.get('file_size_mb')} MB")
        print(f"  字符数: {doc.metadata.get('char_count'):,}")
        print(f"  内容预览: {doc.text[:100]}...\n")
    
    # 打印统计信息
    loader.print_stats(documents)


def example_2_load_specific_types():
    """示例 2: 只加载特定类型的文档"""
    
    print("\n" + "=" * 70)
    print("示例 2: 只加载 PDF 文档")
    print("=" * 70 + "\n")
    
    loader = DocumentLoader(
        input_dir="./data/documents",
        recursive=True,
    )
    
    # 只加载 PDF 文件
    documents = loader.load_documents(
        file_extensions=['.pdf']
    )
    
    print(f"找到 {len(documents)} 个 PDF 文档\n")
    
    # 统计信息
    stats = loader.get_document_stats(documents)
    print(f"总页数/片段: {stats['total_documents']}")
    print(f"总大小: {stats['total_size_mb']} MB")
    print(f"总字符数: {stats['total_chars']:,}")
    print(f"总单词数: {stats['total_words']:,}")


def example_3_load_single_file():
    """示例 3: 加载单个文件"""
    
    print("\n" + "=" * 70)
    print("示例 3: 加载单个文件")
    print("=" * 70 + "\n")
    
    loader = DocumentLoader()
    
    # 指定文件路径
    file_path = "./data/documents/sample.pdf"
    
    try:
        documents = loader.load_single_document(file_path)
        
        print(f"成功加载文件: {file_path}")
        print(f"生成文档数: {len(documents)}\n")
        
        for i, doc in enumerate(documents[:3], 1):  # 只显示前3个
            print(f"第 {i} 页/段:")
            print(f"  字符数: {doc.metadata.get('char_count'):,}")
            print(f"  单词数: {doc.metadata.get('word_count'):,}")
            if 'page_number' in doc.metadata:
                print(f"  页码: {doc.metadata['page_number']}/{doc.metadata['total_pages']}")
            print()
    
    except FileNotFoundError:
        print(f"文件不存在: {file_path}")
        print("提示: 请将文档放入 data/documents/ 目录")
    except Exception as e:
        print(f"加载失败: {e}")


def main():
    """运行示例"""
    
    print("=" * 70)
    print("文档加载器使用示例（简化版）")
    print("=" * 70)
    
    examples = {
        '1': ('加载目录下所有文档', example_1_load_directory),
        '2': ('只加载 PDF 文档', example_2_load_specific_types),
        '3': ('加载单个文件', example_3_load_single_file),
    }
    
    print("\n请选择要运行的示例:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. 运行所有示例")
    
    choice = input("\n请输入选项 (默认: 1): ").strip() or '1'
    
    try:
        if choice == '0':
            for _, func in examples.values():
                try:
                    func()
                except Exception as e:
                    print(f"\n示例运行出错: {e}\n")
        elif choice in examples:
            _, func = examples[choice]
            func()
        else:
            print(f"无效选项: {choice}")
    except KeyboardInterrupt:
        print("\n\n已取消")
    
    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)
    print("\n提示: 详细的文档加载器功能请参考 docs/DOCUMENT_LOADER_GUIDE.md\n")


if __name__ == "__main__":
    main()
