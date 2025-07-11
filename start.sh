#!/bin/bash
# 奇幻冒险游戏 - Linux/WSL启动器

echo "🎮 奇幻冒险游戏 - Linux/WSL启动器"
echo "==============================="
echo

# 检查Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ 未找到Python，请先安装Python 3.6+"
    exit 1
fi

echo "✅ 使用Python: $PYTHON_CMD"
echo

# 运行游戏
$PYTHON_CMD run_game.py