#!/bin/bash

# AI 数据分析助手启动脚本

echo "========================================="
echo "   🤖 AI 数据分析助手"
echo "========================================="
echo ""

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  警告: .env 文件不存在"
    echo "请复制 .env.example 并配置：cp .env.example .env"
    echo ""
fi

# 检查依赖
echo "检查依赖包..."
pip3 show gradio > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  警告: 依赖包未安装"
    echo "请运行: pip install -r requirements.txt"
    echo ""
fi

echo ""
echo "正在启动服务..."
echo "访问地址: http://localhost:7860"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================="
echo ""

# 启动服务
python web_ui.py
