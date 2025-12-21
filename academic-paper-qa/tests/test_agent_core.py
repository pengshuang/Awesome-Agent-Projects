"""
Agent 核心模块测试

测试 AcademicAgent 的各项功能
"""

import sys
from pathlib import Path
import tempfile
import shutil

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import AcademicAgent, create_agent
from init_system import initialize_system


def test_agent_initialization():
    """测试 1: Agent 初始化"""
    print("\n" + "=" * 60)
    print("测试 1: Agent 初始化")
    print("=" * 60)
    
    try:
        # 初始化系统
        initialize_system()
        
        # 创建临时目录
        temp_dir = Path(tempfile.mkdtemp())
        docs_dir = temp_dir / "documents"
        index_dir = temp_dir / "index"
        docs_dir.mkdir()
        
        # 创建 Agent（不自动加载）
        agent = AcademicAgent(
            documents_dir=str(docs_dir),
            index_dir=str(index_dir),
            auto_load=False,
        )
        
        # 检查属性
        assert agent.documents_dir == docs_dir, "文档目录设置错误"
        assert agent.index_dir == index_dir, "索引目录设置错误"
        assert agent.index is None, "索引应为空"
        assert agent.query_engine is None, "查询引擎应为空"
        
        print("  ✓ Agent 初始化成功")
        print(f"  ✓ 文档目录: {agent.documents_dir}")
        print(f"  ✓ 索引目录: {agent.index_dir}")
        
        # 清理
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_index_exists_check():
    """测试 2: 索引存在性检查"""
    print("\n" + "=" * 60)
    print("测试 2: 索引存在性检查")
    print("=" * 60)
    
    try:
        initialize_system()
        
        temp_dir = Path(tempfile.mkdtemp())
        index_dir = temp_dir / "index"
        index_dir.mkdir()
        
        agent = AcademicAgent(
            documents_dir=temp_dir,
            index_dir=index_dir,
            auto_load=False,
        )
        
        # 测试空目录
        assert not agent._index_exists(), "空目录不应有索引"
        print("  ✓ 空目录检查通过")
        
        # 创建部分文件
        (index_dir / "docstore.json").write_text("{}")
        assert not agent._index_exists(), "部分文件不算完整索引"
        print("  ✓ 部分文件检查通过")
        
        # 创建完整文件
        (index_dir / "index_store.json").write_text("{}")
        (index_dir / "vector_store.json").write_text("{}")
        assert agent._index_exists(), "完整文件应被识别为索引"
        print("  ✓ 完整文件检查通过")
        
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_agent_with_real_data():
    """测试 3: 使用真实数据测试 Agent"""
    print("\n" + "=" * 60)
    print("测试 3: 使用真实数据测试 Agent")
    print("=" * 60)
    
    try:
        initialize_system()
        
        # 使用项目中的真实文档
        docs_dir = Path(__file__).parent.parent / "data" / "documents"
        
        if not docs_dir.exists() or not list(docs_dir.glob("*.pdf")):
            print("  ⚠ 跳过测试：未找到文档目录或 PDF 文件")
            return
        
        # 创建临时索引目录
        temp_index_dir = Path(tempfile.mkdtemp())
        
        # 创建 Agent
        agent = AcademicAgent(
            documents_dir=str(docs_dir),
            index_dir=str(temp_index_dir),
            auto_load=True,
        )
        
        # 检查索引是否构建成功
        assert agent.index is not None, "索引应已构建"
        assert agent.query_engine is not None, "查询引擎应已创建"
        print("  ✓ 索引构建成功")
        
        # 测试列出论文
        papers = agent.list_papers(detailed=False)
        assert len(papers) > 0, "应该有论文"
        print(f"  ✓ 成功列出 {len(papers)} 篇论文")
        
        # 测试查询
        result = agent.query("这篇论文的主题是什么？", verbose=False)
        assert 'answer' in result, "结果应包含答案"
        assert len(result['answer']) > 0, "答案不应为空"
        print(f"  ✓ 查询成功，答案长度: {len(result['answer'])} 字符")
        
        # 清理
        shutil.rmtree(temp_index_dir)
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_get_stats():
    """测试 4: 获取统计信息"""
    print("\n" + "=" * 60)
    print("测试 4: 获取统计信息")
    print("=" * 60)
    
    try:
        initialize_system()
        
        temp_dir = Path(tempfile.mkdtemp())
        
        agent = AcademicAgent(
            documents_dir=temp_dir,
            index_dir=temp_dir / "index",
            auto_load=False,
        )
        
        stats = agent.get_stats()
        
        # 检查必要的统计信息
        required_keys = [
            'documents_dir',
            'index_dir',
            'index_exists',
            'documents_loaded',
            'query_engine_ready',
        ]
        
        for key in required_keys:
            assert key in stats, f"统计信息应包含 {key}"
        
        print("  ✓ 统计信息完整")
        print("\n  统计详情:")
        for key, value in stats.items():
            print(f"    {key}: {value}")
        
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_create_agent_function():
    """测试 5: create_agent 便捷函数"""
    print("\n" + "=" * 60)
    print("测试 5: create_agent 便捷函数")
    print("=" * 60)
    
    try:
        initialize_system()
        
        # 使用真实文档目录
        docs_dir = Path(__file__).parent.parent / "data" / "documents"
        
        if not docs_dir.exists() or not list(docs_dir.glob("*.pdf")):
            print("  ⚠ 跳过测试：未找到文档目录或 PDF 文件")
            return
        
        temp_index_dir = Path(tempfile.mkdtemp())
        
        # 使用便捷函数创建 Agent
        agent = create_agent(
            documents_dir=str(docs_dir),
            index_dir=str(temp_index_dir),
            force_rebuild=False,
        )
        
        # 检查 Agent 已就绪
        assert agent.index is not None, "索引应已加载"
        assert agent.query_engine is not None, "查询引擎应已创建"
        
        print("  ✓ create_agent 函数工作正常")
        print(f"  ✓ Agent 信息:\n{agent}")
        
        shutil.rmtree(temp_index_dir)
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """运行所有测试"""
    print("=" * 60)
    print("Agent 核心模块测试套件")
    print("=" * 60)
    
    tests = [
        test_agent_initialization,
        test_index_exists_check,
        test_agent_with_real_data,
        test_get_stats,
        test_create_agent_function,
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
