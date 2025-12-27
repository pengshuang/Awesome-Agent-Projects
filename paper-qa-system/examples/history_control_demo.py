"""
多轮对话历史控制示例

演示如何控制多轮对话的历史轮数限制
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent import AcademicAgent

def demo_basic_history_control():
    """基础历史控制示例"""
    print("=" * 60)
    print("示例 1: 初始化时设置历史轮数")
    print("=" * 60)
    
    # 方式1: 初始化时指定（推荐）
    agent = AcademicAgent(
        auto_load=False,
        max_history_turns=5  # 只保留最近5轮对话
    )
    
    print(f"✓ 历史轮数限制: {agent.max_history_turns} 轮")
    print(f"✓ 对应消息数: {agent.max_history_turns * 2} 条（用户+助手）")
    print()


def demo_dynamic_history_control():
    """动态修改历史控制示例"""
    print("=" * 60)
    print("示例 2: 运行时动态修改历史轮数")
    print("=" * 60)
    
    # 创建 agent，默认10轮
    agent = AcademicAgent(auto_load=False)
    print(f"初始限制: {agent.max_history_turns} 轮\n")
    
    # 模拟对话
    for i in range(8):
        agent._update_chat_history(
            f"问题 {i+1}",
            f"回答 {i+1}"
        )
    
    info = agent.get_chat_history_info()
    print(f"当前对话: {info['current_turns']} 轮 / {info['max_turns']} 轮")
    print(f"是否已满: {'是' if info['is_full'] else '否'}\n")
    
    # 动态修改为只保留3轮
    print("📝 将历史限制改为 3 轮...")
    agent.set_max_history_turns(3)
    
    info = agent.get_chat_history_info()
    print(f"修改后对话: {info['current_turns']} 轮 / {info['max_turns']} 轮")
    print(f"历史已自动裁剪: 8轮 -> {info['current_turns']}轮\n")


def demo_large_history():
    """大历史轮数示例"""
    print("=" * 60)
    print("示例 3: 设置大历史轮数（适合长对话）")
    print("=" * 60)
    
    # 对于需要长期记忆的场景
    agent = AcademicAgent(
        auto_load=False,
        max_history_turns=50  # 保留最近50轮
    )
    
    print(f"✓ 大历史模式: {agent.max_history_turns} 轮")
    print(f"✓ 适用场景: 深度讨论、多文档对比分析、连续推理")
    print(f"✓ 注意: 历史越长，Token消耗越多\n")


def demo_minimal_history():
    """最小历史示例"""
    print("=" * 60)
    print("示例 4: 最小历史轮数（节省Token）")
    print("=" * 60)
    
    # 对于简单问答，只需要很少历史
    agent = AcademicAgent(
        auto_load=False,
        max_history_turns=1  # 只保留上一轮
    )
    
    print(f"✓ 最小历史模式: {agent.max_history_turns} 轮")
    print(f"✓ 适用场景: 独立问答、节省成本、快速响应")
    print(f"✓ 优点: Token消耗最少\n")


def demo_history_info():
    """查看历史信息示例"""
    print("=" * 60)
    print("示例 5: 查看历史状态信息")
    print("=" * 60)
    
    agent = AcademicAgent(auto_load=False, max_history_turns=5)
    
    # 模拟3轮对话
    for i in range(3):
        agent._update_chat_history(f"问题 {i+1}", f"回答 {i+1}")
    
    info = agent.get_chat_history_info()
    
    print(f"📊 历史状态:")
    print(f"   - 当前轮数: {info['current_turns']}")
    print(f"   - 最大限制: {info['max_turns']}")
    print(f"   - 总消息数: {info['total_messages']}")
    print(f"   - 是否已满: {info['is_full']}")
    print(f"   - 剩余空间: {info['max_turns'] - info['current_turns']} 轮\n")


def demo_real_usage():
    """实际使用场景示例"""
    print("=" * 60)
    print("示例 6: 实际使用场景")
    print("=" * 60)
    
    # 场景1: 快速问答系统
    print("\n📱 场景1: 快速问答（Token敏感）")
    quick_agent = AcademicAgent(auto_load=False, max_history_turns=2)
    print(f"   配置: {quick_agent.max_history_turns} 轮历史")
    
    # 场景2: 学术讨论系统
    print("\n📚 场景2: 深度学术讨论")
    academic_agent = AcademicAgent(auto_load=False, max_history_turns=20)
    print(f"   配置: {academic_agent.max_history_turns} 轮历史")
    
    # 场景3: 文档分析助手
    print("\n📄 场景3: 多文档对比分析")
    analysis_agent = AcademicAgent(auto_load=False, max_history_turns=30)
    print(f"   配置: {analysis_agent.max_history_turns} 轮历史")
    
    # 场景4: 动态调整
    print("\n⚙️  场景4: 根据用户等级动态调整")
    
    def create_agent_for_user(user_level: str):
        """根据用户等级创建不同配置的agent"""
        config = {
            "free": 5,      # 免费用户：5轮
            "basic": 15,    # 基础用户：15轮
            "premium": 50   # 高级用户：50轮
        }
        return AcademicAgent(
            auto_load=False,
            max_history_turns=config.get(user_level, 10)
        )
    
    for level in ["free", "basic", "premium"]:
        agent = create_agent_for_user(level)
        print(f"   {level.upper()} 用户: {agent.max_history_turns} 轮")


def demo_best_practices():
    """最佳实践建议"""
    print("\n" + "=" * 60)
    print("💡 最佳实践建议")
    print("=" * 60)
    
    practices = [
        ("一般问答", "5-10轮", "平衡性能和体验"),
        ("深度讨论", "20-30轮", "保留足够上下文"),
        ("长期对话", "50+轮", "完整记忆，Token消耗大"),
        ("快速响应", "1-3轮", "最小延迟和成本"),
    ]
    
    for scenario, turns, reason in practices:
        print(f"\n📌 {scenario}:")
        print(f"   推荐: {turns}")
        print(f"   原因: {reason}")


if __name__ == "__main__":
    print("\n🚀 多轮对话历史控制示例\n")
    
    # 运行所有示例
    demo_basic_history_control()
    demo_dynamic_history_control()
    demo_large_history()
    demo_minimal_history()
    demo_history_info()
    demo_real_usage()
    demo_best_practices()
    
    print("\n" + "=" * 60)
    print("✅ 所有示例完成")
    print("=" * 60)
