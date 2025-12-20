"""
模拟面试系统 - Web UI
基于 Gradio 实现的 Web 界面
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Tuple
import time

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入系统初始化
from init_system import initialize_system

# 初始化系统（必须在导入其他模块之前）
initialize_system()

import gradio as gr
from loguru import logger

from src import ResumeLoader, ResumeEvaluator, InterviewAgent
from config import SystemConfig

# 全局变量
resume_loader: Optional[ResumeLoader] = None
resume_evaluator: Optional[ResumeEvaluator] = None
interview_agent: Optional[InterviewAgent] = None

# 简历相关状态
current_resume_content: Optional[str] = None
current_resume_metadata: dict = {}


def initialize_components():
    """初始化组件"""
    global resume_loader, resume_evaluator
    
    try:
        resume_loader = ResumeLoader()
        resume_evaluator = ResumeEvaluator()
        
        logger.info("所有组件初始化成功")
        return "✅ 系统初始化成功"
    except Exception as e:
        logger.error(f"组件初始化失败: {e}")
        return f"❌ 初始化失败: {str(e)}"


def upload_resume(file) -> Tuple[str, str]:
    """
    上传并解析简历
    
    Args:
        file: Gradio 文件对象
        
    Returns:
        (状态信息, 简历内容预览)
    """
    global current_resume_content, current_resume_metadata, resume_loader
    
    if not file:
        return "⚠️ 请上传简历文件", ""
    
    try:
        logger.info(f"开始加载简历: {file.name}")
        
        # 加载简历
        result = resume_loader.load_resume(file.name)
        current_resume_content = result["content"]
        current_resume_metadata = result["metadata"]
        
        # 生成状态信息
        status = f"""✅ 简历加载成功！

📄 文件名: {current_resume_metadata['file_name']}
📏 文件大小: {current_resume_metadata['file_size'] / 1024:.2f} KB
📝 内容长度: {current_resume_metadata['content_length']} 字符
⏱️  加载耗时: {current_resume_metadata['load_time']:.2f}秒
"""
        
        # 简历内容预览（前500字符）
        preview = current_resume_content[:500]
        if len(current_resume_content) > 500:
            preview += "\n\n... (后续内容已省略)"
        
        logger.info("简历加载成功")
        return status, preview
    
    except Exception as e:
        logger.error(f"简历加载失败: {e}")
        return f"❌ 加载失败: {str(e)}", ""


def evaluate_resume(position: str, requirements: str) -> str:
    """
    评估简历
    
    Args:
        position: 目标岗位
        requirements: 岗位要求
        
    Returns:
        评估结果
    """
    global current_resume_content, resume_evaluator
    
    if not current_resume_content:
        return "❌ 请先上传简历"
    
    try:
        logger.info("开始评估简历...")
        
        # 执行评估
        result = resume_evaluator.evaluate(
            resume_content=current_resume_content,
            position=position if position else None,
            requirements=requirements if requirements else None,
        )
        
        # 格式化输出
        output = f"""# 简历评估报告

{result['evaluation']}

---
⏱️ 评估耗时: {result['metadata']['elapsed_time']:.2f}秒
"""
        
        logger.info("简历评估完成")
        return output
    
    except Exception as e:
        logger.error(f"简历评估失败: {e}")
        return f"❌ 评估失败: {str(e)}"


def quick_score_resume() -> str:
    """快速评分"""
    global current_resume_content, resume_evaluator
    
    if not current_resume_content:
        return "❌ 请先上传简历"
    
    try:
        logger.info("开始快速评分...")
        result = resume_evaluator.quick_score(current_resume_content)
        
        output = f"""# 快速评分

{result['score_text']}

---
⏱️ 耗时: {result['metadata']['elapsed_time']:.2f}秒
"""
        
        return output
    
    except Exception as e:
        logger.error(f"快速评分失败: {e}")
        return f"❌ 评分失败: {str(e)}"


def get_improvement_suggestions() -> str:
    """获取改进建议"""
    global current_resume_content, resume_evaluator
    
    if not current_resume_content:
        return "❌ 请先上传简历"
    
    try:
        logger.info("生成改进建议...")
        result = resume_evaluator.suggest_improvements(current_resume_content)
        
        output = f"""# 简历改进建议

{result['suggestions']}

