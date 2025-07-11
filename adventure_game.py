#!/usr/bin/env python3
import random
import time
import os
import json

# 颜色代码
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def colored_print(text, color=Colors.WHITE):
    """带颜色的打印函数"""
    print(f"{color}{text}{Colors.END}")

def health_bar(current, maximum, length=20):
    """生成生命值条"""
    filled = int(length * current / maximum)
    bar = '█' * filled + '░' * (length - filled)
    
    if current / maximum > 0.6:
        color = Colors.GREEN
    elif current / maximum > 0.3:
        color = Colors.YELLOW
    else:
        color = Colors.RED
    
    return f"{color}[{bar}]{Colors.END} {current}/{maximum}"

class Player:
    def __init__(self, name):
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
        """添加宠物"""
        if len(self.pets) >= 3:  # 最多3只宠物
            return False, "宠物数量已达上限"
        
        pet = Pet(name, pet_type)
        self.pets.append(pet)
        
        if not self.active_pet:
            self.active_pet = pet
        
        colored_print(f"🎉 获得新宠物: {pet.get_display_name()}！", Colors.GREEN)
        return True, "宠物已添加"
    
    def switch_pet(self, pet_index):
        """切换宠物"""
        if 0 <= pet_index < len(self.pets):
            self.active_pet = self.pets[pet_index]
            colored_print(f"🔄 切换到宠物: {self.active_pet.get_display_name()}", Colors.CYAN)
            return True
        return False
    
    def show_pets(self):
        """显示宠物列表"""
        if not self.pets:
            colored_print("你还没有宠物", Colors.YELLOW)
            return
        
        colored_print("🐾 === 宠物列表 ===", Colors.BOLD)
        for i, pet in enumerate(self.pets):
            status = "★" if pet == self.active_pet else " "
            print(f"{i+1}.{status} {pet.get_display_name()}")
            print(f"   忠诚度: {pet.loyalty}/100, 经验: {pet.exp}/100")
    
    def feed_pet(self, pet_index):
        """喂养宠物"""
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
        """获取状态效果的显示名称"""
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
        """应用状态效果"""
        if effect in self.status_effects:
            self.status_effects[effect]["duration"] = duration
            effect_name = self.get_effect_display_name(effect)
            colored_print(f"✨ 获得状态效果: {effect_name} ({duration}回合)", Colors.YELLOW)
    
    def process_status_effects(self):
        """处理状态效果"""
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
        """检查是否被眩晕"""
        return self.status_effects["stun"]["duration"] > 0
    
    def is_frozen(self):
        """检查是否被冰冻"""
        return self.status_effects["freeze"]["duration"] > 0
    
    def check_achievements(self):
        """检查并解锁成就"""
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
        """显示所有成就"""
        print("\n🏆 === 成就系统 ===")
        for name, data in self.achievements.items():
            status = "✅" if data["completed"] else "❌"
            print(f"{status} {name}: {data['description']}")
        
        completed = sum(1 for data in self.achievements.values() if data["completed"])
        print(f"\n总进度: {completed}/{len(self.achievements)} ({completed/len(self.achievements)*100:.1f}%)")
    
    def track_near_death(self):
        """追踪濒死状态"""
        if self.health <= 10 and self.health > 0:
            self.stats["near_death_survived"] += 1
    
    def update_quest(self, quest_type, enemy_name=None):
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
        """尝试闪避攻击，包含宠物加成"""
        dodge_chance = 0.10
        if self.active_pet:
            dodge_chance += self.active_pet.abilities.get("dodge_boost", 0)
        
        if random.random() < dodge_chance:
            colored_print("💨 成功闪避了攻击！", Colors.CYAN)
            return True
        return False
    
    def equip_item(self, item):
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
        self.exp += amount
        if self.exp >= 100:
            self.level += 1
            self.exp -= 100
            self.health = min(100, self.health + 20)
            self.mana = 50
            print(f"🎉 恭喜升级到 {self.level} 级！生命值和法力值恢复！")
            self.unlock_skills()
    
    def unlock_skills(self):
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
            
            # 加载房屋数据
            house_data = save_data.get('house', {})
            if house_data.get('owned', False) and house_data.get('house_type'):
                player.house = House(
                    house_data['house_type'],
                    house_data['name'],
                    house_data['price'],
                    house_data['rooms']
                )
                player.house.owned = house_data['owned']
                player.house.comfort_level = house_data.get('comfort_level', 1)
                player.house.upgrades = house_data.get('upgrades', [])
                
                # 恢复家具数据
                furnishings_data = house_data.get('furnishings', {})
                for furn_id, furn_data in furnishings_data.items():
                    player.house.furnishings[furn_id] = Furnishing(
                        furn_data['name'],
                        furn_data['item_type'],
                        furn_data['price'],
                        furn_data['comfort_bonus'],
                        furn_data['description']
                    )
            
            player.current_save_slot = slot  # 设置当前存档槽位
            
            print(f"📂 从槽位 {slot} 加载游戏成功！")
            return player
        except Exception as e:
            print(f"❌ 加载失败: {e}")
            return None

class Pet:
    def __init__(self, name, pet_type, level=1):
        self.name = name
        self.pet_type = pet_type
        self.level = level
        self.exp = 0
        self.loyalty = 50
        self.abilities = self.get_abilities()
    
    def get_abilities(self):
        """根据宠物类型获取能力"""
        abilities = {
            "🐺 幼狼": {"attack_boost": 5, "special": "howl"},
            "🐉 小龙": {"attack_boost": 10, "special": "flame"},
            "🦅 鹰": {"dodge_boost": 0.05, "special": "scout"},
            "🐻 熊崽": {"defense_boost": 3, "special": "shield"},
            "🐱 猫": {"crit_boost": 0.03, "special": "stealth"}
        }
        return abilities.get(self.pet_type, {"attack_boost": 2})
    
    def level_up(self):
        """宠物升级"""
        if self.exp >= 100:
            self.level += 1
            self.exp -= 100
            self.loyalty = min(100, self.loyalty + 5)
            colored_print(f"🎉 {self.name} 升级到 {self.level} 级！", Colors.GREEN)
            return True
        return False
    
    def gain_exp(self, amount):
        """获得经验"""
        self.exp += amount
        self.level_up()
    
    def use_special_ability(self, battle_context=None):
        """使用特殊能力"""
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
        """获取显示名称"""
        return f"{self.pet_type} {self.name} (Lv.{self.level})"

class Enemy:
    def __init__(self, name, health, attack):
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
        """应用状态效果"""
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
        """处理状态效果"""
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
        """检查是否被眩晕"""
        return self.status_effects["stun"]["duration"] > 0
    
    def is_frozen(self):
        """检查是否被冰冻"""
        return self.status_effects["freeze"]["duration"] > 0

