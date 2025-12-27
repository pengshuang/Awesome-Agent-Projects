"""
Web 搜索功能测试
整合了多个搜索测试文件
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from src.tools.web_search import WebSearchTool


def test_basic_search():
    """基础搜索测试"""
    print("\n" + "="*70)
    print("测试 1: 基础搜索功能")
    print("="*70 + "\n")
    
    engine = os.getenv("WEB_SEARCH_ENGINE", "duckduckgo")
    print(f"使用搜索引擎: {engine}\n")
    
    tool = WebSearchTool(max_results=3, engine=engine)
    
    test_queries = [
        "Who is the president of the USA?",
        "What is Python programming?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"查询 {i}: {query}")
        print('='*70 + '\n')
        
        try:
            results = tool.search(query)
            
            if results:
                print(f"✅ 找到 {len(results)} 个结果:\n")
                for j, result in enumerate(results, 1):
                    print(f"[{j}] {result['title']}")
                    print(f"    📎 {result['url']}")
                    snippet = result['snippet'][:150].replace('\n', ' ')
                    print(f"    💬 {snippet}...\n")
            else:
                print("⚠️ 未找到结果\n")
                
        except Exception as e:
            print(f"❌ 搜索失败: {e}\n")
    
    print("="*70)
    print("✅ 基础搜索测试完成")
    print("="*70 + "\n")


def test_multiple_engines():
    """测试多个搜索引擎"""
    print("\n" + "="*70)
    print("测试 2: 多搜索引擎测试")
    print("="*70 + "\n")
    
    engines = ["duckduckgo", "searxng"]
    query = "artificial intelligence 2024"
    
    for engine in engines:
        print(f"\n{'='*70}")
        print(f"测试搜索引擎: {engine}")
        print(f"{'='*70}\n")
        
        try:
            tool = WebSearchTool(max_results=2, engine=engine)
            results = tool.search(query)
            
            if results:
                print(f"✅ 使用 {engine} 找到 {len(results)} 个结果")
                for i, result in enumerate(results, 1):
                    print(f"  [{i}] {result['title'][:50]}...")
            else:
                print(f"⚠️ {engine} 未找到结果")
                
        except Exception as e:
            print(f"❌ {engine} 测试失败: {e}")
    
    print("\n" + "="*70)
    print("✅ 多引擎测试完成")
    print("="*70 + "\n")


def test_search_with_agent():
    """测试与 Agent 的集成"""
    print("\n" + "="*70)
    print("测试 3: Agent 集成测试")
    print("="*70 + "\n")
    
    try:
        from src.agent import AcademicAgent
        
        print("创建 Agent (不加载索引)...")
        agent = AcademicAgent(auto_load=False)
        
        print("执行联网搜索查询...\n")
        result = agent.query_direct(
            question="What is machine learning?",
            enable_web_search=True
        )
        
        web_sources = result.get('web_sources', [])
        print(f"✅ 搜索成功！找到 {len(web_sources)} 个网络资源")
        
        if web_sources:
            print("\n网络资源:")
            for i, source in enumerate(web_sources, 1):
                print(f"  [{i}] {source['title']}")
                print(f"      {source['url']}")
        
        print("\n答案预览:")
        answer = result.get('answer', '')
        print(answer[:200] + "..." if len(answer) > 200 else answer)
        
        print("\n" + "="*70)
        print("✅ Agent 集成测试完成")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ Agent 集成测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("Web 搜索功能完整测试套件")
    print("="*70)
    
    test_basic_search()
    test_multiple_engines()
    test_search_with_agent()
    
    print("\n" + "="*70)
    print("🎉 所有测试完成！")
    print("="*70 + "\n")
