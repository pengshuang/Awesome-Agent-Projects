"""
高级查询选项示例

演示 Agent 的高级查询选项和参数调优
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import AcademicAgent
from init_system import initialize_system


def example_1_custom_top_k():
    """示例 1: 自定义 top_k 参数"""
    print("\n" + "=" * 70)
    print("示例 1: 自定义检索文档数量 (top_k)")
    print("=" * 70 + "\n")
    
    initialize_system()
    agent = AcademicAgent()
    
    question = "这篇论文的主要创新点是什么？"
    
    # 测试不同的 top_k 值
    for top_k in [3, 5, 10]:
        print(f"\n使用 top_k={top_k} 进行查询:")
        print("-" * 70)
        
        result = agent.query(
            question,
            top_k=top_k,
            verbose=False
        )
        
        print(f"检索了 {result['metadata']['num_sources']} 个文档片段")
        print(f"回答长度: {len(result['answer'])} 字符")
        print(f"耗时: {result['metadata']['elapsed_time']:.2f} 秒")


def example_2_source_documents():
    """示例 2: 查看源文档"""
    print("\n" + "=" * 70)
    print("示例 2: 显示源文档详细信息")
    print("=" * 70 + "\n")
    
    initialize_system()
    agent = AcademicAgent()
    
    question = "论文中使用了哪些实验方法？"
    
    print(f"问题: {question}\n")
    
    result = agent.query(question, verbose=False)
    
    print(f"回答:\n{result['answer']}\n")
    
    # 显示源文档详情
    if result['source_nodes']:
        print(f"\n参考的 {len(result['source_nodes'])} 个文档片段:\n")
        
        for i, node in enumerate(result['source_nodes'], 1):
            score = node.score if hasattr(node, 'score') else 'N/A'
            file_name = node.metadata.get('file_name', 'Unknown')
            page = node.metadata.get('page_number', 'N/A')
            text_preview = node.text[:150].replace('\n', ' ') if hasattr(node, 'text') else 'N/A'
            
            print(f"[{i}] 文件: {file_name}")
            print(f"    页码: {page}")
            print(f"    相似度: {score}")
            print(f"    内容: {text_preview}...")
            print()


def example_3_query_performance():
    """示例 3: 查询性能分析"""
    print("\n" + "=" * 70)
    print("示例 3: 查询性能对比")
    print("=" * 70 + "\n")
    
    initialize_system()
    agent = AcademicAgent()
    
    questions = [
        "什么是深度学习？",
        "论文的实验结果如何？",
        "作者提出的方法有哪些优点？",
    ]
    
    print("测试多个查询的性能:\n")
    
    total_time = 0
    for i, question in enumerate(questions, 1):
        result = agent.query(question, verbose=False)
        elapsed = result['metadata']['elapsed_time']
        total_time += elapsed
        
        print(f"{i}. {question}")
        print(f"   耗时: {elapsed:.2f} 秒, 检索: {result['metadata']['num_sources']} 个片段")
    
    print(f"\n平均耗时: {total_time / len(questions):.2f} 秒")


def main():
    """主函数"""
    print("=" * 70)
    print("高级查询选项演示")
    print("=" * 70)
    
    examples = {
        '1': ('自定义 top_k', example_1_custom_top_k),
        '2': ('查看源文档', example_2_source_documents),
        '3': ('性能分析', example_3_query_performance),
    }
    
    print("\n请选择要运行的示例:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. 运行所有示例")
    
    choice = input("\n请输入选项 (默认: 1): ").strip() or '1'
    
    try:
        if choice == '0':
            for _, func in examples.values():
                func()
        elif choice in examples:
            _, func = examples[choice]
            func()
        else:
            print(f"无效选项: {choice}")
    except Exception as e:
        print(f"\n执行出错: {e}")
        print("请确保已运行 build_index.py 构建索引")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
