#!/bin/bash

# 代码自动格式化脚本
# 使用方法: ./scripts/format_code.sh

set -e

echo "🎨 开始格式化代码..."
echo ""

# 1. 使用 black 格式化
echo "📝 1/2 格式化代码 (black)..."
if command -v black &> /dev/null; then
    black src/ tests/
    echo "✅ black 格式化完成"
else
    echo "⚠️  black 未安装，请运行: pip install black"
fi
echo ""

# 2. 使用 isort 排序 import
echo "📦 2/2 排序 import (isort)..."
if command -v isort &> /dev/null; then
    isort src/ tests/
    echo "✅ isort 排序完成"
else
    echo "⚠️  isort 未安装，请运行: pip install isort"
fi
echo ""

echo "✅ 代码格式化完成！"