class NPC:
    def __init__(self, name, npc_type, dialogue, services=None):
        self.name = name
        self.npc_type = npc_type  # merchant, quest_giver, guard, etc.
        self.dialogue = dialogue
        self.services = services or []
        self.friendship = 0
        self.quests_given = []
    
    def talk(self, player):
        """与NPC对话"""
        colored_print(f"\n💬 {self.name}: {self.dialogue}", Colors.CYAN)
        
        if self.services:
            print("\n可用服务:")
            for i, service in enumerate(self.services):
                print(f"{i+1}. {service}")
            print("0. 结束对话")
            
            try:
                choice = int(input("选择服务: "))
                if 1 <= choice <= len(self.services):
                    return self.services[choice-1]
                elif choice == 0:
                    return None
            except ValueError:
                colored_print("无效输入", Colors.RED)
        
        return None
    
    def increase_friendship(self, amount=1):
        """增加好友度"""
        self.friendship = min(100, self.friendship + amount)

class Town:
    def __init__(self, name):
        self.name = name
        self.npcs = {}
        self.buildings = {}
        self.player_house = None
        self.bulletin_board = BulletinBoard()
    
    def add_npc(self, npc_id, npc):
        """添加NPC"""
        self.npcs[npc_id] = npc
    
    def add_building(self, building_id, building):
        """添加建筑"""
        self.buildings[building_id] = building
    
    def show_town(self, player):
        """显示城镇界面"""
        colored_print(f"\n🏘️ === 欢迎来到 {self.name} ===", Colors.BOLD + Colors.YELLOW)
        print("🌅 阳光明媚的小镇，居民们友善地向你打招呼")
        
        if player.pets:
            print(f"🐾 你的宠物 {player.active_pet.name if player.active_pet else '们'} 好奇地四处张望")
        
        print("\n🏢 可访问的地点:")
        print("1. 🏪 武器商店 - 购买武器装备")
        print("2. 🔮 魔法商店 - 购买技能书和药水")
        print("3. 🐾 宠物商店 - 宠物相关服务")
        print("4. 🏠 房屋中介 - 购买和管理房屋")
        print("5. 📋 任务公告板 - 查看可用任务")
        print("6. 🍺 酒馆 - 休息和打听消息")
        print("7. 💰 银行 - 存取金币")
        print("8. 🎯 竞技场 - 战斗训练")
        print("9. 🚪 离开城镇")
        
        return True

class BulletinBoard:
    def __init__(self):
        self.quests = [
            {
                "title": "📦 商队护送",
                "description": "护送商队安全通过森林",
                "reward": {"gold": 150, "exp": 80},
                "requirements": {"level": 3},
                "type": "escort"
            },
            {
                "title": "🐺 狼群威胁",
                "description": "消灭威胁村庄的狼群",
                "reward": {"gold": 200, "exp": 100},
                "requirements": {"enemies_defeated": 10},
                "type": "hunt"
            },
            {
                "title": "💎 失落的宝石",
                "description": "寻找丢失的珍贵宝石",
                "reward": {"gold": 300, "item": "💎 宝石"},
                "requirements": {"level": 5},
                "type": "collect"
            }
        ]
    
    def show_quests(self, player):
        """显示可用任务"""
        colored_print("\n📋 === 任务公告板 ===", Colors.BOLD)
        available_quests = []
        
        for i, quest in enumerate(self.quests):
            if self.check_requirements(quest, player):
                available_quests.append((i, quest))
                print(f"{len(available_quests)}. {quest['title']}")
                print(f"   {quest['description']}")
                print(f"   奖励: {quest['reward']['gold']}金币")
                if 'exp' in quest['reward']:
                    print(f"         {quest['reward']['exp']}经验")
                if 'item' in quest['reward']:
                    print(f"         {quest['reward']['item']}")
                print()
        
        if not available_quests:
            colored_print("目前没有适合你的任务", Colors.YELLOW)
            return
        
        try:
            choice = int(input("选择任务 (0-返回): "))
            if 1 <= choice <= len(available_quests):
                quest_index, quest = available_quests[choice-1]
                self.accept_quest(quest, player)
        except ValueError:
            colored_print("无效输入", Colors.RED)
    
    def check_requirements(self, quest, player):
        """检查任务要求"""
        reqs = quest["requirements"]
        if "level" in reqs and player.level < reqs["level"]:
            return False
        if "enemies_defeated" in reqs and player.stats["enemies_defeated"] < reqs["enemies_defeated"]:
            return False
        return True
    
    def accept_quest(self, quest, player):
        """接受任务"""
        colored_print(f"✅ 接受任务: {quest['title']}", Colors.GREEN)
        # 这里可以添加任务到玩家的任务列表
        # 简单起见，直接给予奖励
        player.gold += quest["reward"]["gold"]
        if "exp" in quest["reward"]:
            player.gain_exp(quest["reward"]["exp"])
        if "item" in quest["reward"]:
            player.inventory.append(quest["reward"]["item"])
        colored_print("任务奖励已发放！", Colors.GREEN)

# 城镇建筑类
class WeaponShop:
    def __init__(self):
        self.name = "🏪 铁匠铺"
        self.owner = "哈默大叔"
        self.inventory = [
            ("⚔️ 铁剑", 100, "优质的铁制长剑"),
            ("🗡️ 精钢剑", 200, "锋利的精钢武器"),
            ("🛡️ 盾牌", 80, "坚固的木制盾牌"),
            ("🛡️ 铁甲", 150, "重型防护装备"),
            ("🏹 长弓", 120, "远程攻击武器"),
            ("⚔️ 双手剑", 250, "威力巨大的双手武器")
        ]
    
    def visit(self, player):
        colored_print(f"\n{self.name}", Colors.BOLD + Colors.BLUE)
        colored_print(f"💬 {self.owner}: 欢迎来到我的铁匠铺！这里有最好的武器装备！", Colors.CYAN)
        
        while True:
            print(f"\n💰 你的金币: {player.gold}")
            print("\n商品列表:")
            for i, (item, price, desc) in enumerate(self.inventory):
                print(f"{i+1}. {item} - {price}金币 ({desc})")
            
            print("0. 离开商店")
            
            try:
                choice = int(input("选择商品: "))
                if 1 <= choice <= len(self.inventory):
                    item, price, desc = self.inventory[choice-1]
                    if player.gold >= price:
                        player.gold -= price
                        player.inventory.append(item)
                        player.stats["items_bought"] += 1
                        colored_print(f"✅ 购买了 {item}！", Colors.GREEN)
                        player.check_achievements()
                    else:
                        colored_print("❌ 金币不足！", Colors.RED)
                elif choice == 0:
                    colored_print(f"💬 {self.owner}: 欢迎下次再来！", Colors.CYAN)
                    break
                else:
                    colored_print("❌ 无效选择", Colors.RED)
            except ValueError:
                colored_print("❌ 请输入数字", Colors.RED)

