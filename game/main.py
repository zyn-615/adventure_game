#!/usr/bin/env python3
"""
奇幻冒险游戏 - 模块化版本
主游戏入口
"""

import sys
import os

# 添加游戏包到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.core import Player, Enemy, Pet, Colors, colored_print, health_bar
from game.systems import CombatSystem, AchievementSystem, SaveLoadSystem
from game.world import WeaponShop, MagicShop, PetShop, shop, discount_shop

def main():
    """主游戏入口函数"""
    # 导入原始游戏逻辑
    from adventure_game import main as original_main
    
    # 显示模块化版本信息
    colored_print("🎮 奇幻冒险游戏 - 模块化版本 v3.2", Colors.BOLD + Colors.CYAN)
    colored_print("✨ 代码结构已优化，采用模块化设计", Colors.GREEN)
    print()
    
    # 启动原始游戏
    original_main()

if __name__ == "__main__":
    main()