"""
快速入门示例
演示如何使用核心功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from init_system import initialize_system
from src import ResumeLoader, ResumeEvaluator, InterviewAgent

# 初始化系统
initialize_system()


def example_resume_loading():
    """示例 1: 简历加载"""
    print("\n" + "=" * 70)
    print("示例 1: 简历加载")
    print("=" * 70)
    
    loader = ResumeLoader()
    
    # 加载简历（请替换为你的简历文件路径）
    resume_path = "data/resumes/sample.pdf"
    
    if not Path(resume_path).exists():
        print(f"⚠️ 简历文件不存在: {resume_path}")
        print("请上传一份 PDF 格式的简历到 data/resumes/ 目录")
        return None
    
    result = loader.load_resume(resume_path)
    
    print(f"\n✅ 简历加载成功！")
    print(f"文件名: {result['metadata']['file_name']}")
    print(f"内容长度: {result['metadata']['content_length']} 字符")
    print(f"\n内容预览:\n{result['content'][:200]}...\n")
    
    return result["content"]


def example_resume_evaluation(resume_content: str):
    """示例 2: 简历评估"""
    print("\n" + "=" * 70)
    print("示例 2: 简历评估")
    print("=" * 70)
    
    evaluator = ResumeEvaluator()
    
    # 快速评分
    print("\n执行快速评分...")
    score_result = evaluator.quick_score(resume_content)
    print(f"\n{score_result['score_text']}\n")
    
    # 完整评估（可选，需要较长时间）
    # print("\n执行完整评估...")
    # eval_result = evaluator.evaluate(
    #     resume_content=resume_content,
    #     position="Python 开发工程师",
    # )
    # print(f"\n{eval_result['evaluation']}\n")


def example_interview(resume_content: str):
    """示例 3: 模拟面试"""
    print("\n" + "=" * 70)
    print("示例 3: 模拟面试")
    print("=" * 70)
    
    # 创建面试 Agent
    agent = InterviewAgent(
        resume_content=resume_content,
        interview_type="technical",
        enable_web_search=False,  # 示例中关闭联网搜索
    )
    
    # 开始面试
    print("\n🎬 开始面试...")
    opening = agent.start_interview()
    print(f"\n面试官: {opening['opening']}\n")
    
    # 模拟回答
    user_answer = "我有3年的Python开发经验，主要使用Django框架开发Web应用..."
    print(f"候选人: {user_answer}\n")
    
    # 面试官回复
    print("面试官正在思考...")
    response = agent.chat(user_answer)
    print(f"\n面试官: {response['response']}\n")
    
    # 查看面试总结
    summary = agent.get_interview_summary()
    print(f"\n面试总结:")
    print(f"- 面试类型: {summary['interview_type']}")
    print(f"- 对话轮数: {summary['total_turns']}")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("AI 模拟面试系统 - 快速入门示例")
    print("=" * 70)
    
    # 1. 加载简历
    resume_content = example_resume_loading()
    
    if not resume_content:
        print("\n⚠️ 请先准备一份简历文件")
        print("将 PDF 格式的简历放到 data/resumes/ 目录")
        print("然后重新运行此脚本")
        return
    
    # 2. 评估简历
    example_resume_evaluation(resume_content)
    
    # 3. 模拟面试
    example_interview(resume_content)
    
    print("\n" + "=" * 70)
    print("示例运行完成！")
    print("=" * 70)
    print("\n💡 提示:")
    print("- 运行 python3 web_ui.py 启动完整的 Web 界面")
    print("- 查看 docs/USER_GUIDE.md 了解详细使用方法")
    print("- 查看 docs/DEVELOPER_GUIDE.md 了解开发指南")


if __name__ == "__main__":
    main()