class MagicShop:
    def __init__(self):
        self.name = "🔮 魔法商店"
        self.owner = "莉娜法师"
        self.inventory = [
            ("🧪 法力药水", 20, "恢复25法力值"),
            ("💚 治疗药水", 30, "恢复50生命值"),
            ("📜 火球术卷轴", 100, "学习火球术"),
            ("📜 护盾术卷轴", 80, "学习护盾术"),
            ("🔥 火焰宝石", 150, "增强火系技能"),
            ("❄️ 冰霜宝石", 150, "增强冰系技能"),
            ("⚡ 雷电宝石", 150, "增强雷系技能")
        ]
    
    def visit(self, player):
        colored_print(f"\n{self.name}", Colors.BOLD + Colors.MAGENTA)
        colored_print(f"💬 {self.owner}: 欢迎！需要什么魔法物品吗？", Colors.CYAN)
        
        while True:
            print(f"\n💰 你的金币: {player.gold}")
            print("\n商品列表:")
            for i, (item, price, desc) in enumerate(self.inventory):
                print(f"{i+1}. {item} - {price}金币 ({desc})")
            
            print("0. 离开商店")
            
            try:
                choice = int(input("选择商品: "))
                if 1 <= choice <= len(self.inventory):
                    item, price, desc = self.inventory[choice-1]
                    if player.gold >= price:
                        player.gold -= price
                        if item == "🧪 法力药水":
                            player.mana = min(50, player.mana + 25)
                            colored_print(f"✅ 使用了 {item}，恢复25法力值！", Colors.GREEN)
                        elif item == "💚 治疗药水":
                            player.health = min(100, player.health + 50)
                            colored_print(f"✅ 使用了 {item}，恢复50生命值！", Colors.GREEN)
                        else:
                            player.inventory.append(item)
                            colored_print(f"✅ 购买了 {item}！", Colors.GREEN)
                        player.stats["items_bought"] += 1
                        player.check_achievements()
                    else:
                        colored_print("❌ 金币不足！", Colors.RED)
                elif choice == 0:
                    colored_print(f"💬 {self.owner}: 愿魔法与你同在！", Colors.CYAN)
                    break
                else:
                    colored_print("❌ 无效选择", Colors.RED)
            except ValueError:
                colored_print("❌ 请输入数字", Colors.RED)

class PetShop:
    def __init__(self):
        self.name = "🐾 宠物商店"
        self.owner = "安娜"
        self.services = [
            ("🍖 宠物食物", 15, "提升宠物忠诚度"),
            ("💊 宠物治疗", 50, "治愈宠物疾病"),
            ("📈 宠物训练", 100, "提升宠物等级"),
            ("🎁 神秘宠物蛋", 500, "随机获得稀有宠物")
        ]
    
    def visit(self, player):
        colored_print(f"\n{self.name}", Colors.BOLD + Colors.GREEN)
        colored_print(f"💬 {self.owner}: 欢迎来到宠物商店！我们专门照顾各种可爱的小伙伴！", Colors.CYAN)
        
        while True:
            print(f"\n💰 你的金币: {player.gold}")
            if player.active_pet:
                print(f"🐾 当前宠物: {player.active_pet.get_display_name()}")
                print(f"   忠诚度: {player.active_pet.loyalty}/100")
            else:
                print("🐾 你还没有宠物")
            
            print("\n服务列表:")
            for i, (service, price, desc) in enumerate(self.services):
                print(f"{i+1}. {service} - {price}金币 ({desc})")
            
            print("0. 离开商店")
            
            try:
                choice = int(input("选择服务: "))
                if 1 <= choice <= len(self.services):
                    service, price, desc = self.services[choice-1]
                    if player.gold >= price:
                        player.gold -= price
                        
                        if service == "🍖 宠物食物":
                            if player.active_pet:
                                player.active_pet.loyalty = min(100, player.active_pet.loyalty + 20)
                                colored_print(f"✅ {player.active_pet.name} 的忠诚度增加了！", Colors.GREEN)
                            else:
                                colored_print("❌ 你没有宠物", Colors.RED)
                                player.gold += price  # 退款
                        
                        elif service == "💊 宠物治疗":
                            if player.active_pet:
                                player.active_pet.loyalty = min(100, player.active_pet.loyalty + 10)
                                colored_print(f"✅ {player.active_pet.name} 恢复了健康！", Colors.GREEN)
                            else:
                                colored_print("❌ 你没有宠物", Colors.RED)
                                player.gold += price  # 退款
                        
                        elif service == "📈 宠物训练":
                            if player.active_pet:
                                player.active_pet.gain_exp(50)
                                colored_print(f"✅ {player.active_pet.name} 获得了训练经验！", Colors.GREEN)
                            else:
                                colored_print("❌ 你没有宠物", Colors.RED)
                                player.gold += price  # 退款
                        
                        elif service == "🎁 神秘宠物蛋":
                            if len(player.pets) >= 3:
                                colored_print("❌ 宠物数量已达上限", Colors.RED)
                                player.gold += price  # 退款
                            else:
                                rare_pets = ["🦄 独角兽", "🐲 幼龙", "🦅 神鹰", "🐺 银狼"]
                                pet_type = random.choice(rare_pets)
                                pet_name = input(f"神秘宠物蛋孵化出了 {pet_type}！给它起个名字: ")
                                player.add_pet(pet_type, pet_name)
                    else:
                        colored_print("❌ 金币不足！", Colors.RED)
                elif choice == 0:
                    colored_print(f"💬 {self.owner}: 好好照顾你的宠物哦！", Colors.CYAN)
                    break
                else:
                    colored_print("❌ 无效选择", Colors.RED)
            except ValueError:
                colored_print("❌ 请输入数字", Colors.RED)

