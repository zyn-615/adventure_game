"""
Combat System Module - Turn-based combat mechanics for adventure games

This module contains the CombatSystem class which manages:
- Turn-based combat logic
- Status effect processing
- Player and enemy actions
- Combat rewards and progression
- Quest updates related to combat

Dependencies:
    - game.core.enemy: Enemy class
    - game.core.utils: Colors, colored_print, health_bar
    - random: For combat calculations and randomization
"""

import random

# Handle relative imports
try:
    from ..core.enemy import Enemy
    from ..core.utils import Colors, colored_print, health_bar
except ImportError:
    # Standalone execution - adjust path and import
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from game.core.enemy import Enemy
    from game.core.utils import Colors, colored_print, health_bar


class CombatSystem:
    """
    Main combat system class for turn-based battles.
    
    This class handles all combat-related functionality including:
    - Turn-based combat mechanics
    - Status effect processing
    - Player and enemy actions
    - Combat rewards and experience
    - Quest progress updates
    """
    
    def __init__(self):
        """Initialize the combat system."""
        self.current_battle = None
        self.turn_count = 0
        
    def start_battle(self, player, enemy_name, enemy_health, enemy_attack):
        """
        Start a new battle between player and enemy.
        
        Args:
            player: Player instance
            enemy_name (str): Name of the enemy
            enemy_health (int): Enemy's health points
            enemy_attack (int): Enemy's attack damage
            
        Returns:
            bool or str: True if player wins, False if player flees, 
                        "game_over" if player dies
        """
        colored_print(f"\n⚔️  遭遇 {enemy_name}！", Colors.RED)
        
        # Create enemy instance
        enemy = Enemy(enemy_name, enemy_health, enemy_attack)
        self.current_battle = {
            "player": player,
            "enemy": enemy,
            "turn": 0
        }
        
        # Main combat loop
        while enemy.health > 0 and player.health > 0:
            self.turn_count += 1
            print(f"\n{Colors.BOLD}=== 回合开始 ==={Colors.END}")
            
            # Player turn
            player_action_result = self._handle_player_turn(player, enemy)
            if player_action_result == "flee":
                return False
            elif player_action_result == "death":
                break
                
            # Enemy turn
            if enemy.health > 0:
                enemy_action_result = self._handle_enemy_turn(player, enemy)
                if enemy_action_result == "death":
                    break
        
        # Handle battle end
        return self._handle_battle_end(player, enemy)
    
    def _handle_player_turn(self, player, enemy):
        """
        Handle player's turn in combat.
        
        Args:
            player: Player instance
            enemy: Enemy instance
            
        Returns:
            str: "flee" if player flees, "death" if player dies, None otherwise
        """
        # Check player stun status before processing effects
        player_stunned = player.is_stunned()
        
        # Process player status effects
        player.process_status_effects()
        
        # Check if player died from status effects
        if player.health <= 0:
            return "death"
        
        # Display health bars
        print(f"\n你的生命值: {health_bar(player.health, 100)}")
        print(f"{enemy.name} 生命值: {health_bar(enemy.health, enemy.max_health)}")
        
        # Handle player action
        if player_stunned:
            colored_print("⚡ 你被眩晕了，无法行动！", Colors.RED)
        else:
            return self._get_player_action(player, enemy)
        
        return None
    
    def _get_player_action(self, player, enemy):
        """
        Get and execute player's chosen action.
        
        Args:
            player: Player instance
            enemy: Enemy instance
            
        Returns:
            str: "flee" if player flees, None otherwise
        """
        action = input("\n选择行动 (1-攻击 2-逃跑 3-使用物品 4-使用技能): ")
        
        if action == "1":
            return self._handle_attack_action(player, enemy)
        elif action == "2":
            return self._handle_flee_action()
        elif action == "3":
            return self._handle_item_action(player)
        elif action == "4":
            return self._handle_skill_action(player, enemy)
        else:
            colored_print("❌ 无效选择", Colors.RED)
            return self._get_player_action(player, enemy)
    
    def _handle_attack_action(self, player, enemy):
        """Handle player attack action."""
        damage = player.get_attack_damage()
        enemy.health -= damage
        colored_print(f"⚔️ 你对 {enemy.name} 造成了 {damage} 点伤害！", Colors.YELLOW)
        return None
    
    def _handle_flee_action(self):
        """Handle player flee action."""
        if random.random() < 0.7:
            colored_print("🏃 成功逃跑！", Colors.GREEN)
            return "flee"
        else:
            colored_print("💨 逃跑失败！", Colors.RED)
            return None
    
    def _handle_item_action(self, player):
        """Handle player item usage."""
        if "🍞 面包" in player.inventory:
            player.health = min(100, player.health + 30)
            player.inventory.remove("🍞 面包")
            colored_print("🍞 使用面包恢复了30点生命值！", Colors.GREEN)
        else:
            colored_print("❌ 没有可用物品！", Colors.RED)
        return None
    
    def _handle_skill_action(self, player, enemy):
        """Handle player skill usage."""
        available_skills = [skill for skill, data in player.skills.items() 
                           if data["level"] > 0]
        
        if not available_skills:
            colored_print("❌ 没有可用技能！", Colors.RED)
            return None
        
        # Display available skills
        print("\n可用技能:")
        for i, skill in enumerate(available_skills):
            cost = player.skills[skill]["cost"]
            if "damage" in player.skills[skill]:
                damage = player.skills[skill]["damage"]
                print(f"{i+1}. {skill} (伤害: {damage}, 消耗: {cost}法力)")
            else:
                print(f"{i+1}. {skill} (消耗: {cost}法力)")
        
        try:
            skill_choice = int(input("选择技能 (0-返回): "))
            if skill_choice == 0:
                return self._get_player_action(player, enemy)
            elif 1 <= skill_choice <= len(available_skills):
                return self._execute_skill(player, enemy, available_skills[skill_choice-1])
            else:
                colored_print("❌ 无效选择", Colors.RED)
                return self._handle_skill_action(player, enemy)
        except ValueError:
            colored_print("❌ 请输入数字", Colors.RED)
            return self._handle_skill_action(player, enemy)
    
    def _execute_skill(self, player, enemy, skill_name):
        """Execute a player skill."""
        success, result = player.use_skill(skill_name, enemy)
        
        if success:
            if isinstance(result, tuple):
                # Skill with status effect
                damage, effect = result
                enemy.health -= damage
                colored_print(f"🔮 使用 {skill_name}，对 {enemy.name} 造成 {damage} 点伤害！", 
                            Colors.MAGENTA)
                # Apply status effect with 60% chance
                if random.random() < 0.6:
                    enemy.apply_status_effect(effect, 3)
            elif isinstance(result, int):
                # Pure damage skill
                enemy.health -= result
                colored_print(f"🔮 使用 {skill_name}，对 {enemy.name} 造成 {result} 点伤害！", 
                            Colors.MAGENTA)
            else:
                # Other skill effects
                colored_print(f"🔮 使用 {skill_name}，{result}！", Colors.MAGENTA)
        else:
            colored_print(f"❌ {result}", Colors.RED)
        
        return None
    
    def _handle_enemy_turn(self, player, enemy):
        """
        Handle enemy's turn in combat.
        
        Args:
            player: Player instance
            enemy: Enemy instance
            
        Returns:
            str: "death" if enemy dies, None otherwise
        """
        # Check enemy stun status before processing effects
        enemy_stunned = enemy.is_stunned()
        
        # Process enemy status effects
        enemy.process_status_effects()
        
        # Check if enemy died from status effects
        if enemy.health <= 0:
            return "death"
        
        # Handle enemy action
        if enemy_stunned:
            colored_print(f"⚡ {enemy.name} 被眩晕了，无法行动！", Colors.CYAN)
        else:
            self._execute_enemy_attack(player, enemy)
        
        return None
    
    def _execute_enemy_attack(self, player, enemy):
        """Execute enemy attack on player."""
        if not player.try_dodge():
            enemy_damage = max(1, random.randint(5, enemy.attack) - player.get_defense())
            player.health -= enemy_damage
            colored_print(f"😖 {enemy.name} 对你造成了 {enemy_damage} 点伤害！", Colors.RED)
            player.track_near_death()
    
    def _handle_battle_end(self, player, enemy):
        """
        Handle the end of battle and rewards.
        
        Args:
            player: Player instance
            enemy: Enemy instance
            
        Returns:
            bool or str: True if player wins, "game_over" if player dies
        """
        if player.health <= 0:
            colored_print(f"💀 你被 {enemy.name} 击败了...", Colors.RED)
            return "game_over"
        else:
            # Player victory
            reward = random.randint(10, 30)
            exp_reward = random.randint(20, 40)
            player.gold += reward
            player.gain_exp(exp_reward)
            player.stats["enemies_defeated"] += 1
            player.track_near_death()
            player.check_achievements()
            
            colored_print(f"🎉 击败了 {enemy.name}！获得 {reward} 金币和 {exp_reward} 经验！", 
                         Colors.GREEN)
            
            # Update quest progress
            self._update_quest_progress(player, enemy.name)
            
            return True
    
    def _update_quest_progress(self, player, enemy_name):
        """Update quest progress based on defeated enemy."""
        quest_mappings = {
            "forest": ["🐺 野狼", "🕷️ 巨蜘蛛", "🐻 黑熊"],
            "castle": ["💀 骷髅战士", "🐉 小龙", "👻 幽灵"],
            "volcano": ["🔥 火元素", "🌋 岩浆怪", "🐲 火龙"],
            "ice": ["🧊 冰元素", "🐧 冰企鹅", "🐻‍❄️ 冰熊"]
        }
        
        for quest_type, enemies in quest_mappings.items():
            if enemy_name in enemies:
                player.update_quest(quest_type, enemy_name)
                break
    
    def get_battle_stats(self):
        """Get current battle statistics."""
        return {
            "turn_count": self.turn_count,
            "current_battle": self.current_battle
        }
    
    def reset_battle(self):
        """Reset battle state."""
        self.current_battle = None
        self.turn_count = 0