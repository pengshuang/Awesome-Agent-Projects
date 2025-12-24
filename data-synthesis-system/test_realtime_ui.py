"""测试实时显示功能的简单脚本"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models import TaskType

# 测试数据
test_document = """
人工智能（Artificial Intelligence, AI）是计算机科学的一个重要分支。
自1956年达特茅斯会议首次提出"人工智能"这一概念以来，AI已经经历了多次发展浪潮。

早期的人工智能研究主要集中在符号推理和问题求解上。1950年，艾伦·图灵提出了著名的"图灵测试"。
1980年代，专家系统的兴起标志着AI进入了新阶段。

2012年，AlexNet在ImageNet竞赛中的突破性表现标志着深度学习时代的到来。
深度神经网络能够从原始数据中自动学习层次化的特征表示。
"""

def test_iteration_detail_format():
    """测试迭代详情格式化"""
    from web_ui import format_iteration_detail
    
    # 模拟一次迭代的详细数据
    test_detail = {
        "iteration": 1,
        "proposer_output": {
            "question": "为什么1950年代的早期AI研究集中在符号推理上？",
            "answer": "早期AI研究集中在符号推理是因为当时认为人类智能可以通过逻辑规则和符号操作来模拟...",
            "reasoning": "这个问题需要理解早期AI研究的背景和动机"
        },
        "solver_output": {
            "reasoning_steps": [
                "首先理解符号推理的含义",
                "分析1950年代的技术条件",
                "总结为什么选择符号推理"
            ],
            "final_answer": "早期AI研究集中在符号推理，因为..."
        },
        "validator_output": {
            "is_valid": True,
            "reasoning": "答案与参考答案语义一致，推理过程清晰",
            "feedback": None
        },
        "is_valid": True
    }
    
    # 格式化并打印
    formatted = format_iteration_detail(test_detail, 1)
    print(formatted)
    print("\n" + "="*60)
    print("✅ 格式化测试通过！")
    

def test_state_structure():
    """测试状态结构"""
    print("测试状态结构...")
    
    state = {
        "document": test_document,
        "task_type": TaskType.LOGICAL_REASONING.value,
        "max_iterations": 3,
        "current_iteration": 0,
        "history_buffer": [],
        "valid_pairs": [],
        "failed_attempts": 0,
        "is_complete": False,
        "iteration_details": [],
    }
    
    print(f"✅ 初始状态创建成功")
    print(f"   - 文档长度: {len(state['document'])} 字符")
    print(f"   - 任务类型: {state['task_type']}")
    print(f"   - 最大迭代: {state['max_iterations']}")
    print(f"   - 迭代详情列表: {state['iteration_details']}")
    

if __name__ == "__main__":
    print("="*60)
    print("测试 Web UI 实时显示功能")
    print("="*60 + "\n")
    
    test_state_structure()
    print()
    test_iteration_detail_format()
    
    print("\n" + "="*60)
    print("所有测试通过！可以启动 Web UI 查看实时效果")
    print("运行命令: python web_ui.py")
    print("="*60)
