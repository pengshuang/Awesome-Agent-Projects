#!/bin/bash

# 多模态数据合成系统启动脚本

echo "=========================================="
echo "多模态数据合成系统"
echo "=========================================="

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 检查并创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "检查并安装依赖..."
pip install -r requirements.txt

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "警告: 未找到 .env 文件"
    echo "请创建 .env 文件并配置以下环境变量："
    echo "  OPENAI_API_KEY=your_api_key"
    echo "  OPENAI_BASE_URL=your_base_url"
    echo ""
    read -p "是否继续启动？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 创建必要的目录
echo "创建数据目录..."
mkdir -p data/uploads
mkdir -p data/outputs
mkdir -p logs

# 启动 Web UI
echo "=========================================="
echo "启动 Web UI..."
echo "访问地址: http://localhost:7860"
echo "=========================================="

python3 web_ui.py
