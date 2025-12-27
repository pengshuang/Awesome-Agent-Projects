"""
直接 LLM 模式示例

演示不使用向量检索，直接与 LLM 对话
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import AcademicAgent
from init_system import initialize_system


def example_1_basic_llm():
    """示例 1: 基础 LLM 对话"""
    print("\n" + "=" * 70)
    print("示例 1: 基础 LLM 对话")
    print("=" * 70 + "\n")
    
    initialize_system()
    agent = AcademicAgent()
    
    # 直接 LLM 模式，不使用向量检索
    questions = [
        "什么是机器学习？",
        "解释一下 Transformer 架构的工作原理",
        "Python 和 Java 的主要区别是什么？",
    ]
    
    for question in questions:
        print(f"\n问题: {question}")
        print("-" * 70)
        
        result = agent.query_direct(
            question,
            enable_web_search=False  # 不使用联网搜索
        )
        
        print(f"\n回答:\n{result['answer']}\n")
        print(f"耗时: {result['metadata']['elapsed_time']:.2f} 秒")


def example_2_llm_with_web_search():
    """示例 2: LLM + 联网搜索"""
    print("\n" + "=" * 70)
    print("示例 2: LLM 模式 + 联网搜索")
    print("=" * 70 + "\n")
    
    initialize_system()
    agent = AcademicAgent()
    
    # 适合联网搜索的问题
    question = "2024年最新的 AI 模型排行榜"
    
    print(f"问题: {question}")
    print("\n正在查询（LLM + 联网搜索）...\n")
    
    result = agent.query_direct(
        question,
        enable_web_search=True  # 启用联网搜索
    )
    
    print(f"回答:\n{result['answer']}\n")
    
    if result['web_sources']:
        print(f"参考了 {len(result['web_sources'])} 个网络资源:")
        for i, source in enumerate(result['web_sources'], 1):
            print(f"  [{i}] {source['title']}")
            print(f"      {source['url']}")


def example_3_compare_rag_vs_llm():
    """示例 3: 对比 RAG 模式 vs 直接 LLM"""
    print("\n" + "=" * 70)
    print("示例 3: RAG 模式 vs 直接 LLM 模式")
    print("=" * 70 + "\n")
    
    initialize_system()
    agent = AcademicAgent()
    
    question = "深度学习的基本原理是什么？"
    
    print(f"问题: {question}\n")
    
    # RAG 模式（基于本地文档）
    print("方式 1: RAG 模式（检索本地文档）")
    print("-" * 70)
    result_rag = agent.query(question, verbose=False)
    print(f"回答: {result_rag['answer'][:150]}...")
    print(f"参考: {result_rag['metadata']['num_sources']} 个文档片段")
    print(f"耗时: {result_rag['metadata']['elapsed_time']:.2f} 秒\n")
    
    # 直接 LLM 模式
    print("方式 2: 直接 LLM 模式（使用通用知识）")
    print("-" * 70)
    result_llm = agent.query_direct(question, enable_web_search=False)
    print(f"回答: {result_llm['answer'][:150]}...")
    print(f"参考: LLM 通用知识")
    print(f"耗时: {result_llm['metadata']['elapsed_time']:.2f} 秒\n")
    
    print("分析:")
    print("  - RAG 模式: 基于本地文档，答案更专业、更贴近文档内容")
    print("  - LLM 模式: 基于通用知识，答案更广泛、更通俗易懂")


def example_4_interactive_llm():
    """示例 4: 交互式 LLM 对话"""
    print("\n" + "=" * 70)
    print("示例 4: 交互式 LLM 对话")
    print("=" * 70 + "\n")
    
    initialize_system()
    agent = AcademicAgent()
    
    print("进入交互式对话模式（直接 LLM）")
    print("输入 'quit' 或 'exit' 退出\n")
    print("-" * 70)
    
    while True:
        try:
            question = input("\n你的问题: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q', '退出']:
                print("\n再见！")
                break
            
            # 询问是否需要联网搜索
            use_web = input("是否使用联网搜索? (y/N): ").strip().lower() == 'y'
            
            result = agent.query_direct(
                question,
                enable_web_search=use_web
            )
            
            print(f"\n回答:\n{result['answer']}\n")
            
            if use_web and result['web_sources']:
                print(f"参考了 {len(result['web_sources'])} 个网络资源")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n错误: {e}")


def main():
    """主函数"""
    print("=" * 70)
    print("直接 LLM 模式演示")
    print("=" * 70)
    
    examples = {
        '1': ('基础 LLM 对话', example_1_basic_llm),
        '2': ('LLM + 联网搜索', example_2_llm_with_web_search),
        '3': ('RAG vs LLM 对比', example_3_compare_rag_vs_llm),
        '4': ('交互式对话', example_4_interactive_llm),
    }
    
    print("\n请选择要运行的示例:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. 运行所有示例（不含交互式）")
    
    choice = input("\n请输入选项 (默认: 1): ").strip() or '1'
    
    try:
        if choice == '0':
            for key in ['1', '2', '3']:  # 跳过交互式
                _, func = examples[key]
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
