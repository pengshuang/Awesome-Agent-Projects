#!/bin/bash

# 英语学习助手启动脚本

echo "========================================"
echo "   英语学习助手启动中..."
echo "========================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "请先安装 Python 3.8+"
    exit 1
fi

echo "✓ Python 版本: $(python3 --version)"

# 检查依赖
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 首次运行，正在创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "📦 正在安装依赖..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo ""
    echo "✅ 环境设置完成"
else
    echo "✓ 虚拟环境已存在"
    source venv/bin/activate
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  未找到配置文件，正在初始化系统..."
    python3 init_system.py
    
    echo ""
    echo "❗ 请先编辑 .env 文件，配置你的API密钥"
    echo "然后重新运行此脚本"
    exit 1
fi

echo "✓ 配置文件已找到"

# 启动应用
echo ""
echo "🚀 正在启动 Web 应用..."
echo "========================================"
echo ""

python3 web_ui.py

# 退出时停用虚拟环境
deactivate
