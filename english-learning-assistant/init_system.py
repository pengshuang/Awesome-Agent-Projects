#!/usr/bin/env python3
"""系统初始化脚本"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from src.utils.logger import app_logger


def init_system():
    """初始化系统"""
    
    print("="*80)
    print("英语学习助手系统初始化")
    print("="*80)
    
    # 1. 检查目录
    print("\n📁 检查目录结构...")
    directories = [
        settings.DATA_DIR,
        settings.LOG_DIR,
        settings.HISTORY_DIR,
        settings.UPLOAD_DIR,
    ]
    
    for directory in directories:
        if directory.exists():
            print(f"  ✓ {directory}")
        else:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  + {directory} (已创建)")
    
    # 2. 检查配置文件
    print("\n⚙️  检查配置...")
    env_file = Path(".env")
    
    if not env_file.exists():
        print("  ⚠️  未找到 .env 文件，正在创建模板...")
        create_env_template()
        print("  ✓ .env 模板已创建")
        print("  📝 请编辑 .env 文件，填入你的API密钥")
    else:
        print(f"  ✓ .env 文件存在")
    
    # 3. 检查API配置
    print("\n🔑 检查API配置...")
    if settings.LLM_API_KEY:
        print(f"  ✓ LLM API密钥已配置 ({settings.LLM_API_KEY[:10]}...)")
    else:
        print("  ⚠️  LLM API密钥未配置")
    
    if settings.LLM_MODEL:
        print(f"  ✓ 默认模型: {settings.LLM_MODEL}")
    
    # 4. 测试日志系统
    print("\n📝 测试日志系统...")
    try:
        app_logger.info("系统初始化测试日志")
        print(f"  ✓ 日志系统正常")
        print(f"  📂 日志目录: {settings.LOG_DIR}")
    except Exception as e:
        print(f"  ❌ 日志系统异常: {str(e)}")
    
    # 5. 完成
    print("\n" + "="*80)
    print("✅ 系统初始化完成！")
    print("="*80)
    
    if not settings.LLM_API_KEY:
        print("\n⚠️  重要提示：")
        print("1. 请编辑 .env 文件，配置你的API密钥")
        print("2. 配置完成后运行: ./start.sh 或 python web_ui.py")
    else:
        print("\n🚀 启动系统：")
        print("  ./start.sh")
        print("  或")
        print("  python web_ui.py")
    
    print()


def create_env_template():
    """创建.env模板文件"""
    template = """# 英语学习助手配置文件

# ==================== LLM API配置 ====================
# 大语言模型API配置（用于文本对话、翻译等）
LLM_API_KEY=your_api_key_here
LLM_API_BASE=https://dashscope.aliyuncs.com/api/v1
LLM_MODEL=qwen-plus

# ==================== 语音API配置 ====================
# 如果使用相同的API服务，可以不单独配置
# TTS_API_KEY=your_tts_api_key
# TTS_API_BASE=https://dashscope.aliyuncs.com/api/v1

# STT_API_KEY=your_stt_api_key
# STT_API_BASE=https://dashscope.aliyuncs.com/api/v1

# ==================== 视觉API配置 ====================
# 用于图片解析
# VISION_API_KEY=your_vision_api_key
# VISION_API_BASE=https://dashscope.aliyuncs.com/api/v1
VISION_MODEL=qwen-vl-plus

# ==================== 模型参数 ====================
TEMPERATURE=0.7
MAX_TOKENS=2000
TOP_P=0.8
API_TIMEOUT=60
STREAM_ENABLED=true

# ==================== 系统配置 ====================
DEBUG=true
DEFAULT_DIFFICULTY=中级

# ==================== Gradio配置 ====================
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860
GRADIO_SHARE=false
"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(template)


if __name__ == "__main__":
    init_system()