---
⏱️ 耗时: {result['metadata']['elapsed_time']:.2f}秒
"""
        
        return output
    
    except Exception as e:
        logger.error(f"生成建议失败: {e}")
        return f"❌ 生成失败: {str(e)}"


def start_interview(interview_type: str, enable_web: bool) -> Tuple[str, List]:
    """
    开始面试
    
    Args:
        interview_type: 面试类型
        enable_web: 是否启用联网搜索
        
    Returns:
        (开场白, 初始化的聊天历史)
    """
    global current_resume_content, interview_agent
    
    if not current_resume_content:
        return "❌ 请先上传简历", []
    
    try:
        logger.info(f"开始面试 | 类型: {interview_type}")
        
        # 创建面试 Agent
        interview_agent = InterviewAgent(
            resume_content=current_resume_content,
            interview_type=interview_type,
            max_history_turns=SystemConfig.MAX_HISTORY_TURNS,
            enable_web_search=enable_web,
        )
        
        # 生成开场白
        result = interview_agent.start_interview()
        opening = result["opening"]
        
        # 初始化聊天历史
        chat_history = [[None, opening]]
        
        logger.info("面试已开始")
        return opening, chat_history
    
    except Exception as e:
        logger.error(f"开始面试失败: {e}")
        return f"❌ 开始失败: {str(e)}", []


def chat_with_interviewer(
    message: str,
    history: List,
    enable_web: bool,
) -> Tuple[str, List]:
    """
    与面试官对话
    
    Args:
        message: 用户消息
        history: 聊天历史
        enable_web: 是否使用联网搜索
        
    Returns:
        ("", 更新后的聊天历史)
    """
    global interview_agent
    
    if not interview_agent:
        return "", history + [[message, "❌ 请先点击'开始面试'按钮"]]
    
    if not message or not message.strip():
        return "", history
    
    try:
        # 调用面试 Agent
        result = interview_agent.chat(
            user_message=message,
            use_web_search=enable_web,
        )
        
        response = result["response"]
        
        # 构建回复（添加元数据）
        metadata_info = f"\n\n---\n⏱️ {result['metadata']['elapsed_time']:.2f}秒"
        if result['metadata']['used_web_search']:
            metadata_info += f" | 🌐 已联网搜索"
        
        full_response = response + metadata_info
        
        # 更新历史
        history.append([message, full_response])
        
        return "", history
    
    except Exception as e:
        logger.error(f"对话失败: {e}")
        history.append([message, f"❌ 回复失败: {str(e)}"])
        return "", history


def clear_interview() -> Tuple[str, List]:
    """清空面试历史"""
    global interview_agent
    
    if interview_agent:
        interview_agent.clear_history()
        logger.info("面试历史已清空")
    
    return "", []


def get_interview_summary() -> str:
    """获取面试总结"""
    global interview_agent
    
    if not interview_agent:
        return "❌ 尚未开始面试"
    
    try:
        summary = interview_agent.get_interview_summary()
        
        output = f"""# 面试总结

