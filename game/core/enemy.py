"""
Enemy class module for the adventure game.

This module contains the Enemy class which handles enemy entities in the game,
including their health, attack, and status effects management.
"""

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
        Initialize an Enemy instance.
        
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