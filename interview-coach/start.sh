#!/bin/bash

# AI 模拟面试系统启动脚本

echo "========================================"
echo "  AI 模拟面试系统"
echo "========================================"
echo ""

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python 版本: $python_version"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  .env 文件不存在"
    echo "正在从 .env.example 创建 .env 文件..."
    cp .env.example .env
    echo "✓ 已创建 .env 文件，请编辑并填写你的 API Key"
    echo ""
    echo "请执行以下步骤："
    echo "1. 编辑 .env 文件"
    echo "2. 填写 LLM_API_KEY"
    echo "3. 根据需要修改其他配置"
    echo "4. 重新运行此脚本"
    exit 1
fi

echo "✓ .env 文件存在"

# 检查依赖
echo ""
echo "检查依赖..."

if ! python3 -c "import gradio" 2>/dev/null; then
    echo "⚠️  缺少依赖包，正在安装..."
    pip install -r requirements.txt
else
    echo "✓ 依赖已安装"
fi

# 启动应用
echo ""
echo "========================================"
echo "  启动 Web UI"
echo "========================================"
echo ""
echo "访问地址: http://localhost:7860"
echo "按 Ctrl+C 停止服务"
echo ""

python3 web_ui.py
