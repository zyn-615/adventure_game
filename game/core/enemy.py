"""
Enemy class module for the adventure game.

This module contains the Enemy class which handles enemy entities in the game,
including their health, attack, status effects management, and AI decision making.
"""

import random
from .utils import colored_print, Colors


class Enemy:
    """
    Represents an enemy entity in the adventure game.
    
    The Enemy class manages enemy attributes such as health, attack damage,
    and various status effects that can be applied during combat.
    
    Attributes:
        name (str): The name of the enemy
        health (int): Current health points
        max_health (int): Maximum health points
        attack (int): Attack damage value
        status_effects (dict): Dictionary containing status effect data
    """
    
    def __init__(self, name, health, attack):
        """
        Initialize an Enemy instance with AI capabilities.
        
        Args:
            name (str): The name of the enemy
            health (int): Initial health points (also sets max_health)
            attack (int): Attack damage value
        """
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.status_effects = {
            "burn": {"duration": 0, "damage": 5},
            "freeze": {"duration": 0, "slow": True},
            "stun": {"duration": 0, "skip_turn": True},
            "poison": {"duration": 0, "damage": 3}
        }
        
        # AI personality traits
        self.ai_personality = self._generate_ai_personality()
        self.last_player_action = None
        self.consecutive_player_attacks = 0
        
    def _generate_ai_personality(self):
        """Generate AI personality traits for this enemy."""
        personalities = [
            {
                "type": "aggressive",
                "name": "狂暴",
                "description": "优先使用强力攻击，血量低时更加危险",
                "traits": {
                    "aggression": 0.8,
                    "self_preservation": 0.2,
                    "adaptability": 0.4
                }
            },
            {
                "type": "defensive",
                "name": "谨慎",
                "description": "优先自保，会根据玩家状态调整策略",
                "traits": {
                    "aggression": 0.3,
                    "self_preservation": 0.8,
                    "adaptability": 0.7
                }
            },
            {
                "type": "cunning",
                "name": "狡猾",
                "description": "善于利用玩家弱点，会记住玩家行为模式",
                "traits": {
                    "aggression": 0.6,
                    "self_preservation": 0.5,
                    "adaptability": 0.9
                }
            },
            {
                "type": "berserker",
                "name": "狂战士",
                "description": "血量越低攻击越强，不顾防御",
                "traits": {
                    "aggression": 1.0,
                    "self_preservation": 0.1,
                    "adaptability": 0.2
                }
            }
        ]
        
        return random.choice(personalities)
    
    def apply_status_effect(self, effect, duration=3):
        """
        Apply a status effect to the enemy.
        
        Args:
            effect (str): The type of status effect to apply
                         ('burn', 'freeze', 'stun', 'poison')
            duration (int): Duration of the effect in turns (default: 3)
        """
        if effect in self.status_effects:
            self.status_effects[effect]["duration"] = duration
            effect_names = {
                "burn": "🔥 灼烧",
                "freeze": "❄️ 冰冻", 
                "stun": "⚡ 眩晕",
                "poison": "☠️ 中毒"
            }
            effect_name = effect_names.get(effect, effect)
            colored_print(f"✨ {self.name} 获得状态效果: {effect_name} ({duration}回合)", Colors.YELLOW)
    
    def process_status_effects(self):
        """
        Process all active status effects on the enemy.
        
        This method handles damage over time effects, applies movement restrictions,
        and manages the duration of all status effects.
        
        Returns:
            bool: True if any status effects were processed, False otherwise
        """
        messages = []
        
        for effect, data in self.status_effects.items():
            if data["duration"] > 0:
                effect_names = {
                    "burn": "🔥 灼烧",
                    "freeze": "❄️ 冰冻", 
                    "stun": "⚡ 眩晕",
                    "poison": "☠️ 中毒"
                }
                effect_name = effect_names.get(effect, effect)
                
                if effect == "burn" or effect == "poison":
                    damage = data["damage"]
                    self.health -= damage
                    messages.append(f"💔 {self.name} 受到 {effect_name} 伤害: {damage}")
                elif effect == "freeze":
                    messages.append(f"❄️ {self.name} 被冰冻，行动受限")
                elif effect == "stun":
                    messages.append(f"⚡ {self.name} 被眩晕，无法行动")
                
                data["duration"] -= 1
                if data["duration"] <= 0:
                    messages.append(f"⏰ {self.name} 的 {effect_name} 效果结束")
        
        for msg in messages:
            colored_print(msg, Colors.CYAN)
        
        if self.health < 0:
            self.health = 0
            
        return len(messages) > 0
    
    def is_stunned(self):
        """
        Check if the enemy is currently stunned.
        
        Returns:
            bool: True if the enemy is stunned, False otherwise
        """
        return self.status_effects["stun"]["duration"] > 0
    
    def is_frozen(self):
        """
        Check if the enemy is currently frozen.
        
        Returns:
            bool: True if the enemy is frozen, False otherwise
        """
        return self.status_effects["freeze"]["duration"] > 0
        
    def analyze_player_state(self, player):
        """
        Analyze player's current state for AI decision making.
        
        Args:
            player: Player object to analyze
            
        Returns:
            dict: Analysis results
        """
        analysis = {
            "health_ratio": player.health / 100,
            "mana_ratio": player.mana / 50,
            "has_healing_items": "🍞 面包" in player.inventory,
            "active_effects": [],
            "threat_level": "medium",
            "player_level": player.level,
            "has_powerful_weapon": False,
            "has_armor": False,
            "can_use_skills": False,
            "is_vulnerable": False
        }
        
        # Check player's equipment
        if player.equipment.get("weapon") in ["🗡️ 精钢剑", "⚔️ 双手剑", "🏹 长弓"]:
            analysis["has_powerful_weapon"] = True
        if player.equipment.get("armor"):
            analysis["has_armor"] = True
            
        # Check if player can use skills
        analysis["can_use_skills"] = player.mana >= 8
        
        # Check player's active status effects
        for effect, data in player.status_effects.items():
            if data["duration"] > 0:
                analysis["active_effects"].append(effect)
                
        # Check if player is in vulnerable state
        if "stun" in analysis["active_effects"] or "freeze" in analysis["active_effects"]:
            analysis["is_vulnerable"] = True
        
        # More sophisticated threat assessment
        threat_score = 0
        
        # Health factor
        if analysis["health_ratio"] > 0.8:
            threat_score += 3
        elif analysis["health_ratio"] > 0.5:
            threat_score += 2
        elif analysis["health_ratio"] > 0.2:
            threat_score += 1
            
        # Equipment factor
        if analysis["has_powerful_weapon"]:
            threat_score += 2
        if analysis["has_armor"]:
            threat_score += 1
            
        # Level factor
        if player.level >= 5:
            threat_score += 2
        elif player.level >= 3:
            threat_score += 1
            
        # Mana/skills factor
        if analysis["can_use_skills"]:
            threat_score += 1
            
        # Determine threat level
        if threat_score >= 7:
            analysis["threat_level"] = "critical"
        elif threat_score >= 5:
            analysis["threat_level"] = "high"
        elif threat_score >= 3:
            analysis["threat_level"] = "medium"
        elif threat_score >= 1:
            analysis["threat_level"] = "low"
        else:
            analysis["threat_level"] = "minimal"
            
        return analysis
        
    def choose_action(self, player):
        """
        Choose an action based on AI personality and game state.
        
        Args:
            player: Player object to make decision against
            
        Returns:
            dict: Action details
        """
        analysis = self.analyze_player_state(player)
        personality = self.ai_personality["traits"]
        
        # Expanded action set
        actions = [
            {"type": "normal_attack", "weight": 1.0, "damage_multiplier": 1.0},
            {"type": "heavy_attack", "weight": 0.3, "damage_multiplier": 1.5},
            {"type": "defensive_stance", "weight": 0.2, "damage_multiplier": 0.7},
            {"type": "desperate_attack", "weight": 0.1, "damage_multiplier": 2.0},
            {"type": "tactical_retreat", "weight": 0.1, "damage_multiplier": 0.5},
            {"type": "status_focus", "weight": 0.2, "damage_multiplier": 0.8},
            {"type": "opportunistic_strike", "weight": 0.1, "damage_multiplier": 1.8}
        ]
        
        # Advanced action weight adjustments
        self._advanced_action_weights(actions, analysis, personality)
        
        # Choose action based on weights
        total_weight = sum(action["weight"] for action in actions)
        if total_weight <= 0:
            return actions[0]  # Fallback to normal attack
            
        choice = random.uniform(0, total_weight)
        
        for action in actions:
            choice -= action["weight"]
            if choice <= 0:
                return action
                
        return actions[0]  # Fallback
        
    def _advanced_action_weights(self, actions, analysis, personality):
        """Advanced action weight adjustments based on comprehensive analysis."""
        
        # Get current health ratio
        my_health_ratio = self.health / self.max_health
        
        # Map action types to indices for easy access
        action_map = {action["type"]: i for i, action in enumerate(actions)}
        
        # === THREAT LEVEL ADJUSTMENTS ===
        if analysis["threat_level"] == "critical":
            # Facing a very dangerous opponent
            if personality["self_preservation"] > 0.6:
                actions[action_map["defensive_stance"]]["weight"] *= 3.0
                actions[action_map["tactical_retreat"]]["weight"] *= 2.0
            else:
                actions[action_map["desperate_attack"]]["weight"] *= 2.5
                actions[action_map["heavy_attack"]]["weight"] *= 1.8
                
        elif analysis["threat_level"] == "high":
            # Strong opponent, need tactics
            if personality["adaptability"] > 0.7:
                actions[action_map["status_focus"]]["weight"] *= 2.0
                actions[action_map["opportunistic_strike"]]["weight"] *= 1.5
            if personality["aggression"] > 0.7:
                actions[action_map["heavy_attack"]]["weight"] *= 1.5
                
        elif analysis["threat_level"] == "minimal":
            # Weak opponent, be aggressive
            actions[action_map["heavy_attack"]]["weight"] *= 1.8
            actions[action_map["opportunistic_strike"]]["weight"] *= 1.6
            
        # === VULNERABILITY EXPLOITATION ===
        if analysis["is_vulnerable"]:
            # Player is stunned or frozen - capitalize!
            actions[action_map["opportunistic_strike"]]["weight"] *= 4.0
            actions[action_map["heavy_attack"]]["weight"] *= 2.0
            actions[action_map["defensive_stance"]]["weight"] *= 0.1
            
        # === HEALTH-BASED STRATEGIES ===
        if my_health_ratio < 0.3:
            # Low health - desperate measures
            if self.ai_personality["type"] == "berserker":
                actions[action_map["desperate_attack"]]["weight"] *= 3.0
                actions[action_map["heavy_attack"]]["weight"] *= 2.0
            elif personality["self_preservation"] > 0.7:
                actions[action_map["defensive_stance"]]["weight"] *= 2.5
                actions[action_map["tactical_retreat"]]["weight"] *= 2.0
            else:
                actions[action_map["desperate_attack"]]["weight"] *= 1.5
                
        elif my_health_ratio > 0.8:
            # High health - confident
            if personality["aggression"] > 0.5:
                actions[action_map["heavy_attack"]]["weight"] *= 1.3
                actions[action_map["opportunistic_strike"]]["weight"] *= 1.2
                
        # === PLAYER STATE REACTIONS ===
        if analysis["health_ratio"] < 0.2:
            # Player is almost dead
            if personality["aggression"] > 0.5:
                actions[action_map["heavy_attack"]]["weight"] *= 2.0
                actions[action_map["opportunistic_strike"]]["weight"] *= 1.8
            else:
                actions[action_map["normal_attack"]]["weight"] *= 1.5
                
        elif analysis["health_ratio"] > 0.8 and analysis["can_use_skills"]:
            # Player is healthy and dangerous
            if personality["adaptability"] > 0.6:
                actions[action_map["status_focus"]]["weight"] *= 1.8
                actions[action_map["defensive_stance"]]["weight"] *= 1.5
                
        # === EQUIPMENT CONSIDERATIONS ===
        if analysis["has_powerful_weapon"]:
            # Player has dangerous weapon
            if personality["self_preservation"] > 0.5:
                actions[action_map["defensive_stance"]]["weight"] *= 1.5
                actions[action_map["tactical_retreat"]]["weight"] *= 1.3
            elif personality["aggression"] > 0.8:
                actions[action_map["desperate_attack"]]["weight"] *= 1.4
                
        # === BEHAVIORAL PATTERNS ===
        if self.consecutive_player_attacks > 3:
            # Player is being very aggressive
            if personality["adaptability"] > 0.6:
                actions[action_map["defensive_stance"]]["weight"] *= 2.0
                actions[action_map["tactical_retreat"]]["weight"] *= 1.5
            elif self.ai_personality["type"] == "cunning":
                actions[action_map["status_focus"]]["weight"] *= 1.8
                actions[action_map["opportunistic_strike"]]["weight"] *= 1.4
                
        # === HEALING PREVENTION ===
        if analysis["has_healing_items"] and analysis["health_ratio"] < 0.4:
            # Player is low on health and has healing items
            actions[action_map["heavy_attack"]]["weight"] *= 1.6
            actions[action_map["opportunistic_strike"]]["weight"] *= 1.4
            
        # === PERSONALITY-SPECIFIC ADJUSTMENTS ===
        ai_type = self.ai_personality["type"]
        
        if ai_type == "cunning":
            # Cunning enemies prefer status effects and opportunistic strikes
            actions[action_map["status_focus"]]["weight"] *= 1.5
            actions[action_map["opportunistic_strike"]]["weight"] *= 1.3
            
        elif ai_type == "defensive":
            # Defensive enemies prefer safe strategies
            actions[action_map["defensive_stance"]]["weight"] *= 1.8
            actions[action_map["tactical_retreat"]]["weight"] *= 1.4
            actions[action_map["desperate_attack"]]["weight"] *= 0.3
            
        elif ai_type == "aggressive":
            # Aggressive enemies prefer direct attacks
            actions[action_map["heavy_attack"]]["weight"] *= 1.6
            actions[action_map["normal_attack"]]["weight"] *= 1.2
            actions[action_map["tactical_retreat"]]["weight"] *= 0.4
            
        elif ai_type == "berserker":
            # Berserkers become more dangerous when hurt
            damage_bonus = 1.0 + (1.0 - my_health_ratio) * 0.8
            actions[action_map["desperate_attack"]]["weight"] *= damage_bonus
            actions[action_map["heavy_attack"]]["weight"] *= damage_bonus * 0.8
            actions[action_map["defensive_stance"]]["weight"] *= 0.2
            
        # === ZERO OUT NEGATIVE WEIGHTS ===
        for action in actions:
            if action["weight"] < 0:
                action["weight"] = 0
            
    def execute_action(self, player, action):
        """
        Execute the chosen action against the player.
        
        Args:
            player: Player object to attack
            action: Action dict from choose_action
            
        Returns:
            int: Damage dealt
        """
        base_damage = random.randint(5, self.attack)
        final_damage = int(base_damage * action["damage_multiplier"])
        
        # Apply player's defense
        defense = player.get_defense()
        final_damage = max(1, final_damage - defense)
        
        # Execute different action types with enhanced flavor text
        action_type = action["type"]
        
        if action_type == "normal_attack":
            colored_print(f"⚔️ {self.name} 发动普通攻击！", Colors.RED)
            
        elif action_type == "heavy_attack":
            colored_print(f"💥 {self.name} 发动重击！({self.ai_personality['name']})", Colors.RED + Colors.BOLD)
            
        elif action_type == "defensive_stance":
            colored_print(f"🛡️ {self.name} 采取防御姿态！", Colors.YELLOW)
            # Defensive stance may also heal slightly
            if self.health < self.max_health:
                heal_amount = min(5, self.max_health - self.health)
                self.health += heal_amount
                colored_print(f"   🩹 {self.name} 恢复了 {heal_amount} 点生命值", Colors.GREEN)
                
        elif action_type == "desperate_attack":
            colored_print(f"💀 {self.name} 发动拼命攻击！", Colors.RED + Colors.BOLD)
            # Desperate attack may hurt self slightly
            self_damage = random.randint(1, 3)
            self.health -= self_damage
            colored_print(f"   💔 {self.name} 因拼命攻击受到 {self_damage} 点反伤", Colors.RED)
            
        elif action_type == "tactical_retreat":
            colored_print(f"🏃 {self.name} 采取战术后撤！", Colors.CYAN)
            # Tactical retreat may avoid some damage but deals less
            if random.random() < 0.3:
                final_damage = 0
                colored_print(f"   🌪️ {self.name} 完全避开了反击！", Colors.CYAN)
                
        elif action_type == "status_focus":
            colored_print(f"🔮 {self.name} 专注于施加状态效果！", Colors.MAGENTA)
            # Status focus has chance to apply burn or poison
            if random.random() < 0.4:
                effect = random.choice(["burn", "poison"])
                if hasattr(player, 'apply_status_effect'):
                    player.apply_status_effect(effect, 2)
                    colored_print(f"   ✨ {self.name} 对你施加了状态效果！", Colors.MAGENTA)
                    
        elif action_type == "opportunistic_strike":
            colored_print(f"🎯 {self.name} 发动机会攻击！", Colors.YELLOW + Colors.BOLD)
            # Opportunistic strike has higher crit chance
            if random.random() < 0.3:
                final_damage = int(final_damage * 1.5)
                colored_print(f"   💥 暴击！额外伤害！", Colors.YELLOW)
                
        else:
            colored_print(f"⚔️ {self.name} 发动攻击！", Colors.RED)
            
        return final_damage
        
    def update_ai_memory(self, player_action):
        """
        Update AI memory based on player's last action.
        
        Args:
            player_action: The action player just took
        """
        self.last_player_action = player_action
        
        if player_action == "attack":
            self.consecutive_player_attacks += 1
        else:
            self.consecutive_player_attacks = 0
            
    def get_ai_taunt(self):
        """Get a taunt message based on AI personality."""
        taunts = {
            "aggressive": [
                "💀 感受我的怒火！",
                "⚡ 我要撕碎你！",
                "🔥 血战到底！"
            ],
            "defensive": [
                "🛡️ 我不会轻易倒下！",
                "⚖️ 谨慎才能获胜！",
                "🎯 等待最佳时机..."
            ],
            "cunning": [
                "🦊 你的弱点我都看穿了！",
                "🎭 让我们来玩个游戏...",
                "🔍 我在观察你的每一步！"
            ],
            "berserker": [
                "💢 血腥！更多血腥！",
                "⚡ 痛苦让我更强！",
                "🌪️ 毁灭一切！"
            ]
        }
        
        personality_type = self.ai_personality["type"]
        if personality_type in taunts:
            return random.choice(taunts[personality_type])
        return "👹 准备战斗！"