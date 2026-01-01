#!/usr/bin/env python3
"""英语学习助手 Web UI

基于Gradio构建的交互式英语学习平台
"""

import sys
import gradio as gr
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import settings
from config.prompts import PROMPTS, PROMPT_TEMPLATES
from src.agent.english_agent import EnglishLearningAgent
from src.services.translation import translation_service
from src.services.writing import writing_service
from src.services.speaking import speaking_service
from src.services.multimodal import multimodal_service
from src.utils.logger import app_logger
from src.utils.storage import storage


# 全局变量
current_agent = None


def initialize_agent(user_id: str = "default", difficulty: str = "中级"):
    """初始化Agent"""
    global current_agent
    current_agent = EnglishLearningAgent(user_id=user_id, difficulty=difficulty)
    app_logger.info(f"Agent已初始化: {user_id}, 难度: {difficulty}")
    return "✅ Agent初始化成功！"


def chat_with_agent(message, history, difficulty):
    """与Agent对话"""
    global current_agent
    
    if not message.strip():
        return history, ""
    
    # 确保Agent已初始化
    if current_agent is None or current_agent.difficulty != difficulty:
        current_agent = EnglishLearningAgent(difficulty=difficulty)
    
    # 流式输出
    history.append([message, ""])
    
    try:
        for chunk in current_agent.chat(message, stream=True):
            if chunk:
                history[-1][1] += chunk
                yield history, ""
    except Exception as e:
        error_msg = f"❌ 对话失败: {str(e)}"
        app_logger.error(error_msg)
        history[-1][1] = error_msg
        yield history, ""
    
    return history, ""


def translate_text(text, task_type):
    """翻译功能"""
    if not text.strip():
        return "⚠️ 请输入要翻译的内容"
    
    try:
        result = translation_service.translate(text, task_type)
        return result
    except Exception as e:
        return f"❌ 翻译失败: {str(e)}"


def correct_writing(content, requirement):
    """批改写作"""
    if not content.strip():
        return "⚠️ 请输入要批改的作文内容"
    
    try:
        result = writing_service.correct_writing(content, requirement)
        return result
    except Exception as e:
        return f"❌ 批改失败: {str(e)}"


def polish_writing(content, style):
    """润色写作"""
    if not content.strip():
        return "⚠️ 请输入要润色的内容"
    
    try:
        result = writing_service.polish_writing(content, style)
        return result
    except Exception as e:
        return f"❌ 润色失败: {str(e)}"


def text_to_speech(text, voice, speed):
    """文本转语音"""
    if not text.strip():
        return None, "⚠️ 请输入要转换的文本"
    
    try:
        audio_data = speaking_service.text_to_speech(text, voice, speed)
        if audio_data:
            # 保存到临时文件
            audio_path = settings.DATA_DIR / "temp_audio.mp3"
            with open(audio_path, 'wb') as f:
                f.write(audio_data)
            return str(audio_path), "✅ 转换成功！"
        else:
            return None, "❌ 转换失败"
    except Exception as e:
        return None, f"❌ 转换失败: {str(e)}"


def speech_to_text(audio_file):
    """语音转文本"""
    if audio_file is None:
        return "⚠️ 请先录音"
    
    try:
        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        
        text = speaking_service.speech_to_text(audio_data, language="en")
        if text:
            return f"识别结果：\n\n{text}"
        else:
            return "❌ 识别失败，请重试"
    except Exception as e:
        return f"❌ 识别失败: {str(e)}"


