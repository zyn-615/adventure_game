#!/usr/bin/env python3
"""
Test script for the Player module
"""

from game.core.player import Player
from game.core.pet import Pet
from game.core.utils import Colors, colored_print

def test_player_module():
    """Test the Player module functionality"""
    print("=== Testing Player Module ===\n")
    
    # Test 1: Player creation
    print("1. Testing Player creation...")
    player = Player("Test Hero")
    assert player.name == "Test Hero"
    assert player.health == 100
    assert player.level == 1
    print("✅ Player creation successful\n")
    
    # Test 2: Pet system
    print("2. Testing Pet system...")
    success, message = player.add_pet("🐺 幼狼", "测试狼")
    assert success == True
    assert len(player.pets) == 1
    assert player.active_pet is not None
    print("✅ Pet system working\n")
    
    # Test 3: Skills system
    print("3. Testing Skills system...")
    initial_mana = player.mana
    success, damage = player.use_skill("🔥 火球术")
    assert success == True
    assert player.mana < initial_mana
    print("✅ Skills system working\n")
    
    # Test 4: Status effects
    print("4. Testing Status effects...")
    player.apply_status_effect("burn", 2)
    assert player.status_effects["burn"]["duration"] == 2
    player.process_status_effects()
    assert player.status_effects["burn"]["duration"] == 1
    print("✅ Status effects working\n")
    
    # Test 5: Equipment system
    print("5. Testing Equipment system...")
    player.inventory.append("⚔️ 铁剑")
    player.equip_item("⚔️ 铁剑")
    assert player.equipment["weapon"] == "⚔️ 铁剑"
    print("✅ Equipment system working\n")
    
    # Test 6: Experience and leveling
    print("6. Testing Experience system...")
    initial_level = player.level
    player.gain_exp(100)  # Should level up
    assert player.level == initial_level + 1
    print("✅ Experience system working\n")
    
    # Test 7: Achievement system
    print("7. Testing Achievement system...")
    player.stats["enemies_defeated"] = 1
    achievements = player.check_achievements()
    assert "🏆 初出茅庐" in achievements
    print("✅ Achievement system working\n")
    
    # Test 8: Quest system
    print("8. Testing Quest system...")
    initial_progress = player.quests["🐺 森林清理"]["progress"]
    player.update_quest("forest", "🐺 野狼")
    assert player.quests["🐺 森林清理"]["progress"] > initial_progress
    print("✅ Quest system working\n")
    
    colored_print("🎉 All Player module tests passed!", Colors.GREEN)

if __name__ == "__main__":
    test_player_module()