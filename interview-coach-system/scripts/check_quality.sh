#!/bin/bash

# 代码质量检查脚本
# 使用方法: ./scripts/check_quality.sh

set -e

echo "🔍 开始代码质量检查..."
echo ""

# 1. 代码格式检查（black）
echo "📝 1/4 检查代码格式 (black)..."
if command -v black &> /dev/null; then
    black --check src/ tests/ || echo "⚠️  代码格式不符合规范，运行 'black src/ tests/' 修复"
else
    echo "⚠️  black 未安装，跳过格式检查"
fi
echo ""

# 2. import 排序检查（isort）
echo "📦 2/4 检查 import 排序 (isort)..."
if command -v isort &> /dev/null; then
    isort --check-only src/ tests/ || echo "⚠️  import 排序不规范，运行 'isort src/ tests/' 修复"
else
    echo "⚠️  isort 未安装，跳过 import 检查"
fi
echo ""

# 3. 代码风格检查（flake8）
echo "🔧 3/4 检查代码风格 (flake8)..."
if command -v flake8 &> /dev/null; then
    flake8 src/ tests/ || echo "⚠️  代码风格存在问题"
else
    echo "⚠️  flake8 未安装，跳过风格检查"
fi
echo ""

# 4. 类型检查（mypy）
echo "🎯 4/4 检查类型注解 (mypy)..."
if command -v mypy &> /dev/null; then
    mypy src/ || echo "⚠️  类型检查发现问题"
else
    echo "⚠️  mypy 未安装，跳过类型检查"
fi
echo ""

echo "✅ 代码质量检查完成！"