def evaluate_pronunciation(audio_file, reference_text):
    """评估发音"""
    if audio_file is None:
        return "⚠️ 请先录音"
    
    if not reference_text.strip():
        return "⚠️ 请输入参考文本"
    
    try:
        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        
        result = speaking_service.evaluate_speaking(audio_data, reference_text)
        
        if result.get("success"):
            overall_score = result.get('overall_score', 0)
            
            # 根据总分确定评级和颜色
            if overall_score >= 90:
                grade = "优秀"
                grade_color = "#10b981"
                score_bg = "#d1fae5"
            elif overall_score >= 75:
                grade = "良好"
                grade_color = "#3b82f6"
                score_bg = "#dbeafe"
            elif overall_score >= 60:
                grade = "及格"
                grade_color = "#f59e0b"
                score_bg = "#fef3c7"
            else:
                grade = "需加强"
                grade_color = "#ef4444"
                score_bg = "#fee2e2"
            
            feedback = f"""
<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 12px 12px 0 0; margin: -10px -10px 0 -10px;">
        <h2 style="color: white; margin: 0; font-size: 24px;">📊 发音评估结果</h2>
    </div>
    
    <div style="background-color: #f8fafc; padding: 20px; border-radius: 0 0 12px 12px; margin: 0 -10px -10px -10px;">
        <!-- 文本对比区域 -->
        <div style="background-color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="margin-bottom: 12px;">
                <span style="color: #64748b; font-size: 14px; font-weight: 600;">识别文本：</span>
                <div style="background-color: #f1f5f9; padding: 10px; border-radius: 6px; margin-top: 5px; border-left: 4px solid #3b82f6;">
                    <span style="color: #1e293b; font-size: 15px;">{result.get('recognized_text', 'N/A')}</span>
                </div>
            </div>
            <div>
                <span style="color: #64748b; font-size: 14px; font-weight: 600;">参考文本：</span>
                <div style="background-color: #f1f5f9; padding: 10px; border-radius: 6px; margin-top: 5px; border-left: 4px solid #10b981;">
                    <span style="color: #1e293b; font-size: 15px;">{result.get('reference_text', 'N/A')}</span>
                </div>
            </div>
        </div>
        
        <!-- 总分展示区域 -->
        <div style="background: {score_bg}; padding: 20px; border-radius: 8px; margin-bottom: 15px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="font-size: 18px; color: #64748b; margin-bottom: 8px;">总体评分</div>
            <div style="font-size: 48px; font-weight: bold; color: {grade_color}; margin: 10px 0;">
                {overall_score}<span style="font-size: 24px;">/100</span>
            </div>
            <div style="font-size: 20px; color: {grade_color}; font-weight: 600;">
                {grade}
            </div>
        </div>
        
        <!-- 详细评分区域 -->
        <div style="background-color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="color: #1e293b; font-size: 18px; margin-top: 0; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">📈 详细评分</h3>
            
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                    <span style="color: #475569; font-weight: 500;">准确度</span>
                    <span style="color: #1e293b; font-weight: 600;">{result.get('accuracy_score', 0)}/100</span>
                </div>
                <div style="background-color: #e2e8f0; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #3b82f6, #2563eb); height: 100%; width: {result.get('accuracy_score', 0)}%; border-radius: 4px;"></div>
                </div>
            </div>
            
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                    <span style="color: #475569; font-weight: 500;">流利度</span>
                    <span style="color: #1e293b; font-weight: 600;">{result.get('fluency_score', 0)}/100</span>
                </div>
                <div style="background-color: #e2e8f0; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #8b5cf6, #7c3aed); height: 100%; width: {result.get('fluency_score', 0)}%; border-radius: 4px;"></div>
                </div>
            </div>
            
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                    <span style="color: #475569; font-weight: 500;">完整度</span>
                    <span style="color: #1e293b; font-weight: 600;">{result.get('completeness_score', 0)}/100</span>
                </div>
                <div style="background-color: #e2e8f0; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #10b981, #059669); height: 100%; width: {result.get('completeness_score', 0)}%; border-radius: 4px;"></div>
                </div>
            </div>
        </div>
        
        <!-- 详细反馈区域 -->
        <div style="background-color: #fffbeb; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="color: #92400e; font-size: 18px; margin-top: 0; margin-bottom: 12px;">💡 详细反馈</h3>
            <div style="color: #78350f; line-height: 1.6; white-space: pre-wrap;">
{result.get('detailed_feedback', '')}
            </div>
        </div>
    </div>
</div>
"""
            return feedback
        else:
            return f"""
<div style="background-color: #fee2e2; padding: 20px; border-radius: 8px; border-left: 4px solid #ef4444;">
    <h3 style="color: #991b1b; margin-top: 0;">❌ 评估失败</h3>
    <p style="color: #7f1d1d; margin-bottom: 0;">{result.get("message", "未知错误")}</p>
</div>
"""
    
    except Exception as e:
        return f"""
<div style="background-color: #fee2e2; padding: 20px; border-radius: 8px; border-left: 4px solid #ef4444;">
    <h3 style="color: #991b1b; margin-top: 0;">❌ 评估失败</h3>
    <p style="color: #7f1d1d; margin-bottom: 0;">{str(e)}</p>
</div>
"""


def analyze_file(file):
    """分析上传的文件"""
    if file is None:
        return "⚠️ 请先上传文件"
    
    try:
        result = multimodal_service.process_upload(file.name)
        return result
    except Exception as e:
        return f"❌ 文件分析失败: {str(e)}"


