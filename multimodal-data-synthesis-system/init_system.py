"""系统初始化脚本"""

import os
import sys
from pathlib import Path

def init_system():
    """初始化系统"""
    print("=" * 50)
    print("多模态数据合成系统 - 初始化")
    print("=" * 50)
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    
    # 创建必要的目录
    directories = [
        project_root / "data" / "uploads",
        project_root / "data" / "outputs",
        project_root / "logs",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ 创建目录: {directory}")
    
    # 检查 .env 文件
    env_file = project_root / ".env"
    if not env_file.exists():
        print("\n⚠️  未找到 .env 文件")
        print("创建示例 .env 文件...")
        
        env_content = """# OpenAI API 配置
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# LLM 配置
LLM_MODEL_NAME=gpt-4-vision-preview
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048
"""
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✓ 已创建 .env 文件: {env_file}")
        print("请编辑 .env 文件并填入您的 API 配置")
    else:
        print(f"✓ 找到 .env 文件: {env_file}")
    
    # 检查依赖
    print("\n检查 Python 依赖...")
    try:
        import langchain
        import langgraph
        import gradio
        import openai
        import pydantic
        print("✓ 所有依赖已安装")
    except ImportError as e:
        print(f"⚠️  缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
    
    print("\n" + "=" * 50)
    print("初始化完成！")
    print("=" * 50)
    print("\n运行以下命令启动系统:")
    print("  bash start.sh")
    print("或")
    print("  python web_ui.py")
    print()


if __name__ == "__main__":
    init_system()
