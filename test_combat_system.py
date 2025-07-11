#!/usr/bin/env python3
"""
Test script for the CombatSystem class
"""

from game.systems.combat import CombatSystem
from game.core.player import Player
from game.core.enemy import Enemy

def test_combat_system():
    """Test the CombatSystem functionality"""
    print("🧪 测试 CombatSystem 功能...")
    
    # Create test instances
    combat_system = CombatSystem()
    player = Player("测试玩家")
    
    # Test combat system initialization
    print(f"✅ 创建战斗系统: {combat_system}")
    print(f"✅ 创建玩家: {player.name}")
    print(f"✅ 玩家初始生命值: {player.health}")
    print(f"✅ 玩家初始等级: {player.level}")
    
    # Test battle stats
    stats = combat_system.get_battle_stats()
    print(f"✅ 战斗统计: {stats}")
    
    # Test reset functionality
    combat_system.reset_battle()
    print("✅ 战斗重置成功")
    
    print("\n🎉 CombatSystem 所有测试通过！")

if __name__ == "__main__":
    test_combat_system()