"""
快速开始示例

演示最简单的使用方式：3 步开始问答
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import create_agent
from init_system import initialize_system


def main():
    """快速开始 - 3 步上手"""
    
    print("=" * 70)
    print("学术论文问答系统 - 快速开始（3 步上手）")
    print("=" * 70 + "\n")
    
    # 步骤 1: 初始化系统
    print("步骤 1/3: 初始化系统配置...")
    initialize_system()
    print("✓ 完成\n")
    
    # 步骤 2: 创建 Agent（自动加载或构建索引）
    print("步骤 2/3: 创建 Agent（自动加载索引）...")
    try:
        agent = create_agent()
        print("✓ 完成\n")
    except ValueError as e:
        print(f"✗ 失败: {e}")
        print("\n提示: 请先将文档放入 data/documents/ 目录")
        print("      或运行 python examples/build_index.py 构建索引\n")
        return
    
    # 步骤 3: 执行查询
    print("步骤 3/3: 执行查询\n")
    print("-" * 70)
    
    # 示例问题
    questions = [
        "这篇论文的主要贡献是什么？",
        "论文中提出了什么新方法？",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n问题 {i}: {question}")
        
        try:
            result = agent.query(question, verbose=False)
            
            print(f"\n回答:\n{result['answer']}\n")
            print(f"参考来源: {result['metadata']['num_sources']} 个文档片段")
            print(f"耗时: {result['metadata']['elapsed_time']:.2f} 秒")
            print("-" * 70)
            
        except Exception as e:
            print(f"查询失败: {e}")
    
    print("\n" + "=" * 70)
    print("✓ 快速开始示例完成！")
    print("=" * 70)
    print("\n更多示例请查看:")
    print("  - agent_demo.py: Agent 完整功能演示")
    print("  - web_search_demo.py: 联网搜索功能")
    print("  - direct_llm_demo.py: 直接 LLM 对话模式\n")


if __name__ == "__main__":
    main()
