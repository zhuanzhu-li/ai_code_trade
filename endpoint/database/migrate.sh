#!/bin/bash
# 数据库迁移工具 - Unix/Linux Shell脚本
# 用法: ./migrate.sh [command] [version]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印彩色消息
print_error() {
    echo -e "${RED}错误: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 检查Python是否可用
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        print_error "未找到Python，请确保Python 3已安装"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# 检查Python版本
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.6"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "需要Python 3.6或更高版本，当前版本: $PYTHON_VERSION"
    exit 1
fi

# 切换到脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查是否安装了必要的依赖
if ! $PYTHON_CMD -c "import pymysql" 2>/dev/null; then
    print_error "未找到pymysql模块"
    echo "请运行以下命令安装依赖:"
    echo "  pip install pymysql python-dotenv"
    exit 1
fi

# 检查.env文件是否存在
if [ ! -f "../../.env" ]; then
    print_warning ".env文件不存在，请确保数据库配置正确"
fi

# 执行Python迁移脚本
print_success "启动数据库迁移工具..."
$PYTHON_CMD migrate.py "$@"
