"""
Player Module - Main player class for adventure games

This module contains the Player class which manages:
- Player stats (health, mana, gold, level, experience)
- Inventory and equipment management
- Skills and abilities system
- Status effects system
- Pet management
- Quest system
- Achievement system
- Save/load functionality

Dependencies:
    - utils: For Colors, colored_print, health_bar
    - pet: For Pet class
    - random: For randomized events and combat
    - json: For save/load functionality
    - os: For file operations
"""

import random
import json
import os

# Handle relative imports
try:
    from .utils import Colors, colored_print, health_bar
    from .pet import Pet
except ImportError:
    # Standalone execution - adjust path and import
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from game.core.utils import Colors, colored_print, health_bar
    from game.core.pet import Pet


class Player:
    """
    Main player class for adventure games
    
    This class handles all player-related functionality including:
    - Character stats and progression
    - Inventory and equipment management
    - Skills and magic system
    - Status effects and combat
    - Pet management
    - Quest and achievement tracking
    - Game save/load functionality
    """
    
    def __init__(self, name):
        """
        Initialize a new player character
        
        Args:
            name (str): The player's name
        """
        self.name = name
        self.health = 100
        self.gold = 50
        self.inventory = ["🗡️ 木剑", "🍞 面包"]
        self.level = 1
        self.exp = 0
        self.skills = {
            "🔥 火球术": {"level": 1, "cost": 10, "damage": 30, "effect": "burn"},
            "❄️ 冰冻术": {"level": 0, "cost": 15, "damage": 25, "effect": "freeze"},
            "⚡ 闪电术": {"level": 0, "cost": 20, "damage": 40, "effect": "stun"},
            "💚 治疗术": {"level": 1, "cost": 8, "heal": 25, "effect": "heal"},
            "🛡️ 护盾术": {"level": 0, "cost": 12, "effect": "shield"}
        }
        self.mana = 50
        self.equipment = {
            "weapon": "🗡️ 木剑",
            "armor": None,
            "accessory": None
        }
        self.quests = {
            "🐺 森林清理": {"completed": False, "progress": 0, "target": 3, "reward": 100},
            "🏰 古堡探索": {"completed": False, "progress": 0, "target": 1, "reward": 200},
            "💎 宝石收集": {"completed": False, "progress": 0, "target": 2, "reward": 150},
            "🌋 火山征服": {"completed": False, "progress": 0, "target": 2, "reward": 300},
            "❄️ 冰窟探险": {"completed": False, "progress": 0, "target": 1, "reward": 250}
        }
        self.current_save_slot = None  # 记录当前使用的存档槽位
        self.achievements = {
            "🏆 初出茅庐": {"description": "击败第一个敌人", "completed": False},
            "💰 小富翁": {"description": "拥有超过500金币", "completed": False},
            "⚔️ 战士": {"description": "击败50个敌人", "completed": False},
            "🌟 传奇": {"description": "达到10级", "completed": False},
            "🛡️ 坚韧": {"description": "生命值降到10以下并存活", "completed": False},
            "🔮 法师": {"description": "使用技能50次", "completed": False},
            "🏪 购物狂": {"description": "购买20件物品", "completed": False},
            "💎 收藏家": {"description": "拥有5个宝石", "completed": False},
            "🎯 完美主义": {"description": "完成所有任务", "completed": False},
            "🌈 幸运儿": {"description": "触发10次随机事件", "completed": False}
        }
        self.stats = {
            "enemies_defeated": 0,
            "skills_used": 0,
            "items_bought": 0,
            "random_events": 0,
            "near_death_survived": 0
        }
        # 状态效果系统
        self.status_effects = {
            "burn": {"duration": 0, "damage": 5},      # 灼烧：持续伤害
            "freeze": {"duration": 0, "slow": True},    # 冰冻：降低行动能力
            "stun": {"duration": 0, "skip_turn": True}, # 眩晕：跳过回合
            "poison": {"duration": 0, "damage": 3},     # 中毒：持续伤害
            "shield": {"duration": 0, "defense": 10},   # 护盾：增加防御
            "regenerate": {"duration": 0, "heal": 5}    # 再生：持续治疗
        }
        # 宠物系统
        self.pets = []
        self.active_pet = None
    
    def show_status(self):
        """Display complete player status including stats, equipment, quests, and pets"""
        colored_print(f"\n📊 === {self.name} 的状态 ===", Colors.BOLD)
        print(f"❤️  生命值: {health_bar(self.health, 100)}")
        print(f"💙 法力值: {health_bar(self.mana, 50)}")
        colored_print(f"💰 金币: {self.gold}", Colors.YELLOW)
        colored_print(f"⭐ 等级: {self.level} (经验: {self.exp}/100)", Colors.CYAN)
        if self.current_save_slot:
            print(f"💾 当前存档: 槽位 {self.current_save_slot}")
        print(f"🎒 物品: {', '.join(self.inventory)}")
        colored_print("🔮 技能:", Colors.MAGENTA)
        for skill, data in self.skills.items():
            if data["level"] > 0:
                print(f"   {skill} (Lv.{data['level']}) - 消耗: {data['cost']}法力")
        colored_print("⚔️ 装备:", Colors.BLUE)
        for slot, item in self.equipment.items():
            if item:
                print(f"   {slot.capitalize()}: {item}")
            else:
                print(f"   {slot.capitalize()}: 无")
        colored_print("📋 任务:", Colors.GREEN)
        for quest, data in self.quests.items():
            if not data["completed"]:
                print(f"   {quest}: {data['progress']}/{data['target']} (奖励: {data['reward']}金币)")
        
        # 显示已完成的成就
        completed_achievements = [name for name, data in self.achievements.items() if data["completed"]]
        colored_print(f"🏆 成就: {len(completed_achievements)}/{len(self.achievements)} 已完成", Colors.YELLOW)
        
        # 显示当前状态效果
        active_effects = [name for name, data in self.status_effects.items() if data["duration"] > 0]
        if active_effects:
            colored_print("🌟 当前状态效果:", Colors.MAGENTA)
            for effect in active_effects:
                duration = self.status_effects[effect]["duration"]
                effect_name = self.get_effect_display_name(effect)
                print(f"   {effect_name} (剩余{duration}回合)")
        
        # 显示宠物信息
        if self.active_pet:
            colored_print(f"🐾 当前宠物: {self.active_pet.get_display_name()}", Colors.CYAN)
            print(f"   忠诚度: {self.active_pet.loyalty}/100")
            print(f"   经验: {self.active_pet.exp}/100")
    
    def add_pet(self, pet_type, name):
        """
        Add a new pet to the player's collection
        
        Args:
            pet_type (str): Type of pet to add
            name (str): Name for the pet
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if len(self.pets) >= 3:  # 最多3只宠物
            return False, "宠物数量已达上限"
        
        pet = Pet(name, pet_type)
        self.pets.append(pet)
        
        if not self.active_pet:
            self.active_pet = pet
        
        colored_print(f"🎉 获得新宠物: {pet.get_display_name()}！", Colors.GREEN)
        return True, "宠物已添加"
    
    def switch_pet(self, pet_index):
        """
        Switch to a different active pet
        
        Args:
            pet_index (int): Index of pet to switch to
            
        Returns:
            bool: True if switch was successful
        """
        if 0 <= pet_index < len(self.pets):
            self.active_pet = self.pets[pet_index]
            colored_print(f"🔄 切换到宠物: {self.active_pet.get_display_name()}", Colors.CYAN)
            return True
        return False
    
    def show_pets(self):
        """Display all owned pets with their stats"""
        if not self.pets:
            colored_print("你还没有宠物", Colors.YELLOW)
            return
        
        colored_print("🐾 === 宠物列表 ===", Colors.BOLD)
        for i, pet in enumerate(self.pets):
            status = "★" if pet == self.active_pet else " "
            print(f"{i+1}.{status} {pet.get_display_name()}")
            print(f"   忠诚度: {pet.loyalty}/100, 经验: {pet.exp}/100")
    
    def feed_pet(self, pet_index):
        """
        Feed a pet to increase loyalty
        
        Args:
            pet_index (int): Index of pet to feed
            
        Returns:
            bool: True if feeding was successful
        """
        if 0 <= pet_index < len(self.pets):
            pet = self.pets[pet_index]
            if "🍞 面包" in self.inventory:
                self.inventory.remove("🍞 面包")
                pet.loyalty = min(100, pet.loyalty + 10)
                colored_print(f"🍞 喂养了 {pet.name}，忠诚度增加！", Colors.GREEN)
                return True
            else:
                colored_print("没有食物喂养宠物", Colors.RED)
                return False
        return False
    
    def get_effect_display_name(self, effect):
        """
        Get display name for status effects
        
        Args:
            effect (str): Internal effect name
            
        Returns:
            str: Formatted display name
        """
        effect_names = {
            "burn": "🔥 灼烧",
            "freeze": "❄️ 冰冻", 
            "stun": "⚡ 眩晕",
            "poison": "☠️ 中毒",
            "shield": "🛡️ 护盾",
            "regenerate": "💚 再生"
        }
        return effect_names.get(effect, effect)
    
    def apply_status_effect(self, effect, duration=3):
        """
        Apply a status effect to the player
        
        Args:
            effect (str): Type of status effect
            duration (int): Duration in turns (default: 3)
        """
        if effect in self.status_effects:
            self.status_effects[effect]["duration"] = duration
            effect_name = self.get_effect_display_name(effect)
            colored_print(f"✨ 获得状态效果: {effect_name} ({duration}回合)", Colors.YELLOW)
    
    def process_status_effects(self):
        """
        Process all active status effects and apply their effects
        
        Returns:
            bool: True if any effects were processed
        """
        messages = []
        
        # 处理每个状态效果
        for effect, data in self.status_effects.items():
            if data["duration"] > 0:
                effect_name = self.get_effect_display_name(effect)
                
                # 根据效果类型处理
                if effect == "burn" or effect == "poison":
                    damage = data["damage"]
                    self.health -= damage
                    messages.append(f"💔 {effect_name} 造成 {damage} 点伤害")
                
                elif effect == "regenerate":
                    heal = data["heal"]
                    self.health = min(100, self.health + heal)
                    messages.append(f"💚 {effect_name} 恢复 {heal} 点生命值")
                
                elif effect == "shield":
                    messages.append(f"🛡️ {effect_name} 提供额外防御")
                
                elif effect == "freeze":
                    messages.append(f"❄️ {effect_name} 影响行动")
                
                elif effect == "stun":
                    messages.append(f"⚡ {effect_name} 无法行动")
                
                # 减少持续时间
                data["duration"] -= 1
                if data["duration"] <= 0:
                    messages.append(f"⏰ {effect_name} 效果结束")
        
        # 显示所有状态效果消息
        for msg in messages:
            colored_print(msg, Colors.CYAN)
        
        # 确保生命值不低于0
        if self.health < 0:
            self.health = 0
        
        return len(messages) > 0
    
    def is_stunned(self):
        """
        Check if player is currently stunned
        
        Returns:
            bool: True if stunned
        """
        return self.status_effects["stun"]["duration"] > 0
    
    def is_frozen(self):
        """
        Check if player is currently frozen
        
        Returns:
            bool: True if frozen
        """
        return self.status_effects["freeze"]["duration"] > 0
    
    def check_achievements(self):
        """
        Check and unlock achievements based on player stats
        
        Returns:
            list: List of newly unlocked achievements
        """
        newly_unlocked = []
        
        # 检查各种成就条件
        if not self.achievements["🏆 初出茅庐"]["completed"] and self.stats["enemies_defeated"] >= 1:
            self.achievements["🏆 初出茅庐"]["completed"] = True
            newly_unlocked.append("🏆 初出茅庐")
        
        if not self.achievements["💰 小富翁"]["completed"] and self.gold >= 500:
            self.achievements["💰 小富翁"]["completed"] = True
            newly_unlocked.append("💰 小富翁")
        
        if not self.achievements["⚔️ 战士"]["completed"] and self.stats["enemies_defeated"] >= 50:
            self.achievements["⚔️ 战士"]["completed"] = True
            newly_unlocked.append("⚔️ 战士")
        
        if not self.achievements["🌟 传奇"]["completed"] and self.level >= 10:
            self.achievements["🌟 传奇"]["completed"] = True
            newly_unlocked.append("🌟 传奇")
        
        if not self.achievements["🛡️ 坚韧"]["completed"] and self.stats["near_death_survived"] >= 1:
            self.achievements["🛡️ 坚韧"]["completed"] = True
            newly_unlocked.append("🛡️ 坚韧")
        
        if not self.achievements["🔮 法师"]["completed"] and self.stats["skills_used"] >= 50:
            self.achievements["🔮 法师"]["completed"] = True
            newly_unlocked.append("🔮 法师")
        
        if not self.achievements["🏪 购物狂"]["completed"] and self.stats["items_bought"] >= 20:
            self.achievements["🏪 购物狂"]["completed"] = True
            newly_unlocked.append("🏪 购物狂")
        
        if not self.achievements["💎 收藏家"]["completed"] and self.inventory.count("💎 宝石") >= 5:
            self.achievements["💎 收藏家"]["completed"] = True
            newly_unlocked.append("💎 收藏家")
        
        if not self.achievements["🎯 完美主义"]["completed"] and all(quest["completed"] for quest in self.quests.values()):
            self.achievements["🎯 完美主义"]["completed"] = True
            newly_unlocked.append("🎯 完美主义")
        
        if not self.achievements["🌈 幸运儿"]["completed"] and self.stats["random_events"] >= 10:
            self.achievements["🌈 幸运儿"]["completed"] = True
            newly_unlocked.append("🌈 幸运儿")
        
        # 显示新解锁的成就
        for achievement in newly_unlocked:
            colored_print(f"🎉 成就解锁: {achievement} - {self.achievements[achievement]['description']}", Colors.GREEN)
        
        return newly_unlocked
    
    def show_achievements(self):
        """Display all achievements with completion status"""
        print("\n🏆 === 成就系统 ===")
        for name, data in self.achievements.items():
            status = "✅" if data["completed"] else "❌"
            print(f"{status} {name}: {data['description']}")
        
        completed = sum(1 for data in self.achievements.values() if data["completed"])
        print(f"\n总进度: {completed}/{len(self.achievements)} ({completed/len(self.achievements)*100:.1f}%)")
    
    def track_near_death(self):
        """Track near-death survival for achievements"""
        if self.health <= 10 and self.health > 0:
            self.stats["near_death_survived"] += 1
    
    def update_quest(self, quest_type, enemy_name=None):
        """
        Update quest progress based on actions
        
        Args:
            quest_type (str): Type of quest area/action
            enemy_name (str, optional): Name of defeated enemy
        """
        if quest_type == "forest" and enemy_name in ["🐺 野狼", "🕷️ 巨蜘蛛", "🐻 黑熊"]:
            quest = self.quests["🐺 森林清理"]
            if not quest["completed"]:
                quest["progress"] += 1
                print(f"📋 任务进度: 🐺 森林清理 ({quest['progress']}/{quest['target']})")
                if quest["progress"] >= quest["target"]:
                    quest["completed"] = True
                    self.gold += quest["reward"]
                    print(f"🎉 任务完成！获得 {quest['reward']} 金币奖励！")
        
        elif quest_type == "castle" and enemy_name in ["💀 骷髅战士", "🐉 小龙", "👻 幽灵"]:
            quest = self.quests["🏰 古堡探索"]
            if not quest["completed"]:
                quest["progress"] += 1
                print(f"📋 任务进度: 🏰 古堡探索 ({quest['progress']}/{quest['target']})")
                if quest["progress"] >= quest["target"]:
                    quest["completed"] = True
                    self.gold += quest["reward"]
                    print(f"🎉 任务完成！获得 {quest['reward']} 金币奖励！")
        
        elif quest_type == "volcano" and enemy_name in ["🔥 火元素", "🌋 岩浆怪", "🐲 火龙"]:
            quest = self.quests["🌋 火山征服"]
            if not quest["completed"]:
                quest["progress"] += 1
                print(f"📋 任务进度: 🌋 火山征服 ({quest['progress']}/{quest['target']})")
                if quest["progress"] >= quest["target"]:
                    quest["completed"] = True
                    self.gold += quest["reward"]
                    print(f"🎉 任务完成！获得 {quest['reward']} 金币奖励！")
        
        elif quest_type == "ice" and enemy_name in ["🧊 冰元素", "🐧 冰企鹅", "🐻‍❄️ 冰熊"]:
            quest = self.quests["❄️ 冰窟探险"]
            if not quest["completed"]:
                quest["progress"] += 1
                print(f"📋 任务进度: ❄️ 冰窟探险 ({quest['progress']}/{quest['target']})")
                if quest["progress"] >= quest["target"]:
                    quest["completed"] = True
                    self.gold += quest["reward"]
                    print(f"🎉 任务完成！获得 {quest['reward']} 金币奖励！")
        
        elif quest_type == "gem" and "💎 宝石" in self.inventory:
            quest = self.quests["💎 宝石收集"]
            if not quest["completed"]:
                gem_count = self.inventory.count("💎 宝石")
                quest["progress"] = gem_count
                print(f"📋 任务进度: 💎 宝石收集 ({quest['progress']}/{quest['target']})")
                if quest["progress"] >= quest["target"]:
                    quest["completed"] = True
                    self.gold += quest["reward"]
                    print(f"🎉 任务完成！获得 {quest['reward']} 金币奖励！")
    
    def get_attack_damage(self):
        """
        Calculate total attack damage including weapon and pet bonuses
        
        Returns:
            int: Total damage dealt
        """
        base_damage = random.randint(15, 25)
        weapon_bonus = 0
        if self.equipment["weapon"] == "⚔️ 铁剑":
            weapon_bonus = 10
        elif self.equipment["weapon"] == "🗡️ 精钢剑":
            weapon_bonus = 20
        
        # 添加宠物攻击加成
        pet_bonus = 0
        if self.active_pet and self.active_pet.loyalty > 50:
            pet_bonus = self.active_pet.abilities.get("attack_boost", 0)
        
        total_damage = base_damage + weapon_bonus + pet_bonus
        
        # 计算暴击率（包含宠物加成）
        crit_chance = 0.15
        if self.active_pet:
            crit_chance += self.active_pet.abilities.get("crit_boost", 0)
        
        if random.random() < crit_chance:
            crit_damage = int(total_damage * 1.5)
            colored_print(f"💥 暴击！造成 {crit_damage} 点伤害！", Colors.RED)
            return crit_damage
        
        return total_damage
    
    def get_defense(self):
        """
        Calculate total defense value including armor and effects
        
        Returns:
            int: Total defense value
        """
        defense = 0
        if self.equipment["armor"] == "🛡️ 盾牌":
            defense = 5
        elif self.equipment["armor"] == "🛡️ 铁甲":
            defense = 10
        
        # 添加护盾效果
        if self.status_effects["shield"]["duration"] > 0:
            defense += self.status_effects["shield"]["defense"]
        
        return defense
    
    def try_dodge(self):
        """
        Attempt to dodge an attack, including pet bonuses
        
        Returns:
            bool: True if dodge was successful
        """
        dodge_chance = 0.10
        if self.active_pet:
            dodge_chance += self.active_pet.abilities.get("dodge_boost", 0)
        
        if random.random() < dodge_chance:
            colored_print("💨 成功闪避了攻击！", Colors.CYAN)
            return True
        return False
    
    def equip_item(self, item):
        """
        Equip an item from inventory
        
        Args:
            item (str): Item name to equip
        """
        if item in self.inventory:
            if item in ["🗡️ 木剑", "⚔️ 铁剑", "🗡️ 精钢剑", "🏹 长弓", "⚔️ 双手剑"]:
                if self.equipment["weapon"] and self.equipment["weapon"] != item:
                    self.inventory.append(self.equipment["weapon"])
                self.equipment["weapon"] = item
                self.inventory.remove(item)
                print(f"✅ 装备了 {item}！")
            elif item in ["🛡️ 盾牌", "🛡️ 铁甲"]:
                if self.equipment["armor"] and self.equipment["armor"] != item:
                    self.inventory.append(self.equipment["armor"])
                self.equipment["armor"] = item
                self.inventory.remove(item)
                print(f"✅ 装备了 {item}！")
            else:
                print(f"❌ {item} 无法装备")
        else:
            print(f"❌ 物品栏中没有 {item}")
    
    def gain_exp(self, amount):
        """
        Gain experience points and handle level ups
        
        Args:
            amount (int): Experience points to gain
        """
        self.exp += amount
        if self.exp >= 100:
            self.level += 1
            self.exp -= 100
            self.health = min(100, self.health + 20)
            self.mana = 50
            print(f"🎉 恭喜升级到 {self.level} 级！生命值和法力值恢复！")
            self.unlock_skills()
    
    def unlock_skills(self):
        """Unlock new skills based on player level"""
        if self.level >= 3 and self.skills["❄️ 冰冻术"]["level"] == 0:
            self.skills["❄️ 冰冻术"]["level"] = 1
            colored_print("🎊 解锁新技能: ❄️ 冰冻术！", Colors.CYAN)
        if self.level >= 4 and self.skills["🛡️ 护盾术"]["level"] == 0:
            self.skills["🛡️ 护盾术"]["level"] = 1
            colored_print("🎊 解锁新技能: 🛡️ 护盾术！", Colors.CYAN)
        if self.level >= 5 and self.skills["⚡ 闪电术"]["level"] == 0:
            self.skills["⚡ 闪电术"]["level"] = 1
            colored_print("🎊 解锁新技能: ⚡ 闪电术！", Colors.CYAN)
    
    def use_skill(self, skill_name, target=None):
        """
        Use a skill if available and player has enough mana
        
        Args:
            skill_name (str): Name of skill to use
            target (optional): Target for the skill
            
        Returns:
            tuple: (success: bool, result: varies)
        """
        if skill_name not in self.skills or self.skills[skill_name]["level"] == 0:
            return False, "技能未学会"
        
        skill = self.skills[skill_name]
        if self.mana < skill["cost"]:
            return False, "法力不足"
        
        self.mana -= skill["cost"]
        self.stats["skills_used"] += 1  # 追踪技能使用次数
        
        if "damage" in skill:
            damage = skill["damage"] + random.randint(-5, 5)
            # 应用状态效果
            if "effect" in skill and target:
                effect_chance = 0.6  # 60%概率触发状态效果
                if random.random() < effect_chance:
                    if hasattr(target, 'apply_status_effect'):
                        target.apply_status_effect(skill["effect"], 3)
                    else:
                        # 如果是对敌人使用，返回效果信息
                        return True, (damage, skill["effect"])
            return True, damage
        elif "heal" in skill:
            heal_amount = skill["heal"] + random.randint(-5, 5)
            self.health = min(100, self.health + heal_amount)
            return True, heal_amount
        elif skill_name == "🛡️ 护盾术":
            self.apply_status_effect("shield", 5)
            return True, "护盾激活"
        
        return False, "技能使用失败"
    
    def save_game(self, slot=None):
        """
        Save the game to a specific slot
        
        Args:
            slot (int, optional): Save slot number (1-5)
        """
        if slot is None:
            # 如果有当前存档槽位，询问是否快速保存
            if self.current_save_slot is not None:
                quick_save = input(f"是否快速保存到槽位 {self.current_save_slot}？(Y/n): ")
                if quick_save.lower() != 'n':
                    slot = self.current_save_slot
            
            if slot is None:
                print("\n💾 === 选择存档槽位 ===")
                for i in range(1, 6):  # 5个存档槽位
                    save_file = f"savegame_{i}.json"
                    if os.path.exists(save_file):
                        try:
                            with open(save_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            print(f"{i}. 槽位{i} - {data.get('name', '未知')} (等级 {data.get('level', 1)})")
                        except:
                            print(f"{i}. 槽位{i} - 损坏的存档")
                    else:
                        print(f"{i}. 槽位{i} - 空")
                
                try:
                    slot = int(input("选择存档槽位 (1-5): "))
                    if not (1 <= slot <= 5):
                        print("❌ 无效槽位")
                        return
                except ValueError:
                    print("❌ 请输入数字")
                    return
        
        save_data = {
            'name': self.name,
            'health': self.health,
            'gold': self.gold,
            'inventory': self.inventory,
            'level': self.level,
            'exp': self.exp,
            'skills': self.skills,
            'mana': self.mana,
            'equipment': self.equipment,
            'quests': self.quests,
            'achievements': self.achievements,
            'stats': self.stats,
            'status_effects': self.status_effects,
            'pets': [{"name": pet.name, "type": pet.pet_type, "level": pet.level, 
                     "exp": pet.exp, "loyalty": pet.loyalty} for pet in self.pets],
            'active_pet_index': self.pets.index(self.active_pet) if self.active_pet else -1,
            'house': {
                'house_type': self.house.house_type if hasattr(self, 'house') and self.house else None,
                'name': self.house.name if hasattr(self, 'house') and self.house else None,
                'price': self.house.price if hasattr(self, 'house') and self.house else None,
                'rooms': self.house.rooms if hasattr(self, 'house') and self.house else None,
                'owned': self.house.owned if hasattr(self, 'house') and self.house else False,
                'furnishings': {k: {'name': v.name, 'item_type': v.item_type, 'price': v.price, 
                               'comfort_bonus': v.comfort_bonus, 'description': v.description} 
                               for k, v in self.house.furnishings.items()} if hasattr(self, 'house') and self.house else {},
                'upgrades': self.house.upgrades if hasattr(self, 'house') and self.house else [],
                'comfort_level': self.house.comfort_level if hasattr(self, 'house') and self.house else 1
            }
        }
        
        save_file = f"savegame_{slot}.json"
        try:
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            self.current_save_slot = slot  # 记录当前存档槽位
            print(f"💾 游戏已保存到槽位 {slot}！")
        except Exception as e:
            print(f"❌ 保存失败: {e}")
    
    @classmethod
    def load_game(cls):
        """
        Load a game from saved data
        
        Returns:
            Player or None: Loaded player instance or None if failed
        """
        print("\n📂 === 选择要加载的存档 ===")
        available_saves = []
        
        for i in range(1, 6):  # 5个存档槽位
            save_file = f"savegame_{i}.json"
            if os.path.exists(save_file):
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"{i}. 槽位{i} - {data.get('name', '未知')} (等级 {data.get('level', 1)})")
                    available_saves.append(i)
                except:
                    print(f"{i}. 槽位{i} - 损坏的存档")
            else:
                print(f"{i}. 槽位{i} - 空")
        
        if not available_saves:
            print("❌ 没有找到任何存档文件")
            return None
        
        try:
            slot = int(input("选择要加载的槽位 (0-取消): "))
            if slot == 0:
                return None
            if slot not in available_saves:
                print("❌ 该槽位没有存档或存档损坏")
                return None
        except ValueError:
            print("❌ 请输入数字")
            return None
        
        save_file = f"savegame_{slot}.json"
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            player = cls(save_data['name'])
            player.health = save_data['health']
            player.gold = save_data['gold']
            player.inventory = save_data['inventory']
            player.level = save_data['level']
            player.exp = save_data['exp']
            player.skills = save_data.get('skills', player.skills)
            player.mana = save_data.get('mana', 50)
            player.equipment = save_data.get('equipment', player.equipment)
            player.quests = save_data.get('quests', player.quests)
            player.achievements = save_data.get('achievements', player.achievements)
            player.stats = save_data.get('stats', player.stats)
            player.status_effects = save_data.get('status_effects', player.status_effects)
            
            # 加载宠物数据
            pets_data = save_data.get('pets', [])
            player.pets = []
            for pet_data in pets_data:
                pet = Pet(pet_data['name'], pet_data['type'], pet_data['level'])
                pet.exp = pet_data['exp']
                pet.loyalty = pet_data['loyalty']
                player.pets.append(pet)
            
            active_pet_index = save_data.get('active_pet_index', -1)
            if active_pet_index >= 0 and active_pet_index < len(player.pets):
                player.active_pet = player.pets[active_pet_index]
            
            # 加载房屋数据 (House and Furnishing classes would need to be imported when available)
            house_data = save_data.get('house', {})
            if house_data.get('owned', False) and house_data.get('house_type'):
                # This section would need House and Furnishing classes to be implemented
                # For now, we'll skip this to avoid import errors
                pass
            
            player.current_save_slot = slot  # 设置当前存档槽位
            
            print(f"📂 从槽位 {slot} 加载游戏成功！")
            return player
        except Exception as e:
            print(f"❌ 加载失败: {e}")
            return None


# Example usage and testing
if __name__ == "__main__":
    # Create a sample player
    player = Player("测试玩家")
    
    print("Player Created:")
    player.show_status()
    
    # Test adding a pet
    print("\nAdding a pet...")
    success, message = player.add_pet("🐺 幼狼", "小白")
    print(f"Add pet result: {success}, {message}")
    
    # Test showing pets
    print("\nShowing pets...")
    player.show_pets()
    
    # Test skill usage
    print("\nUsing a skill...")
    success, result = player.use_skill("🔥 火球术")
    print(f"Skill result: {success}, {result}")
    
    # Test status effect
    print("\nApplying status effect...")
    player.apply_status_effect("burn", 3)
    player.process_status_effects()
    
    # Test achievement checking
    print("\nChecking achievements...")
    player.stats["enemies_defeated"] = 1
    new_achievements = player.check_achievements()
    print(f"New achievements: {new_achievements}")