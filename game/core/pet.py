"""
Pet Module - Pet class for adventure games
"""

import random
from .utils import Colors, colored_print


class Pet:
    """
    A pet companion class for adventure games
    
    Attributes:
        name (str): The pet's name
        pet_type (str): The type of pet (with emoji)
        level (int): Current level of the pet
        exp (int): Current experience points
        loyalty (int): Loyalty level (0-100)
        abilities (dict): Pet's abilities based on type
    """
    
    def __init__(self, name, pet_type, level=1):
        """
        Initialize a new pet
        
        Args:
            name (str): The pet's name
            pet_type (str): The type of pet
            level (int, optional): Starting level. Defaults to 1.
        """
        self.name = name
        self.pet_type = pet_type
        self.level = level
        self.exp = 0
        self.loyalty = 50
        self.abilities = self.get_abilities()
    
    def get_abilities(self):
        """
        Get abilities based on pet type
        
        Returns:
            dict: Dictionary containing the pet's abilities
        """
        abilities = {
            "🐺 幼狼": {"attack_boost": 5, "special": "howl"},
            "🐉 小龙": {"attack_boost": 10, "special": "flame"},
            "🦅 鹰": {"dodge_boost": 0.05, "special": "scout"},
            "🐻 熊崽": {"defense_boost": 3, "special": "shield"},
            "🐱 猫": {"crit_boost": 0.03, "special": "stealth"}
        }
        return abilities.get(self.pet_type, {"attack_boost": 2})
    
    def level_up(self):
        """
        Level up the pet if it has enough experience
        
        Returns:
            bool: True if level up occurred, False otherwise
        """
        if self.exp >= 100:
            self.level += 1
            self.exp -= 100
            self.loyalty = min(100, self.loyalty + 5)
            colored_print(f"🎉 {self.name} 升级到 {self.level} 级！", Colors.GREEN)
            return True
        return False
    
    def gain_exp(self, amount):
        """
        Add experience points to the pet and check for level up
        
        Args:
            amount (int): Amount of experience to add
        """
        self.exp += amount
        self.level_up()
    
    def use_special_ability(self, battle_context=None):
        """
        Use the pet's special ability
        
        Args:
            battle_context (optional): Context for battle situations
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if self.loyalty < 30:
            return False, "宠物忠诚度不足"
        
        ability = self.abilities.get("special")
        if ability == "howl":
            return True, "嗥叫增强士气，下次攻击伤害+50%"
        elif ability == "flame":
            return True, "喷火攻击，造成额外15点伤害"
        elif ability == "scout":
            return True, "侦查发现宝藏，获得额外20金币"
        elif ability == "shield":
            return True, "护盾保护，减少50%伤害"
        elif ability == "stealth":
            return True, "潜行攻击，下次攻击必定暴击"
        
        return False, "未知能力"
    
    def get_display_name(self):
        """
        Get the formatted display name of the pet
        
        Returns:
            str: Formatted pet name with type and level
        """
        return f"{self.pet_type} {self.name} (Lv.{self.level})"


# Example usage and testing
if __name__ == "__main__":
    # Create a sample pet
    pet = Pet("小火", "🐉 小龙")
    
    print("Pet Created:")
    print(f"Name: {pet.get_display_name()}")
    print(f"Abilities: {pet.abilities}")
    print(f"Loyalty: {pet.loyalty}")
    
    # Test gaining experience
    print("\nGaining experience...")
    pet.gain_exp(50)
    print(f"Experience: {pet.exp}/100")
    
    # Test special ability
    print("\nUsing special ability...")
    success, message = pet.use_special_ability()
    print(f"Success: {success}, Message: {message}")
    
    # Test level up
    print("\nGaining more experience...")
    pet.gain_exp(60)
    print(f"New level: {pet.level}")
    print(f"Experience: {pet.exp}/100")
    print(f"Loyalty: {pet.loyalty}")