def get_agent_summary():
    """获取Agent学习总结"""
    global current_agent
    
    if current_agent is None:
        return "⚠️ 请先与Agent开始对话"
    
    try:
        summary = current_agent.generate_summary()
        return summary
    except Exception as e:
        return f"❌ 生成总结失败: {str(e)}"


def get_profile_info():
    """获取学生档案"""
    global current_agent
    
    if current_agent is None:
        return "⚠️ 请先与Agent开始对话"
    
    try:
        profile = current_agent.get_profile_summary()
        info = f"""## 📋 学生档案

- **用户ID：** {profile['用户ID']}
- **当前难度：** {profile['当前难度']}
- **练习次数：** {profile['练习次数']}
- **对话轮数：** {profile['对话轮数']}
- **薄弱项：** {', '.join(profile['薄弱项'])}
"""
        return info
    except Exception as e:
        return f"❌ 获取档案失败: {str(e)}"


def clear_chat_history():
    """清空对话历史"""
    global current_agent
    
    if current_agent:
        current_agent.clear_history()
    
    return [], "✅ 对话历史已清空"


def get_prompt_content(prompt_name):
    """获取Prompt内容"""
    if prompt_name in PROMPT_TEMPLATES:
        return PROMPT_TEMPLATES[prompt_name]
    return "未找到对应的Prompt"


def update_prompt(prompt_name, new_content):
    """更新Prompt（仅当前会话有效）"""
    if prompt_name in PROMPT_TEMPLATES:
        PROMPT_TEMPLATES[prompt_name] = new_content
        return "✅ Prompt已更新（当前会话有效）"
    return "❌ 更新失败：未找到对应的Prompt"