class Tavern:
    def __init__(self):
        self.name = "🍺 月光酒馆"
        self.owner = "汤姆老板"
        self.services = [
            ("🍺 麦酒", 10, "恢复体力，增加临时攻击力"),
            ("🍖 烤肉", 25, "饱腹感，恢复生命值"),
            ("🛏️ 休息", 50, "完全恢复生命值和法力值"),
            ("📰 打听消息", 20, "获得有用信息")
        ]
        self.rumors = [
            "听说火山深处有一条巨龙守护着宝藏",
            "最近森林里的怪物变得很活跃",
            "有商人在古堡附近发现了稀有宝石",
            "传说冰窟里有强大的冰系武器",
            "竞技场正在举办新的挑战赛"
        ]
    
    def visit(self, player):
        colored_print(f"\n{self.name}", Colors.BOLD + Colors.YELLOW)
        colored_print(f"💬 {self.owner}: 欢迎来到月光酒馆！来一杯吗？", Colors.CYAN)
        
        while True:
            print(f"\n💰 你的金币: {player.gold}")
            print("🎵 酒馆里传来轻松的音乐声")
            
            print("\n服务列表:")
            for i, (service, price, desc) in enumerate(self.services):
                print(f"{i+1}. {service} - {price}金币 ({desc})")
            
            print("0. 离开酒馆")
            
            try:
                choice = int(input("选择服务: "))
                if 1 <= choice <= len(self.services):
                    service, price, desc = self.services[choice-1]
                    if player.gold >= price:
                        player.gold -= price
                        
                        if service == "🍺 麦酒":
                            player.apply_status_effect("regenerate", 3)
                            colored_print("✅ 你感到精神焕发！", Colors.GREEN)
                        
                        elif service == "🍖 烤肉":
                            player.health = min(100, player.health + 40)
                            colored_print("✅ 美味的烤肉让你恢复了体力！", Colors.GREEN)
                        
                        elif service == "🛏️ 休息":
                            player.health = 100
                            player.mana = 50
                            # 清除负面状态效果
                            for effect in ["burn", "freeze", "stun", "poison"]:
                                player.status_effects[effect]["duration"] = 0
                            colored_print("✅ 你睡了一个好觉，完全恢复了！", Colors.GREEN)
                        
                        elif service == "📰 打听消息":
                            rumor = random.choice(self.rumors)
                            colored_print(f"💬 消息: {rumor}", Colors.YELLOW)
                            
                    else:
                        colored_print("❌ 金币不足！", Colors.RED)
                elif choice == 0:
                    colored_print(f"💬 {self.owner}: 随时欢迎回来！", Colors.CYAN)
                    break
                else:
                    colored_print("❌ 无效选择", Colors.RED)
            except ValueError:
                colored_print("❌ 请输入数字", Colors.RED)

class House:
    def __init__(self, house_type, name, price, rooms=None):
        self.house_type = house_type
        self.name = name
        self.price = price
        self.rooms = rooms or []
        self.owned = False
        self.furnishings = {}
        self.upgrades = []
        self.comfort_level = 1
        self.rent_days_left = 0
        
    def get_description(self):
        descriptions = {
            "cottage": "🏠 一个温馨的小屋，适合初次置业",
            "house": "🏘️ 一栋舒适的房屋，有多个房间",
            "mansion": "🏰 豪华的大宅，彰显身份地位"
        }
        return descriptions.get(self.house_type, "一处房产")
    
    def calculate_daily_comfort(self):
        base_comfort = self.comfort_level * 10
        furnishing_bonus = len(self.furnishings) * 5
        upgrade_bonus = len(self.upgrades) * 15
        return base_comfort + furnishing_bonus + upgrade_bonus

class Furnishing:
    def __init__(self, name, item_type, price, comfort_bonus=0, description=""):
        self.name = name
        self.item_type = item_type
        self.price = price
        self.comfort_bonus = comfort_bonus
        self.description = description

