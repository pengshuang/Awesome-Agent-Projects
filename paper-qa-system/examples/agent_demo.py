"""
学术论文问答 Agent 使用示例

演示如何使用 AcademicAgent 进行文档索引和智能问答
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import AcademicAgent, create_agent
from init_system import initialize_system
from loguru import logger


def example_1_basic_usage():
    """示例 1: 基础使用"""
    print("\n" + "=" * 70)
    print("示例 1: 基础使用")
    print("=" * 70 + "\n")
    
    # 初始化系统（配置 LLM 和 Embedding）
    initialize_system()
    
    # 创建 Agent（自动加载或构建索引）
    agent = AcademicAgent()
    
    # 查看 Agent 信息
    print(agent)
    
    # 列出已加载的论文
    papers = agent.list_papers(detailed=True)
    
    print(f"\n总共加载了 {len(papers)} 篇论文")


def example_2_query():
    """示例 2: 执行查询"""
    print("\n" + "=" * 70)
    print("示例 2: 执行查询")
    print("=" * 70 + "\n")
    
    # 初始化系统
    initialize_system()
    
    # 创建 Agent
    agent = AcademicAgent()
    
    # 准备问题
    questions = [
        "这篇论文的主要贡献是什么？",
        "论文中提出了什么新方法？",
        "实验结果如何？",
    ]
    
    # 逐个查询
    for i, question in enumerate(questions, 1):
        print(f"\n问题 {i}: {question}")
        print("-" * 70)
        
        # 执行查询
        result = agent.query(question, verbose=True)
        
        # 显示答案
        print(f"\n回答:\n{result['answer']}\n")
        
        # 显示参考来源
        if result['source_nodes']:
            print(f"参考了 {len(result['source_nodes'])} 个文档片段")
        
        print()


def example_3_rebuild_index():
    """示例 3: 强制重建索引"""
    print("\n" + "=" * 70)
    print("示例 3: 强制重建索引")
    print("=" * 70 + "\n")
    
    # 初始化系统
    initialize_system()
    
    # 创建 Agent，但不自动加载
    agent = AcademicAgent(auto_load=False)
    
    # 强制重建索引
    print("开始重建索引...\n")
    agent.rebuild_index()
    
    print("\n索引重建完成！")


def example_4_custom_paths():
    """示例 4: 自定义路径"""
    print("\n" + "=" * 70)
    print("示例 4: 自定义路径")
    print("=" * 70 + "\n")
    
    # 初始化系统
    initialize_system()
    
    # 使用自定义路径创建 Agent
    agent = AcademicAgent(
        documents_dir="./data/documents",
        index_dir="./data/custom_index",
    )
    
    # 查看统计信息
    stats = agent.get_stats()
    print("\nAgent 统计信息:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def example_5_interactive():
    """示例 5: 交互式问答"""
    print("\n" + "=" * 70)
    print("示例 5: 交互式问答")
    print("=" * 70 + "\n")
    
    # 初始化系统
    initialize_system()
    
    # 创建 Agent
    agent = create_agent()
    
    # 列出论文
    print("\n可用的论文:")
    agent.list_papers(detailed=False)
    
    print("\n" + "=" * 70)
    print("开始交互式问答（输入 'quit' 退出）")
    print("=" * 70 + "\n")
    
    while True:
        try:
            # 获取用户输入
            question = input("\n请输入你的问题: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q', '退出']:
                print("\n再见！")
                break
            
            # 执行查询
            result = agent.query(question, verbose=False)
            
            # 显示答案
            print(f"\n回答:\n{result['answer']}\n")
            print(f"(耗时: {result['metadata']['elapsed_time']:.2f} 秒)")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            logger.error(f"查询出错: {e}")


def example_6_advanced_query():
    """示例 6: 高级查询选项"""
    print("\n" + "=" * 70)
    print("示例 6: 高级查询选项")
    print("=" * 70 + "\n")
    
    # 初始化系统
    initialize_system()
    
    # 创建 Agent
    agent = AcademicAgent()
    
    question = "论文的核心创新点是什么？"
    
    # 使用不同的 top_k 值
    for top_k in [3, 5, 10]:
        print(f"\n使用 top_k={top_k} 进行查询:")
        print("-" * 70)
        
        result = agent.query(question, top_k=top_k, verbose=False)
        
        print(f"检索了 {result['metadata']['num_sources']} 个文档片段")
        print(f"回答长度: {len(result['answer'])} 字符")
        print(f"耗时: {result['metadata']['elapsed_time']:.2f} 秒")


def main():
    """主函数"""
    print("=" * 70)
    print("学术论文问答 Agent 使用示例")
    print("=" * 70)
    
    examples = {
        '1': ('基础使用', example_1_basic_usage),
        '2': ('执行查询', example_2_query),
        '3': ('强制重建索引', example_3_rebuild_index),
        '4': ('自定义路径', example_4_custom_paths),
        '5': ('交互式问答', example_5_interactive),
        '6': ('高级查询选项', example_6_advanced_query),
    }
    
    print("\n请选择要运行的示例:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. 运行所有示例")
    
    choice = input("\n请输入选项 (默认: 1): ").strip() or '1'
    
    if choice == '0':
        # 运行所有示例
        for key, (name, func) in examples.items():
            try:
                func()
            except Exception as e:
                logger.error(f"示例 {key} 运行失败: {e}")
    elif choice in examples:
        # 运行选定的示例
        _, func = examples[choice]
        try:
            func()
        except Exception as e:
            logger.error(f"示例运行失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"无效的选项: {choice}")


if __name__ == "__main__":
    main()