# 构建Gradio界面
def create_ui():
    """创建Web界面"""
    
    # 自定义CSS
    custom_css = """
    .gradio-container {
        font-family: 'Microsoft YaHei', Arial, sans-serif !important;
    }
    .main-title {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 20px;
    }
    .section-title {
        color: #34495e;
        border-bottom: 2px solid #3498db;
        padding-bottom: 5px;
        margin-top: 20px;
    }
    """
    
    with gr.Blocks(
        title="英语学习助手",
        theme=gr.themes.Soft(primary_hue="blue"),
        css=custom_css
    ) as app:
        
        # 标题
        gr.Markdown("""
        <div class="main-title">
        <h1>🎓 AI英语学习助手</h1>
        <p>基于智能Agent的个性化英语学习平台</p>
        </div>
        """)
        
        # 主要功能区域
        with gr.Tabs() as tabs:
            
            # Tab 1: AI智能对话
            with gr.Tab("💬 AI智能对话"):
                gr.Markdown("### 与AI英语导师进行智能对话练习")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        chatbot = gr.Chatbot(
                            label="对话区",
                            height=500,
                            show_label=True,
                            bubble_full_width=False
                        )
                        
                        with gr.Row():
                            msg_input = gr.Textbox(
                                label="输入消息",
                                placeholder="在这里输入你的问题或想说的话...",
                                lines=2,
                                scale=4
                            )
                            send_btn = gr.Button("发送", variant="primary", scale=1)
                        
                        with gr.Row():
                            clear_btn = gr.Button("清空历史", variant="secondary")
                            summary_btn = gr.Button("生成学习总结", variant="secondary")
                    
                    with gr.Column(scale=1):
                        difficulty_radio = gr.Radio(
                            choices=["初级", "中级", "高级"],
                            value="中级",
                            label="学习难度",
                            interactive=True
                        )
                        
                        profile_output = gr.Markdown("点击下方按钮查看学习档案")
                        profile_btn = gr.Button("查看学习档案")
                        
                        gr.Markdown("""
                        **使用提示：**
                        - 自由与AI导师对话
                        - AI会根据你的水平调整教学内容
                        - 实时纠正语法和表达错误
                        - 定期查看学习总结和薄弱项
                        """)
                
                # 事件绑定
                send_btn.click(
                    chat_with_agent,
                    inputs=[msg_input, chatbot, difficulty_radio],
                    outputs=[chatbot, msg_input]
                )
                msg_input.submit(
                    chat_with_agent,
                    inputs=[msg_input, chatbot, difficulty_radio],
                    outputs=[chatbot, msg_input]
                )
                clear_btn.click(
                    clear_chat_history,
                    outputs=[chatbot, profile_output]
                )
                summary_btn.click(
                    get_agent_summary,
                    outputs=profile_output
                )
                profile_btn.click(
                    get_profile_info,
                    outputs=profile_output
                )
            
            # Tab 2: 翻译解析
            with gr.Tab("🔤 翻译解析"):
                gr.Markdown("### 中英互译 + 详细学习解析")
                
                with gr.Row():
                    with gr.Column():
                        translation_type = gr.Radio(
                            choices=[("通用翻译", "general"), ("单词解析", "word"), ("长难句解析", "sentence")],
                            value="general",
                            label="翻译类型"
                        )
                        translation_input = gr.Textbox(
                            label="输入内容",
                            placeholder="输入要翻译的英文或中文内容...",
                            lines=8
                        )
                        translate_btn = gr.Button("开始翻译", variant="primary")
                    
                    with gr.Column():
                        translation_output = gr.Markdown(label="翻译结果")
                
                translate_btn.click(
                    translate_text,
                    inputs=[translation_input, translation_type],
                    outputs=translation_output
                )
            
            # Tab 3: 写作批改
            with gr.Tab("✍️ 写作批改"):
                gr.Markdown("### 英文写作批改与润色")
                
                with gr.Tabs():
                    with gr.Tab("批改作文"):
                        with gr.Row():
                            with gr.Column():
                                writing_input = gr.Textbox(
                                    label="作文内容",
                                    placeholder="输入你的英文作文...",
                                    lines=12
                                )
                                requirement_input = gr.Textbox(
                                    label="写作要求（可选）",
                                    placeholder="例如：议论文、邮件格式等",
                                    value="通用写作"
                                )
                                correct_btn = gr.Button("开始批改", variant="primary")
                            
                            with gr.Column():
                                correction_output = gr.Markdown(label="批改结果")
                        
                        correct_btn.click(
                            correct_writing,
                            inputs=[writing_input, requirement_input],
                            outputs=correction_output
                        )
                    
                    with gr.Tab("润色优化"):
                        with gr.Row():
                            with gr.Column():
                                polish_input = gr.Textbox(
                                    label="原文内容",
                                    placeholder="输入要润色的英文内容...",
                                    lines=12
                                )
                                style_dropdown = gr.Dropdown(
                                    choices=["日常", "学术", "商务", "创意"],
                                    value="日常",
                                    label="目标风格"
                                )
                                polish_btn = gr.Button("开始润色", variant="primary")
                            
                            with gr.Column():
                                polish_output = gr.Markdown(label="润色结果")
                        
                        polish_btn.click(
                            polish_writing,
                            inputs=[polish_input, style_dropdown],
                            outputs=polish_output
                        )
            
            # Tab 4: 口语练习
            with gr.Tab("🎤 口语练习"):
                gr.Markdown("### 语音跟读 + 发音评分")
                
                with gr.Tabs():
                    with gr.Tab("跟读练习"):
                        with gr.Row():
                            with gr.Column():
                                tts_text = gr.Textbox(
                                    label="练习文本",
                                    placeholder="输入要朗读的英文内容...",
                                    lines=4,
                                    value="Hello, I'm learning English with AI assistant."
                                )
                                
                                with gr.Row():
                                    tts_voice = gr.Dropdown(
                                        choices=[
                                            ("英文女声", "Cherry"),
                                        ],
                                        value="Cherry",
                                        label="发音类型"
                                    )
                                    tts_speed = gr.Slider(
                                        minimum=0.5,
                                        maximum=2.0,
                                        value=1.0,
                                        step=0.1,
                                        label="语速"
                                    )
                                
                                tts_btn = gr.Button("生成语音", variant="primary")
                                tts_audio = gr.Audio(label="参考发音", type="filepath")
                                tts_status = gr.Textbox(label="状态", interactive=False)
                                
                                gr.Markdown("---")
                                
                                user_audio = gr.Audio(
                                    label="你的录音",
                                    type="filepath",
                                    sources=["microphone"]
                                )
                                eval_btn = gr.Button("评估发音", variant="primary")
                            
                            with gr.Column():
                                eval_output = gr.Markdown(label="评估结果")
                        
                        tts_btn.click(
                            text_to_speech,
                            inputs=[tts_text, tts_voice, tts_speed],
                            outputs=[tts_audio, tts_status]
                        )
                        
                        eval_btn.click(
                            evaluate_pronunciation,
                            inputs=[user_audio, tts_text],
                            outputs=eval_output
                        )
                    
                    with gr.Tab("自由录音"):
                        with gr.Row():
                            with gr.Column():
                                free_audio = gr.Audio(
                                    label="录音",
                                    type="filepath",
                                    sources=["microphone"]
                                )
                                transcribe_btn = gr.Button("识别语音", variant="primary")
                            
                            with gr.Column():
                                transcribe_output = gr.Textbox(
                                    label="识别结果",
                                    lines=10,
                                    interactive=False
                                )
                        
                        transcribe_btn.click(
                            speech_to_text,
                            inputs=free_audio,
                            outputs=transcribe_output
                        )
            
            # Tab 5: 图片/PDF解析
            with gr.Tab("📄 图片/PDF解析"):
                gr.Markdown("### 上传图片或PDF，AI帮你翻译讲解")
                
                with gr.Row():
                    with gr.Column():
                        file_input = gr.File(
                            label="上传文件",
                            file_types=[".jpg", ".jpeg", ".png", ".gif", ".pdf"]
                        )
                        analyze_btn = gr.Button("开始解析", variant="primary")
                        
                        gr.Markdown("""
                        **支持格式：**
                        - 图片：JPG, PNG, GIF等
                        - 文档：PDF
                        
                        **功能：**
                        - 识别图片/PDF中的英文内容
                        - 提供中文翻译
                        - 讲解重点词汇和语法
                        - 补充文化背景知识
                        """)
                    
                    with gr.Column():
                        file_output = gr.Markdown(label="解析结果")
                
                analyze_btn.click(
                    analyze_file,
                    inputs=file_input,
                    outputs=file_output
                )
            
            # Tab 6: Prompt管理
            with gr.Tab("⚙️ Prompt管理"):
                gr.Markdown("### 查看和调整系统Prompt")
                
                prompt_names = list(PROMPT_TEMPLATES.keys())
                prompt_display_names = {
                    "agent_system": "Agent系统提示词",
                    "agent_chat": "Agent对话提示词",
                    "translation": "翻译解析提示词",
                    "word_analysis": "单词解析提示词",
                    "sentence_analysis": "长难句解析提示词",
                    "writing_correction": "写作批改提示词",
                    "writing_polish": "写作润色提示词",
                    "speaking_correction": "口语纠错提示词",
                    "speaking_practice": "口语练习提示词",
                    "vision_analysis": "图片解析提示词",
                    "pdf_analysis": "PDF解析提示词",
                    "summary": "学习总结提示词",
                    "difficulty_adjustment": "难度调整提示词",
                }
                
                with gr.Row():
                    with gr.Column(scale=1):
                        prompt_selector = gr.Dropdown(
                            choices=[(prompt_display_names.get(k, k), k) for k in prompt_names],
                            label="选择Prompt",
                            value=prompt_names[0] if prompt_names else None
                        )
                        load_prompt_btn = gr.Button("加载Prompt", variant="secondary")
                        save_prompt_btn = gr.Button("保存修改（临时）", variant="primary")
                        prompt_status = gr.Textbox(label="状态", interactive=False)
                    
                    with gr.Column(scale=3):
                        prompt_editor = gr.Textbox(
                            label="Prompt内容",
                            lines=20,
                            max_lines=30,
                            show_label=True,
                            interactive=True
                        )
                
                load_prompt_btn.click(
                    get_prompt_content,
                    inputs=prompt_selector,
                    outputs=prompt_editor
                )
                
                save_prompt_btn.click(
                    update_prompt,
                    inputs=[prompt_selector, prompt_editor],
                    outputs=prompt_status
                )
        
        # 页脚
        gr.Markdown("""
        ---
        <div style="text-align: center; color: #7f8c8d;">
        <p>💡 提示：所有功能均通过第三方LLM API实现，请确保已正确配置API密钥</p>
        <p>📝 配置文件：<code>.env</code> | 日志目录：<code>logs/</code></p>
        </div>
        """)
    
    return app


def main():
    """主函数"""
    app_logger.info("="*80)
    app_logger.info("英语学习助手启动中...")
    app_logger.info(f"版本: {settings.APP_VERSION}")
    app_logger.info(f"配置文件: {ROOT_DIR / '.env'}")
    app_logger.info("="*80)
    
    # 创建UI
    app = create_ui()
    
    # 启动服务
    app_logger.info(f"正在启动Gradio服务器...")
    app_logger.info(f"地址: http://{settings.GRADIO_SERVER_NAME}:{settings.GRADIO_SERVER_PORT}")
    
    app.launch(
        server_name=settings.GRADIO_SERVER_NAME,
        server_port=settings.GRADIO_SERVER_PORT,
        share=settings.GRADIO_SHARE,
        show_error=True,
        quiet=False
    )


if __name__ == "__main__":
    main()
