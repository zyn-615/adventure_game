"""
Boss Combat System - Enhanced combat mechanics for boss battles
"""

import random
from ..core.boss import Boss
from ..core.utils import Colors, colored_print, health_bar
from .combat import CombatSystem


class BossCombatSystem(CombatSystem):
    """
    Enhanced combat system specifically for boss battles.
    
    Features:
    - Multi-phase boss mechanics
    - Special ability management
    - Strategic turn-based combat
    - Enhanced player options during boss fights
    """
    
    def __init__(self):
        super().__init__()
        self.boss_defeated = []
        self.current_boss = None
        
    def start_boss_battle(self, player, boss_name, boss_health, boss_attack, boss_type="standard"):
        """
        Start a boss battle with enhanced mechanics.
        
        Args:
            player: Player instance
            boss_name: Name of the boss
            boss_health: Boss health points
            boss_attack: Boss attack damage
            boss_type: Type of boss (dragon, lich, giant, standard)
            
        Returns:
            str: Battle result
        """
        colored_print(f"\n🏰 === 💀 BOSS战斗开始！ 💀 ===", Colors.RED + Colors.BOLD)
        colored_print(f"🎯 挑战者: {boss_name}", Colors.RED)
        
        # Create boss instance
        boss = Boss(boss_name, boss_health, boss_attack, boss_type)
        self.current_boss = boss
        
        # Display boss introduction
        self._display_boss_introduction(boss)
        
        # Pre-battle preparation
        self._boss_battle_preparation(player, boss)
        
        # Main boss battle loop
        result = self._boss_battle_loop(player, boss)
        
        # Post-battle cleanup
        self._boss_battle_cleanup(player, boss, result)
        
        return result
    
    def _display_boss_introduction(self, boss):
        """Display boss introduction and warnings."""
        colored_print(f"\n💀 {boss.name} 出现了！", Colors.RED + Colors.BOLD)
        
        # Boss type specific introductions
        if boss.boss_type == "dragon":
            colored_print("🐉 古老的龙族统治者苏醒了！", Colors.RED)
            colored_print("   它的怒火将焚烧一切！", Colors.YELLOW)
        elif boss.boss_type == "lich":
            colored_print("💀 不死的法师从深渊中崛起！", Colors.MAGENTA)
            colored_print("   死亡的力量在它身边环绕！", Colors.CYAN)
        elif boss.boss_type == "giant":
            colored_print("🏔️ 山岳般的巨人屹立在你面前！", Colors.BLUE)
            colored_print("   大地在它的脚步声中颤抖！", Colors.YELLOW)
        else:
            colored_print("👑 强大的敌人挡住了你的去路！", Colors.RED)
            colored_print("   这将是一场艰苦的战斗！", Colors.YELLOW)
        
        # Display boss stats
        boss.display_boss_info()
        
        # Warning message
        colored_print("\n⚠️ 警告：Boss战斗具有多个阶段，需要策略性战斗！", Colors.YELLOW + Colors.BOLD)
        colored_print("💡 提示：合理使用技能、物品和防御来获得胜利！", Colors.CYAN)
    
    def _boss_battle_preparation(self, player, boss):
        """Allow player to prepare before boss battle."""
        colored_print("\n🛡️ 战斗准备阶段", Colors.CYAN + Colors.BOLD)
        colored_print("你可以在战斗开始前做最后的准备...", Colors.CYAN)
        
        while True:
            print("\n选择准备行动:")
            print("1. 🍞 使用治疗物品")
            print("2. 🔮 查看技能状态")
            print("3. 🎒 检查装备")
            print("4. 🐾 宠物准备")
            print("5. ⚔️ 开始战斗！")
            
            try:
                choice = input("选择 (1-5): ")
                
                if choice == "1":
                    self._use_preparation_item(player)
                elif choice == "2":
                    self._display_skill_status(player)
                elif choice == "3":
                    self._display_equipment_status(player)
                elif choice == "4":
                    self._pet_preparation(player)
                elif choice == "5":
                    colored_print("⚔️ 战斗开始！", Colors.RED + Colors.BOLD)
                    break
                else:
                    colored_print("❌ 无效选择", Colors.RED)
            except (ValueError, EOFError):
                colored_print("❌ 请输入有效数字", Colors.RED)
    
    def _use_preparation_item(self, player):
        """Allow player to use items before battle."""
        if "🍞 面包" in player.inventory:
            old_health = player.health
            player.health = min(100, player.health + 30)
            player.inventory.remove("🍞 面包")
            heal_amount = player.health - old_health
            colored_print(f"🍞 使用了面包，恢复了 {heal_amount} 生命值！", Colors.GREEN)
        else:
            colored_print("❌ 没有可用的治疗物品", Colors.RED)
    
    def _display_skill_status(self, player):
        """Display player's skill status."""
        colored_print(f"\n🔮 法力值: {player.mana}/50", Colors.MAGENTA)
        colored_print("可用技能:", Colors.CYAN)
        
        for skill, data in player.skills.items():
            if data["level"] > 0:
                status = "✅ 可用" if player.mana >= data["cost"] else "❌ 法力不足"
                colored_print(f"   {skill}: {status} (消耗: {data['cost']} 法力)", Colors.CYAN)
    
    def _display_equipment_status(self, player):
        """Display player's equipment status."""
        colored_print("\n🎒 装备状态:", Colors.BLUE)
        for slot, item in player.equipment.items():
            if item:
                colored_print(f"   {slot}: {item}", Colors.BLUE)
            else:
                colored_print(f"   {slot}: 无", Colors.YELLOW)
    
    def _pet_preparation(self, player):
        """Handle pet preparation."""
        if player.active_pet:
            colored_print(f"\n🐾 活跃宠物: {player.active_pet.get_display_name()}", Colors.GREEN)
            colored_print(f"   等级: {player.active_pet.level} | 忠诚度: {player.active_pet.loyalty}", Colors.GREEN)
            
            # Option to feed pet
            if "🍞 面包" in player.inventory and player.active_pet.loyalty < 100:
                feed = input("是否喂养宠物提升忠诚度？(y/n): ")
                if feed.lower() == 'y':
                    player.inventory.remove("🍞 面包")
                    player.active_pet.loyalty = min(100, player.active_pet.loyalty + 20)
                    colored_print("🐾 宠物忠诚度提升了！", Colors.GREEN)
        else:
            colored_print("❌ 没有活跃宠物", Colors.RED)
    
    def _boss_battle_loop(self, player, boss):
        """Main boss battle loop with enhanced mechanics."""
        turn_count = 0
        
        while boss.health > 0 and player.health > 0:
            turn_count += 1
            colored_print(f"\n{'='*50}", Colors.BOLD)
            colored_print(f"⚔️ 第 {turn_count} 回合", Colors.BOLD + Colors.YELLOW)
            colored_print(f"{'='*50}", Colors.BOLD)
            
            # Process player turn
            result = self._process_boss_player_turn(player, boss)
            if result:
                return result
            
            # Check if boss is defeated
            if boss.health <= 0:
                break
            
            # Process boss turn
            result = self._process_boss_enemy_turn(player, boss)
            if result:
                return result
            
            # Display turn summary
            self._display_turn_summary(player, boss, turn_count)
        
        # Determine battle outcome
        if player.health <= 0:
            return "game_over"
        elif boss.health <= 0:
            return "victory"
        else:
            return "draw"
    
    def _process_boss_player_turn(self, player, boss):
        """Process player's turn in boss battle."""
        colored_print(f"\n🛡️ === 你的回合 ===", Colors.BLUE + Colors.BOLD)
        
        # Check player stun status
        player_stunned = player.is_stunned()
        
        # Process player status effects
        player.process_status_effects()
        
        if player.health <= 0:
            return "game_over"
        
        # Player action
        if player_stunned:
            colored_print("⚡ 你被眩晕了，无法行动！", Colors.RED)
            return None
        
        # Enhanced player options for boss battles
        return self._get_boss_player_action(player, boss)
    
    def _get_boss_player_action(self, player, boss):
        """Get player action with enhanced boss battle options."""
        while True:
            print(f"\n选择行动:")
            print("1. ⚔️ 攻击")
            print("2. 🛡️ 防御")
            print("3. 🍞 使用物品")
            print("4. 🔮 使用技能")
            print("5. 🐾 宠物行动")
            print("6. 📊 查看状态")
            print("7. 🏃 逃跑")
            
            try:
                choice = input("选择 (1-7): ")
                
                if choice == "1":
                    return self._boss_attack_action(player, boss)
                elif choice == "2":
                    return self._boss_defense_action(player, boss)
                elif choice == "3":
                    return self._boss_item_action(player, boss)
                elif choice == "4":
                    return self._boss_skill_action(player, boss)
                elif choice == "5":
                    return self._boss_pet_action(player, boss)
                elif choice == "6":
                    self._display_battle_status(player, boss)
                    continue
                elif choice == "7":
                    return self._boss_flee_action(player, boss)
                else:
                    colored_print("❌ 无效选择", Colors.RED)
                    continue
            except (ValueError, EOFError):
                colored_print("❌ 请输入有效数字", Colors.RED)
                continue
    
    def _boss_attack_action(self, player, boss):
        """Handle player attack with critical hit chance."""
        damage = player.get_attack_damage()
        
        # Critical hit chance
        crit_chance = 0.15
        if player.active_pet and player.active_pet.pet_type == "🐱 猫":
            crit_chance += 0.1
        
        if random.random() < crit_chance:
            damage = int(damage * 1.5)
            colored_print(f"💥 暴击！你对 {boss.name} 造成了 {damage} 点伤害！", Colors.YELLOW + Colors.BOLD)
        else:
            colored_print(f"⚔️ 你对 {boss.name} 造成了 {damage} 点伤害！", Colors.YELLOW)
        
        boss.health -= damage
        boss.update_ai_memory("attack")
        return None
    
    def _boss_defense_action(self, player, boss):
        """Handle player defense action."""
        colored_print("🛡️ 你采取了防御姿态！", Colors.CYAN)
        
        # Defensive stance provides temporary benefits
        if hasattr(player, 'apply_status_effect'):
            player.apply_status_effect("shield", 2)
        
        # Small heal if player has regeneration ability
        if random.random() < 0.3:
            heal = random.randint(5, 10)
            player.health = min(100, player.health + heal)
            colored_print(f"🩹 专注防御让你恢复了 {heal} 生命值！", Colors.GREEN)
        
        return None
    
    def _boss_item_action(self, player, boss):
        """Handle player item usage."""
        if "🍞 面包" in player.inventory:
            old_health = player.health
            player.health = min(100, player.health + 30)
            player.inventory.remove("🍞 面包")
            heal_amount = player.health - old_health
            colored_print(f"🍞 使用了面包，恢复了 {heal_amount} 生命值！", Colors.GREEN)
        else:
            colored_print("❌ 没有可用物品", Colors.RED)
        return None
    
    def _boss_skill_action(self, player, boss):
        """Handle player skill usage with enhanced effects."""
        available_skills = []
        for skill, data in player.skills.items():
            if data["level"] > 0 and player.mana >= data["cost"]:
                available_skills.append((skill, data))
        
        if not available_skills:
            colored_print("❌ 没有可用技能", Colors.RED)
            return None
        
        print("\n可用技能:")
        for i, (skill, data) in enumerate(available_skills):
            print(f"{i+1}. {skill} (消耗: {data['cost']} 法力)")
        
        try:
            choice = int(input("选择技能 (0-返回): "))
            if choice == 0:
                return self._get_boss_player_action(player, boss)
            elif 1 <= choice <= len(available_skills):
                skill, data = available_skills[choice-1]
                return self._execute_boss_skill(player, boss, skill, data)
            else:
                colored_print("❌ 无效选择", Colors.RED)
                return self._get_boss_player_action(player, boss)
        except (ValueError, EOFError):
            colored_print("❌ 请输入有效数字", Colors.RED)
            return self._get_boss_player_action(player, boss)
    
    def _execute_boss_skill(self, player, boss, skill, data):
        """Execute player skill against boss."""
        player.mana -= data["cost"]
        player.stats["skills_used"] += 1
        
        if data["effect"] == "heal":
            old_health = player.health
            player.health = min(100, player.health + data["heal"])
            heal_amount = player.health - old_health
            colored_print(f"💚 使用了 {skill}，恢复了 {heal_amount} 生命值！", Colors.GREEN)
        else:
            damage = data["damage"]
            
            # Enhanced damage against bosses
            if boss.phase >= 2:
                damage = int(damage * 1.1)  # 10% bonus in later phases
            
            boss.health -= damage
            colored_print(f"✨ 使用了 {skill}，对 {boss.name} 造成了 {damage} 点伤害！", Colors.CYAN)
            
            # Apply status effects with higher success rate against bosses
            if data["effect"] != "heal" and random.random() < 0.7:
                boss.apply_status_effect(data["effect"], 2)
        
        boss.update_ai_memory("skill")
        return None
    
    def _boss_pet_action(self, player, boss):
        """Handle pet action in boss battle."""
        if not player.active_pet:
            colored_print("❌ 没有活跃宠物", Colors.RED)
            return None
        
        pet = player.active_pet
        colored_print(f"🐾 {pet.get_display_name()} 行动！", Colors.GREEN)
        
        # Pet special abilities are more effective against bosses
        if pet.loyalty > 70 and random.random() < 0.6:
            result = pet.use_special_ability(player)
            if result:
                colored_print(f"   {result}", Colors.GREEN)
        
        # Pet attack
        pet_damage = random.randint(5, 15) + pet.level
        boss.health -= pet_damage
        colored_print(f"🐾 {pet.name} 对 {boss.name} 造成了 {pet_damage} 点伤害！", Colors.GREEN)
        
        # Pet gains experience
        pet.gain_exp(5)
        
        return None
    
    def _display_battle_status(self, player, boss):
        """Display current battle status."""
        colored_print("\n📊 === 战斗状态 ===", Colors.CYAN + Colors.BOLD)
        
        # Player status
        colored_print(f"🛡️ 你的状态:", Colors.BLUE)
        print(f"   生命值: {health_bar(player.health, 100)}")
        print(f"   法力值: {player.mana}/50")
        print(f"   等级: {player.level}")
        
        # Boss status
        boss.display_boss_info()
        
        # Active effects
        player_effects = [effect for effect, data in player.status_effects.items() if data["duration"] > 0]
        boss_effects = [effect for effect, data in boss.status_effects.items() if data["duration"] > 0]
        
        if player_effects:
            colored_print(f"   你的状态效果: {', '.join(player_effects)}", Colors.MAGENTA)
        if boss_effects:
            colored_print(f"   {boss.name} 的状态效果: {', '.join(boss_effects)}", Colors.MAGENTA)
    
    def _boss_flee_action(self, player, boss):
        """Handle flee attempt from boss battle."""
        colored_print("🏃 试图逃离boss战斗...", Colors.YELLOW)
        
        # Boss battles are harder to flee from
        flee_chance = 0.3
        if player.level >= boss.phase + 2:
            flee_chance = 0.5
        
        if random.random() < flee_chance:
            colored_print("🏃 成功逃脱了！但是错过了击败boss的机会...", Colors.GREEN)
            return "flee"
        else:
            colored_print("💨 逃跑失败！Boss挡住了你的去路！", Colors.RED)
            return None
    
    def _process_boss_enemy_turn(self, player, boss):
        """Process boss's turn with enhanced AI."""
        colored_print(f"\n👑 === {boss.name} 的回合 ===", Colors.RED + Colors.BOLD)
        
        # Check boss stun status
        boss_stunned = boss.is_stunned()
        
        # Process boss status effects
        boss.process_status_effects()
        
        if boss.health <= 0:
            return "victory"
        
        # Boss action
        if boss_stunned:
            colored_print(f"⚡ {boss.name} 被眩晕了，无法行动！", Colors.CYAN)
            return None
        
        # Boss uses enhanced AI
        action = boss.choose_boss_action(player)
        damage = boss.execute_boss_action(player, action)
        
        # Apply damage with dodge chance
        if action.get("ability_data", {}).get("effect") != "unavoidable":
            if not player.try_dodge():
                player.health -= damage
                if damage > 0:
                    colored_print(f"😖 你受到了 {damage} 点伤害！", Colors.RED)
                player.track_near_death()
            else:
                colored_print(f"🌟 你躲避了攻击！", Colors.GREEN)
        else:
            # Unavoidable attack
            player.health -= damage
            if damage > 0:
                colored_print(f"😖 你受到了 {damage} 点不可避免的伤害！", Colors.RED)
            player.track_near_death()
        
        if player.health <= 0:
            return "game_over"
        
        return None
    
    def _display_turn_summary(self, player, boss, turn_count):
        """Display summary at end of turn."""
        colored_print(f"\n📋 回合 {turn_count} 结束", Colors.CYAN)
        
        # Health status
        player_health_percent = int((player.health / 100) * 100)
        boss_health_percent = int((boss.health / boss.max_health) * 100)
        
        print(f"   你的生命值: {player_health_percent}%")
        print(f"   {boss.name} 生命值: {boss_health_percent}%")
        
        # Phase transitions
        if boss.check_phase_transition():
            colored_print(f"   🔥 {boss.name} 阶段转换！", Colors.RED)
    
    def _boss_battle_cleanup(self, player, boss, result):
        """Handle post-battle cleanup and rewards."""
        if result == "victory":
            self._handle_boss_victory(player, boss)
        elif result == "game_over":
            self._handle_boss_defeat(player, boss)
        elif result == "flee":
            self._handle_boss_flee(player, boss)
        
        self.current_boss = None
    
    def _handle_boss_victory(self, player, boss):
        """Handle boss victory rewards."""
        colored_print(f"\n🎉 === 胜利！ ===", Colors.GREEN + Colors.BOLD)
        colored_print(f"💀 你击败了 {boss.name}！", Colors.GREEN)
        
        # Calculate rewards based on boss difficulty
        base_reward = 100
        phase_bonus = boss.phase * 50
        turn_bonus = max(0, 100 - boss.turn_count * 2)  # Faster victory = better reward
        
        gold_reward = base_reward + phase_bonus + turn_bonus
        exp_reward = 50 + boss.phase * 25
        
        player.gold += gold_reward
        player.gain_exp(exp_reward)
        player.stats["enemies_defeated"] += 1
        
        colored_print(f"💰 获得金币: {gold_reward}", Colors.YELLOW)
        colored_print(f"✨ 获得经验: {exp_reward}", Colors.CYAN)
        
        # Boss-specific rewards
        if boss.boss_type == "dragon":
            special_item = "🐉 龙鳞护甲"
        elif boss.boss_type == "lich":
            special_item = "💀 死灵法杖"
        elif boss.boss_type == "giant":
            special_item = "🏔️ 巨人之锤"
        else:
            special_item = "👑 王者徽章"
        
        player.inventory.append(special_item)
        colored_print(f"🎁 获得特殊物品: {special_item}", Colors.MAGENTA)
        
        # Add boss to defeated list
        self.boss_defeated.append(boss.name)
        
        # Check achievements
        player.check_achievements()
    
    def _handle_boss_defeat(self, player, boss):
        """Handle boss defeat."""
        colored_print(f"\n💀 === 失败... ===", Colors.RED + Colors.BOLD)
        colored_print(f"👑 {boss.name} 战胜了你！", Colors.RED)
        colored_print("🔄 重新挑战需要更好的策略和装备！", Colors.YELLOW)
    
    def _handle_boss_flee(self, player, boss):
        """Handle fleeing from boss."""
        colored_print(f"\n🏃 === 逃脱 ===", Colors.YELLOW + Colors.BOLD)
        colored_print(f"你逃离了与 {boss.name} 的战斗", Colors.YELLOW)
        colored_print("💭 下次再来挑战吧！", Colors.CYAN)