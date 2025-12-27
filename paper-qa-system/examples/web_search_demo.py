"""
联网搜索示例

演示如何使用联网搜索增强问答能力
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import AcademicAgent
from init_system import initialize_system


def example_1_rag_with_web_search():
    """示例 1: RAG 模式 + 联网搜索"""
    print("\n" + "=" * 70)
    print("示例 1: RAG 模式 + 联网搜索")
    print("=" * 70 + "\n")
    
    initialize_system()
    agent = AcademicAgent()
    
    # 启用联网搜索的查询
    question = "LlamaIndex 的最新版本有哪些新特性？"
    
    print(f"问题: {question}\n")
    print("执行查询（启用联网搜索）...")
    
    result = agent.query(
        question,
        enable_web_search=True,  # 启用联网搜索
        verbose=False
    )
    
    print(f"\n回答:\n{result['answer']}\n")
    
    # 显示网络搜索结果
    if result['web_sources']:
        print(f"联网找到 {len(result['web_sources'])} 个相关资源:")
        for i, source in enumerate(result['web_sources'], 1):
            print(f"\n  [{i}] {source['title']}")
            print(f"      URL: {source['url']}")
            print(f"      摘要: {source['snippet'][:100]}...")
    else:
        print("未找到网络资源")
    
    print(f"\n本地文档参考: {result['metadata']['num_sources']} 个片段")
    print(f"耗时: {result['metadata']['elapsed_time']:.2f} 秒")


def example_2_compare_with_without_web():
    """示例 2: 对比启用/禁用联网搜索"""
    print("\n" + "=" * 70)
    print("示例 2: 对比启用/禁用联网搜索")
    print("=" * 70 + "\n")
    
    initialize_system()
    agent = AcademicAgent()
    
    question = "2024年人工智能领域有哪些重大突破？"
    
    # 不使用联网搜索
    print("方式 1: 仅使用本地文档")
    print("-" * 70)
    result_no_web = agent.query(
        question,
        enable_web_search=False,
        verbose=False
    )
    print(f"回答: {result_no_web['answer'][:200]}...\n")
    
    # 使用联网搜索
    print("方式 2: 使用本地文档 + 联网搜索")
    print("-" * 70)
    result_with_web = agent.query(
        question,
        enable_web_search=True,
        verbose=False
    )
    print(f"回答: {result_with_web['answer'][:200]}...\n")
    
    # 对比
    print("对比分析:")
    print(f"  - 仅本地: {result_no_web['metadata']['num_sources']} 个文档片段")
    print(f"  - 本地+网络: {result_with_web['metadata']['num_sources']} 个文档 + {result_with_web['metadata']['num_web_sources']} 个网络资源")


def example_3_web_search_for_new_topics():
    """示例 3: 对新话题使用联网搜索"""
    print("\n" + "=" * 70)
    print("示例 3: 查询本地文档不存在的新话题")
    print("=" * 70 + "\n")
    
    initialize_system()
    agent = AcademicAgent()
    
    # 本地文档可能没有的新话题
    new_topics = [
        "GPT-4 Turbo 的新功能",
        "Claude 3.5 Sonnet 的性能评测",
        "Gemini Pro 1.5 的技术细节",
    ]
    
    for topic in new_topics:
        print(f"\n查询: {topic}")
        print("-" * 70)
        
        result = agent.query(
            topic,
            enable_web_search=True,
            verbose=False
        )
        
        print(f"找到 {result['metadata']['num_web_sources']} 个网络资源")
        
        if result['web_sources']:
            print(f"最相关: {result['web_sources'][0]['title']}")


def main():
    """主函数"""
    print("=" * 70)
    print("联网搜索功能演示")
    print("=" * 70)
    
    print("\n提示: 确保 .env 文件中设置了 ENABLE_WEB_SEARCH=true")
    
    examples = {
        '1': ('RAG 模式 + 联网搜索', example_1_rag_with_web_search),
        '2': ('对比启用/禁用联网', example_2_compare_with_without_web),
        '3': ('查询新话题', example_3_web_search_for_new_topics),
    }
    
    print("\n请选择要运行的示例:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. 运行所有示例")
    
    choice = input("\n请输入选项 (默认: 1): ").strip() or '1'
    
    try:
        if choice == '0':
            for key, (name, func) in examples.items():
                func()
        elif choice in examples:
            _, func = examples[choice]
            func()
        else:
            print(f"无效选项: {choice}")
    except Exception as e:
        print(f"\n执行出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
