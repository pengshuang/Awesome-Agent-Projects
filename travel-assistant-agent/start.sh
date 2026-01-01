#!/bin/bash

# 智能旅游助手Agent - 快速启动脚本

echo "=========================================="
echo "   🌏 智能旅游助手Agent - 启动中...    "
echo "=========================================="
echo ""

# 检查Python版本
echo "📋 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python版本: $python_version"
echo ""

# 检查是否存在.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  未检测到.env配置文件"
    echo "正在创建.env文件..."
    cp .env.example .env
    echo "✅ 已创建.env文件，请编辑该文件并填入您的API密钥"
    echo ""
    echo "配置步骤："
    echo "1. 打开.env文件"
    echo "2. 将 your_api_key_here 替换为您的真实API密钥"
    echo "3. 保存后重新运行本脚本"
    echo ""
    exit 1
fi

# 检查是否安装了依赖
echo "📦 检查依赖包..."
if ! python3 -c "import gradio" 2>/dev/null; then
    echo "⚠️  未检测到依赖包，正在安装..."
    pip install -r requirements.txt
    echo "✅ 依赖包安装完成"
else
    echo "✅ 依赖包已安装"
fi
echo ""

# 启动应用
echo "🚀 启动应用..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 app.py
