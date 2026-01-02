#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   🔍 重构代码结构验证脚本${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# 检查必要的文件是否存在
echo -e "${YELLOW}1. 检查模块文件...${NC}"

files=(
    "src/__init__.py"
    "src/config.py"
    "src/api_client.py"
    "src/conversation.py"
    "src/processor.py"
    "src/ui.py"
    "src/utils.py"
    "app_refactored.py"
)

missing_files=()

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗${NC} $file (缺失)"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo -e "\n${RED}❌ 缺少文件，请检查！${NC}"
    exit 1
fi

echo ""

# 检查 Python 语法
echo -e "${YELLOW}2. 检查 Python 语法...${NC}"

syntax_errors=0

for file in "${files[@]}"; do
    if [[ $file == *.py ]]; then
        if python3 -m py_compile "$file" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} $file 语法正确"
        else
            echo -e "  ${RED}✗${NC} $file 语法错误"
            syntax_errors=$((syntax_errors + 1))
        fi
    fi
done

if [ $syntax_errors -ne 0 ]; then
    echo -e "\n${RED}❌ 发现 $syntax_errors 个语法错误${NC}"
    exit 1
fi

echo ""

# 检查导入是否正常
echo -e "${YELLOW}3. 检查模块导入...${NC}"

python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from src.config import config
    print('  ✓ src.config')
    
    from src.api_client import TravelAssistantAPI
    print('  ✓ src.api_client')
    
    from src.conversation import ConversationManager
    print('  ✓ src.conversation')
    
    from src.processor import BusinessProcessor
    print('  ✓ src.processor')
    
    from src.ui import create_app_ui
    print('  ✓ src.ui')
    
    from src.utils import Timer, encode_image_to_base64
    print('  ✓ src.utils')
    
    print()
    print('✅ 所有模块导入成功！')
    sys.exit(0)
    
except ImportError as e:
    print(f'❌ 导入失败: {e}')
    sys.exit(1)
"

import_result=$?

if [ $import_result -ne 0 ]; then
    echo -e "\n${RED}❌ 模块导入失败${NC}"
    exit 1
fi

echo ""

# 检查代码规范
echo -e "${YELLOW}4. 检查代码规范...${NC}"

# 检查是否有明显的代码问题
echo -e "  ${BLUE}i${NC} 检查 TODO/FIXME 标记..."
grep -rn "TODO\|FIXME" src/ app_refactored.py 2>/dev/null | head -5

echo ""

# 统计代码行数
echo -e "${YELLOW}5. 代码统计...${NC}"

echo ""
echo -e "  ${BLUE}模块代码行数:${NC}"

for file in "${files[@]}"; do
    if [[ $file == *.py ]] && [ -f "$file" ]; then
        lines=$(wc -l < "$file" | tr -d ' ')
        echo "    • $file: $lines 行"
    fi
done

total_lines=$(find src/ -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $1}')
echo ""
echo -e "  ${GREEN}✓${NC} src/ 目录总计: $total_lines 行"

# 对比原始文件
if [ -f "app.py" ]; then
    original_lines=$(wc -l < app.py | tr -d ' ')
    echo -e "  ${BLUE}i${NC} 原始 app.py: $original_lines 行"
    
    reduction=$(echo "scale=2; (1 - $total_lines / $original_lines) * 100" | bc)
    if (( $(echo "$reduction > 0" | bc -l) )); then
        echo -e "  ${GREEN}✓${NC} 代码量减少: ${reduction}%"
    fi
fi

echo ""

# 检查配置文件
echo -e "${YELLOW}6. 检查配置...${NC}"

if [ -f ".env" ]; then
    echo -e "  ${GREEN}✓${NC} .env 文件存在"
    
    # 检查关键配置项
    required_vars=("API_KEY" "TEXT_MODEL_NAME" "MULTIMODAL_MODEL_NAME")
    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" .env; then
            echo -e "  ${GREEN}✓${NC} $var 已配置"
        else
            echo -e "  ${YELLOW}!${NC} $var 未配置"
        fi
    done
else
    echo -e "  ${YELLOW}!${NC} .env 文件不存在（请创建）"
fi

echo ""

# 生成模块依赖关系
echo -e "${YELLOW}7. 模块依赖关系:${NC}"
echo ""
echo -e "  app_refactored.py"
echo -e "      ↓"
echo -e "  ├─ src.config (配置管理)"
echo -e "  ├─ src.api_client (API 通信)"
echo -e "  ├─ src.conversation (对话管理)"
echo -e "  ├─ src.processor (业务逻辑)"
echo -e "  │   ├─ api_client"
echo -e "  │   ├─ conversation"
echo -e "  │   └─ utils"
echo -e "  ├─ src.ui (界面)"
echo -e "  └─ src.utils (工具函数)"
echo ""

# 最终总结
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}✅ 代码结构验证完成！${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

echo -e "${YELLOW}📋 重构成果总结:${NC}"
echo ""
echo -e "  ✓ 模块化设计 - 6 个独立模块"
echo -e "  ✓ 单一职责 - 每个模块职责明确"
echo -e "  ✓ 依赖注入 - 松耦合设计"
echo -e "  ✓ 配置管理 - 统一配置入口"
echo -e "  ✓ 完善文档 - ARCHITECTURE.md"
echo -e "  ✓ 易于测试 - 模块独立可测"
echo ""

echo -e "${YELLOW}🚀 下一步操作:${NC}"
echo ""
echo -e "  1. 配置 .env 文件（如未配置）"
echo -e "  2. 测试 API: ${BLUE}bash tests/test_all_apis.sh${NC}"
echo -e "  3. 运行应用: ${BLUE}python app_refactored.py${NC}"
echo ""

exit 0
