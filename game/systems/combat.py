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
        
        # 显示敌人AI个性
        colored_print(f"💭 {enemy.name} 展现出{enemy.ai_personality['name']}的特质", Colors.MAGENTA)
        colored_print(f"   {enemy.ai_personality['description']}", Colors.CYAN)
        
        # 有概率显示敌人挑衅
        if random.random() < 0.3:
            colored_print(f"🗣️ {enemy.name}: {enemy.get_ai_taunt()}", Colors.YELLOW)
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
        
        # 更新敌人AI记忆
        enemy.update_ai_memory("attack")
        
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
        """Handle player item usage action."""
        usable_items = []
        
        # 检查可用物品
        if "🍞 面包" in player.inventory:
            usable_items.append("🍞 面包")
        if "🧪 神秘药水" in player.inventory:
            usable_items.append("🧪 神秘药水")
            
        if not usable_items:
            colored_print("❌ 没有可用物品", Colors.RED)
            return None
            
        if len(usable_items) == 1:
            # 只有一个物品，直接使用
            item = usable_items[0]
            player.use_item(item)
        else:
            # 多个物品，让玩家选择
            colored_print("选择要使用的物品:", Colors.CYAN)
            for i, item in enumerate(usable_items):
                print(f"{i+1}. {item}")
            print("0. 取消")
            
            try:
                choice = int(input("选择物品 (0-取消): "))
                if choice == 0:
                    colored_print("取消使用物品", Colors.YELLOW)
                    return None
                elif 1 <= choice <= len(usable_items):
                    item = usable_items[choice-1]
                    player.use_item(item)
                else:
                    colored_print("❌ 无效选择", Colors.RED)
                    return None
            except ValueError:
                colored_print("❌ 请输入数字", Colors.RED)
                return None
                
        return None
    
    def _handle_skill_action(self, player, enemy):
        """Handle player skill usage action."""
        if player.mana < 8:
            colored_print("❌ 法力不足", Colors.RED)
            return None
        
        print("\n可用技能:")
        available_skills = []
        for skill, data in player.skills.items():
            if data["level"] > 0 and player.mana >= data["cost"]:
                available_skills.append((skill, data))
        
        if not available_skills:
            colored_print("❌ 没有可用技能", Colors.RED)
            return None
        
        for i, (skill, data) in enumerate(available_skills):
            print(f"{i+1}. {skill} (消耗 {data['cost']} 法力)")
        
        try:
            choice = int(input("选择技能 (0-返回): "))
            if 1 <= choice <= len(available_skills):
                skill, data = available_skills[choice-1]
                player.mana -= data["cost"]
                player.stats["skills_used"] += 1
                
                if data["effect"] == "heal":
                    player.health = min(100, player.health + data["heal"])
                    colored_print(f"💚 使用了 {skill}，恢复 {data['heal']} 生命值！", Colors.GREEN)
                else:
                    damage = data["damage"]
                    enemy.health -= damage
                    colored_print(f"✨ 使用了 {skill}，对 {enemy.name} 造成 {damage} 点伤害！", Colors.CYAN)
                    
                    # 应用状态效果
                    if data["effect"] != "heal" and random.random() < 0.6:
                        enemy.apply_status_effect(data["effect"])
                
                # 更新敌人AI记忆
                enemy.update_ai_memory("skill")
                
            elif choice == 0:
                return self._get_player_action(player, enemy)
            else:
                colored_print("❌ 无效选择", Colors.RED)
                return self._handle_skill_action(player, enemy)
        except ValueError:
            colored_print("❌ 请输入数字", Colors.RED)
            return self._handle_skill_action(player, enemy)
        
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
        """Execute enemy attack on player using AI decision making."""
        # 让敌人选择行动
        action = enemy.choose_action(player)
        damage = enemy.execute_action(player, action)
        
        # 应用伤害
        if not player.try_dodge():
            player.health -= damage
            colored_print(f"😖 对你造成了 {damage} 点伤害！", Colors.RED)
            player.track_near_death()
        else:
            colored_print(f"🌟 你躲避了攻击！", Colors.GREEN)
    
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
            # Player victory - 平衡奖励系统
            # 基础奖励
            base_gold = 15
            base_exp = 25
            
            # 根据敌人血量调整奖励
            health_multiplier = max(1.0, enemy.max_health / 50)
            
            # 根据敌人攻击力调整奖励
            attack_multiplier = max(1.0, enemy.attack / 20)
            
            # 计算最终奖励
            reward = int(base_gold * health_multiplier * attack_multiplier)
            exp_reward = int(base_exp * health_multiplier * attack_multiplier * 0.8)
            
            # 添加随机变化
            reward += random.randint(-5, 10)
            exp_reward += random.randint(-5, 15)
            
            # 确保最小奖励
            reward = max(10, reward)
            exp_reward = max(15, exp_reward)
            
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