📋 **面试类型**: {summary['interview_type']}
🔢 **对话轮数**: {summary['total_turns']} 轮
📝 **消息数量**: {summary['history_length']} 条
📄 **简历状态**: {'已加载' if summary['has_resume'] else '未加载'}
🌐 **联网搜索**: {'已启用' if summary['web_search_enabled'] else '未启用'}
"""
        
        return output
    
    except Exception as e:
        logger.error(f"获取总结失败: {e}")
        return f"❌ 获取失败: {str(e)}"


# ============================================================================
# Gradio UI 界面
# ============================================================================

def create_ui():
    """创建 Gradio UI"""
    
    with gr.Blocks(
        title="AI 模拟面试系统",
        theme=gr.themes.Soft(),
    ) as app:
        
        gr.Markdown("""
        # 🎯 AI 模拟面试系统
        
        基于大语言模型的智能面试模拟系统，帮助你准备面试、优化简历。
        
        **功能特点**：
        - 📄 支持 PDF 格式简历导入
        - 🔍 多维度简历评估与打分
        - 💬 多轮对话模拟面试
        - 🌐 支持联网搜索（验证回答、获取最新信息）
        - 🤖 支持多种 LLM API（DeepSeek、OpenAI、Qwen 等）
        """)
        
        # ====================================================================
        # Tab 1: 简历管理
        # ====================================================================
        with gr.Tab("📄 简历管理"):
            gr.Markdown("## 上传简历")
            
            with gr.Row():
                with gr.Column(scale=1):
                    resume_file = gr.File(
                        label="上传简历（PDF 格式）",
                        file_types=[".pdf"],
                    )
                    upload_btn = gr.Button("📤 加载简历", variant="primary")
                
                with gr.Column(scale=2):
                    resume_status = gr.Textbox(
                        label="状态",
                        lines=6,
                        interactive=False,
                    )
            
            resume_preview = gr.Textbox(
                label="简历内容预览",
                lines=10,
                interactive=False,
            )
            
            # 绑定事件
            upload_btn.click(
                fn=upload_resume,
                inputs=[resume_file],
                outputs=[resume_status, resume_preview],
            )
        
        # ====================================================================
        # Tab 2: 简历评估
        # ====================================================================
        with gr.Tab("🔍 简历评估"):
            gr.Markdown("## 简历评估与打分")
            
            with gr.Row():
                with gr.Column():
                    position_input = gr.Textbox(
                        label="目标岗位（可选）",
                        placeholder="例如：高级Python开发工程师",
                    )
                    requirements_input = gr.Textbox(
                        label="岗位要求（可选）",
                        placeholder="例如：3年以上Python开发经验，熟悉Django/Flask...",
                        lines=3,
                    )
                    
                    with gr.Row():
                        evaluate_btn = gr.Button("📊 完整评估", variant="primary")
                        quick_score_btn = gr.Button("⚡ 快速评分")
                        suggestions_btn = gr.Button("💡 改进建议")
            
            evaluation_output = gr.Markdown(
                label="评估结果",
            )
            
            # 绑定事件
            evaluate_btn.click(
                fn=evaluate_resume,
                inputs=[position_input, requirements_input],
                outputs=[evaluation_output],
            )
            
            quick_score_btn.click(
                fn=quick_score_resume,
                inputs=[],
                outputs=[evaluation_output],
            )
            
            suggestions_btn.click(
                fn=get_improvement_suggestions,
                inputs=[],
                outputs=[evaluation_output],
            )
        
        # ====================================================================
        # Tab 3: 模拟面试
        # ====================================================================
        with gr.Tab("💼 模拟面试"):
            gr.Markdown("## 多轮对话模拟面试")
            
            with gr.Row():
                with gr.Column(scale=1):
                    interview_type = gr.Radio(
                        label="面试类型",
                        choices=[
                            ("技术面试", "technical"),
                            ("行为面试", "behavioral"),
                            ("综合面试", "comprehensive"),
                        ],
                        value="technical",
                    )
                    
                    enable_web_search = gr.Checkbox(
                        label="启用联网搜索",
                        value=True,
                        info="面试官可以搜索最新信息来验证你的回答",
                    )
                    
                    start_interview_btn = gr.Button("🎬 开始面试", variant="primary")
                    clear_interview_btn = gr.Button("🗑️ 清空历史")
                    summary_btn = gr.Button("📊 面试总结")
                
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        label="面试对话",
                        height=500,
                    )
                    
                    with gr.Row():
                        user_input = gr.Textbox(
                            label="你的回答",
                            placeholder="请输入你的回答...",
                            scale=4,
                        )
                        submit_btn = gr.Button("发送", scale=1, variant="primary")
            
            summary_output = gr.Markdown(label="面试总结")
            
            # 绑定事件
            start_interview_btn.click(
                fn=start_interview,
                inputs=[interview_type, enable_web_search],
                outputs=[summary_output, chatbot],
            )
            
            submit_btn.click(
                fn=chat_with_interviewer,
                inputs=[user_input, chatbot, enable_web_search],
                outputs=[user_input, chatbot],
            )
            
            user_input.submit(
                fn=chat_with_interviewer,
                inputs=[user_input, chatbot, enable_web_search],
                outputs=[user_input, chatbot],
            )
            
            clear_interview_btn.click(
                fn=clear_interview,
                inputs=[],
                outputs=[user_input, chatbot],
            )
            
            summary_btn.click(
                fn=get_interview_summary,
                inputs=[],
                outputs=[summary_output],
            )
        
        # ====================================================================
        # Tab 4: 系统设置
        # ====================================================================
        with gr.Tab("⚙️ 系统设置"):
            gr.Markdown("## 系统信息")
            
            system_info = gr.Markdown(f"""
            **LLM 模型**: {SystemConfig.LLM_MODEL}
            
            **API 地址**: {SystemConfig.LLM_API_BASE}
            
            **联网搜索**: {'已启用' if SystemConfig.ENABLE_WEB_SEARCH else '未启用'}
            
            **搜索引擎**: {SystemConfig.WEB_SEARCH_ENGINE}
            
            **最大历史轮数**: {SystemConfig.MAX_HISTORY_TURNS}
            
            **日志级别**: {SystemConfig.LOG_LEVEL}
            """)
        
        # ====================================================================
        # 页脚
        # ====================================================================
        gr.Markdown("""
        ---
        💡 **使用提示**：
        1. 先在「简历管理」上传你的简历
        2. 在「简历评估」获取专业评估和改进建议
        3. 在「模拟面试」开始面试练习
        
        ⚠️ **注意事项**：
        - 请确保在 `.env` 文件中配置了 LLM API Key
        - 联网搜索功能需要稳定的网络连接
        - 面试过程中可以随时清空历史重新开始
        """)
    
    return app


def main():
    """主函数"""
    logger.info("=" * 70)
    logger.info("启动 AI 模拟面试系统 Web UI")
    logger.info("=" * 70)
    
    # 初始化组件
    init_msg = initialize_components()
    logger.info(init_msg)
    
    # 创建并启动 UI
    app = create_ui()
    
    # 启动服务器
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )


if __name__ == "__main__":
    main()
