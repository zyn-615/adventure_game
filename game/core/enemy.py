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
            "threat_level": "medium"
        }
        
        # Check player's active status effects
        for effect, data in player.status_effects.items():
            if data["duration"] > 0:
                analysis["active_effects"].append(effect)
        
        # Determine threat level
        if analysis["health_ratio"] < 0.3:
            analysis["threat_level"] = "low"
        elif analysis["health_ratio"] > 0.7 and analysis["mana_ratio"] > 0.5:
            analysis["threat_level"] = "high"
        elif player.active_pet and player.active_pet.loyalty > 70:
            analysis["threat_level"] = "high"
            
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
        
        # Base actions available
        actions = [
            {"type": "normal_attack", "weight": 1.0, "damage_multiplier": 1.0},
            {"type": "heavy_attack", "weight": 0.3, "damage_multiplier": 1.5},
            {"type": "defensive_stance", "weight": 0.2, "damage_multiplier": 0.7}
        ]
        
        # Modify action weights based on personality and situation
        self._adjust_action_weights(actions, analysis, personality)
        
        # Choose action based on weights
        total_weight = sum(action["weight"] for action in actions)
        choice = random.uniform(0, total_weight)
        
        for action in actions:
            choice -= action["weight"]
            if choice <= 0:
                return action
                
        return actions[0]  # Fallback
        
    def _adjust_action_weights(self, actions, analysis, personality):
        """Adjust action weights based on AI analysis."""
        
        # Aggressive personalities prefer heavy attacks
        if personality["aggression"] > 0.6:
            actions[1]["weight"] *= 1.5  # Heavy attack
            
        # Defensive personalities prefer defensive stance when threatened
        if personality["self_preservation"] > 0.6 and analysis["threat_level"] == "high":
            actions[2]["weight"] *= 2.0  # Defensive stance
            
        # Cunning enemies adapt to player behavior
        if personality["adaptability"] > 0.7:
            if self.consecutive_player_attacks > 2:
                actions[2]["weight"] *= 1.8  # Become more defensive
            if analysis["health_ratio"] < 0.4:
                actions[1]["weight"] *= 1.3  # Desperate heavy attacks
                
        # Berserker behavior - more aggressive when low on health
        if self.ai_personality["type"] == "berserker":
            health_ratio = self.health / self.max_health
            if health_ratio < 0.5:
                actions[1]["weight"] *= (1.0 + (1.0 - health_ratio))
                
        # React to player's low health
        if analysis["health_ratio"] < 0.3:
            if personality["aggression"] > 0.5:
                actions[1]["weight"] *= 1.4  # Finish them off
            else:
                actions[0]["weight"] *= 1.2  # Play it safe
                
        # React to player having healing items
        if analysis["has_healing_items"] and personality["adaptability"] > 0.5:
            actions[1]["weight"] *= 1.2  # Try to prevent healing
            
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
        
        # Execute action with flavor text
        if action["type"] == "normal_attack":
            colored_print(f"⚔️ {self.name} 发动普通攻击！", Colors.RED)
        elif action["type"] == "heavy_attack":
            colored_print(f"💥 {self.name} 发动重击！({self.ai_personality['name']})", Colors.RED + Colors.BOLD)
        elif action["type"] == "defensive_stance":
            colored_print(f"🛡️ {self.name} 采取防御姿态！", Colors.YELLOW)
            
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