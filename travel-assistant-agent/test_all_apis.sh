#!/bin/bash

# API 一键测试脚本
# 用于快速测试文本 API 和多模态 API 是否可用

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 输出带颜色的日志
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 主程序开始
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          🧪 旅游助手 API 一键测试脚本                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 检查 Python 环境
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    log_error "未找到 Python 环境，请先安装 Python 3.8+"
    exit 1
fi

# 确定使用的 python 命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

log_info "使用 Python: $($PYTHON_CMD --version)"

# 检查依赖
log_info "检查依赖包..."
$PYTHON_CMD -c "import requests; import dotenv" 2>/dev/null || {
    log_warning "缺少必要的依赖包，正在尝试安装..."
    $PYTHON_CMD -m pip install requests python-dotenv
}

# 检查 .env 文件
if [ ! -f ".env" ]; then
    log_error ".env 文件不存在"
    log_info "请先创建 .env 文件，参考 .env.example"
    exit 1
fi

log_success ".env 文件存在"

# 读取配置
source .env

if [ -z "$API_KEY" ]; then
    log_error "API_KEY 未配置，请在 .env 文件中设置"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    📝 配置信息                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
log_info "API 密钥：✅ 已配置 (长度: ${#API_KEY})"
log_info "API URL: ${API_BASE_URL}"
log_info "文本模型: ${TEXT_MODEL_NAME}"
log_info "视觉模型: ${MULTIMODAL_MODEL_NAME}"
log_info "超时设置: 文本=${TEXT_API_TIMEOUT}s, 多模态=${MULTIMODAL_API_TIMEOUT}s"
echo ""

# 测试文本 API
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              1️⃣  测试文本 LLM API (qwen3-max)                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

if $PYTHON_CMD test_text_api.py; then
    TEXT_API_RESULT=0
    log_success "文本 API 测试通过 ✅"
else
    TEXT_API_RESULT=1
    log_error "文本 API 测试失败 ❌"
fi

echo ""

# 测试多模态 API
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           2️⃣  测试多模态 LLM API (qwen-vl-plus)              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

if $PYTHON_CMD test_multimodal_api.py; then
    MULTIMODAL_API_RESULT=0
    log_success "多模态 API 测试通过 ✅"
else
    MULTIMODAL_API_RESULT=1
    log_error "多模态 API 测试失败 ❌"
fi

echo ""

# 测试结果汇总
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    📊 测试结果汇总                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

if [ $TEXT_API_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ 文本 API: 通过${NC}"
else
    echo -e "${RED}❌ 文本 API: 失败${NC}"
fi

if [ $MULTIMODAL_API_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ 多模态 API: 通过${NC}"
else
    echo -e "${RED}❌ 多模态 API: 失败${NC}"
fi

echo ""

# 最终结果
if [ $TEXT_API_RESULT -eq 0 ] && [ $MULTIMODAL_API_RESULT -eq 0 ]; then
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                  🎉 所有 API 测试通过！                       ║"
    echo "║              应用已就绪，可以启动 Web 服务                    ║"
    echo "║                  运行: python app.py                          ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    exit 0
else
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║              ⚠️  有 API 测试失败                              ║"
    echo "║            请检查以下内容：                                   ║"
    echo "║  1. API_KEY 是否正确配置                                      ║"
    echo "║  2. 网络连接是否正常                                          ║"
    echo "║  3. .env 配置是否完整                                         ║"
    echo "║  4. 查看上面的详细日志信息                                    ║"
    echo "║                                                              ║"
    echo "║  更多帮助请查看: API_TEST_GUIDE.md                           ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    exit 1
fi
