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
from config import get_config

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


def upload_resume(file) -> str:
    """
    上传并解析简历
    
    Args:
        file: Gradio 文件对象
        
    Returns:
        状态信息（Markdown 格式）
    """
    global current_resume_content, current_resume_metadata, resume_loader
    
    if not file:
        return "⚠️ 请上传简历文件"
    
    try:
        logger.info(f"开始加载简历: {file.name}")
        
        # 加载简历
        result = resume_loader.load_resume(file.name)
        current_resume_content = result.content
        current_resume_metadata = result.metadata
        
        # 生成状态信息（Markdown 格式）
        status = f"""## ✅ 简历加载成功！

| 项目 | 信息 |
|------|------|
| 📄 文件名 | {current_resume_metadata.file_name} |
| 📏 文件大小 | {current_resume_metadata.file_size / 1024:.2f} KB |
| 📝 内容长度 | {current_resume_metadata.content_length} 字符 |
| ⏱️ 加载耗时 | {current_resume_metadata.load_time:.2f}秒 |
"""
        
        logger.info("简历加载成功")
        return status
    
    except Exception as e:
        logger.error(f"简历加载失败: {e}")
        return f"## ❌ 加载失败\n\n```\n{str(e)}\n```"


def use_sample_resume() -> str:
    """使用内置示例简历，方便用户无需上传即可体验功能"""
    global current_resume_content, current_resume_metadata

    # 简单的示例简历文本（可按需替换为更详细示例）
    sample = (
        "姓名：张三\n"
        "求职意向：Python 后端工程师\n"
        "教育背景：某大学，计算机科学，2016-2020\n"
        "工作经历：\n"
        "- 公司A（2020-2022）：负责后端服务开发，使用 Flask 与 MySQL；\n"
        "- 公司B（2022-至今）：参与微服务架构设计，使用 FastAPI 与 Redis、Kafka；\n"
        "项目经验：\n"
        "- 项目X：实现高并发接口，QPS 提升 3 倍；\n"
        "- 项目Y：构建数据同步服务，降低延迟 40%。\n"
        "技能：Python, FastAPI, Flask, SQL, Redis, Docker, K8s\n"
        "自我评价：具备扎实后端开发能力，擅长性能优化与系统设计。"
    )

    # 填充元数据（模拟 ResumeMetadata）
    current_resume_content = sample
    current_resume_metadata = {
        "file_name": "sample_resume.txt",
        "file_path": "<内置示例>",
        "file_size": len(sample.encode("utf-8")),
        "content_length": len(sample),
        "load_time": 0.0,
    }

    # 返回与 upload_resume 相同格式的状态 Markdown
    status = f"""## ✅ 示例简历已加载！

| 项目 | 信息 |
|------|------|
| 📄 文件名 | {current_resume_metadata['file_name']} |
| 📏 文件大小 | {current_resume_metadata['file_size'] / 1024:.2f} KB |
| 📝 内容长度 | {current_resume_metadata['content_length']} 字符 |
| ⏱️ 加载耗时 | {current_resume_metadata['load_time']:.2f}秒 |
"""

    logger.info("示例简历已加载到内存")
    return status


def evaluate_resume(position: str, requirements: str, progress=gr.Progress()) -> str:
    """
    评估简历
    
    Args:
        position: 目标岗位
        requirements: 岗位要求
        progress: 进度条对象
        
    Returns:
        评估结果
    """
    global current_resume_content, resume_evaluator
    
    if not current_resume_content:
        return "❌ 请先上传简历"
    
    try:
        progress(0, desc="正在准备评估...")
        logger.info("开始评估简历...")
        
        progress(0.3, desc="正在分析简历内容...")
        
        # 执行评估
        progress(0.5, desc="正在调用 AI 模型评估...")
        result = resume_evaluator.evaluate(
            resume_content=current_resume_content,
            position=position if position else None,
            requirements=requirements if requirements else None,
        )
        
        progress(0.9, desc="正在生成评估报告...")
        
        # 格式化输出（Markdown 格式）
        output = f"""# 📊 简历评估报告

{result['evaluation']}

---

⏱️ **评估耗时**: {result['metadata']['elapsed_time']:.2f}秒 | 🤖 **模型**: {result['metadata']['model']}
"""
        
        logger.info("简历评估完成")
        return output
    
    except Exception as e:
        logger.error(f"简历评估失败: {e}")
        return f"## ❌ 评估失败\n\n```\n{str(e)}\n```"


