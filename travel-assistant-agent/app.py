"""
智能旅游助手Agent - 主程序
基于Gradio 4.x的生产级旅游智能助手Web应用
"""

import os
import json
import base64
import requests
from datetime import datetime
from typing import Optional, Tuple, List
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from PIL import Image

# 导入Prompt配置
from config.prompts import (
    AGENT_CORE_SYSTEM_PROMPT,
    MULTIMODAL_IMAGE_PROMPT,
    MULTIMODAL_VIDEO_PROMPT,
    VOICE_INTERACTION_PROMPT,
    REQUIREMENT_COMPLETION_PROMPT,
    ITINERARY_GENERATION_PROMPT,
    ITINERARY_ADJUSTMENT_PROMPT,
    EMERGENCY_SOLUTION_PROMPT,
    get_combined_prompt
)

# 加载环境变量
load_dotenv()

# ==================== 配置参数 ====================
API_KEY = os.getenv("API_KEY", "")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.anthropic.com")

# 文本模型和多模态模型（支持分开配置）
TEXT_MODEL_NAME = os.getenv("TEXT_MODEL_NAME", "claude-3-5-sonnet-20241022")
MULTIMODAL_MODEL_NAME = os.getenv("MULTIMODAL_MODEL_NAME", "") or TEXT_MODEL_NAME  # 如果未配置，使用文本模型

# 兼容旧配置（如果用户只配置了MODEL_NAME）
if not TEXT_MODEL_NAME or TEXT_MODEL_NAME == "claude-3-5-sonnet-20241022":
    legacy_model = os.getenv("MODEL_NAME", "")
    if legacy_model:
        TEXT_MODEL_NAME = legacy_model
        MULTIMODAL_MODEL_NAME = legacy_model

MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.85"))

# 数据存储路径
SAVE_DIR = Path("data/saved_itineraries")
SAVE_DIR.mkdir(parents=True, exist_ok=True)


# ==================== API调用封装 ====================
class TravelAssistantAPI:
    """旅游助手API调用封装类"""
    
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = API_BASE_URL
        self.text_model = TEXT_MODEL_NAME  # 文本对话模型
        self.multimodal_model = MULTIMODAL_MODEL_NAME  # 多模态模型
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    
    def call_text_api(self, user_message: str, system_prompt: str = None, 
                     temperature: float = TEMPERATURE, max_tokens: int = MAX_TOKENS) -> str:
        """
        调用文本对话API（使用文本模型）
        
        Args:
            user_message: 用户输入的消息
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
        
        Returns:
            API返回的文本内容
        """
        try:
            # 使用文本模型
            payload = {
                "model": self.text_model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.base_url}/v1/messages",
                headers=self.headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"]
            else:
                return f"❌ API调用失败（状态码: {response.status_code}）\n提示：请检查API密钥配置是否正确"
                
        except requests.exceptions.Timeout:
            return "❌ 请求超时，网络有点慢哦，请稍后重试"
        except Exception as e:
            return f"❌ 发生错误：{str(e)}\n提示：请检查网络连接和API配置"
    
    def call_multimodal_api(self, user_message: str, image_data: str, 
                           media_type: str = "image/jpeg") -> str:
        """
        调用多模态API（图片识别，使用多模态模型）
        
        Args:
            user_message: 用户消息
            image_data: Base64编码的图片数据
            media_type: 媒体类型
        
        Returns:
            API返回的识别结果
        """
        try:
            # 使用多模态模型
            payload = {
                "model": self.multimodal_model,
                "max_tokens": MAX_TOKENS,
                "temperature": TEMPERATURE,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": user_message
                            }
                        ]
                    }
                ],
                "system": MULTIMODAL_IMAGE_PROMPT
            }
            
            response = requests.post(
                f"{self.base_url}/v1/messages",
                headers=self.headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"]
            else:
                return f"❌ 图片识别失败（状态码: {response.status_code}）"
                
        except Exception as e:
            return f"❌ 图片识别出错：{str(e)}"
    
    def call_with_retry(self, func, *args, **kwargs):
        """带重试机制的API调用"""
        max_retries = 1
        for attempt in range(max_retries + 1):
            result = func(*args, **kwargs)
            if not result.startswith("❌"):
                return result
            if attempt < max_retries:
                continue
        return result


# 初始化API客户端
api_client = TravelAssistantAPI()


# ==================== 对话历史管理 ====================
class ConversationManager:
    """对话历史管理器"""
    
    def __init__(self):
        self.history = []
        self.current_scenario = None  # 当前场景类型
        self.user_requirements = {}  # 用户需求信息
    
    def add_message(self, role: str, content: str):
        """添加消息到历史"""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def get_context(self, last_n: int = 5) -> str:
        """获取最近N轮对话上下文"""
        recent = self.history[-last_n*2:] if len(self.history) > last_n*2 else self.history
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent])
        return context
    
    def clear(self):
        """清空历史"""
        self.history = []
        self.current_scenario = None
        self.user_requirements = {}
    
    def detect_scenario(self, user_input: str) -> Optional[str]:
        """检测用户需求场景"""
        scenarios = {
            "亲子游": ["亲子", "孩子", "小孩", "儿童", "宝宝", "带娃"],
            "老年游": ["老人", "父母", "长辈", "爸妈", "老年"],
            "学生穷游": ["学生", "穷游", "预算少", "省钱", "便宜"],
            "情侣游": ["情侣", "蜜月", "浪漫", "两个人"],
            "轻奢游": ["轻奢", "高端", "奢华", "五星", "品质"],
            "境外游": ["国外", "出国", "境外", "国际"]
        }
        
        for scenario, keywords in scenarios.items():
            if any(keyword in user_input for keyword in keywords):
                self.current_scenario = scenario
                return scenario
        return None


