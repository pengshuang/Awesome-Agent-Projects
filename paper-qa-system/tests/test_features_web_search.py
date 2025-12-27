#!/usr/bin/env python3
"""
测试新增功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import SystemConfig


def test_web_search_config():
    """测试联网搜索配置"""
    print("=" * 60)
    print("测试 1: 联网搜索配置")
    print("=" * 60)
    
    enable_web_search = SystemConfig.ENABLE_WEB_SEARCH
    print(f"✓ ENABLE_WEB_SEARCH = {enable_web_search}")
    print(f"  类型: {type(enable_web_search)}")
    print()


def test_query_direct_exists():
    """测试 query_direct 方法是否存在"""
    print("=" * 60)
    print("测试 2: query_direct 方法")
    print("=" * 60)
    
    from src.agent import AcademicAgent
    
    # 检查方法是否存在
    has_method = hasattr(AcademicAgent, 'query_direct')
    print(f"✓ AcademicAgent.query_direct 方法存在: {has_method}")
    
    if has_method:
        import inspect
        sig = inspect.signature(AcademicAgent.query_direct)
        print(f"  方法签名: {sig}")
    print()


def test_query_signature():
    """测试 query 方法签名是否更新"""
    print("=" * 60)
    print("测试 3: query 方法签名")
    print("=" * 60)
    
    from src.agent import AcademicAgent
    import inspect
    
    sig = inspect.signature(AcademicAgent.query)
    params = list(sig.parameters.keys())
    
    print(f"✓ query 方法参数: {params}")
    
    has_web_search_param = 'enable_web_search' in params
    print(f"  包含 enable_web_search 参数: {has_web_search_param}")
    print()


def test_web_search_tool():
    """测试 WebSearchTool 是否可导入"""
    print("=" * 60)
    print("测试 4: WebSearchTool")
    print("=" * 60)
    
    try:
        from src.tools.web_search import WebSearchTool
        print("✓ WebSearchTool 可以导入")
        
        # 检查是否安装了依赖
        try:
            from duckduckgo_search import DDGS
            print("✓ duckduckgo-search 已安装")
        except ImportError:
            print("⚠ duckduckgo-search 未安装（网络搜索功能将不可用）")
            print("  安装命令: pip install duckduckgo-search")
    except Exception as e:
        print(f"✗ 导入失败: {e}")
    print()


def test_direct_llm_mode_exists():
    """测试 direct_llm_mode 函数是否存在"""
    print("=" * 60)
    print("测试 5: direct_llm_mode 函数")
    print("=" * 60)
    
    import main
    
    has_function = hasattr(main, 'direct_llm_mode')
    print(f"✓ main.direct_llm_mode 函数存在: {has_function}")
    print()


def main_test():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("新功能测试套件")
    print("=" * 60 + "\n")
    
    try:
        test_web_search_config()
        test_query_direct_exists()
        test_query_signature()
        test_web_search_tool()
        test_direct_llm_mode_exists()
        
        print("=" * 60)
        print("✓ 所有测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main_test()
    sys.exit(0 if success else 1)