def quick_score_resume(progress=gr.Progress()) -> str:
    """快速评分"""
    global current_resume_content, resume_evaluator
    
    if not current_resume_content:
        return "❌ 请先上传简历"
    
    try:
        progress(0, desc="正在准备快速评分...")
        logger.info("开始快速评分...")
        
        progress(0.4, desc="正在调用 AI 模型评分...")
        result = resume_evaluator.quick_score(current_resume_content)
        
        progress(0.9, desc="正在生成评分结果...")
        
        output = f"""# ⚡ 快速评分

{result['score_text']}

---

⏱️ **耗时**: {result['metadata']['elapsed_time']:.2f}秒 | 🤖 **模型**: {result['metadata']['model']}
"""
        
        return output
    
    except Exception as e:
        logger.error(f"快速评分失败: {e}")
        return f"## ❌ 评分失败\n\n```\n{str(e)}\n```"


def get_improvement_suggestions(progress=gr.Progress()) -> str:
    """获取改进建议"""
    global current_resume_content, resume_evaluator
    
    if not current_resume_content:
        return "❌ 请先上传简历"
    
    try:
        progress(0, desc="正在准备生成建议...")
        logger.info("生成改进建议...")
        
        progress(0.4, desc="正在分析简历并调用 AI...")
        result = resume_evaluator.suggest_improvements(current_resume_content)
        
        progress(0.9, desc="正在整理改进建议...")
        
        output = f"""# 💡 简历改进建议

{result['suggestions']}

---

⏱️ **耗时**: {result['metadata']['elapsed_time']:.2f}秒 | 🤖 **模型**: {result['metadata']['model']}
"""
        
        return output
    
    except Exception as e:
        logger.error(f"生成建议失败: {e}")
        return f"## ❌ 生成失败\n\n```\n{str(e)}\n```"


def analyze_job_position(job_input: str, question_count: int) -> str:
    """岗位解读与面试问题生成
    
    Args:
        job_input: 岗位JD链接或手动输入的岗位要求
        question_count: 生成的问题数量
        
    Returns:
        分析结果和面试问题列表
    """
    global current_resume_content
    
    if not current_resume_content:
        return "❌ 请先上传简历"
    
    if not job_input or not job_input.strip():
        return "❌ 请输入岗位链接或岗位要求"
    
    try:
        logger.info(f"开始岗位解读，生成 {question_count} 个面试问题...")
        
        start_time = time.time()
        
        # 判断是链接还是文本
        job_requirements = job_input.strip()
        if job_input.startswith(('http://', 'https://')):
            # TODO: 未来可以添加网页爬取功能
            # 目前先提示用户手动复制JD内容
            return """# ⚠️ 链接解析功能开发中

目前暂不支持直接解析招聘链接，请手动复制岗位JD内容并粘贴到输入框中。

## 操作步骤

1. 打开招聘链接
2. 复制岗位描述（JD）的完整内容
3. 粘贴到下方的"岗位要求"输入框
4. 点击"生成面试问题"按钮
"""
        
        # 获取配置和 LLM 客户端
        from config import get_llm_client
        from config.settings import get_config
        from config.prompts import PromptTemplates
        
        config = get_config()
        client, model, temperature = get_llm_client(
            api_key=config.llm_api_key,
            api_base=config.llm_api_base,
            model=config.llm_model,
            temperature=config.llm_temperature
        )
        
        # 构建提示词
        prompt = PromptTemplates.JOB_ANALYSIS.format(
            job_requirements=job_requirements,
            resume_content=current_resume_content,
            question_count=question_count,
        )
        
        # 打印Prompt日志
        logger.info(f"[LLM API] 岗位解读 - Prompt:\n{'-'*60}\n{prompt}\n{'-'*60}")
        
        # 调用 LLM
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        
        result = response.choices[0].message.content
        elapsed_time = time.time() - start_time
        
        # 格式化输出
        output = f"""{result}

---

⏱️ **分析耗时**: {elapsed_time:.2f}秒 | 🤖 **模型**: {model}
"""
        
        logger.info(f"岗位解读完成，生成了 {question_count} 个问题")
        return output
    
    except Exception as e:
        logger.error(f"岗位解读失败: {e}")
        return f"## ❌ 分析失败\n\n```\n{str(e)}\n```"