# 初始化对话管理器
conversation_mgr = ConversationManager()


# ==================== 核心功能函数 ====================
def process_text_message(user_input: str, history: List) -> Tuple[List, str]:
    """
    处理文本消息
    
    Args:
        user_input: 用户输入
        history: 对话历史
    
    Returns:
        更新后的历史记录和清空的输入框
    """
    if not user_input.strip():
        return history, ""
    
    # 检测场景
    scenario = conversation_mgr.detect_scenario(user_input)
    
    # 构建系统提示词
    system_prompt = get_combined_prompt(
        AGENT_CORE_SYSTEM_PROMPT,
        scenario=scenario,
        additional_context=conversation_mgr.get_context()
    )
    
    # 添加用户消息到历史
    conversation_mgr.add_message("user", user_input)
    history.append([user_input, None])
    
    # 调用API
    response = api_client.call_with_retry(
        api_client.call_text_api,
        user_message=user_input,
        system_prompt=system_prompt
    )
    
    # 添加助手回复到历史
    conversation_mgr.add_message("assistant", response)
    history[-1][1] = response
    
    return history, ""


def process_image_upload(image_path: str, history: List) -> List:
    """
    处理图片上传和识别
    
    Args:
        image_path: 图片路径
        history: 对话历史
    
    Returns:
        更新后的历史记录
    """
    if not image_path:
        return history
    
    try:
        # 读取并编码图片
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # 判断图片格式
        img = Image.open(image_path)
        img_format = img.format.lower()
        media_type = f"image/{img_format}" if img_format in ["jpeg", "jpg", "png", "webp"] else "image/jpeg"
        
        # 添加用户消息
        user_msg = "📷 [用户上传了一张图片，请识别图片中的旅游相关内容]"
        history.append([user_msg, "正在识别图片..."])
        
        # 调用多模态API
        response = api_client.call_multimodal_api(
            user_message="请识别这张图片中的旅游相关内容，并给出详细的攻略建议。",
            image_data=image_data,
            media_type=media_type
        )
        
        # 更新历史
        conversation_mgr.add_message("user", user_msg)
        conversation_mgr.add_message("assistant", response)
        history[-1][1] = response
        
    except Exception as e:
        error_msg = f"❌ 图片处理失败：{str(e)}"
        history[-1][1] = error_msg
    
    return history


