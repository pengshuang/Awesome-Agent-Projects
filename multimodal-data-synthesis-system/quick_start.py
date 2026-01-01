"""快速启动脚本 - 提供便捷的命令行入口"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))


def main():
    parser = argparse.ArgumentParser(
        description="多模态数据合成系统 - 快速启动",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python quick_start.py                    # 启动 Web UI
  python quick_start.py --init             # 初始化系统
  python quick_start.py --check            # 检查环境
        """
    )
    
    parser.add_argument(
        '--init',
        action='store_true',
        help='初始化系统（创建目录、配置文件等）'
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='检查环境和依赖'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=7860,
        help='Web UI 端口（默认：7860）'
    )
    
    args = parser.parse_args()
    
    if args.init:
        print("🔧 初始化系统...")
        from init_system import init_system
        init_system()
        return
    
    if args.check:
        print("🔍 检查环境...")
        check_environment()
        return
    
    # 默认：启动 Web UI
    print("🚀 启动 Web UI...")
    print(f"📍 访问地址: http://localhost:{args.port}")
    print("按 Ctrl+C 停止服务\n")
    
    from web_ui import launch_ui
    launch_ui()


def check_environment():
    """检查环境和依赖"""
    import importlib
    from pathlib import Path
    
    print("\n" + "=" * 50)
    print("环境检查")
    print("=" * 50)
    
    # 检查 Python 版本
    import sys
    python_version = sys.version_info
    print(f"\n✓ Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("  ⚠️  建议使用 Python 3.8 或更高版本")
    
    # 检查必要的依赖
    dependencies = [
        ('langchain', 'LangChain'),
        ('langgraph', 'LangGraph'),
        ('gradio', 'Gradio'),
        ('openai', 'OpenAI SDK'),
        ('pydantic', 'Pydantic'),
        ('PIL', 'Pillow')
    ]
    
    print("\n依赖检查:")
    missing = []
    
    for module_name, display_name in dependencies:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"  ✓ {display_name}: {version}")
        except ImportError:
            print(f"  ✗ {display_name}: 未安装")
            missing.append(module_name)
    
    if missing:
        print(f"\n⚠️  缺少依赖: {', '.join(missing)}")
        print("运行以下命令安装:")
        print("  pip install -r requirements.txt")
    
    # 检查配置文件
    print("\n配置检查:")
    
    env_file = Path(".env")
    if env_file.exists():
        print("  ✓ .env 文件存在")
        
        # 检查关键配置
        with open(env_file) as f:
            content = f.read()
            if 'OPENAI_API_KEY=your_api_key' in content:
                print("  ⚠️  请更新 .env 文件中的 API Key")
            else:
                print("  ✓ API Key 已配置")
    else:
        print("  ✗ .env 文件不存在")
        print("  运行: python init_system.py")
    
    # 检查目录
    print("\n目录检查:")
    directories = [
        Path("data/uploads"),
        Path("data/outputs"),
        Path("logs")
    ]
    
    for directory in directories:
        if directory.exists():
            print(f"  ✓ {directory}")
        else:
            print(f"  ✗ {directory} (运行 init_system.py 创建)")
    
    print("\n" + "=" * 50)
    print("检查完成")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
