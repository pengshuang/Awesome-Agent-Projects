"""
配置测试文件
用于测试运行配置
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入系统初始化（用于测试环境）
from init_system import initialize_system

# 初始化测试环境
initialize_system()
