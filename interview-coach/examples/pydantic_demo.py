"""
Pydantic 数据模型使用示例
展示如何使用新的数据模型
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from pydantic import ValidationError
from src.models.resume import ResumeData, ResumeMetadata
from src.models.evaluation import EvaluationResult, ScoreDetails
from src.models.interview import (
    InterviewSession,
    InterviewMessage,
    MessageRole,
    InterviewType,
)
from config.settings import get_config


def example_resume_models():
    """示例 1: 简历数据模型"""
    print("\n" + "=" * 70)
    print("示例 1: 简历数据模型（Pydantic）")
    print("=" * 70)
    
    # 创建简历元数据
    metadata = ResumeMetadata(
        file_name="resume.pdf",
        file_path="/data/resumes/resume.pdf",
        file_size=1048576,  # 1MB
        content_length=5000,
        load_time=1.23,
    )
    
    # 访问计算属性
    print(f"\n文件大小: {metadata.file_size_mb} MB")
    
    # 创建简历数据
    resume = ResumeData(
        content="这是一份简历内容，包含个人信息、工作经历、项目经验等...",
        metadata=metadata,
    )
    
    # 访问计算属性
    print(f"字数统计: {resume.word_count}")
    print(f"内容预览: {resume.preview}")
    
    # 导出为字典
    print("\n导出为字典:")
    print(resume.model_dump())
    
    # 导出为 JSON
    print("\n导出为 JSON:")
    print(resume.model_dump_json(indent=2))
    
    # 数据验证示例
    print("\n数据验证示例:")
    try:
        bad_resume = ResumeData(
            content="",  # 空内容会触发验证错误
            metadata=metadata,
        )
    except ValidationError as e:
        print("验证失败（预期行为）:")
        for error in e.errors():
            print(f"  - {error['loc']}: {error['msg']}")


def example_evaluation_models():
    """示例 2: 评估结果模型"""
    print("\n" + "=" * 70)
    print("示例 2: 评估结果模型（Pydantic）")
    print("=" * 70)
    
    # 创建评分详情
    scores = ScoreDetails(
        basic_info=8.5,
        work_experience=7.0,
        project_quality=8.0,
        skill_match=7.5,
        education=9.0,
        overall_impression=8.0,
    )
    
    # 自动计算的属性
    print(f"\n总分: {scores.total_score}/100")
    print(f"评级: {scores.grade}")
    
    # 创建评估结果
    evaluation = EvaluationResult(
        evaluation_text="## 评估结果\n\n这是一份优秀的简历...",
        position="Python 后端工程师",
        requirements="3年以上Python开发经验",
        strengths=["技术栈匹配", "项目经验丰富", "教育背景优秀"],
        weaknesses=["缺少量化指标"],
        suggestions=["添加具体的项目数据和成果"],
        score_details=scores,
        model="gpt-3.5-turbo",
        elapsed_time=5.23,
    )
    
    # 访问摘要
    print(f"\n评估摘要: {evaluation.summary}")
    
    # 导出部分数据
    print("\n导出部分数据（排除完整文本）:")
    partial_data = evaluation.model_dump(
        exclude={"evaluation_text"}, include={"position", "summary", "score_details"}
    )
    print(partial_data)
    
    # 数据验证示例
    print("\n数据验证示例:")
    try:
        bad_scores = ScoreDetails(
            basic_info=11.0,  # 超出范围 (0-10)
            work_experience=7.0,
            project_quality=8.0,
            skill_match=7.5,
            education=9.0,
            overall_impression=8.0,
        )
    except ValidationError as e:
        print("验证失败（预期行为）:")
        for error in e.errors():
            print(f"  - {error['loc']}: {error['msg']}")


def example_interview_models():
    """示例 3: 面试会话模型"""
    print("\n" + "=" * 70)
    print("示例 3: 面试会话模型（Pydantic）")
    print("=" * 70)
    
    # 创建面试会话
    session = InterviewSession(
        interview_type=InterviewType.TECHNICAL,
        resume_content="候选人简历内容...",
        enable_web_search=True,
        max_history_turns=20,
    )
    
    # 添加消息
    session.add_message(
        role=MessageRole.ASSISTANT,
        content="您好！欢迎参加今天的技术面试。请先做个自我介绍。",
        tokens=50,
    )
    
    session.add_message(
        role=MessageRole.USER,
        content="您好！我是张三，有3年的Python开发经验...",
        tokens=30,
    )
    
    session.add_message(
        role=MessageRole.ASSISTANT,
        content="很好！请详细介绍一下您最近的项目经验。",
        tokens=25,
    )
    
    # 访问会话统计
    print(f"\n会话摘要: {session.summary}")
    print(f"总轮数: {session.total_turns}")
    print(f"时长: {session.duration_minutes} 分钟")
    print(f"总Token: {session.total_tokens}")
    print(f"是否进行中: {session.is_active}")
    
    # 获取对话历史（用于 LLM API）
    history = session.get_history(max_turns=2)
    print(f"\n最近2轮对话:")
    for msg in history:
        print(f"  {msg['role']}: {msg['content'][:50]}...")
    
    # 结束会话
    session.end_session()
    print(f"\n会话已结束")
    print(f"最终时长: {session.duration_minutes} 分钟")
    
    # 导出为 JSON
    print("\n导出为 JSON（部分）:")
    session_data = session.model_dump(
        exclude={"resume_content", "messages"},
        include={"interview_type", "summary", "total_turns", "duration_minutes"},
    )
    print(session_data)


def example_config_settings():
    """示例 4: 配置管理（Pydantic Settings）"""
    print("\n" + "=" * 70)
    print("示例 4: 配置管理（Pydantic Settings）")
    print("=" * 70)
    
    # 获取配置实例（单例）
    config = get_config()
    
    # 访问配置
    print(f"\nLLM 模型: {config.llm_model}")
    print(f"LLM Base: {config.llm_api_base}")
    print(f"温度: {config.temperature}")
    print(f"联网搜索: {'启用' if config.enable_web_search else '禁用'}")
    print(f"搜索引擎: {config.web_search_engine}")
    
    # 访问计算属性（路径）
    print(f"\n项目根目录: {config.base_dir}")
    print(f"简历目录: {config.resumes_dir}")
    print(f"日志目录: {config.logs_dir}")
    
    # 获取配置摘要
    print(f"\n{config.get_summary()}")
    
    # 导出配置（排除敏感信息）
    config_data = config.model_dump(exclude={"llm_api_key"})
    print(f"\n配置数据（排除API Key）:")
    print(config_data)


def example_json_serialization():
    """示例 5: JSON 序列化和反序列化"""
    print("\n" + "=" * 70)
    print("示例 5: JSON 序列化和反序列化")
    print("=" * 70)
    
    # 创建数据
    metadata = ResumeMetadata(
        file_name="resume.pdf",
        file_path="/data/resumes/resume.pdf",
        file_size=1048576,
        content_length=5000,
        load_time=1.23,
    )
    
    resume = ResumeData(content="简历内容...", metadata=metadata)
    
    # 导出为 JSON 字符串
    json_str = resume.model_dump_json(indent=2)
    print(f"\n导出为 JSON:")
    print(json_str)
    
    # 从 JSON 字符串加载
    loaded_resume = ResumeData.model_validate_json(json_str)
    print(f"\n从 JSON 加载成功:")
    print(f"文件名: {loaded_resume.metadata.file_name}")
    print(f"内容长度: {loaded_resume.metadata.content_length}")
    
    # 从字典加载
    data_dict = resume.model_dump()
    loaded_from_dict = ResumeData.model_validate(data_dict)
    print(f"\n从字典加载成功:")
    print(f"预览: {loaded_from_dict.preview}")


def example_schema_generation():
    """示例 6: JSON Schema 生成"""
    print("\n" + "=" * 70)
    print("示例 6: JSON Schema 生成（用于 API 文档）")
    print("=" * 70)
    
    # 生成 JSON Schema
    import json
    
    schema = InterviewSession.model_json_schema()
    print(f"\nInterviewSession JSON Schema:")
    print(json.dumps(schema, indent=2, ensure_ascii=False))


def main():
    """运行所有示例"""
    print("\n" + "=" * 70)
    print("Pydantic 数据模型使用示例")
    print("=" * 70)
    
    example_resume_models()
    example_evaluation_models()
    example_interview_models()
    
    try:
        example_config_settings()
    except Exception as e:
        print(f"\n⚠️ 配置示例跳过（需要配置 .env 文件）: {e}")
    
    example_json_serialization()
    example_schema_generation()
    
    print("\n" + "=" * 70)
    print("所有示例运行完成！")
    print("=" * 70)
    print("\n💡 提示:")
    print("  - 查看 docs/PYDANTIC_GUIDE.md 了解更多用法")
    print("  - 所有数据模型都支持自动验证和序列化")
    print("  - 使用 model_dump() 和 model_dump_json() 导出数据")
    print("  - 使用 model_validate() 和 model_validate_json() 加载数据")


if __name__ == "__main__":
    main()