def start_interview(interview_type: str, enable_web: bool) -> List:
    """
    开始面试
    
    Args:
        interview_type: 面试类型
        enable_web: 是否启用联网搜索
        
    Returns:
        初始化的聊天历史
    """
    global current_resume_content, interview_agent
    
    if not current_resume_content:
        return [{"role": "assistant", "content": "❌ 请先上传简历"}]
    
    try:
        logger.info(f"开始面试 | 类型: {interview_type}")
        
        # 获取配置
        config = get_config()
        
        # 创建面试 Agent
        interview_agent = InterviewAgent(
            resume_content=current_resume_content,
            interview_type=interview_type,
            max_history_turns=config.max_history_turns,
            enable_web_search=enable_web,
        )
        
        # 生成开场白
        result = interview_agent.start_interview()
        opening = result["opening"]
        
        # 初始化聊天历史 - 使用 tuple 格式 (None, bot_message)
        chat_history = [
            (None, opening)
        ]
        
        logger.info("面试已开始")
        return chat_history
    
    except Exception as e:
        logger.error(f"开始面试失败: {e}")
        return [(None, f"❌ 开始失败: {str(e)}")]


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
        history_copy = history.copy() if history else []
        history_copy.append((message, "❌ 请先点击'开始面试'按钮"))
        return "", history_copy
    
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
        
        # 更新历史 - 使用 tuple 格式 (user_msg, bot_msg)
        updated_history = history.copy() if history else []
        updated_history.append((message, full_response))
        
        return "", updated_history
    
    except Exception as e:
        logger.error(f"对话失败: {e}")
        updated_history = history.copy() if history else []
        updated_history.append((message, f"❌ 回复失败: {str(e)}"))
        return "", updated_history


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
        
        output = f"""# 📊 面试总结

| 项目 | 信息 |
|------|------|
| 📋 面试类型 | {summary['interview_type']} |
| 🔢 对话轮数 | {summary['total_turns']} 轮 |
| 📝 消息数量 | {summary['history_length']} 条 |
| 📄 简历状态 | {'✅ 已加载' if summary['has_resume'] else '❌ 未加载'} |
| 🌐 联网搜索 | {'✅ 已启用' if summary['web_search_enabled'] else '❌ 未启用'} |
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
    
    # 自定义 CSS 样式
    custom_css = """
    /* 全局主题配色 */
    .gradio-container {
        font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
    }
    
    /* 主标题样式（浅色柔和） */
    .main-header {
        background: linear-gradient(135deg, #ede9ff 0%, #f3e8ff 100%);
        padding: 1.6rem;
        border-radius: 12px;
        color: #222233;
        text-align: center;
        box-shadow: 0 6px 18px rgba(30, 30, 60, 0.06);
        margin-bottom: 1.6rem;
        border: 1px solid rgba(99, 102, 241, 0.08);
    }
    
    /* 按钮美化 */
    button[variant="primary"] {
        background: linear-gradient(135deg, #f3e8ff 0%, #e9d8fd 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.12) !important;
        color: #2b2b39 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.18s ease !important;
        box-shadow: 0 3px 8px rgba(30, 41, 59, 0.06) !important;
    }
    
    button[variant="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 14px rgba(30, 41, 59, 0.08) !important;
    }
    
    /* 输入框美化 */
    textarea, input[type="text"] {
        border-radius: 8px !important;
        border: 2px solid #e0e7ff !important;
        transition: all 0.3s ease !important;
    }
    
    textarea:focus, input[type="text"]:focus {
        border-color: rgba(99, 102, 241, 0.34) !important;
        box-shadow: 0 0 0 6px rgba(99, 102, 241, 0.06) !important;
    }
    
    /* 功能卡片 */
    .feature-card {
        background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(30, 41, 59, 0.06);
    }
    
    /* 聊天机器人样式 */
    .chatbot {
        border-radius: 12px !important;
        box-shadow: 0 3px 12px rgba(20,24,28,0.06) !important;
        background: linear-gradient(180deg, #ffffff 0%, #fbfbfe 100%) !important;
        border: 1px solid rgba(15, 23, 42, 0.04) !important;
    }
    """
    
    # 禁用 API 路由，避免与 Pydantic 模型冲突
    with gr.Blocks(
        css=custom_css,
        theme=gr.themes.Soft(
            primary_hue="purple",
            secondary_hue="blue",
            neutral_hue="slate",
        ),
        analytics_enabled=False
    ) as app:
        
        # 主标题区域
        with gr.Row():
            gr.HTML("""
            <div class="main-header">
                <h1 style="font-size: 2.5rem; margin: 0 0 1rem 0; font-weight: 700;">🎯 AI 模拟面试系统</h1>
                <p style="font-size: 1.1rem; margin: 0; opacity: 0.95;">基于大语言模型的智能面试模拟系统，助您准备面试、优化简历</p>
            </div>
            """)
        
        # 功能特点展示
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="feature-card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📄</div>
                    <h3 style="margin: 0.5rem 0; color: #667eea;">简历解析</h3>
                    <p style="margin: 0; color: #64748b; font-size: 0.9rem;">支持PDF格式智能解析</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="feature-card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</div>
                    <h3 style="margin: 0.5rem 0; color: #764ba2;">智能评估</h3>
                    <p style="margin: 0; color: #64748b; font-size: 0.9rem;">多维度评估与打分</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="feature-card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">💬</div>
                    <h3 style="margin: 0.5rem 0; color: #667eea;">模拟面试</h3>
                    <p style="margin: 0; color: #64748b; font-size: 0.9rem;">多轮对话真实场景</p>
                </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="feature-card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌐</div>
                    <h3 style="margin: 0.5rem 0; color: #764ba2;">联网搜索</h3>
                    <p style="margin: 0; color: #64748b; font-size: 0.9rem;">实时验证答案准确性</p>
                </div>
                """)
        
        gr.Markdown("""
        ---
        ### 💡 使用指南
        
        **第一步**：在「📄 简历管理」上传您的简历 → **第二步**：在「🔍 简历评估」获取专业评估 → **第三步**：在「💼 模拟面试」开始面试练习
        """)
        
        # ====================================================================
        # Tab 1: 简历管理
        # ====================================================================
        with gr.Tab("📄 简历管理"):
            gr.HTML("""
            <div style="padding: 1rem; background: linear-gradient(135deg, #e0e7ff 0%, #f3e7ff 100%); border-radius: 10px; margin-bottom: 1rem;">
                <h2 style="margin: 0; color: #5b21b6;">📤 上传简历文档</h2>
                <p style="margin: 0.5rem 0 0 0; color: #7c3aed;">支持 PDF 格式，系统将自动解析简历内容</p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    resume_file = gr.File(
                        label="选择简历文件",
                        file_types=[".pdf"],
                    )
                    upload_btn = gr.Button(
                        "📤 开始加载简历",
                        variant="primary",
                        size="lg"
                    )
                    sample_btn = gr.Button(
                        "📄 使用示例简历",
                        variant="secondary",
                        size="md"
                    )
                
                with gr.Column(scale=2):
                    resume_status = gr.Markdown(
                        value="💭 **等待上传**：请选择您的简历文件并点击加载按钮"
                    )
            
            # 绑定示例按钮事件（无需上传即可体验）
            sample_btn.click(
                fn=use_sample_resume,
                inputs=[],
                outputs=[resume_status],
            )
            
            # 绑定事件
            upload_btn.click(
                fn=upload_resume,
                inputs=[resume_file],
                outputs=[resume_status],
            )
        
        # ====================================================================
        # Tab 2: 简历评估
        # ====================================================================
        with gr.Tab("🔍 简历评估"):
            gr.HTML("""
            <div style="padding: 1rem; background: linear-gradient(135deg, #dbeafe 0%, #e0f2fe 100%); border-radius: 10px; margin-bottom: 1rem;">
                <h2 style="margin: 0; color: #0369a1;">📊 专业简历评估</h2>
                <p style="margin: 0.5rem 0 0 0; color: #0284c7;">AI 分析简历质量，提供多维度评分和改进建议</p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column():
                    position_input = gr.Textbox(
                        label="🎯 目标岗位（可选）",
                        placeholder="例如：高级Python开发工程师、全栈工程师...",
                        info="填写目标岗位可获得更精准的评估"
                    )
                    requirements_input = gr.Textbox(
                        label="📋 岗位要求（可选）",
                        placeholder="例如：3年以上Python开发经验，熟悉Django/Flask框架，有大型项目经验...",
                        lines=3,
                        info="详细描述岗位要求，评估结果将更有针对性"
                    )
                    
                    with gr.Row():
                        evaluate_btn = gr.Button(
                            "📊 完整评估分析",
                            variant="primary",
                            size="lg"
                        )
                        quick_score_btn = gr.Button(
                            "⚡ 快速评分",
                            variant="secondary",
                            size="lg"
                        )
                        suggestions_btn = gr.Button(
                            "💡 改进建议",
                            variant="secondary",
                            size="lg"
                        )
            
            evaluation_output = gr.Markdown(
                value="📝 **准备就绪**：上传简历后即可开始评估分析"
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
        # Tab 3: 岗位解读
        # ====================================================================
        with gr.Tab("🎯 岗位解读"):
            gr.HTML("""
            <div style="padding: 1rem; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 10px; margin-bottom: 1rem;">
                <h2 style="margin: 0; color: #92400e;">🎯 智能岗位分析</h2>
                <p style="margin: 0.5rem 0 0 0; color: #b45309;">基于岗位JD和简历，自动生成针对性面试问题</p>
            </div>
            """)
            
            gr.Markdown("""
            <div style="background: #fffbeb; padding: 1rem; border-radius: 8px; border-left: 4px solid #f59e0b;">
            
            ### 📖 使用步骤
            
            1. **📋 粘贴JD内容** - 复制招聘岗位的完整职位描述
            2. **🔢 选择问题数量** - 根据需要选择生成5-20个问题
            3. **🚀 一键生成** - 点击按钮开始智能分析
            4. **📊 查看结果** - 获得岗位分析和面试问题列表
            
            </div>
            """)
            
            with gr.Row():
                with gr.Column():
                    job_input = gr.Textbox(
                        label="📄 岗位描述 (Job Description)",
                        placeholder="请粘贴完整的岗位JD内容...\n\n包括：\n• 岗位职责\n• 任职要求\n• 技能要求\n• 福利待遇等",
                        lines=10,
                        info="JD内容越详细，生成的问题越精准"
                    )
                    
                    question_count_slider = gr.Slider(
                        label="🔢 生成问题数量",
                        minimum=5,
                        maximum=20,
                        value=10,
                        step=1,
                        info="建议选择10-15个问题，覆盖技术和行为面试",
                    )
                    
                    analyze_btn = gr.Button(
                        "🔍 生成面试问题",
                        variant="primary",
                        size="lg"
                    )
            
            job_analysis_output = gr.Markdown(
                value="""
<div style="background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); padding: 1.5rem; border-radius: 10px; border-left: 4px solid #10b981;">

#### 💡 温馨提示

请先完成以下准备工作：

✅ **已上传简历** - 系统将基于您的背景生成问题

📋 **输入岗位JD** - 粘贴完整的职位描述内容

🎯 **选择问题数量** - 建议10-15个覆盖全面

生成的问题将综合考虑：
- 🎯 岗位核心要求匹配度
- 📚 您的技能和经验背景  
- 💼 项目经验相关性分析

</div>
                """
            )
            
            # 绑定事件
            analyze_btn.click(
                fn=analyze_job_position,
                inputs=[job_input, question_count_slider],
                outputs=[job_analysis_output],
            )
        
        # ====================================================================
        # Tab 4: 模拟面试
        # ====================================================================
        with gr.Tab("💼 模拟面试"):
            gr.HTML("""
            <div style="padding: 1rem; background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%); border-radius: 10px; margin-bottom: 1rem;">
                <h2 style="margin: 0; color: #9f1239;">💬 AI 面试官对话</h2>
                <p style="margin: 0.5rem 0 0 0; color: #be123c;">真实模拟面试场景，多轮对话练习，提升面试表现</p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                        <h3 style="margin: 0 0 0.5rem 0; color: #374151;">⚙️ 面试设置</h3>
                    </div>
                    """)
                    
                    interview_type = gr.Radio(
                        label="🎭 选择面试类型",
                        choices=[
                            ("💻 技术面试", "technical"),
                            ("🤝 行为面试", "behavioral"),
                            ("🎯 综合面试", "comprehensive"),
                        ],
                        value="technical",
                        info="不同类型侧重点不同"
                    )
                    
                    enable_web_search = gr.Checkbox(
                        label="🌐 启用联网搜索",
                        value=True,
                        info="面试官可实时搜索验证答案",
                    )
                    
                    gr.HTML("<div style='height: 1rem;'></div>")
                    
                    start_interview_btn = gr.Button(
                        "🎬 开始面试",
                        variant="primary",
                        size="lg"
                    )
                    clear_interview_btn = gr.Button(
                        "🗑️ 清空对话",
                        variant="secondary",
                        size="lg"
                    )
                    summary_btn = gr.Button(
                        "📊 查看总结",
                        variant="secondary",
                        size="lg"
                    )
                    
                    gr.HTML("<div style='height: 1rem;'></div>")
                    
                    # 面试总结输出区域
                    summary_output = gr.Markdown(
                        label="📊 面试统计",
                        value=""
                    )
                
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        label="💬 面试对话区",
                        height=500,
                        bubble_full_width=False,
                        show_label=True,
                    )
                    
                    with gr.Row():
                        user_input = gr.Textbox(
                            label="💭 输入您的回答",
                            placeholder="请认真思考后输入您的回答...",
                            scale=4,
                            show_label=False,
                            container=False,
                        )
                        submit_btn = gr.Button(
                            "📤 发送",
                            scale=1,
                            variant="primary"
                        )
            
            # 绑定事件
            start_interview_btn.click(
                fn=start_interview,
                inputs=[interview_type, enable_web_search],
                outputs=[chatbot],
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
        
        # 页脚信息
        gr.HTML("""
        <div style="margin-top: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 10px; text-align: center; border-top: 2px solid #e2e8f0;">
            <p style="margin: 0; color: #64748b; font-size: 0.9rem;">
                🎯 AI 模拟面试系统 | 
                <span style="color: #667eea;">由大语言模型驱动</span> | 
                © 2025 All Rights Reserved
            </p>
            <p style="margin: 0.5rem 0 0 0; color: #94a3b8; font-size: 0.8rem;">
                💡 提示：建议使用 Chrome、Edge 或 Safari 浏览器以获得最佳体验
            </p>
        </div>
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
    app.queue()  # 启用队列以处理并发请求
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True,
        show_api=False,  # 禁用 API 文档生成
    )


if __name__ == "__main__":
    main()
