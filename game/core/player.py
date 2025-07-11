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
            "🔥 火球术": {"level": 1, "cost": 8, "damage": 35, "effect": "burn"},
            "❄️ 冰冻术": {"level": 0, "cost": 12, "damage": 30, "effect": "freeze"},
            "⚡ 闪电术": {"level": 0, "cost": 15, "damage": 45, "effect": "stun"},
            "💚 治疗术": {"level": 1, "cost": 6, "heal": 30, "effect": "heal"},
            "🛡️ 护盾术": {"level": 0, "cost": 10, "effect": "shield"}
        }
        self.mana = 100
        self.max_mana = 100
        self.equipment = {
            "weapon": "🗡️ 木剑",
            "armor": None,
            "accessory": None
        }
        self.quests = {
            # 基础任务
            "🐺 森林清理": {"completed": False, "progress": 0, "target": 3, "reward": 100, "type": "combat"},
            "🏰 古堡探索": {"completed": False, "progress": 0, "target": 1, "reward": 200, "type": "combat"},
            "💎 宝石收集": {"completed": False, "progress": 0, "target": 2, "reward": 150, "type": "collect"},
            "🌋 火山征服": {"completed": False, "progress": 0, "target": 2, "reward": 300, "type": "combat"},
            "❄️ 冰窟探险": {"completed": False, "progress": 0, "target": 1, "reward": 250, "type": "combat"},
            
            # 新增区域任务
            "🌊 深海守护": {"completed": False, "progress": 0, "target": 5, "reward": 400, "type": "combat"},
            "🏜️ 沙漠商队": {"completed": False, "progress": 0, "target": 3, "reward": 350, "type": "combat"},
            "🏛️ 地下城净化": {"completed": False, "progress": 0, "target": 4, "reward": 500, "type": "combat"},
            "🌌 星空探索": {"completed": False, "progress": 0, "target": 2, "reward": 600, "type": "combat"},
            "🎪 奇幻马戏团": {"completed": False, "progress": 0, "target": 3, "reward": 300, "type": "combat"},
            
            # 收集类任务
            "🧪 炼金材料": {"completed": False, "progress": 0, "target": 5, "reward": 200, "type": "collect"},
            "📚 古老知识": {"completed": False, "progress": 0, "target": 3, "reward": 250, "type": "collect"},
            "🎭 神秘面具": {"completed": False, "progress": 0, "target": 1, "reward": 400, "type": "collect"},
            "🔮 魔法水晶": {"completed": False, "progress": 0, "target": 4, "reward": 350, "type": "collect"},
            
            # 挑战类任务
            "⚔️ 武器大师": {"completed": False, "progress": 0, "target": 1, "reward": 500, "type": "challenge"},
            "🛡️ 防御专家": {"completed": False, "progress": 0, "target": 1, "reward": 400, "type": "challenge"},
            "🏆 竞技冠军": {"completed": False, "progress": 0, "target": 10, "reward": 800, "type": "challenge"},
            "🎯 神射手": {"completed": False, "progress": 0, "target": 50, "reward": 300, "type": "challenge"},
            
            # 社交类任务  
            "🤝 友谊之桥": {"completed": False, "progress": 0, "target": 5, "reward": 200, "type": "social"},
            "💰 商业帝国": {"completed": False, "progress": 0, "target": 1000, "reward": 100, "type": "social"},
            "🎨 艺术赞助": {"completed": False, "progress": 0, "target": 3, "reward": 300, "type": "social"}
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
            "near_death_survived": 0,
            "potion_buff": 0  # 药水增益次数
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
        
        # 战斗日志系统
        self.battle_log = []
        self.max_battle_logs = 5  # 保存最近5场战斗的日志
    
    def show_status(self):
        """Display complete player status including stats, equipment, quests, and pets"""
        colored_print(f"\n📊 === {self.name} 的状态 ===", Colors.BOLD)
        print(f"❤️  生命值: {health_bar(self.health, 100)}")
        print(f"💙 法力值: {health_bar(self.mana, self.max_mana)}")
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
    
    def _update_quests_compatibility(self):
        """
        更新任务兼容性 - 为旧存档添加新任务
        这确保了从旧版本加载的存档能够包含所有新任务
        """
        # v4.8新增的任务列表
        new_quests_v48 = {
            # 新增区域任务
            "🌊 深海守护": {"completed": False, "progress": 0, "target": 5, "reward": 400, "type": "combat"},
            "🏜️ 沙漠商队": {"completed": False, "progress": 0, "target": 3, "reward": 350, "type": "combat"},
            "🏛️ 地下城净化": {"completed": False, "progress": 0, "target": 4, "reward": 500, "type": "combat"},
            "🌌 星空探索": {"completed": False, "progress": 0, "target": 2, "reward": 600, "type": "combat"},
            "🎪 奇幻马戏团": {"completed": False, "progress": 0, "target": 3, "reward": 300, "type": "combat"},
            
            # 收集类任务
            "🧪 炼金材料": {"completed": False, "progress": 0, "target": 5, "reward": 200, "type": "collect"},
            "📚 古老知识": {"completed": False, "progress": 0, "target": 3, "reward": 250, "type": "collect"},
            "🎭 神秘面具": {"completed": False, "progress": 0, "target": 1, "reward": 400, "type": "collect"},
            "🔮 魔法水晶": {"completed": False, "progress": 0, "target": 4, "reward": 350, "type": "collect"},
            
            # 挑战类任务
            "⚔️ 武器大师": {"completed": False, "progress": 0, "target": 1, "reward": 500, "type": "challenge"},
            "🛡️ 防御专家": {"completed": False, "progress": 0, "target": 1, "reward": 400, "type": "challenge"},
            "🏆 竞技冠军": {"completed": False, "progress": 0, "target": 10, "reward": 800, "type": "challenge"},
            "🎯 神射手": {"completed": False, "progress": 0, "target": 50, "reward": 300, "type": "challenge"},
            
            # 社交类任务  
            "🤝 友谊之桥": {"completed": False, "progress": 0, "target": 5, "reward": 200, "type": "social"},
            "💰 商业帝国": {"completed": False, "progress": 0, "target": 1000, "reward": 100, "type": "social"},
            "🎨 艺术赞助": {"completed": False, "progress": 0, "target": 3, "reward": 300, "type": "social"}
        }
        
        # 检查并添加缺失的任务
        added_quests = []
        for quest_name, quest_data in new_quests_v48.items():
            if quest_name not in self.quests:
                self.quests[quest_name] = quest_data.copy()
                added_quests.append(quest_name)
        
        # 如果添加了新任务，显示提示
        if added_quests:
            print(f"🆕 兼容性更新：为你的存档添加了 {len(added_quests)} 个新任务！")
            print("💡 你现在可以探索新的区域和挑战新的任务了！")
    
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
        
        elif quest_type == "ocean" and enemy_name in ["🐙 章鱼", "🦈 鲨鱼", "🐋 海怪"]:
            quest = self.quests["🌊 深海守护"]
            if not quest["completed"]:
                quest["progress"] += 1
                print(f"📋 任务进度: 🌊 深海守护 ({quest['progress']}/{quest['target']})")
                if quest["progress"] >= quest["target"]:
                    quest["completed"] = True
                    self.gold += quest["reward"]
                    print(f"🎉 任务完成！获得 {quest['reward']} 金币奖励！")
        
        elif quest_type == "desert" and enemy_name in ["🦂 沙漠蝎", "🐍 毒蛇", "🐪 沙漠之王"]:
            quest = self.quests["🏜️ 沙漠商队"]
            if not quest["completed"]:
                quest["progress"] += 1
                print(f"📋 任务进度: 🏜️ 沙漠商队 ({quest['progress']}/{quest['target']})")
                if quest["progress"] >= quest["target"]:
                    quest["completed"] = True
                    self.gold += quest["reward"]
                    print(f"🎉 任务完成！获得 {quest['reward']} 金币奖励！")
        
        elif quest_type == "dungeon" and enemy_name in ["🧟 僵尸", "🐲 地龙", "👑 地下君主"]:
            quest = self.quests["🏛️ 地下城净化"]
            if not quest["completed"]:
                quest["progress"] += 1
                print(f"📋 任务进度: 🏛️ 地下城净化 ({quest['progress']}/{quest['target']})")
                if quest["progress"] >= quest["target"]:
                    quest["completed"] = True
                    self.gold += quest["reward"]
                    print(f"🎉 任务完成！获得 {quest['reward']} 金币奖励！")
        
        elif quest_type == "star" and enemy_name in ["⭐ 星灵", "🌟 流星", "🌙 月神使者"]:
            quest = self.quests["🌌 星空探索"]
            if not quest["completed"]:
                quest["progress"] += 1
                print(f"📋 任务进度: 🌌 星空探索 ({quest['progress']}/{quest['target']})")
                if quest["progress"] >= quest["target"]:
                    quest["completed"] = True
                    self.gold += quest["reward"]
                    print(f"🎉 任务完成！获得 {quest['reward']} 金币奖励！")
        
        elif quest_type == "circus" and enemy_name in ["🤡 魔法小丑", "🎭 变形师", "🎪 马戏团长"]:
            quest = self.quests["🎪 奇幻马戏团"]
            if not quest["completed"]:
                quest["progress"] += 1
                print(f"📋 任务进度: 🎪 奇幻马戏团 ({quest['progress']}/{quest['target']})")
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
        
        # 武器攻击力数值化
        weapon_stats = {
            "🗡️ 木剑": 5,
            "⚔️ 铁剑": 15,
            "🗡️ 精钢剑": 25,
            "🏹 长弓": 20,
            "⚔️ 双手剑": 30,
            # Boss奖励武器
            "🐉 龙鳞护甲": 10,  # 防御型装备但有攻击加成
            "💀 死灵法杖": 35,
            "🏔️ 巨人之锤": 40,
            "👑 王者徽章": 20,
            # 传说装备
            "⚔️ 传说之剑": 45
        }
        
        current_weapon = self.equipment.get("weapon")
        if current_weapon in weapon_stats:
            weapon_bonus = weapon_stats[current_weapon]
        
        # 添加宠物攻击加成
        pet_bonus = 0
        if self.active_pet and self.active_pet.loyalty > 50:
            pet_bonus = self.active_pet.abilities.get("attack_boost", 0)
        
        total_damage = base_damage + weapon_bonus + pet_bonus
        
        # 检查药水增益
        if self.stats.get("potion_buff", 0) > 0:
            total_damage *= 2  # 伤害翻倍
            self.stats["potion_buff"] -= 1  # 消耗增益
            colored_print("💪 药水增益生效！伤害翻倍！", Colors.YELLOW)
        
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
        
        # 防具防御力数值化
        armor_stats = {
            "🛡️ 盾牌": 8,
            "🛡️ 铁甲": 15,
            # Boss奖励防具
            "🐉 龙鳞护甲": 25,
            "💀 死灵法杖": 5,  # 法杖提供少量魔法防御
            "🏔️ 巨人之锤": 10,  # 重武器提供一定防御
            "👑 王者徽章": 12,
            # 传说装备
            "⚔️ 传说之剑": 8  # 传说之剑提供少量防御
        }
        
        current_armor = self.equipment.get("armor")
        if current_armor in armor_stats:
            defense += armor_stats[current_armor]
        
        # 武器也可能提供防御（如盾牌类武器）
        current_weapon = self.equipment.get("weapon")
        if current_weapon in armor_stats:
            defense += armor_stats[current_weapon]
        
        # 添加护盾效果
        if self.status_effects["shield"]["duration"] > 0:
            defense += self.status_effects["shield"]["defense"]
        
        # 添加宠物防御加成
        if self.active_pet and self.active_pet.loyalty > 50:
            defense += self.active_pet.abilities.get("defense_boost", 0)
        
        return defense
    
    def get_detailed_stats(self):
        """
        获取详细的角色属性统计
        
        Returns:
            dict: 包含所有详细属性的字典
        """
        # 基础属性
        base_attack = random.randint(15, 25)  # 基础攻击力范围
        base_defense = 0
        
        # 武器属性
        weapon_stats = {
            "🗡️ 木剑": {"attack": 5, "defense": 0},
            "⚔️ 铁剑": {"attack": 15, "defense": 0},
            "🗡️ 精钢剑": {"attack": 25, "defense": 0},
            "🏹 长弓": {"attack": 20, "defense": 0},
            "⚔️ 双手剑": {"attack": 30, "defense": 0},
            "💀 死灵法杖": {"attack": 35, "defense": 5},
            "🏔️ 巨人之锤": {"attack": 40, "defense": 10},
            "👑 王者徽章": {"attack": 20, "defense": 12},
            "⚔️ 传说之剑": {"attack": 45, "defense": 8}
        }
        
        # 防具属性
        armor_stats = {
            "🛡️ 盾牌": {"attack": 0, "defense": 8},
            "🛡️ 铁甲": {"attack": 0, "defense": 15},
            "🐉 龙鳞护甲": {"attack": 10, "defense": 25}
        }
        
        # 计算装备加成
        weapon_bonus = {"attack": 0, "defense": 0}
        armor_bonus = {"attack": 0, "defense": 0}
        
        current_weapon = self.equipment.get("weapon")
        current_armor = self.equipment.get("armor")
        
        if current_weapon and current_weapon in weapon_stats:
            weapon_bonus = weapon_stats[current_weapon]
        
        if current_armor and current_armor in armor_stats:
            armor_bonus = armor_stats[current_armor]
        
        # 宠物加成
        pet_bonus = {"attack": 0, "defense": 0, "crit": 0, "dodge": 0}
        if self.active_pet and self.active_pet.loyalty > 50:
            pet_abilities = self.active_pet.abilities
            pet_bonus["attack"] = pet_abilities.get("attack_boost", 0)
            pet_bonus["defense"] = pet_abilities.get("defense_boost", 0)
            pet_bonus["crit"] = pet_abilities.get("crit_boost", 0) * 100  # 转为百分比
            pet_bonus["dodge"] = pet_abilities.get("dodge_boost", 0) * 100  # 转为百分比
        
        # 状态效果加成
        status_bonus = {"attack": 0, "defense": 0}
        if self.status_effects["shield"]["duration"] > 0:
            status_bonus["defense"] = self.status_effects["shield"]["defense"]
        
        # 计算总属性
        total_attack_min = base_attack + weapon_bonus["attack"] + armor_bonus["attack"] + pet_bonus["attack"]
        total_attack_max = 25 + weapon_bonus["attack"] + armor_bonus["attack"] + pet_bonus["attack"]
        total_defense = base_defense + weapon_bonus["defense"] + armor_bonus["defense"] + pet_bonus["defense"] + status_bonus["defense"]
        
        # 计算暴击率和闪避率
        base_crit = 15.0  # 基础暴击率15%
        base_dodge = 10.0  # 基础闪避率10%
        
        total_crit = base_crit + pet_bonus["crit"]
        total_dodge = base_dodge + pet_bonus["dodge"]
        
        return {
            "attack": {
                "base": f"{base_attack}-25",
                "weapon": weapon_bonus["attack"],
                "armor": armor_bonus["attack"],
                "pet": pet_bonus["attack"],
                "total": f"{total_attack_min}-{total_attack_max}"
            },
            "defense": {
                "base": base_defense,
                "weapon": weapon_bonus["defense"],
                "armor": armor_bonus["defense"],
                "pet": pet_bonus["defense"],
                "status": status_bonus["defense"],
                "total": total_defense
            },
            "rates": {
                "crit": f"{total_crit:.1f}%",
                "dodge": f"{total_dodge:.1f}%"
            },
            "equipment": {
                "weapon": current_weapon or "无",
                "armor": current_armor or "无"
            }
        }
    
    def show_detailed_stats(self):
        """显示详细的属性面板"""
        stats = self.get_detailed_stats()
        
        colored_print(f"\n📊 === {self.name} 详细属性 ===", Colors.BOLD + Colors.CYAN)
        
        # 基础信息
        colored_print("🎯 基础信息:", Colors.YELLOW)
        print(f"   等级: {self.level} | 经验: {self.exp}/100")
        print(f"   生命值: {self.health}/100")
        print(f"   法力值: {self.mana}/{self.max_mana}")
        print(f"   金币: {self.gold}")
        
        # 战斗属性
        colored_print("\n⚔️ 战斗属性:", Colors.RED)
        print(f"   攻击力: {stats['attack']['total']}")
        print(f"     基础: {stats['attack']['base']}")
        if stats['attack']['weapon'] > 0:
            print(f"     武器: +{stats['attack']['weapon']}")
        if stats['attack']['armor'] > 0:
            print(f"     防具: +{stats['attack']['armor']}")
        if stats['attack']['pet'] > 0:
            print(f"     宠物: +{stats['attack']['pet']}")
        
        print(f"   防御力: {stats['defense']['total']}")
        if stats['defense']['weapon'] > 0:
            print(f"     武器: +{stats['defense']['weapon']}")
        if stats['defense']['armor'] > 0:
            print(f"     防具: +{stats['defense']['armor']}")
        if stats['defense']['pet'] > 0:
            print(f"     宠物: +{stats['defense']['pet']}")
        if stats['defense']['status'] > 0:
            print(f"     状态: +{stats['defense']['status']}")
        
        # 特殊属性
        colored_print("\n🎲 特殊属性:", Colors.MAGENTA)
        print(f"   暴击率: {stats['rates']['crit']}")
        print(f"   闪避率: {stats['rates']['dodge']}")
        
        # 装备信息
        colored_print("\n🎒 当前装备:", Colors.BLUE)
        print(f"   武器: {stats['equipment']['weapon']}")
        print(f"   防具: {stats['equipment']['armor']}")
        
        # 宠物信息
        if self.active_pet:
            colored_print("\n🐾 活跃宠物:", Colors.GREEN)
            print(f"   名称: {self.active_pet.get_display_name()}")
            print(f"   等级: {self.active_pet.level}")
            print(f"   忠诚度: {self.active_pet.loyalty}/100")
            print(f"   经验: {self.active_pet.exp}/100")
        
        # 状态效果
        active_effects = [name for name, data in self.status_effects.items() if data["duration"] > 0]
        if active_effects:
            colored_print("\n🌟 当前状态效果:", Colors.YELLOW)
            for effect in active_effects:
                duration = self.status_effects[effect]["duration"]
                effect_name = self.get_effect_display_name(effect)
                print(f"   {effect_name} (剩余{duration}回合)")
    
    def compare_equipment(self, new_item):
        """
        比较新装备与当前装备的属性差异
        
        Args:
            new_item (str): 要比较的新装备名称
            
        Returns:
            dict: 装备比较结果
        """
        # 获取当前属性
        current_stats = self.get_detailed_stats()
        
        # 创建临时玩家状态来计算新装备属性
        temp_equipment = self.equipment.copy()
        
        # 确定装备类型
        weapon_items = ["🗡️ 木剑", "⚔️ 铁剑", "🗡️ 精钢剑", "🏹 长弓", "⚔️ 双手剑", 
                       "💀 死灵法杖", "🏔️ 巨人之锤", "👑 王者徽章", "⚔️ 传说之剑"]
        armor_items = ["🛡️ 盾牌", "🛡️ 铁甲", "🐉 龙鳞护甲"]
        
        equipment_type = None
        old_item = None
        
        if new_item in weapon_items:
            equipment_type = "weapon"
            old_item = temp_equipment.get("weapon")
            temp_equipment["weapon"] = new_item
        elif new_item in armor_items:
            equipment_type = "armor"
            old_item = temp_equipment.get("armor")
            temp_equipment["armor"] = new_item
        else:
            return {"error": "无法识别的装备类型"}
        
        # 计算新装备的属性（临时修改装备）
        original_equipment = self.equipment.copy()
        self.equipment = temp_equipment
        new_stats = self.get_detailed_stats()
        self.equipment = original_equipment  # 恢复原装备
        
        # 计算属性差异
        def parse_attack_range(attack_str):
            """解析攻击力范围字符串，返回最小值"""
            if "-" in attack_str:
                return int(attack_str.split("-")[0])
            return int(attack_str)
        
        old_attack = parse_attack_range(current_stats["attack"]["total"])
        new_attack = parse_attack_range(new_stats["attack"]["total"])
        
        attack_diff = new_attack - old_attack
        defense_diff = new_stats["defense"]["total"] - current_stats["defense"]["total"]
        
        return {
            "equipment_type": equipment_type,
            "old_item": old_item or "无",
            "new_item": new_item,
            "changes": {
                "attack": attack_diff,
                "defense": defense_diff
            },
            "old_stats": current_stats,
            "new_stats": new_stats
        }
    
    def show_equipment_comparison(self, new_item):
        """显示装备比较界面"""
        comparison = self.compare_equipment(new_item)
        
        if "error" in comparison:
            colored_print(f"❌ {comparison['error']}", Colors.RED)
            return False
        
        colored_print(f"\n🔍 === 装备比较 ===", Colors.BOLD + Colors.CYAN)
        
        # 显示装备变更
        equipment_type_name = "武器" if comparison["equipment_type"] == "weapon" else "防具"
        colored_print(f"🎯 {equipment_type_name}更换:", Colors.YELLOW)
        print(f"   当前: {comparison['old_item']}")
        print(f"   新装备: {comparison['new_item']}")
        
        # 显示属性变化
        colored_print("\n📈 属性变化:", Colors.BLUE)
        
        # 攻击力变化
        attack_change = comparison["changes"]["attack"]
        if attack_change > 0:
            colored_print(f"   ⚔️ 攻击力: +{attack_change} ↗️", Colors.GREEN)
        elif attack_change < 0:
            colored_print(f"   ⚔️ 攻击力: {attack_change} ↘️", Colors.RED)
        else:
            colored_print(f"   ⚔️ 攻击力: 无变化", Colors.YELLOW)
        
        # 防御力变化
        defense_change = comparison["changes"]["defense"]
        if defense_change > 0:
            colored_print(f"   🛡️ 防御力: +{defense_change} ↗️", Colors.GREEN)
        elif defense_change < 0:
            colored_print(f"   🛡️ 防御力: {defense_change} ↘️", Colors.RED)
        else:
            colored_print(f"   🛡️ 防御力: 无变化", Colors.YELLOW)
        
        # 显示详细对比
        colored_print("\n📋 详细对比:", Colors.MAGENTA)
        print(f"   攻击力: {comparison['old_stats']['attack']['total']} → {comparison['new_stats']['attack']['total']}")
        print(f"   防御力: {comparison['old_stats']['defense']['total']} → {comparison['new_stats']['defense']['total']}")
        
        # 装备建议
        total_improvement = attack_change + defense_change
        if total_improvement > 0:
            colored_print("💡 建议: 这是一个属性提升，建议装备！", Colors.GREEN)
        elif total_improvement < 0:
            colored_print("💡 建议: 这会降低属性，请谨慎考虑。", Colors.RED)
        else:
            colored_print("💡 建议: 属性没有明显变化。", Colors.YELLOW)
        
        return True
    
    def add_battle_log(self, battle_data):
        """
        添加战斗日志记录
        
        Args:
            battle_data (dict): 战斗数据
        """
        import datetime
        
        # 创建战斗日志条目
        log_entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "location": battle_data.get("location", "未知区域"),
            "enemy": battle_data.get("enemy", "未知敌人"),
            "result": battle_data.get("result", "未知"),  # victory, defeat, flee
            "duration": battle_data.get("duration", 0),  # 战斗回合数
            "damage_dealt": battle_data.get("damage_dealt", 0),
            "damage_taken": battle_data.get("damage_taken", 0),
            "skills_used": battle_data.get("skills_used", []),
            "rewards": battle_data.get("rewards", {}),
            "player_level": self.level,
            "player_health_start": battle_data.get("player_health_start", 100),
            "player_health_end": self.health
        }
        
        # 添加到日志列表
        self.battle_log.append(log_entry)
        
        # 保持最大日志数量限制
        if len(self.battle_log) > self.max_battle_logs:
            self.battle_log.pop(0)  # 移除最旧的日志
    
    def show_battle_log(self):
        """显示战斗日志"""
        colored_print("\n📜 === 战斗日志 ===", Colors.BOLD + Colors.CYAN)
        
        if not self.battle_log:
            colored_print("📝 还没有战斗记录", Colors.YELLOW)
            return
        
        print(f"📊 显示最近 {len(self.battle_log)} 场战斗记录:\n")
        
        for i, log in enumerate(reversed(self.battle_log), 1):
            # 战斗结果图标
            result_icons = {
                "victory": "🏆 胜利",
                "defeat": "💀 失败", 
                "flee": "🏃 逃跑"
            }
            result_icon = result_icons.get(log["result"], "❓ 未知")
            
            # 显示战斗摘要
            colored_print(f"📖 战斗 #{i} - {result_icon}", Colors.BOLD)
            print(f"   🕐 时间: {log['timestamp']}")
            print(f"   📍 地点: {log['location']}")
            print(f"   👹 敌人: {log['enemy']}")
            print(f"   ⏱️  持续: {log['duration']} 回合")
            print(f"   ⚔️ 造成伤害: {log['damage_dealt']}")
            print(f"   💔 受到伤害: {log['damage_taken']}")
            
            # 显示使用的技能
            if log['skills_used']:
                skills_text = ", ".join(log['skills_used'])
                print(f"   🔮 使用技能: {skills_text}")
            
            # 显示奖励
            if log['rewards'] and log['result'] == 'victory':
                rewards_text = []
                if log['rewards'].get('gold', 0) > 0:
                    rewards_text.append(f"{log['rewards']['gold']}金币")
                if log['rewards'].get('exp', 0) > 0:
                    rewards_text.append(f"{log['rewards']['exp']}经验")
                if rewards_text:
                    print(f"   🎁 奖励: {', '.join(rewards_text)}")
            
            # 显示生命值变化
            health_change = log['player_health_end'] - log['player_health_start']
            if health_change < 0:
                print(f"   ❤️ 生命值: {log['player_health_start']} → {log['player_health_end']} ({health_change})")
            elif health_change > 0:
                print(f"   ❤️ 生命值: {log['player_health_start']} → {log['player_health_end']} (+{health_change})")
            else:
                print(f"   ❤️ 生命值: {log['player_health_start']} (无变化)")
            
            print()  # 空行分隔
        
        # 显示统计数据
        self._show_battle_statistics()
    
    def _show_battle_statistics(self):
        """显示战斗统计数据"""
        if not self.battle_log:
            return
        
        colored_print("📈 === 战斗统计 ===", Colors.BOLD + Colors.BLUE)
        
        # 计算统计数据
        total_battles = len(self.battle_log)
        victories = sum(1 for log in self.battle_log if log['result'] == 'victory')
        defeats = sum(1 for log in self.battle_log if log['result'] == 'defeat')
        flees = sum(1 for log in self.battle_log if log['result'] == 'flee')
        
        total_damage_dealt = sum(log['damage_dealt'] for log in self.battle_log)
        total_damage_taken = sum(log['damage_taken'] for log in self.battle_log)
        total_rounds = sum(log['duration'] for log in self.battle_log)
        
        # 计算胜率
        win_rate = (victories / total_battles * 100) if total_battles > 0 else 0
        
        print(f"🎯 总战斗数: {total_battles}")
        print(f"🏆 胜利: {victories} | 💀 失败: {defeats} | 🏃 逃跑: {flees}")
        print(f"📊 胜率: {win_rate:.1f}%")
        print(f"⚔️ 总伤害输出: {total_damage_dealt}")
        print(f"💔 总承受伤害: {total_damage_taken}")
        if total_battles > 0:
            print(f"📈 平均每场战斗:")
            print(f"   伤害输出: {total_damage_dealt // total_battles}")
            print(f"   承受伤害: {total_damage_taken // total_battles}")
            print(f"   持续回合: {total_rounds / total_battles:.1f}")
        
        # 最常战斗的地点
        locations = {}
        for log in self.battle_log:
            location = log['location']
            locations[location] = locations.get(location, 0) + 1
        
        if locations:
            most_common_location = max(locations, key=locations.get)
            print(f"🗺️ 最常战斗地点: {most_common_location} ({locations[most_common_location]}次)")
    
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
    
    def use_item(self, item):
        """
        使用物品
        
        Args:
            item (str): 要使用的物品名称
        """
        if item not in self.inventory:
            colored_print(f"❌ 背包中没有 {item}", Colors.RED)
            return False
            
        if item == "🍞 面包":
            old_health = self.health
            self.health = min(100, self.health + 30)
            self.inventory.remove(item)
            heal_amount = self.health - old_health
            colored_print(f"🍞 使用了面包，恢复了 {heal_amount} 生命值！", Colors.GREEN)
            return True
            
        elif item == "🧪 神秘药水":
            colored_print("🧪 你喝下了神秘药水...", Colors.MAGENTA)
            
            # 神秘药水随机效果
            effects = [
                ("health", "💚 药水恢复了你的生命值！", 50),
                ("mana", "🔮 药水恢复了你的法力值！", 25),
                ("both", "✨ 药水同时恢复了生命值和法力值！", (30, 15)),
                ("buff", "💪 药水增强了你的力量！下次攻击伤害翻倍！", None),
                ("skill", "📚 药水让你领悟了新的技能！", None)
            ]
            
            effect_type, message, value = random.choice(effects)
            self.inventory.remove(item)
            
            if effect_type == "health":
                old_health = self.health
                self.health = min(100, self.health + value)
                colored_print(message, Colors.GREEN)
                colored_print(f"   恢复了 {self.health - old_health} 生命值！", Colors.GREEN)
                
            elif effect_type == "mana":
                old_mana = self.mana
                self.mana = min(self.max_mana, self.mana + value)
                colored_print(message, Colors.MAGENTA)
                colored_print(f"   恢复了 {self.mana - old_mana} 法力值！", Colors.MAGENTA)
                
            elif effect_type == "both":
                health_restore, mana_restore = value
                old_health = self.health
                old_mana = self.mana
                self.health = min(100, self.health + health_restore)
                self.mana = min(self.max_mana, self.mana + mana_restore)
                colored_print(message, Colors.CYAN)
                colored_print(f"   恢复了 {self.health - old_health} 生命值和 {self.mana - old_mana} 法力值！", Colors.CYAN)
                
            elif effect_type == "buff":
                colored_print(message, Colors.YELLOW)
                # 这里可以设置一个临时buff标记
                self.stats["potion_buff"] = 1  # 下次攻击翻倍
                
            elif effect_type == "skill":
                colored_print(message, Colors.CYAN)
                # 随机学会一个技能
                available_skills = [skill for skill, data in self.skills.items() if data["level"] == 0]
                if available_skills:
                    skill = random.choice(available_skills)
                    self.skills[skill]["level"] = 1
                    colored_print(f"   🔮 学会了技能: {skill}！", Colors.MAGENTA)
                else:
                    # 如果没有可学技能，给经验
                    self.gain_exp(100)
                    colored_print("   ✨ 获得了 100 经验值！", Colors.CYAN)
            
            return True
            
        else:
            colored_print(f"❌ {item} 无法使用", Colors.RED)
            return False
    
    def equip_item(self, item):
        """
        Equip an item from inventory
        
        Args:
            item (str): Item name to equip
        """
        if item in self.inventory:
            # 武器装备
            weapon_items = ["🗡️ 木剑", "⚔️ 铁剑", "🗡️ 精钢剑", "🏹 长弓", "⚔️ 双手剑", 
                           "💀 死灵法杖", "🏔️ 巨人之锤", "👑 王者徽章", "⚔️ 传说之剑"]
            
            if item in weapon_items:
                if self.equipment["weapon"] and self.equipment["weapon"] != item:
                    self.inventory.append(self.equipment["weapon"])
                self.equipment["weapon"] = item
                self.inventory.remove(item)
                print(f"✅ 装备了 {item}！")
                
            # 防具装备
            elif item in ["🛡️ 盾牌", "🛡️ 铁甲", "🐉 龙鳞护甲"]:
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
            
            # 升级时恢复生命值，但不重置法力值
            old_health = self.health
            self.health = min(100, self.health + 20)
            health_gained = self.health - old_health
            
            # 恢复一些法力值，但不是全满
            old_mana = self.mana
            self.mana = min(self.max_mana, self.mana + 25)  # 恢复25点法力
            mana_gained = self.mana - old_mana
            
            print(f"🎉 恭喜升级到 {self.level} 级！")
            if health_gained > 0:
                print(f"❤️ 生命值恢复 {health_gained} 点！")
            if mana_gained > 0:
                print(f"💙 法力值恢复 {mana_gained} 点！")
            
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
            'max_mana': self.max_mana,
            'equipment': self.equipment,
            'quests': self.quests,
            'achievements': self.achievements,
            'stats': self.stats,
            'status_effects': self.status_effects,
            'battle_log': self.battle_log,  # 保存战斗日志
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
            player.mana = save_data.get('mana', 100)
            player.max_mana = save_data.get('max_mana', 100)
            player.equipment = save_data.get('equipment', player.equipment)
            player.quests = save_data.get('quests', player.quests)
            # 兼容性修复：为旧存档添加新任务
            player._update_quests_compatibility()
            player.achievements = save_data.get('achievements', player.achievements)
            player.stats = save_data.get('stats', player.stats)
            player.status_effects = save_data.get('status_effects', player.status_effects)
            player.battle_log = save_data.get('battle_log', [])  # 加载战斗日志
            
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