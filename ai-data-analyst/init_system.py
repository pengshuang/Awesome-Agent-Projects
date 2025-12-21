"""
系统初始化模块
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 加载环境变量
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ 已加载环境变量: {env_file}")
else:
    print(f"⚠️  环境变量文件不存在: {env_file}")
    print(f"提示：请复制 .env.example 并重命名为 .env，然后配置相关参数")


def initialize_system():
    """初始化系统"""
    from config.settings import SystemConfig
    from llama_index.core import Settings
    from config.llm_config import get_llm, get_embedding_model
    from src.utils.logger import setup_logger
    
    # 设置日志
    setup_logger()
    
    # 确保必要目录存在
    SystemConfig.ensure_directories()
    
    # 配置 LlamaIndex 全局设置
    Settings.llm = get_llm()
    Settings.embed_model = get_embedding_model()
    
    print("✅ 系统初始化完成")


if __name__ == "__main__":
    initialize_system()
