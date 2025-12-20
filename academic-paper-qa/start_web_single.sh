#!/bin/bash
# Web UI 单轮问答启动脚本

cd "$(dirname "$0")"
echo "🚀 启动 Web UI 单轮问答..."
echo "📍 访问地址: http://127.0.0.1:7860"
echo ""
python web_ui_single_turn.py
