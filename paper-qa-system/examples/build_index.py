"""
示例：构建索引

用于首次构建文档索引或重建索引
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from config import SystemConfig
from init_system import initialize_system
from src.indexing import DocumentIndexer


def main():
    """构建索引主函数"""
    
    print("=" * 60)
    print("学术论文索引构建工具")
    print("=" * 60)
    print()
    
    # 初始化配置
    print("正在初始化系统配置...")
    try:
        initialize_system()
        print("✓ 配置初始化完成\n")
    except Exception as e:
        print(f"✗ 系统初始化失败: {e}")
        return
    
    # 检查文档目录
    documents_dir = SystemConfig.DOCUMENTS_DIR
    
    if not documents_dir.exists() or not any(documents_dir.iterdir()):
        print(f"⚠️  文档目录为空: {documents_dir}")
        print(f"请将论文文档放入该目录后重新运行此脚本")
        print("支持的格式: PDF, DOCX, DOC, Markdown\n")
        return
    
    # 创建索引构建器
    print("正在初始化索引构建器...")
    indexer = DocumentIndexer(
        vector_store_type=SystemConfig.VECTOR_STORE,
        chunk_size=SystemConfig.CHUNK_SIZE,
        chunk_overlap=SystemConfig.CHUNK_OVERLAP,
    )
    print("✓ 索引构建器初始化完成\n")
    
    # 构建索引
    try:
        print("开始构建索引...")
        print(f"文档目录: {documents_dir}")
        print(f"向量库类型: {SystemConfig.VECTOR_STORE}")
        print(f"Chunk 大小: {SystemConfig.CHUNK_SIZE}")
        print(f"Chunk 重叠: {SystemConfig.CHUNK_OVERLAP}\n")
        
        index = indexer.build_index(document_dir=documents_dir)
        
        print("\n" + "=" * 60)
        print("✓ 索引构建成功！")
        print("=" * 60)
        print()
        print("现在可以运行主程序进行问答:")
        print("  python main.py")
        print()
        
    except Exception as e:
        logger.error(f"索引构建失败: {e}")
        print(f"\n✗ 索引构建失败: {e}\n")
        raise


if __name__ == "__main__":
    main()
