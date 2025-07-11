#!/usr/bin/env python3
"""
测试游戏的主要功能
"""

from adventure_game import Player, Colors, colored_print, health_bar, Pet, Enemy

def test_player_creation():
    """测试玩家创建"""
    player = Player("测试玩家")
    assert player.name == "测试玩家"
    assert player.health == 100
    assert player.level == 1
    assert len(player.achievements) == 10
    assert player.pets == []
    assert player.active_pet is None
    colored_print("✅ 玩家创建测试通过", Colors.GREEN)

def test_status_effects():
    """测试状态效果系统"""
    player = Player("法师")
    
    # 测试应用状态效果
    player.apply_status_effect("burn", 3)
    assert player.status_effects["burn"]["duration"] == 3
    
    # 测试处理状态效果
    initial_health = player.health
    player.process_status_effects()
    assert player.health < initial_health  # 应该受到灼烧伤害
    assert player.status_effects["burn"]["duration"] == 2  # 持续时间减少
    
    colored_print("✅ 状态效果系统测试通过", Colors.GREEN)

def test_pet_system():
    """测试宠物系统"""
    player = Player("驯兽师")
    
    # 测试添加宠物
    success, msg = player.add_pet("🐺 幼狼", "小白")
    assert success == True
    assert len(player.pets) == 1
    assert player.active_pet is not None
    assert player.active_pet.name == "小白"
    
    # 测试宠物属性
    pet = player.active_pet
    assert pet.level == 1
    assert pet.loyalty == 50
    assert "attack_boost" in pet.abilities
    
    # 测试宠物升级
    pet.gain_exp(100)
    assert pet.level == 2
    
    colored_print("✅ 宠物系统测试通过", Colors.GREEN)

def test_enhanced_combat():
    """测试增强的战斗系统"""
    player = Player("战士")
    enemy = Enemy("测试敌人", 50, 10)
    
    # 测试敌人状态效果
    enemy.apply_status_effect("burn", 3)
    assert enemy.status_effects["burn"]["duration"] == 3
    
    # 测试敌人处理状态效果
    initial_health = enemy.health
    enemy.process_status_effects()
    assert enemy.health < initial_health
    
    colored_print("✅ 增强战斗系统测试通过", Colors.GREEN)

def test_pet_combat_bonuses():
    """测试宠物战斗加成"""
    player = Player("驯兽师")
    player.add_pet("🐺 幼狼", "小白")
    
    # 测试攻击力加成
    damage_without_pet = 0
    damage_with_pet = 0
    
    # 临时移除宠物测试
    temp_pet = player.active_pet
    player.active_pet = None
    for _ in range(10):
        damage_without_pet += player.get_attack_damage()
    
    # 恢复宠物测试
    player.active_pet = temp_pet
    player.active_pet.loyalty = 80  # 高忠诚度
    for _ in range(10):
        damage_with_pet += player.get_attack_damage()
    
    # 有宠物时平均伤害应该更高
    assert damage_with_pet > damage_without_pet
    
    colored_print("✅ 宠物战斗加成测试通过", Colors.GREEN)

def run_all_tests():
    """运行所有测试"""
    colored_print("\n🧪 开始运行扩展功能测试...", Colors.BOLD)
    
    test_player_creation()
    test_status_effects()
    test_pet_system()
    test_enhanced_combat()
    test_pet_combat_bonuses()
    
    colored_print("\n🎉 所有扩展功能测试通过！", Colors.BOLD + Colors.GREEN)
    
    # 显示新功能摘要
    colored_print("\n📋 新增功能摘要:", Colors.BOLD)
    improvements = [
        "✨ 状态效果系统 - 灼烧、冰冻、眩晕、中毒等效果",
        "🐾 宠物系统 - 收集、培养和战斗伙伴",
        "⚔️ 增强战斗 - 回合制状态效果处理",
        "🎨 更多视觉效果 - 彩色战斗信息",
        "💾 完整存档支持 - 包含所有新功能数据"
    ]
    
    for improvement in improvements:
        colored_print(f"  {improvement}", Colors.CYAN)
    
    colored_print("\n🎮 可扩展功能建议:", Colors.BOLD)
    suggestions = [
        "🏘️ 城镇和NPC系统",
        "🛠️ 制作系统",
        "🏆 更多成就类型",
        "📊 属性系统",
        "🎯 更多战斗机制"
    ]
    
    for suggestion in suggestions:
        colored_print(f"  {suggestion}", Colors.YELLOW)

if __name__ == "__main__":
    run_all_tests()