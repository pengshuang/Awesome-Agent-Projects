"""智能旅游助手Agent - 主程序"""

import os
import base64
import logging
from datetime import datetime
from typing import Optional, Tuple, List
from pathlib import Path

import gradio as gr
import requests
from dotenv import load_dotenv
from PIL import Image

from config.prompts import (
    AGENT_CORE_SYSTEM_PROMPT,
    MULTIMODAL_IMAGE_PROMPT,
    get_combined_prompt
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# ==================== 配置参数 ====================
API_KEY = os.getenv("API_KEY", "")
API_BASE_URL = os.getenv("API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
TEXT_MODEL_NAME = os.getenv("TEXT_MODEL_NAME", "qwen3-max")
MULTIMODAL_MODEL_NAME = os.getenv("MULTIMODAL_MODEL_NAME", "qwen-vl-plus")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1500"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.85"))
TEXT_API_TIMEOUT = int(os.getenv("TEXT_API_TIMEOUT", "60"))
MULTIMODAL_API_TIMEOUT = int(os.getenv("MULTIMODAL_API_TIMEOUT", "90"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

SAVE_DIR = Path("data/saved_itineraries")
SAVE_DIR.mkdir(parents=True, exist_ok=True)


# ==================== API调用封装 ====================
class TravelAssistantAPI:
    """旅游助手API调用封装类"""
    
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = API_BASE_URL
        self.text_model = TEXT_MODEL_NAME
        self.multimodal_model = MULTIMODAL_MODEL_NAME
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logger.info(f"🚀 API 客户端初始化 | 文本: {self.text_model} | 视觉: {self.multimodal_model}")
    
    def call_text_api(self, user_message: str, system_prompt: str = None, 
                     temperature: float = TEMPERATURE, max_tokens: int = MAX_TOKENS) -> str:
        """调用文本API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})
        
        payload = {
            "model": self.text_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        logger.info(f"📤 发送文本请求 | 模型: {self.text_model} | 超时: {TEXT_API_TIMEOUT}s")
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=TEXT_API_TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result["choices"][0]["message"]["content"]
                    logger.info(f"📥 收到响应 | 长度: {len(response_text)} 字符")
                    return response_text
                else:
                    logger.error(f"❌ API 错误 | 状态码: {response.status_code}")
                    return f"❌ API调用失败（状态码: {response.status_code}）"
                    
            except requests.exceptions.Timeout:
                if attempt < MAX_RETRIES - 1:
                    wait_time = (attempt + 1) * 5
                    logger.warning(f"⏱️ 请求超时（第 {attempt + 1}/{MAX_RETRIES} 次），{wait_time}秒后重试...")
                    import time
                    time.sleep(wait_time)
                else:
                    logger.error(f"⏱️ 请求超时，已达最大重试次数")
                    return "❌ 请求超时，请检查网络后重试"
            except Exception as e:
                logger.error(f"⚠️ 异常: {str(e)}")
                return f"❌ 发生错误：{str(e)}"
        
        return "❌ API 调用失败"
    
    def call_multimodal_api(self, user_message: str, image_data: str, 
                           media_type: str = "image/jpeg") -> str:
        """调用多模态API"""
        payload = {
            "model": self.multimodal_model,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "messages": [
                {"role": "system", "content": MULTIMODAL_IMAGE_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{image_data}"}},
                        {"type": "text", "text": user_message}
                    ]
                }
            ]
        }
        
        logger.info(f"📤 发送图片识别请求 | 模型: {self.multimodal_model}")
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=MULTIMODAL_API_TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result["choices"][0]["message"]["content"]
                    logger.info(f"📥 收到图片识别响应 | 长度: {len(response_text)} 字符")
                    return response_text
                else:
                    logger.error(f"❌ 图片识别失败 | 状态码: {response.status_code}")
                    return f"❌ 图片识别失败（状态码: {response.status_code}）"
                    
            except requests.exceptions.Timeout:
                if attempt < MAX_RETRIES - 1:
                    wait_time = (attempt + 1) * 5
                    logger.warning(f"⏱️ 图片识别超时（第 {attempt + 1}/{MAX_RETRIES} 次），{wait_time}秒后重试...")
                    import time
                    time.sleep(wait_time)
                else:
                    logger.error(f"⏱️ 图片识别超时，已达最大重试次数")
                    return "❌ 图片识别超时，请重试"
            except Exception as e:
                logger.error(f"⚠️ 图片识别异常: {str(e)}")
                return f"❌ 图片识别出错：{str(e)}"
        
        return "❌ 图片识别失败"


# 初始化API客户端
api_client = TravelAssistantAPI()


# ==================== 对话历史管理 ====================
class ConversationManager:
    """对话历史管理器"""
    
    def __init__(self):
        self.history = []
        self.current_scenario = None
        self.user_requirements = {}
    
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
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent])
    
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
    if not user_input or not user_input.strip():
        return history if history else [], ""
    
    try:
        # 确保历史记录是列表
        if history is None:
            history = []
        
        logger.info(f"👤 用户输入: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")
        
        # 检测场景
        scenario = conversation_mgr.detect_scenario(user_input)
        if scenario:
            logger.info(f"🎯 检测到场景: {scenario}")
        
        # 构建系统提示词
        system_prompt = get_combined_prompt(
            AGENT_CORE_SYSTEM_PROMPT,
            scenario=scenario,
            additional_context=conversation_mgr.get_context()
        )
        
        # 添加用户消息到历史
        conversation_mgr.add_message("user", user_input)
        
        # 调用API
        logger.info("⏳ 正在调用大模型...")
        response = api_client.call_text_api(
            user_message=user_input,
            system_prompt=system_prompt
        )
        
        # 添加助手回复到历史 - 确保一次性添加完整的 [user, assistant] 对
        conversation_mgr.add_message("assistant", response)
        history.append([user_input, response])
        
        logger.info(f"✅ 处理完成 | 响应长度: {len(response)} 字符")
        return history, ""
    except Exception as e:
        # 错误处理 - 确保返回有效的历史记录格式
        error_response = f"❌ 处理出错：{str(e)}"
        logger.error(f"❌ 处理文本消息失败: {str(e)}")
        if history and len(history) > 0 and history[-1][1] is None:
            history[-1][1] = error_response
        else:
            history.append([user_input, error_response])
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
        return history if history else []
    
    try:
        # 确保历史记录是列表
        if history is None:
            history = []
        
        logger.info(f"📷 收到图片上传请求: {image_path}")
        
        # 读取并编码图片
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # 判断图片格式
        img = Image.open(image_path)
        img_format = img.format.lower()
        media_type = f"image/{img_format}" if img_format in ["jpeg", "jpg", "png", "webp"] else "image/jpeg"
        img_size = img.size
        
        logger.info(f"📊 图片信息: 格式={media_type}, 尺寸={img_size}, 大小={len(image_data)} bytes")
        
        # 添加用户消息
        user_msg = "📷 [用户上传了一张图片，请识别图片中的旅游相关内容]"
        
        # 调用多模态API
        logger.info("⏳ 正在调用多模态大模型识别图片...")
        response = api_client.call_multimodal_api(
            user_message="请识别这张图片中的旅游相关内容，并给出详细的攻略建议。",
            image_data=image_data,
            media_type=media_type
        )
        
        # 更新历史 - 一次性添加完整的 [user, assistant] 对
        conversation_mgr.add_message("user", user_msg)
        conversation_mgr.add_message("assistant", response)
        history.append([user_msg, response])
        
        logger.info(f"✅ 图片识别完成 | 响应长度: {len(response)} 字符")
        
    except Exception as e:
        # 错误处理 - 确保返回有效的历史记录格式
        error_msg = f"❌ 图片处理失败：{str(e)}"
        logger.error(f"❌ 处理图片上传失败: {str(e)}")
        user_msg = "📷 [用户上传了一张图片，请识别图片中的旅游相关内容]"
        history.append([user_msg, error_msg])
    
    return history if history else []



def save_itinerary(history: List) -> str:
    """保存行程到本地文件"""
    if not history:
        return "⚠️ 当前没有可保存的行程"
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"itinerary_{timestamp}.md"
        filepath = SAVE_DIR / filename
        
        content = "# 我的旅游行程\n\n"
        content += f"**保存时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n---\n\n"
        
        for i, (user_msg, bot_msg) in enumerate(history, 1):
            if user_msg:
                content += f"## 第 {i} 轮对话\n\n**我的需求**:\n{user_msg}\n\n"
            if bot_msg:
                content += f"**智能助手回复**:\n{bot_msg}\n\n---\n\n"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"✅ 行程已保存至：{filepath.name}"
    except Exception as e:
        return f"❌ 保存失败：{str(e)}"


def export_itinerary(history: List) -> str:
    """导出行程为文本格式"""
    if not history:
        return "当前没有可导出的行程"
    
    content = "=" * 50 + "\n我的旅游行程\n"
    content += f"导出时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n" + "=" * 50 + "\n\n"
    
    for i, (user_msg, bot_msg) in enumerate(history, 1):
        if user_msg:
            content += f"【第 {i} 轮对话】\n我的需求:\n{user_msg}\n\n"
        if bot_msg:
            content += f"智能助手回复:\n{bot_msg}\n\n" + "-" * 50 + "\n\n"
    
    return content


def clear_conversation() -> Tuple[List, str]:
    """清空对话历史"""
    conversation_mgr.clear()
    return [], "✅ 对话已清空，开始新的旅游规划吧!"


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
    
    custom_css = """
    .gradio-container {
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
    }
    .main-title {
        text-align: center;
        color: #1890ff;
        font-size: 2.5em;
        font-weight: 600;
        margin: 20px 0;
    }
    .primary-btn {
        background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%) !important;
        border: none !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
    }
    .chatbot {
        border-radius: 12px !important;
        border: 2px solid #e8f4ff !important;
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
                    avatar_images=(None, "./assets/travel-assistant-avatar.png"),
                    elem_classes="chatbot",
                    value=[]  # 初始化为空列表
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
                
                3. **行程保存**
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
        def create_quick_handler(suggestion_text):
            """为每个快速建议创建处理函数"""
            def handler(history):
                return process_text_message(suggestion_text, history)
            return handler
        
        for btn, suggestion in zip(quick_btns, suggestions):
            btn.click(
                fn=create_quick_handler(suggestion),
                inputs=[chatbot],
                outputs=[chatbot, user_input]
            )
        
        # 图片识别
        image_btn.click(
            fn=process_image_upload,
            inputs=[image_input, chatbot],
            outputs=[chatbot]
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
    
    # 打印启动信息
    logger.info("=" * 80)
    logger.info("🚀 正在启动智能旅游助手Agent...")
    logger.info("=" * 80)
    
    # 检查API配置
    if not API_KEY or API_KEY == "":
        logger.warning("⚠️  警告：未检测到API密钥配置")
        logger.warning("请在 .env 文件中配置 API_KEY")
        logger.warning("示例：API_KEY=your_api_key_here")
        logger.warning("继续启动应用，但API调用将失败...")
    else:
        logger.info(f"✅ API密钥已配置（长度: {len(API_KEY)} 字符）")
    
    # 记录配置信息
    logger.info(f"📝 配置信息:")
    logger.info(f"  • API基础URL: {API_BASE_URL}")
    logger.info(f"  • 文本模型: {TEXT_MODEL_NAME}")
    logger.info(f"  • 视觉模型: {MULTIMODAL_MODEL_NAME}")
    logger.info(f"  • Max Tokens: {MAX_TOKENS}")
    logger.info(f"  • 温度参数: {TEMPERATURE}")
    logger.info(f"  • 行程保存路径: {SAVE_DIR.absolute()}")
    logger.info("=" * 80)
    
    # 创建并启动应用
    app = create_ui()
    logger.info("🌐 应用启动成功！浏览器将自动打开在 http://localhost:7860")
    logger.info("=" * 80)
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        show_error=True
    )


if __name__ == "__main__":
    main()