def process_voice_input(audio_path: str, history: List) -> Tuple[List, str]:
    """
    处理语音输入（简化版，使用文本模拟）
    注：实际语音转文字需要额外的语音API，这里用文本模拟语音交互的响应格式
    
    Args:
        audio_path: 音频文件路径
        history: 对话历史
    
    Returns:
        更新后的历史记录和状态信息
    """
    if not audio_path:
        return history, "请先录制语音"
    
    # 这里简化处理，实际项目中需要调用语音转文字API
    voice_text = "用户通过语音询问：给我推荐一个适合周末两天的旅游目的地"
    
    # 使用语音交互专用Prompt
    system_prompt = get_combined_prompt(
        AGENT_CORE_SYSTEM_PROMPT,
        additional_context=VOICE_INTERACTION_PROMPT
    )
    
    # 添加用户消息
    conversation_mgr.add_message("user", f"🎤 {voice_text}")
    history.append([f"🎤 {voice_text}", None])
    
    # 调用API，使用较低的temperature和max_tokens
    response = api_client.call_with_retry(
        api_client.call_text_api,
        user_message=voice_text,
        system_prompt=system_prompt,
        temperature=0.7,
        max_tokens=2048
    )
    
    # 添加回复
    conversation_mgr.add_message("assistant", response)
    history[-1][1] = f"🔊 {response}"
    
    return history, "✅ 语音处理完成"


def save_itinerary(history: List) -> str:
    """
    保存当前行程到本地文件
    
    Args:
        history: 对话历史
    
    Returns:
        保存结果提示
    """
    if not history:
        return "⚠️ 当前没有可保存的行程"
    
    try:
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"itinerary_{timestamp}.md"
        filepath = SAVE_DIR / filename
        
        # 生成Markdown内容
        content = "# 我的旅游行程\n\n"
        content += f"**保存时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n"
        content += "---\n\n"
        
        for i, (user_msg, bot_msg) in enumerate(history, 1):
            if user_msg:
                content += f"## 第 {i} 轮对话\n\n"
                content += f"**我的需求**:\n{user_msg}\n\n"
            if bot_msg:
                content += f"**智能助手回复**:\n{bot_msg}\n\n"
                content += "---\n\n"
        
        # 保存文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"✅ 行程已保存至：{filepath.name}"
    
    except Exception as e:
        return f"❌ 保存失败：{str(e)}"


def export_itinerary(history: List) -> str:
    """
    导出行程为文本格式
    
    Args:
        history: 对话历史
    
    Returns:
        文本格式的行程内容
    """
    if not history:
        return "当前没有可导出的行程"
    
    content = "=" * 50 + "\n"
    content += "我的旅游行程\n"
    content += f"导出时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n"
    content += "=" * 50 + "\n\n"
    
    for i, (user_msg, bot_msg) in enumerate(history, 1):
        if user_msg:
            content += f"【第 {i} 轮对话】\n"
            content += f"我的需求:\n{user_msg}\n\n"
        if bot_msg:
            content += f"智能助手回复:\n{bot_msg}\n\n"
            content += "-" * 50 + "\n\n"
    
    return content


def clear_conversation() -> Tuple[List, str]:
    """
    清空对话历史
    
    Returns:
        空的历史记录和清空提示
    """
    conversation_mgr.clear()
    return [], "✅ 对话已清空，开始新的旅游规划吧！"


def get_quick_suggestions() -> List[str]:
    """获取快速建议选项"""
    return [
        "给我推荐一个适合周末的短途旅行目的地",
        "帮我规划一个3天2夜的杭州行程",
        "带父母去成都旅游，有什么建议？",
        "预算3000元，想去海边玩几天",
        "情侣去哪里旅游比较浪漫？",
        "学生党想穷游，推荐几个性价比高的地方"
    ]


