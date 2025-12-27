#!/bin/bash
# 命令行单轮问答启动脚本

cd "$(dirname "$0")"
python cli_single_turn.py "$@"
