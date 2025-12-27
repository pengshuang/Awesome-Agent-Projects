#!/usr/bin/env python3
"""
多轮对话功能测试脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent import AcademicAgent
from src.utils.logger import logger


def test_chat_history():
    """测试对话历史管理"""
    print("=" * 70)
    print("测试 1: 对话历史管理")
    print("=" * 70)
    
    agent = AcademicAgent(auto_load=False)
    
    # 测试初始状态
    assert len(agent.chat_history) == 0, "初始历史应为空"
    print("✅ 初始历史为空")
    
    # 测试更新历史
    agent._update_chat_history("问题1", "回答1")
    assert len(agent.chat_history) == 2, "应有 2 条消息"
    print("✅ 历史更新正常")
    
    agent._update_chat_history("问题2", "回答2")
    assert len(agent.chat_history) == 4, "应有 4 条消息"
    print("✅ 多轮历史记录正常")
    
    # 测试获取历史
    history = agent.get_chat_history()
    assert len(history) == 4, "获取的历史长度应为 4"
    assert history[0]["role"] == "user", "第一条应是用户消息"
    assert history[1]["role"] == "assistant", "第二条应是助手消息"
    print("✅ 历史格式正确")
    
    # 测试清除历史
    agent.clear_chat_history()
    assert len(agent.chat_history) == 0, "清除后历史应为空"
    print("✅ 历史清除成功")
    
    print("\n✅ 对话历史管理测试通过！\n")


def test_max_history_limit():
    """测试历史长度限制"""
    print("=" * 70)
    print("测试 2: 历史长度限制")
    print("=" * 70)
    
    agent = AcademicAgent(auto_load=False)
    agent.set_max_history_turns(3)  # 最多保留 3 轮
    
    # 添加 5 轮对话
    for i in range(5):
        agent._update_chat_history(f"问题{i+1}", f"回答{i+1}")
    
    # 应只保留最后 3 轮（6 条消息）
    assert len(agent.chat_history) == 6, f"应只保留 6 条消息，实际: {len(agent.chat_history)}"
    assert agent.chat_history[0]["content"] == "问题3", "应保留第 3 轮开始的对话"
    print("✅ 历史长度限制正常")
    
    print("\n✅ 历史长度限制测试通过！\n")


def test_context_prompt():
    """测试上下文提示词构建"""
    print("=" * 70)
    print("测试 3: 上下文提示词构建")
    print("=" * 70)
    
    agent = AcademicAgent(auto_load=False)
    
    # 添加历史
    agent._update_chat_history("什么是机器学习？", "机器学习是人工智能的一个分支...")
    agent._update_chat_history("它有哪些应用？", "机器学习广泛应用于...")
    
    # 构建上下文提示词
    current_question = "能详细说说吗？"
    prompt = agent._build_context_prompt(current_question)
    
    # 检查提示词包含历史和当前问题
    assert "什么是机器学习" in prompt, "提示词应包含历史问题"
    assert "机器学习是人工智能" in prompt, "提示词应包含历史回答"
    assert "能详细说说吗" in prompt, "提示词应包含当前问题"
    assert "对话历史" in prompt or "历史" in prompt, "提示词应有历史标识"
    
    print("✅ 上下文提示词构建正确")
    print(f"\n生成的提示词长度: {len(prompt)} 字符")
    
    print("\n✅ 上下文提示词测试通过！\n")


def test_query_with_history():
    """测试带历史的查询（模拟）"""
    print("=" * 70)
    print("测试 4: 带历史的查询（无需索引）")
    print("=" * 70)
    
    agent = AcademicAgent(auto_load=False)
    
    # 模拟添加历史
    agent._update_chat_history("什么是深度学习？", "深度学习是机器学习的一个子领域...")
    
    # 检查历史状态
    assert len(agent.chat_history) == 2, "应有 2 条消息"
    print(f"✅ 当前历史轮数: {len(agent.chat_history) // 2}")
    
    # 测试构建带历史的提示词
    question = "它和传统方法有什么不同？"
    prompt = agent._build_context_prompt(question)
    
    assert "深度学习" in prompt, "提示词应包含历史信息"
    print("✅ 查询会使用历史上下文")
    
    print("\n✅ 带历史查询测试通过！\n")


def test_set_max_history_turns():
    """测试设置最大历史轮数"""
    print("=" * 70)
    print("测试 5: 设置最大历史轮数")
    print("=" * 70)
    
    agent = AcademicAgent(auto_load=False)
    
    # 默认值
    assert agent.max_history_turns == 10, "默认应为 10 轮"
    print(f"✅ 默认最大轮数: {agent.max_history_turns}")
    
    # 修改最大轮数
    agent.set_max_history_turns(5)
    assert agent.max_history_turns == 5, "应更新为 5 轮"
    print(f"✅ 修改后最大轮数: {agent.max_history_turns}")
    
    # 测试是否生效
    for i in range(10):
        agent._update_chat_history(f"Q{i}", f"A{i}")
    
    assert len(agent.chat_history) <= 10, "历史长度应受限制"
    print(f"✅ 实际保留消息数: {len(agent.chat_history)}")
    
    print("\n✅ 最大历史轮数设置测试通过！\n")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("开始多轮对话功能测试")
    print("=" * 70 + "\n")
    
    try:
        test_chat_history()
        test_max_history_limit()
        test_context_prompt()
        test_query_with_history()
        test_set_max_history_turns()
        
        print("=" * 70)
        print("🎉 所有测试通过！")
        print("=" * 70)
        print("\n✅ 多轮对话功能实现正确")
        print("✅ 对话历史管理正常")
        print("✅ 上下文增强有效")
        print("\n可以开始使用:")
        print("  • 命令行工具: python main_chat.py")
        print("  • Web 界面: python web_ui_chat.py")
        print()
        
        return True
    
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        logger.error("测试出错", exc_info=True)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