# ==================== Gradio界面构建 ====================
def create_ui():
    """创建Gradio界面"""
    
    # 自定义CSS样式
    custom_css = """
    /* 全局样式 */
    .gradio-container {
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
    }
    
    /* 标题样式 */
    .main-title {
        text-align: center;
        color: #1890ff;
        font-size: 2.5em;
        font-weight: 600;
        margin: 20px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1em;
        margin-bottom: 30px;
    }
    
    /* 按钮样式 */
    .primary-btn {
        background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
    }
    
    .primary-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4) !important;
    }
    
    .secondary-btn {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
    }
    
    /* 聊天框样式 */
    .chatbot {
        border-radius: 12px !important;
        border: 2px solid #e8f4ff !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    }
    
    /* 输入框样式 */
    .input-box {
        border-radius: 8px !important;
        border: 2px solid #d9d9d9 !important;
        transition: all 0.3s ease !important;
    }
    
    .input-box:focus {
        border-color: #1890ff !important;
        box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2) !important;
    }
    
    /* 卡片样式 */
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin: 10px 0;
        border-left: 4px solid #1890ff;
    }
    
    /* 响应式适配 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.8em;
        }
        .gradio-container {
            padding: 10px !important;
        }
    }
    """
    
    with gr.Blocks(
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="orange",
            neutral_hue="slate",
        ),
        css=custom_css,
        title="智能旅游助手Agent"
    ) as app:
        
        # 标题区域
        gr.Markdown(
            """
            # 🌏 智能旅游助手Agent
            ### 您的专属AI旅游管家，让每一次出行都完美无忧
            """,
            elem_classes="main-title"
        )
        
        # 主要功能区
        with gr.Row():
            with gr.Column(scale=2):
                # 聊天界面
                chatbot = gr.Chatbot(
                    label="💬 智能对话",
                    height=500,
                    bubble_full_width=False,
                    avatar_images=(None, "🤖"),
                    elem_classes="chatbot"
                )
                
                # 输入区域
                with gr.Row():
                    user_input = gr.Textbox(
                        label="",
                        placeholder="💭 输入您的旅游需求，比如：帮我规划一个3天的北京行程...",
                        lines=2,
                        scale=4,
                        elem_classes="input-box"
                    )
                    send_btn = gr.Button(
                        "发送 📤",
                        scale=1,
                        variant="primary",
                        elem_classes="primary-btn"
                    )
                
                # 快捷操作按钮
                with gr.Row():
                    clear_btn = gr.Button("🗑️ 清空对话", scale=1)
                    save_btn = gr.Button("💾 保存行程", scale=1, elem_classes="secondary-btn")
                
                save_status = gr.Textbox(label="操作提示", interactive=False, visible=True)
            
            # 右侧功能面板
            with gr.Column(scale=1):
                gr.Markdown("### 🎯 快捷功能")
                
                # 快速建议
                with gr.Accordion("💡 快速提问", open=True):
                    quick_btns = []
                    suggestions = get_quick_suggestions()
                    for suggestion in suggestions:
                        btn = gr.Button(suggestion, size="sm")
                        quick_btns.append(btn)
                
                # 图片上传
                with gr.Accordion("📸 图片识别", open=True):
                    gr.Markdown("上传景点、美食、酒店、地图等图片，AI帮您识别并提供攻略")
                    image_input = gr.Image(
                        label="",
                        type="filepath",
                        sources=["upload"],
                        height=200
                    )
                    image_btn = gr.Button("识别图片 🔍", elem_classes="primary-btn")
                
                # 语音交互（简化版）
                with gr.Accordion("🎤 语音对讲", open=False):
                    gr.Markdown("按住录音，松开自动识别（演示版）")
                    audio_input = gr.Audio(
                        label="",
                        sources=["microphone"],
                        type="filepath"
                    )
                    voice_btn = gr.Button("处理语音 🔊", elem_classes="secondary-btn")
                    voice_status = gr.Textbox(label="语音状态", interactive=False)
                
                # 行程导出
                with gr.Accordion("📄 行程导出", open=False):
                    export_output = gr.Textbox(
                        label="",
                        lines=10,
                        placeholder="点击下方按钮导出完整行程...",
                        interactive=False
                    )
                    export_btn = gr.Button("导出为文本 📋", elem_classes="secondary-btn")
        
        # 功能说明
        with gr.Accordion("📖 使用指南", open=False):
            gr.Markdown(
                """
                ### 🎯 核心功能
                
                1. **智能对话规划**
                   - 主动需求挖掘：信息不全时友好追问
                   - 多方案生成：自动提供2-3套差异化方案
                   - 动态调整：随时优化行程，无需重新开始
                
                2. **多模态识别**
                   - 支持上传景点、美食、酒店、地图等图片
                   - AI自动识别并提供详细攻略
                   - 支持JPG、PNG、WEBP格式
                
                3. **语音交互**
                   - 按住录音，松开自动识别
                   - 语音回答口语化，适合播报
                   - 无需看屏幕也能获取信息
                
                4. **行程保存**
                   - 一键保存满意的行程方案
                   - 导出为Markdown或文本格式
                   - 方便分享和查看
                
                ### 💡 使用技巧
                
                - **场景适配**：提及"亲子"、"老人"、"穷游"等关键词，自动适配专属方案
                - **需求明确**：说明目的地、天数、人数、预算，获得更精准的规划
                - **动态优化**：随时提出调整需求，如"行程太赶"、"加个景点"
                - **境外游**：自动补充签证、货币、交通、语言等实用信息
                
                ### ⚙️ 配置说明
                
                首次使用前，请在 `.env` 文件中配置您的API密钥：
                ```
                API_KEY=your_api_key_here
                API_BASE_URL=https://api.anthropic.com
                MODEL_NAME=claude-3-5-sonnet-20241022
                ```
                """
            )
        
        # 底部信息
        gr.Markdown(
            """
            ---
            <div style="text-align: center; color: #999; padding: 20px;">
                <p>💼 生产级智能Agent应用 | 🚀 基于Gradio 4.x | 🤖 纯API驱动 | ⚡ 轻量化部署</p>
                <p style="font-size: 0.9em;">提示：所有AI能力通过第三方大模型API实现，无本地模型依赖</p>
            </div>
            """
        )
        
        # ==================== 事件绑定 ====================
        
        # 文本消息发送
        send_btn.click(
            fn=process_text_message,
            inputs=[user_input, chatbot],
            outputs=[chatbot, user_input]
        )
        
        user_input.submit(
            fn=process_text_message,
            inputs=[user_input, chatbot],
            outputs=[chatbot, user_input]
        )
        
        # 快速建议按钮
        for i, btn in enumerate(quick_btns):
            btn.click(
                fn=lambda s=suggestions[i]: (
                    process_text_message(s, conversation_mgr.history)[0],
                    ""
                ),
                inputs=[],
                outputs=[chatbot, user_input]
            )
        
        # 图片识别
        image_btn.click(
            fn=process_image_upload,
            inputs=[image_input, chatbot],
            outputs=[chatbot]
        )
        
        # 语音处理
        voice_btn.click(
            fn=process_voice_input,
            inputs=[audio_input, chatbot],
            outputs=[chatbot, voice_status]
        )
        
        # 清空对话
        clear_btn.click(
            fn=clear_conversation,
            inputs=[],
            outputs=[chatbot, save_status]
        )
        
        # 保存行程
        save_btn.click(
            fn=save_itinerary,
            inputs=[chatbot],
            outputs=[save_status]
        )
        
        # 导出行程
        export_btn.click(
            fn=export_itinerary,
            inputs=[chatbot],
            outputs=[export_output]
        )
    
    return app


# ==================== 主程序入口 ====================
def main():
    """主程序入口"""
    
    # 检查API配置
    if not API_KEY or API_KEY == "":
        print("⚠️  警告：未检测到API密钥配置")
        print("请在 .env 文件中配置 API_KEY")
        print("示例：API_KEY=your_api_key_here")
        print("\n继续启动应用，但API调用将失败...")
    
    # 创建并启动应用
    print("🚀 正在启动智能旅游助手Agent...")
    print(f"� 文本模型：{TEXT_MODEL_NAME}")
    print(f"🖼️  多模态模型：{MULTIMODAL_MODEL_NAME}")
    if TEXT_MODEL_NAME == MULTIMODAL_MODEL_NAME:
        print("   （使用统一模型处理文本和多模态任务）")
    print(f"🌐 API地址：{API_BASE_URL}")
    print(f"💾 行程保存路径：{SAVE_DIR.absolute()}")
    print("\n✅ 应用启动成功！浏览器将自动打开...")
    
    app = create_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        show_error=True
    )


if __name__ == "__main__":
    main()
