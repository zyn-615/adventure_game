"""
Boss class module for the adventure game.

This module contains the Boss class which extends Enemy with advanced mechanics,
multi-phase battles, special abilities, and strategic combat patterns.
"""

import random
from .enemy import Enemy
from .utils import Colors, colored_print, health_bar


class Boss(Enemy):
    """
    Advanced Boss class with multi-phase battles and special abilities.
    
    Bosses are significantly more challenging enemies with:
    - Multiple combat phases
    - Special abilities and attack patterns
    - Strategic AI that adapts to player behavior
    - Unique mechanics that require tactical thinking
    """
    
    def __init__(self, name, health, attack, boss_type="standard"):
        """
        Initialize a Boss instance.
        
        Args:
            name (str): The boss's name
            health (int): Initial health points
            attack (int): Base attack damage
            boss_type (str): Type of boss determining abilities
        """
        super().__init__(name, health, attack)
        
        # Boss-specific attributes
        self.boss_type = boss_type
        self.phase = 1
        self.max_phase = 3
        self.turn_count = 0
        self.special_cooldown = 0
        self.enrage_triggered = False
        self.abilities_used = []
        
        # Enhanced stats for boss
        self.max_health = int(health * 1.5)  # 50% more health
        self.health = self.max_health
        self.base_attack = attack
        self.attack = int(attack * 1.2)  # 20% more damage
        
        # Phase thresholds
        self.phase_thresholds = [0.66, 0.33, 0.0]  # 66%, 33%, 0% health
        
        # Boss-specific abilities
        self.abilities = self._generate_boss_abilities()
        
        # Strategic patterns
        self.attack_patterns = self._generate_attack_patterns()
        self.current_pattern = 0
        self.pattern_progress = 0
        
    def _generate_boss_abilities(self):
        """Generate boss-specific abilities based on boss type."""
        base_abilities = {
            "cleave": {
                "name": "🌪️ 横扫攻击",
                "description": "对玩家造成150%伤害，无视部分防御",
                "cooldown": 3,
                "damage_multiplier": 1.5,
                "effect": "ignore_defense"
            },
            "intimidate": {
                "name": "😱 威慑咆哮",
                "description": "降低玩家攻击力并可能造成眩晕",
                "cooldown": 4,
                "damage_multiplier": 0.8,
                "effect": "debuff"
            },
            "regenerate": {
                "name": "💚 战斗恢复",
                "description": "恢复自身生命值",
                "cooldown": 5,
                "damage_multiplier": 0.0,
                "effect": "heal"
            },
            "berserker_rage": {
                "name": "💢 狂暴怒火",
                "description": "进入狂暴状态，攻击力大幅提升",
                "cooldown": 6,
                "damage_multiplier": 0.5,
                "effect": "buff"
            },
            "area_attack": {
                "name": "💥 范围攻击",
                "description": "强力范围攻击，难以躲避",
                "cooldown": 4,
                "damage_multiplier": 1.8,
                "effect": "unavoidable"
            },
            "summon_minions": {
                "name": "👹 召唤小兵",
                "description": "召唤小兵协助战斗",
                "cooldown": 7,
                "damage_multiplier": 0.3,
                "effect": "summon"
            },
            "life_drain": {
                "name": "🩸 生命汲取",
                "description": "吸取玩家生命值转化为自己的",
                "cooldown": 5,
                "damage_multiplier": 1.2,
                "effect": "drain"
            },
            "shield_break": {
                "name": "🔨 破盾重击",
                "description": "打破玩家防御并造成巨大伤害",
                "cooldown": 4,
                "damage_multiplier": 2.0,
                "effect": "shield_break"
            }
        }
        
        # Different boss types get different ability sets
        if self.boss_type == "dragon":
            return {
                "cleave": base_abilities["cleave"],
                "berserker_rage": base_abilities["berserker_rage"],
                "area_attack": base_abilities["area_attack"],
                "intimidate": base_abilities["intimidate"]
            }
        elif self.boss_type == "lich":
            return {
                "life_drain": base_abilities["life_drain"],
                "summon_minions": base_abilities["summon_minions"],
                "area_attack": base_abilities["area_attack"],
                "regenerate": base_abilities["regenerate"]
            }
        elif self.boss_type == "giant":
            return {
                "cleave": base_abilities["cleave"],
                "shield_break": base_abilities["shield_break"],
                "intimidate": base_abilities["intimidate"],
                "area_attack": base_abilities["area_attack"]
            }
        else:  # standard boss
            return {
                "cleave": base_abilities["cleave"],
                "intimidate": base_abilities["intimidate"],
                "berserker_rage": base_abilities["berserker_rage"],
                "regenerate": base_abilities["regenerate"]
            }
    
    def _generate_attack_patterns(self):
        """Generate strategic attack patterns for the boss."""
        patterns = [
            {
                "name": "开场试探",
                "sequence": ["normal_attack", "intimidate", "normal_attack"],
                "description": "测试玩家实力的开场模式"
            },
            {
                "name": "连续攻势",
                "sequence": ["heavy_attack", "cleave", "normal_attack"],
                "description": "连续高伤害攻击"
            },
            {
                "name": "战术调整",
                "sequence": ["defensive_stance", "regenerate", "berserker_rage"],
                "description": "恢复并准备强力攻击"
            },
            {
                "name": "终结模式",
                "sequence": ["area_attack", "shield_break", "cleave"],
                "description": "全力以赴的终结攻击"
            }
        ]
        
        # Shuffle patterns for unpredictability
        random.shuffle(patterns)
        return patterns
    
    def get_current_phase(self):
        """Determine current battle phase based on health."""
        health_ratio = self.health / self.max_health
        
        if health_ratio > self.phase_thresholds[0]:
            return 1
        elif health_ratio > self.phase_thresholds[1]:
            return 2
        else:
            return 3
    
    def check_phase_transition(self):
        """Check if boss should transition to next phase."""
        new_phase = self.get_current_phase()
        
        if new_phase > self.phase:
            self.phase = new_phase
            self.on_phase_change()
            return True
        return False
    
    def on_phase_change(self):
        """Handle phase transition effects."""
        colored_print(f"\n🔥 === {self.name} 进入第{self.phase}阶段！ ===", Colors.RED + Colors.BOLD)
        
        if self.phase == 2:
            colored_print(f"💀 {self.name}: 你让我认真起来了！", Colors.RED)
            self.attack = int(self.base_attack * 1.4)  # 40% more damage
            self.special_cooldown = max(0, self.special_cooldown - 1)
            
        elif self.phase == 3:
            colored_print(f"💢 {self.name}: 这是我的真正实力！", Colors.RED + Colors.BOLD)
            self.attack = int(self.base_attack * 1.6)  # 60% more damage
            self.special_cooldown = 0  # Reset cooldown
            self.enrage_triggered = True
            
            # Heal slightly when entering final phase
            heal_amount = int(self.max_health * 0.1)
            self.health = min(self.max_health, self.health + heal_amount)
            colored_print(f"🩹 {self.name} 恢复了 {heal_amount} 生命值！", Colors.RED)
    
    def choose_boss_action(self, player):
        """
        Choose boss action using advanced AI and patterns.
        
        Args:
            player: Player object to make decision against
            
        Returns:
            dict: Action details including special abilities
        """
        self.turn_count += 1
        analysis = self.analyze_player_state(player)
        
        # Check for phase transition
        phase_changed = self.check_phase_transition()
        
        # Reduce cooldowns
        if self.special_cooldown > 0:
            self.special_cooldown -= 1
        
        # Determine if should use special ability
        if self.should_use_special_ability(analysis):
            return self.choose_special_ability(player)
        
        # Use attack pattern system
        if self.should_follow_pattern(analysis):
            return self.get_pattern_action()
        
        # Fall back to enhanced AI decision making
        return self.choose_action(player)
    
    def should_use_special_ability(self, analysis):
        """Determine if boss should use a special ability."""
        if self.special_cooldown > 0:
            return False
        
        # Higher chance in later phases
        base_chance = 0.3 + (self.phase - 1) * 0.2
        
        # More likely when boss is hurt
        health_ratio = self.health / self.max_health
        if health_ratio < 0.5:
            base_chance += 0.3
        
        # More likely against strong opponents
        if analysis["threat_level"] in ["high", "critical"]:
            base_chance += 0.2
        
        return random.random() < base_chance
    
    def choose_special_ability(self, player):
        """Choose which special ability to use."""
        available_abilities = []
        
        for ability_name, ability_data in self.abilities.items():
            if ability_name not in self.abilities_used[-2:]:  # Don't repeat last 2 abilities
                available_abilities.append((ability_name, ability_data))
        
        if not available_abilities:
            available_abilities = list(self.abilities.items())
        
        # Weight abilities based on situation
        weights = []
        for ability_name, ability_data in available_abilities:
            weight = 1.0
            
            # Prefer healing when low on health
            if ability_data["effect"] == "heal" and self.health < self.max_health * 0.4:
                weight *= 3.0
            
            # Prefer damage when player is weak
            player_health_ratio = player.health / 100
            if player_health_ratio < 0.3 and ability_data["damage_multiplier"] > 1.0:
                weight *= 2.0
            
            # Prefer debuffs when player is strong
            if player.level >= 4 and ability_data["effect"] == "debuff":
                weight *= 1.5
            
            weights.append(weight)
        
        # Choose ability based on weights
        total_weight = sum(weights)
        if total_weight > 0:
            choice = random.uniform(0, total_weight)
            for i, weight in enumerate(weights):
                choice -= weight
                if choice <= 0:
                    ability_name, ability_data = available_abilities[i]
                    break
            else:
                ability_name, ability_data = available_abilities[0]
        else:
            ability_name, ability_data = available_abilities[0]
        
        self.abilities_used.append(ability_name)
        self.special_cooldown = ability_data["cooldown"]
        
        return {
            "type": "special_ability",
            "ability": ability_name,
            "ability_data": ability_data,
            "damage_multiplier": ability_data["damage_multiplier"]
        }
    
    def should_follow_pattern(self, analysis):
        """Determine if boss should follow attack pattern."""
        # Follow patterns more in phase 1, less in later phases
        pattern_chance = 0.8 - (self.phase - 1) * 0.2
        
        # Less likely against very strong opponents
        if analysis["threat_level"] == "critical":
            pattern_chance -= 0.3
        
        return random.random() < pattern_chance
    
    def get_pattern_action(self):
        """Get next action from current attack pattern."""
        if self.current_pattern >= len(self.attack_patterns):
            self.current_pattern = 0
            random.shuffle(self.attack_patterns)
        
        pattern = self.attack_patterns[self.current_pattern]
        sequence = pattern["sequence"]
        
        if self.pattern_progress >= len(sequence):
            self.pattern_progress = 0
            self.current_pattern += 1
            if self.current_pattern >= len(self.attack_patterns):
                self.current_pattern = 0
        
        action_name = sequence[self.pattern_progress]
        self.pattern_progress += 1
        
        # Map action names to action types
        if action_name in self.abilities:
            return {
                "type": "special_ability",
                "ability": action_name,
                "ability_data": self.abilities[action_name],
                "damage_multiplier": self.abilities[action_name]["damage_multiplier"]
            }
        else:
            return {
                "type": action_name,
                "damage_multiplier": 1.5 if action_name == "heavy_attack" else 1.0
            }
    
    def execute_boss_action(self, player, action):
        """Execute boss action with special ability handling."""
        if action["type"] == "special_ability":
            return self.execute_special_ability(player, action)
        else:
            return self.execute_action(player, action)
    
    def execute_special_ability(self, player, action):
        """Execute a special boss ability."""
        ability_name = action["ability"]
        ability_data = action["ability_data"]
        
        colored_print(f"\n🌟 {self.name} 使用了 {ability_data['name']}！", Colors.MAGENTA + Colors.BOLD)
        colored_print(f"   {ability_data['description']}", Colors.CYAN)
        
        base_damage = random.randint(int(self.attack * 0.8), int(self.attack * 1.2))
        final_damage = int(base_damage * ability_data["damage_multiplier"])
        
        # Apply special effects
        effect = ability_data["effect"]
        
        if effect == "ignore_defense":
            # Ignore 50% of player defense
            defense = player.get_defense()
            final_damage = max(1, final_damage - int(defense * 0.5))
            colored_print(f"   🔥 攻击无视了部分防御！", Colors.RED)
            
        elif effect == "debuff":
            # Apply debuff to player
            if hasattr(player, 'apply_status_effect'):
                player.apply_status_effect("stun", 1)
                colored_print(f"   😵 你被威慑效果影响！", Colors.RED)
            final_damage = max(1, final_damage - player.get_defense())
            
        elif effect == "heal":
            # Boss heals
            heal_amount = int(self.max_health * 0.15)
            self.health = min(self.max_health, self.health + heal_amount)
            colored_print(f"   💚 {self.name} 恢复了 {heal_amount} 生命值！", Colors.GREEN)
            final_damage = 0
            
        elif effect == "buff":
            # Temporary attack boost
            self.attack = int(self.attack * 1.3)
            colored_print(f"   💪 {self.name} 的攻击力提升了！", Colors.RED)
            final_damage = max(1, final_damage - player.get_defense())
            
        elif effect == "unavoidable":
            # Cannot be dodged
            colored_print(f"   🎯 这次攻击无法躲避！", Colors.RED)
            # Skip dodge check in combat system
            
        elif effect == "drain":
            # Life drain
            defense = player.get_defense()
            final_damage = max(1, final_damage - defense)
            heal_amount = int(final_damage * 0.5)
            self.health = min(self.max_health, self.health + heal_amount)
            colored_print(f"   🩸 {self.name} 吸取了 {heal_amount} 生命值！", Colors.RED)
            
        elif effect == "shield_break":
            # Break player shields/armor temporarily
            if hasattr(player, 'apply_status_effect'):
                # Apply armor break effect
                colored_print(f"   🔨 你的防御被打破了！", Colors.RED)
            final_damage = max(1, final_damage)  # Ignore all defense
            
        elif effect == "summon":
            # Summon effect (visual only for now)
            colored_print(f"   👹 {self.name} 召唤了援军！", Colors.MAGENTA)
            # Add small heal to represent minion support
            self.health = min(self.max_health, self.health + 10)
            final_damage = max(1, final_damage - player.get_defense())
            
        else:
            # Default damage calculation
            final_damage = max(1, final_damage - player.get_defense())
        
        return final_damage
    
    def get_boss_status(self):
        """Get boss status information for display."""
        health_ratio = self.health / self.max_health
        phase_name = ["初始", "愤怒", "狂暴"][self.phase - 1]
        
        status = {
            "name": self.name,
            "health": self.health,
            "max_health": self.max_health,
            "health_ratio": health_ratio,
            "phase": self.phase,
            "phase_name": phase_name,
            "turn_count": self.turn_count,
            "special_cooldown": self.special_cooldown,
            "enrage_triggered": self.enrage_triggered
        }
        
        return status
    
    def display_boss_info(self):
        """Display boss information during combat."""
        status = self.get_boss_status()
        
        # Health bar with phase indication
        health_display = health_bar(self.health, self.max_health, 30)
        colored_print(f"\n👑 {self.name} [{status['phase_name']}阶段]", Colors.RED + Colors.BOLD)
        print(f"   生命值: {health_display}")
        
        # Special cooldown indicator
        if self.special_cooldown > 0:
            colored_print(f"   ⏳ 特殊能力冷却: {self.special_cooldown} 回合", Colors.YELLOW)
        else:
            colored_print(f"   ⚡ 特殊能力就绪！", Colors.MAGENTA)
        
        # Phase warnings
        if self.phase == 2 and not hasattr(self, '_phase2_warned'):
            colored_print(f"   ⚠️ {self.name} 进入愤怒状态！攻击力提升！", Colors.YELLOW)
            self._phase2_warned = True
        elif self.phase == 3 and not hasattr(self, '_phase3_warned'):
            colored_print(f"   ☠️ {self.name} 进入狂暴状态！极度危险！", Colors.RED + Colors.BOLD)
            self._phase3_warned = True