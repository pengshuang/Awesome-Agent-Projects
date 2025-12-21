#!/bin/bash
# 命令行多轮问答启动脚本

cd "$(dirname "$0")"
python cli_multi_turn.py "$@"