class HouseBroker:
    def __init__(self):
        self.available_houses = {
            "cottage_1": House("cottage", "🏠 温馨小屋", 1000, ["客厅", "卧室"]),
            "cottage_2": House("cottage", "🏠 森林小屋", 1200, ["客厅", "卧室", "厨房"]),
            "house_1": House("house", "🏘️ 市郊别墅", 3000, ["客厅", "卧室", "厨房", "书房"]),
            "house_2": House("house", "🏘️ 花园洋房", 4000, ["客厅", "卧室", "厨房", "书房", "花园"]),
            "mansion_1": House("mansion", "🏰 贵族庄园", 10000, ["大厅", "主卧", "客卧", "厨房", "书房", "花园", "酒窖"])
        }
        
        self.furnishings = {
            "bed": Furnishing("🛏️ 舒适床铺", "bedroom", 200, 10, "提高休息质量"),
            "sofa": Furnishing("🛋️ 沙发", "living", 300, 8, "客厅必备家具"),
            "dining_table": Furnishing("🍽️ 餐桌", "dining", 250, 6, "用餐的好地方"),
            "bookshelf": Furnishing("📚 书架", "study", 400, 12, "存放书籍，提升智慧"),
            "fireplace": Furnishing("🔥 壁炉", "living", 600, 15, "温暖舒适的象征"),
            "garden_set": Furnishing("🌸 花园套装", "garden", 500, 20, "美丽的花园装饰"),
            "kitchen_set": Furnishing("🍳 厨房套装", "kitchen", 450, 10, "完整的厨房设备")
        }
        
        self.upgrades = {
            "security": {"name": "🔒 安全系统", "price": 800, "description": "提高房屋安全性"},
            "heating": {"name": "🔥 供暖系统", "price": 1000, "description": "冬天也很温暖"},
            "garden": {"name": "🌺 扩建花园", "price": 1500, "description": "扩大花园面积"},
            "storage": {"name": "📦 储物空间", "price": 600, "description": "增加储物能力"}
        }
    
    def show_available_houses(self, player):
        colored_print("\n🏠 === 可购买房屋 ===", Colors.BOLD + Colors.CYAN)
        
        available_count = 0
        for house_id, house in self.available_houses.items():
            if not house.owned:
                available_count += 1
                print(f"\n{available_count}. {house.name}")
                print(f"   💰 价格: {house.price} 金币")
                print(f"   📝 {house.get_description()}")
                print(f"   🏠 房间: {', '.join(house.rooms)}")
        
        if available_count == 0:
            colored_print("📍 目前没有可购买的房屋", Colors.YELLOW)
            return False
        
        return True
    
    def buy_house(self, player, house_choice):
        available_houses = [house for house in self.available_houses.values() if not house.owned]
        
        if 1 <= house_choice <= len(available_houses):
            house = available_houses[house_choice - 1]
            
            if player.gold >= house.price:
                player.gold -= house.price
                house.owned = True
                player.house = house
                
                colored_print(f"🎉 恭喜！你成功购买了 {house.name}！", Colors.GREEN)
                colored_print(f"💰 花费了 {house.price} 金币", Colors.YELLOW)
                
                player.add_achievement("homeowner", "🏠 房屋主人", "购买了第一套房产")
                return True
            else:
                colored_print(f"❌ 金币不足！需要 {house.price} 金币，你只有 {player.gold} 金币", Colors.RED)
        else:
            colored_print("❌ 无效选择", Colors.RED)
        
        return False
    
    def show_furnishings(self, player):
        if not hasattr(player, 'house') or not player.house:
            colored_print("❌ 你还没有房屋！", Colors.RED)
            return False
        
        colored_print("\n🛋️ === 可购买家具 ===", Colors.BOLD + Colors.CYAN)
        
        count = 0
        for furn_id, furn in self.furnishings.items():
            if furn_id not in player.house.furnishings:
                count += 1
                print(f"\n{count}. {furn.name}")
                print(f"   💰 价格: {furn.price} 金币")
                print(f"   🎯 舒适度: +{furn.comfort_bonus}")
                print(f"   📝 {furn.description}")
        
        if count == 0:
            colored_print("📍 所有家具都已购买！", Colors.GREEN)
            return False
        
        return True
    
    def buy_furnishing(self, player, furn_choice):
        if not hasattr(player, 'house') or not player.house:
            colored_print("❌ 你还没有房屋！", Colors.RED)
            return False
        
        available_furn = [(fid, f) for fid, f in self.furnishings.items() 
                         if fid not in player.house.furnishings]
        
        if 1 <= furn_choice <= len(available_furn):
            furn_id, furn = available_furn[furn_choice - 1]
            
            if player.gold >= furn.price:
                player.gold -= furn.price
                player.house.furnishings[furn_id] = furn
                
                colored_print(f"🎉 成功购买了 {furn.name}！", Colors.GREEN)
                colored_print(f"💰 花费了 {furn.price} 金币", Colors.YELLOW)
                colored_print(f"🎯 房屋舒适度提升了 {furn.comfort_bonus} 点！", Colors.CYAN)
                
                return True
            else:
                colored_print(f"❌ 金币不足！需要 {furn.price} 金币", Colors.RED)
        else:
            colored_print("❌ 无效选择", Colors.RED)
        
        return False
    
    def show_house_status(self, player):
        if not hasattr(player, 'house') or not player.house:
            colored_print("❌ 你还没有房屋！", Colors.RED)
            return
        
        house = player.house
        colored_print(f"\n🏠 === {house.name} ===", Colors.BOLD + Colors.CYAN)
        print(f"🏠 房屋类型: {house.get_description()}")
        print(f"🏠 房间数量: {len(house.rooms)}")
        print(f"🎯 舒适度等级: {house.comfort_level}")
        print(f"💫 每日舒适度加成: +{house.calculate_daily_comfort()}")
        
        if house.furnishings:
            print(f"\n🛋️ 已有家具 ({len(house.furnishings)}):")
            for furn in house.furnishings.values():
                print(f"   {furn.name} - 舒适度 +{furn.comfort_bonus}")
        else:
            print("\n🛋️ 家具: 无")
        
        if house.upgrades:
            print(f"\n⬆️ 升级项目 ({len(house.upgrades)}):")
            for upgrade in house.upgrades:
                print(f"   {upgrade}")
        else:
            print("\n⬆️ 升级项目: 无")
    
    def rest_at_home(self, player):
        if not hasattr(player, 'house') or not player.house:
            colored_print("❌ 你还没有房屋！", Colors.RED)
            return False
        
        house = player.house
        comfort_bonus = house.calculate_daily_comfort()
        
        health_restore = min(20 + comfort_bonus // 5, player.max_health - player.health)
        mana_restore = min(15 + comfort_bonus // 8, player.max_mana - player.mana)
        
        player.health += health_restore
        player.mana += mana_restore
        
        colored_print(f"😴 你在 {house.name} 中舒适地休息了一夜", Colors.GREEN)
        colored_print(f"❤️ 恢复了 {health_restore} 生命值", Colors.GREEN)
        colored_print(f"💙 恢复了 {mana_restore} 魔力值", Colors.BLUE)
        
        if comfort_bonus > 50:
            colored_print("✨ 舒适的环境让你精神倍增！", Colors.YELLOW)
            if player.active_pet:
                player.active_pet.add_experience(5)
                colored_print(f"🐾 你的宠物 {player.active_pet.name} 也很开心，获得了 5 经验值", Colors.CYAN)
        
        return True
    
    def interact(self, player):
        while True:
            colored_print("\n🏠 === 房屋中介 ===", Colors.BOLD + Colors.CYAN)
            print("欢迎来到翡翠谷房屋中介！我们为您提供最优质的房产服务。")
            
            if hasattr(player, 'house') and player.house:
                print(f"\n🏠 你的房产: {player.house.name}")
                print("1. 🛋️ 购买家具")
                print("2. 📊 查看房屋状态") 
                print("3. 😴 在家休息")
                print("4. 🔄 返回城镇")
                max_choice = 4
            else:
                print("\n1. 🏠 购买房屋")
                print("2. 🔄 返回城镇")
                max_choice = 2
            
            try:
                choice = int(input(f"请选择 (1-{max_choice}): "))
                
                if not hasattr(player, 'house') or not player.house:
                    if choice == 1:
                        if self.show_available_houses(player):
                            try:
                                house_choice = int(input("\n请选择要购买的房屋 (输入0返回): "))
                                if house_choice == 0:
                                    continue
                                self.buy_house(player, house_choice)
                            except ValueError:
                                colored_print("❌ 请输入数字", Colors.RED)
                    elif choice == 2:
                        break
                    else:
                        colored_print("❌ 无效选择", Colors.RED)
                else:
                    if choice == 1:
                        if self.show_furnishings(player):
                            try:
                                furn_choice = int(input("\n请选择要购买的家具 (输入0返回): "))
                                if furn_choice == 0:
                                    continue
                                self.buy_furnishing(player, furn_choice)
                            except ValueError:
                                colored_print("❌ 请输入数字", Colors.RED)
                    elif choice == 2:
                        self.show_house_status(player)
                    elif choice == 3:
                        self.rest_at_home(player)
                    elif choice == 4:
                        break
                    else:
                        colored_print("❌ 无效选择", Colors.RED)
            except ValueError:
                colored_print("❌ 请输入数字", Colors.RED)

def manage_saves():
    while True:
        print("\n📁 === 存档管理 ===")
        print("1. 📋 查看所有存档")
        print("2. 🗑️ 删除存档")
        print("3. 🔄 返回主菜单")
        
        try:
            choice = int(input("请选择 (1-3): "))
            
            if choice == 1:
                print("\n📋 === 存档列表 ===")
                for i in range(1, 6):
                    save_file = f"savegame_{i}.json"
                    if os.path.exists(save_file):
                        try:
                            with open(save_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            print(f"槽位{i}: {data.get('name', '未知')} - 等级 {data.get('level', 1)} - 金币 {data.get('gold', 0)}")
                        except:
                            print(f"槽位{i}: 损坏的存档")
                    else:
                        print(f"槽位{i}: 空")
            
            elif choice == 2:
                print("\n🗑️ === 删除存档 ===")
                existing_saves = []
                for i in range(1, 6):
                    save_file = f"savegame_{i}.json"
                    if os.path.exists(save_file):
                        try:
                            with open(save_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            print(f"{i}. 槽位{i} - {data.get('name', '未知')} (等级 {data.get('level', 1)})")
                            existing_saves.append(i)
                        except:
                            print(f"{i}. 槽位{i} - 损坏的存档")
                            existing_saves.append(i)
                
                if not existing_saves:
                    print("❌ 没有存档可以删除")
                    continue
                
                try:
                    slot = int(input("选择要删除的槽位 (0-取消): "))
                    if slot == 0:
                        continue
                    if slot not in existing_saves:
                        print("❌ 该槽位没有存档")
                        continue
                    
                    confirm = input(f"确定要删除槽位{slot}的存档吗？(y/N): ")
                    if confirm.lower() == 'y':
                        save_file = f"savegame_{slot}.json"
                        os.remove(save_file)
                        print(f"✅ 槽位{slot}的存档已删除")
                    else:
                        print("❌ 取消删除")
                except ValueError:
                    print("❌ 请输入数字")
            
            elif choice == 3:
                break
            
            else:
                print("❌ 无效选择")
        
        except ValueError:
            print("❌ 请输入数字")

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def type_text(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def battle(player, enemy_name, enemy_health, enemy_attack):
    colored_print(f"\n⚔️  遭遇 {enemy_name}！", Colors.RED)
    
    # 创建敌人对象
    enemy = Enemy(enemy_name, enemy_health, enemy_attack)
    
    while enemy.health > 0 and player.health > 0:
        # 处理玩家状态效果
        print(f"\n{Colors.BOLD}=== 回合开始 ==={Colors.END}")
        player.process_status_effects()
        
        # 如果玩家死亡，结束战斗
        if player.health <= 0:
            break
        
        print(f"\n你的生命值: {health_bar(player.health, 100)}")
        print(f"{enemy.name} 生命值: {health_bar(enemy.health, enemy.max_health)}")
        
        # 检查玩家是否被眩晕
        if player.is_stunned():
            colored_print("⚡ 你被眩晕了，无法行动！", Colors.RED)
        else:
            action = input("\n选择行动 (1-攻击 2-逃跑 3-使用物品 4-使用技能): ")
            
            if action == "1":
                damage = player.get_attack_damage()
                enemy.health -= damage
                colored_print(f"⚔️ 你对 {enemy.name} 造成了 {damage} 点伤害！", Colors.YELLOW)
            
            elif action == "2":
                if random.random() < 0.7:
                    colored_print("🏃 成功逃跑！", Colors.GREEN)
                    return False
                else:
                    colored_print("💨 逃跑失败！", Colors.RED)
            
            elif action == "3":
                if "🍞 面包" in player.inventory:
                    player.health = min(100, player.health + 30)
                    player.inventory.remove("🍞 面包")
                    colored_print("🍞 使用面包恢复了30点生命值！", Colors.GREEN)
                else:
                    colored_print("❌ 没有可用物品！", Colors.RED)
            
            elif action == "4":
                available_skills = [skill for skill, data in player.skills.items() if data["level"] > 0]
                if not available_skills:
                    colored_print("❌ 没有可用技能！", Colors.RED)
                    continue
                
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
                        continue
                    elif 1 <= skill_choice <= len(available_skills):
                        chosen_skill = available_skills[skill_choice-1]
                        success, result = player.use_skill(chosen_skill, enemy)
                        
                        if success:
                            if isinstance(result, tuple):
                                # 技能有状态效果
                                damage, effect = result
                                enemy.health -= damage
                                colored_print(f"🔮 使用 {chosen_skill}，对 {enemy.name} 造成 {damage} 点伤害！", Colors.MAGENTA)
                                # 应用状态效果
                                if random.random() < 0.6:  # 60%概率触发
                                    enemy.apply_status_effect(effect, 3)
                            elif isinstance(result, int):
                                # 普通伤害技能
                                enemy.health -= result
                                colored_print(f"🔮 使用 {chosen_skill}，对 {enemy.name} 造成 {result} 点伤害！", Colors.MAGENTA)
                            else:
                                # 其他技能效果
                                colored_print(f"🔮 使用 {chosen_skill}，{result}！", Colors.MAGENTA)
                        else:
                            colored_print(f"❌ {result}", Colors.RED)
                    else:
                        colored_print("❌ 无效选择", Colors.RED)
                        continue
                except ValueError:
                    colored_print("❌ 请输入数字", Colors.RED)
                    continue
        
        # 敌人行动
        if enemy.health > 0:
            # 处理敌人状态效果
            enemy.process_status_effects()
            
            # 如果敌人死亡，结束战斗
            if enemy.health <= 0:
                break
            
            # 检查敌人是否被眩晕
            if enemy.is_stunned():
                colored_print(f"⚡ {enemy.name} 被眩晕了，无法行动！", Colors.CYAN)
            else:
                # 敌人攻击
                if not player.try_dodge():
                    enemy_damage = max(1, random.randint(5, enemy.attack) - player.get_defense())
                    player.health -= enemy_damage
                    colored_print(f"😖 {enemy.name} 对你造成了 {enemy_damage} 点伤害！", Colors.RED)
                    player.track_near_death()
    
    if player.health <= 0:
        colored_print(f"💀 你被 {enemy.name} 击败了...", Colors.RED)
        return "game_over"
    else:
        reward = random.randint(10, 30)
        exp_reward = random.randint(20, 40)
        player.gold += reward
        player.gain_exp(exp_reward)
        player.stats["enemies_defeated"] += 1
        player.track_near_death()
        player.check_achievements()
        colored_print(f"🎉 击败了 {enemy.name}！获得 {reward} 金币和 {exp_reward} 经验！", Colors.GREEN)
        
        # 更新任务进度
        if enemy.name in ["🐺 野狼", "🕷️ 巨蜘蛛", "🐻 黑熊"]:
            player.update_quest("forest", enemy.name)
        elif enemy.name in ["💀 骷髅战士", "🐉 小龙", "👻 幽灵"]:
            player.update_quest("castle", enemy.name)
        elif enemy.name in ["🔥 火元素", "🌋 岩浆怪", "🐲 火龙"]:
            player.update_quest("volcano", enemy.name)
        elif enemy.name in ["🧊 冰元素", "🐧 冰企鹅", "🐻‍❄️ 冰熊"]:
            player.update_quest("ice", enemy.name)
        
        return True

def random_event(player):
    events = [
        {
            "name": "🌟 神秘商人",
            "description": "你遇到了一个神秘商人，他愿意以半价出售物品！",
            "type": "shop_discount"
        },
        {
            "name": "🍄 魔法蘑菇",
            "description": "你发现了一个发光的蘑菇！",
            "type": "heal",
            "value": 20
        },
        {
            "name": "💰 宝箱",
            "description": "你发现了一个被遗弃的宝箱！",
            "type": "gold",
            "value": random.randint(30, 80)
        },
        {
            "name": "🧙 智慧老人",
            "description": "一位智慧老人传授给你经验！",
            "type": "exp",
            "value": random.randint(40, 70)
        },
        {
            "name": "🌪️ 魔法风暴",
            "description": "魔法风暴恢复了你的法力值！",
            "type": "mana",
            "value": 30
        }
    ]
    
    event = random.choice(events)
    player.stats["random_events"] += 1  # 追踪随机事件次数
    print(f"\n✨ {event['name']}")
    print(f"   {event['description']}")
    
    if event["type"] == "heal":
        player.health = min(100, player.health + event["value"])
        print(f"   恢复了 {event['value']} 点生命值！")
    elif event["type"] == "gold":
        player.gold += event["value"]
        print(f"   获得了 {event['value']} 金币！")
    elif event["type"] == "exp":
        player.gain_exp(event["value"])
        print(f"   获得了 {event['value']} 经验值！")
    elif event["type"] == "mana":
        player.mana = min(50, player.mana + event["value"])
        print(f"   恢复了 {event['value']} 法力值！")
    elif event["type"] == "shop_discount":
        discount_shop(player)
    
    player.check_achievements()  # 检查成就

def discount_shop(player):
    print("\n🏪 === 神秘商店 (半价优惠!) ===")
    items = [
        ("🍞 面包", 5, "恢复30生命值"),
        ("⚔️ 铁剑", 50, "增加攻击力"),
        ("🛡️ 盾牌", 40, "减少受到伤害"),
        ("🗡️ 精钢剑", 100, "大幅增加攻击力"),
        ("🛡️ 铁甲", 75, "大幅减少受到伤害"),
        ("🧪 法力药水", 10, "恢复25法力值")
    ]
    
    for i, (item, price, desc) in enumerate(items):
        print(f"{i+1}. {item} - {price}金币 ({desc})")
    
    try:
        choice = int(input(f"\n你有 {player.gold} 金币，要买什么？(0-离开): "))
        if 1 <= choice <= len(items):
            item, price, desc = items[choice-1]
            if player.gold >= price:
                player.gold -= price
                player.stats["items_bought"] += 1  # 追踪购买的物品数量
                if item == "🧪 法力药水":
                    player.mana = min(50, player.mana + 25)
                    print(f"✅ 使用了 {item}，恢复25法力值！")
                else:
                    player.inventory.append(item)
                    print(f"✅ 购买了 {item}！")
                player.check_achievements()  # 检查成就
            else:
                print("❌ 金币不足！")
        elif choice == 0:
            print("👋 离开神秘商店")
        else:
            print("❌ 无效选择")
    except ValueError:
        print("❌ 请输入数字")

def shop(player):
    print("\n🏪 === 商店 ===")
    items = [
        ("🍞 面包", 10, "恢复30生命值"),
        ("⚔️ 铁剑", 100, "增加攻击力"),
        ("🛡️ 盾牌", 80, "减少受到伤害"),
        ("🗡️ 精钢剑", 200, "大幅增加攻击力"),
        ("🛡️ 铁甲", 150, "大幅减少受到伤害"),
        ("💎 宝石", 300, "神秘物品"),
        ("🧪 法力药水", 20, "恢复25法力值")
    ]
    
    for i, (item, price, desc) in enumerate(items):
        print(f"{i+1}. {item} - {price}金币 ({desc})")
    
    try:
        choice = int(input(f"\n你有 {player.gold} 金币，要买什么？(0-退出): "))
        if 1 <= choice <= len(items):
            item, price, desc = items[choice-1]
            if player.gold >= price:
                player.gold -= price
                player.stats["items_bought"] += 1  # 追踪购买的物品数量
                if item == "🧪 法力药水":
                    player.mana = min(50, player.mana + 25)
                    print(f"✅ 使用了 {item}，恢复25法力值！")
                elif item == "💎 宝石":
                    player.inventory.append(item)
                    print(f"✅ 购买了 {item}！")
                    player.update_quest("gem")
                else:
                    player.inventory.append(item)
                    print(f"✅ 购买了 {item}！")
                player.check_achievements()  # 检查成就
            else:
                print("❌ 金币不足！")
        elif choice == 0:
            print("👋 离开商店")
        else:
            print("❌ 无效选择")
    except ValueError:
        print("❌ 请输入数字")

def main():
    clear_screen()
    colored_print("🌟 欢迎来到奇幻冒险世界！ 🌟", Colors.BOLD + Colors.CYAN)
    colored_print("=" * 40, Colors.BLUE)
    
    print("1. 🆕 开始新游戏")
    print("2. 📂 加载游戏")
    print("3. 📁 存档管理")
    print("4. 🚪 退出")
    
    try:
        start_choice = int(input("请选择 (1-4): "))
        if start_choice == 1:
            name = input("🧙 请输入你的角色名字: ")
            player = Player(name)
        elif start_choice == 2:
            player = Player.load_game()
            if player is None:
                name = input("🧙 请输入你的角色名字: ")
                player = Player(name)
        elif start_choice == 3:
            manage_saves()
            return main()  # 回到主菜单
        elif start_choice == 4:
            print("👋 感谢游玩！再见！")
            return
        else:
            print("❌ 无效选择，开始新游戏")
            name = input("🧙 请输入你的角色名字: ")
            player = Player(name)
    except ValueError:
        print("❌ 无效输入，开始新游戏")
        name = input("🧙 请输入你的角色名字: ")
        player = Player(name)
    
    type_text(f"\n✨ 欢迎，勇敢的 {player.name}！你的冒险即将开始...")
    
    locations = [
        ("🌲 神秘森林", [("🐺 野狼", 40, 15), ("🕷️ 巨蜘蛛", 30, 12), ("🐻 黑熊", 80, 22)]),
        ("🏔️ 山洞", [("🦇 蝙蝠", 25, 10), ("👹 哥布林", 50, 18), ("🐉 洞穴龙", 120, 28)]),
        ("🏰 古堡", [("💀 骷髅战士", 60, 20), ("🐉 小龙", 100, 25), ("👻 幽灵", 45, 16)]),
        ("🌋 火山", [("🔥 火元素", 70, 24), ("🌋 岩浆怪", 90, 26), ("🐲 火龙", 150, 35)]),
        ("❄️ 冰窟", [("🧊 冰元素", 65, 20), ("🐧 冰企鹅", 35, 14), ("🐻‍❄️ 冰熊", 110, 30)])
    ]
    
    while player.health > 0:
        print("\n" + "="*50)
        print("🗺️  你在世界地图上...")
        print("选择你的下一步行动:")
        print("1. 🌲 探索神秘森林")
        print("2. 🏔️ 进入山洞")
        print("3. 🏰 挑战古堡")
        print("4. 🌋 探索火山")
        print("5. ❄️ 进入冰窟")
        print("6. 🏘️ 访问城镇")
        print("7. 🏪 访问商店")
        print("8. 📊 查看状态")
        print("9. 🎒 管理装备")
        print("10. 🐾 宠物管理")
        print("11. 🏆 查看成就")
        print("12. 💾 保存游戏")
        print("13. 🚪 退出游戏")
        
        try:
            choice = int(input("\n请选择 (1-13): "))
            
            if choice in [1, 2, 3, 4, 5]:
                location_name, enemies = locations[choice-1]
                print(f"\n🚶 进入 {location_name}...")
                
                if random.random() < 0.8:  # 80% 概率遇到敌人
                    enemy_name, enemy_health, enemy_attack = random.choice(enemies)
                    result = battle(player, enemy_name, enemy_health, enemy_attack)
                    
                    if result == "game_over":
                        print("\n💀 游戏结束！")
                        break
                    elif result == True and player.active_pet:
                        # 宠物获得经验
                        pet_exp = random.randint(10, 20)
                        player.active_pet.gain_exp(pet_exp)
                        colored_print(f"🐾 {player.active_pet.name} 获得 {pet_exp} 经验！", Colors.CYAN)
                else:
                    # 20% 概率触发随机事件
                    if random.random() < 0.6:
                        random_event(player)
                    else:
                        treasure = random.randint(5, 20)
                        player.gold += treasure
                        print(f"✨ 你发现了 {treasure} 金币的宝藏！")
                        # 5% 概率遇到宠物
                        if random.random() < 0.05 and len(player.pets) < 3:
                            pet_types = ["🐺 幼狼", "🐉 小龙", "🦅 鹰", "🐻 熊崽", "🐱 猫"]
                            pet_type = random.choice(pet_types)
                            pet_name = input(f"你遇到了一只 {pet_type}！给它起个名字: ")
                            player.add_pet(pet_type, pet_name)
            
            elif choice == 6:
                visit_town(player)
            
            elif choice == 7:
                shop(player)
            
            elif choice == 8:
                player.show_status()
            
            elif choice == 9:
                equip_items = [item for item in player.inventory 
                              if item in ["🗡️ 木剑", "⚔️ 铁剑", "🗡️ 精钢剑", "🛡️ 盾牌", "🛡️ 铁甲"]]
                if equip_items:
                    print("\n🎒 可装备物品:")
                    for i, item in enumerate(equip_items):
                        print(f"{i+1}. {item}")
                    try:
                        equip_choice = int(input("选择装备 (0-返回): "))
                        if 1 <= equip_choice <= len(equip_items):
                            player.equip_item(equip_items[equip_choice-1])
                        elif equip_choice == 0:
                            pass
                        else:
                            print("❌ 无效选择")
                    except ValueError:
                        print("❌ 请输入数字")
                else:
                    print("❌ 没有可装备的物品")
            
            elif choice == 10:
                # 宠物管理
                while True:
                    colored_print("\n🐾 === 宠物管理 ===", Colors.BOLD)
                    player.show_pets()
                    print("\n1. 切换宠物")
                    print("2. 喂养宠物")
                    print("3. 返回主菜单")
                    
                    try:
                        pet_choice = int(input("选择操作 (1-3): "))
                        if pet_choice == 1:
                            if player.pets:
                                try:
                                    pet_index = int(input("选择宠物 (输入编号): ")) - 1
                                    if player.switch_pet(pet_index):
                                        pass
                                    else:
                                        colored_print("无效的宠物编号", Colors.RED)
                                except ValueError:
                                    colored_print("请输入数字", Colors.RED)
                            else:
                                colored_print("你还没有宠物", Colors.YELLOW)
                        elif pet_choice == 2:
                            if player.pets:
                                try:
                                    pet_index = int(input("选择要喂养的宠物 (输入编号): ")) - 1
                                    player.feed_pet(pet_index)
                                except ValueError:
                                    colored_print("请输入数字", Colors.RED)
                            else:
                                colored_print("你还没有宠物", Colors.YELLOW)
                        elif pet_choice == 3:
                            break
                        else:
                            colored_print("无效选择", Colors.RED)
                    except ValueError:
                        colored_print("请输入数字", Colors.RED)
            
            elif choice == 11:
                player.show_achievements()
            
            elif choice == 12:
                player.save_game()
            
            elif choice == 13:
                print("👋 感谢游玩！再见！")
                break
            
            else:
                print("❌ 无效选择，请重试")
                
        except ValueError:
            print("❌ 请输入数字")
        except KeyboardInterrupt:
            print("\n\n👋 游戏被中断，再见！")
            break
    
    print(f"\n🎮 最终统计:")
    print(f"⭐ 最终等级: {player.level}")
    print(f"💰 剩余金币: {player.gold}")
    print(f"🎒 收集物品: {len(player.inventory)} 件")

def visit_town(player):
    """访问城镇"""
    # 创建城镇和建筑
    town = Town("翡翠谷镇")
    
    # 初始化各种商店
    weapon_shop = WeaponShop()
    magic_shop = MagicShop()
    pet_shop = PetShop()
    tavern = Tavern()
    house_broker = HouseBroker()
    
    while True:
        town.show_town(player)
        
        try:
            choice = int(input("\n选择地点 (1-9): "))
            
            if choice == 1:
                weapon_shop.visit(player)
            elif choice == 2:
                magic_shop.visit(player)
            elif choice == 3:
                pet_shop.visit(player)
            elif choice == 4:
                # 房屋中介
                house_broker.interact(player)
            elif choice == 5:
                # 任务公告板
                town.bulletin_board.show_quests(player)
            elif choice == 6:
                tavern.visit(player)
            elif choice == 7:
                # 银行
                colored_print("\n💰 翡翠银行", Colors.BOLD)
                colored_print("💬 银行家: 欢迎来到翡翠银行！", Colors.CYAN)
                colored_print("💬 银行家: 目前我们的服务正在升级中，请稍后再来！", Colors.CYAN)
            elif choice == 8:
                # 竞技场
                colored_print("\n🎯 竞技场", Colors.BOLD)
                colored_print("💬 教练: 竞技场正在准备新的挑战！", Colors.CYAN)
                colored_print("💬 教练: 请稍后再来体验！", Colors.CYAN)
            elif choice == 9:
                colored_print("🚪 你离开了翡翠谷镇", Colors.YELLOW)
                break
            else:
                colored_print("❌ 无效选择", Colors.RED)
        except ValueError:
            colored_print("❌ 请输入数字", Colors.RED)

if __name__ == "__main__":
    main()