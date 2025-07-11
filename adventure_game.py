#!/usr/bin/env python3
"""
奇幻冒险游戏 - 原始版本 (向后兼容)
现在使用模块化架构
"""

import random
import time
import os
import json

# 从模块化版本导入核心组件
from game.core import Player, Enemy, Pet, Boss, Colors, colored_print, health_bar, stat_progress_bar
from game.systems import CombatSystem, BossCombatSystem
from game.world import WeaponShop, MagicShop, PetShop, shop, discount_shop

# Player class is now imported from game.core

# Pet class is now imported from game.core

# Enemy class is now imported from game.core

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
                            player.mana = player.max_mana  # 恢复到最大法力值
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
                
                # Add homeowner achievement logic could be added here if needed
                # player.add_achievement("homeowner", "🏠 房屋主人", "购买了第一套房产")
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

def random_event(player):
    # 基础事件
    basic_events = [
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
    
    # 特殊互动事件
    interactive_events = [
        {
            "name": "🗡️ 剑之试炼",
            "description": "一把古老的剑插在石头中，传说只有勇者能拔出它！",
            "type": "interactive",
            "action": "sword_trial"
        },
        {
            "name": "🔮 水晶神谕",
            "description": "一个神秘的水晶球开始发光，似乎要告诉你什么...",
            "type": "interactive", 
            "action": "crystal_oracle"
        },
        {
            "name": "🎲 幸运骰子",
            "description": "你发现了一个金色的骰子，要试试运气吗？",
            "type": "interactive",
            "action": "luck_dice"
        },
        {
            "name": "🐾 迷失小动物",
            "description": "一只受伤的小动物蜷缩在路边，看起来需要帮助...",
            "type": "interactive",
            "action": "help_animal"
        },
        {
            "name": "📜 古老卷轴",
            "description": "你发现了一卷古老的羊皮纸，上面记载着神秘的知识...",
            "type": "interactive",
            "action": "ancient_scroll"
        }
    ]
    
    # 负面事件（增加挑战性）
    negative_events = [
        {
            "name": "🌫️ 迷雾陷阱",
            "description": "突然降下的迷雾让你迷失了方向...",
            "type": "negative",
            "effect": "confusion"
        },
        {
            "name": "🕳️ 隐藏陷阱",
            "description": "你不小心踩到了一个隐藏的陷阱！",
            "type": "damage",
            "value": random.randint(5, 15)
        },
        {
            "name": "👻 幽灵干扰",
            "description": "一个恶作剧的幽灵偷走了你的一些法力！",
            "type": "mana_drain",
            "value": random.randint(5, 10)
        }
    ]
    
    # 根据概率选择事件类型
    event_roll = random.random()
    if event_roll < 0.6:  # 60% 基础事件
        events = basic_events
    elif event_roll < 0.85:  # 25% 互动事件
        events = interactive_events
    else:  # 15% 负面事件
        events = negative_events
    
    event = random.choice(events)
    player.stats["random_events"] += 1
    
    colored_print(f"\n✨ {event['name']}", Colors.BOLD + Colors.CYAN)
    colored_print(f"   {event['description']}", Colors.CYAN)
    
    # 处理不同类型的事件
    if event["type"] == "heal":
        player.health = min(100, player.health + event["value"])
        colored_print(f"   💚 恢复了 {event['value']} 点生命值！", Colors.GREEN)
    elif event["type"] == "gold":
        player.gold += event["value"]
        colored_print(f"   💰 获得了 {event['value']} 金币！", Colors.YELLOW)
    elif event["type"] == "exp":
        player.gain_exp(event["value"])
        colored_print(f"   ✨ 获得了 {event['value']} 经验值！", Colors.CYAN)
    elif event["type"] == "mana":
        player.mana = min(player.max_mana, player.mana + event["value"])
        colored_print(f"   🔮 恢复了 {event['value']} 法力值！", Colors.MAGENTA)
    elif event["type"] == "shop_discount":
        discount_shop(player)
    elif event["type"] == "interactive":
        handle_interactive_event(player, event["action"])
    elif event["type"] == "damage":
        player.health = max(1, player.health - event["value"])
        colored_print(f"   💥 受到了 {event['value']} 点伤害！", Colors.RED)
    elif event["type"] == "mana_drain":
        player.mana = max(0, player.mana - event["value"])
        colored_print(f"   👻 失去了 {event['value']} 点法力！", Colors.RED)
    elif event["type"] == "negative":
        if event["effect"] == "confusion":
            colored_print("   😵 你感到头晕目眩，下次战斗开始时法力减少5点！", Colors.RED)
            player.mana = max(0, player.mana - 5)
    
    player.check_achievements()

def handle_interactive_event(player, action):
    """处理互动事件"""
    if action == "sword_trial":
        colored_print("\n⚔️ 你决定尝试拔出这把剑...", Colors.YELLOW)
        choice = input("你要如何尝试？(1-用力拔取 / 2-轻柔尝试 / 3-放弃): ")
        
        if choice == "1":
            if random.random() < 0.3:  # 30% 成功率
                colored_print("✅ 剑被你拔了出来！这是一把传说中的武器！", Colors.GREEN)
                player.inventory.append("⚔️ 传说之剑")
                colored_print("   获得了 ⚔️ 传说之剑！", Colors.YELLOW)
            else:
                colored_print("❌ 剑纹丝不动，你的手被震伤了！", Colors.RED)
                player.health = max(1, player.health - 10)
        elif choice == "2":
            if random.random() < 0.6:  # 60% 成功率
                colored_print("✅ 你轻柔地触碰剑柄，感受到一股神秘的力量！", Colors.GREEN)
                player.gain_exp(50)
                colored_print("   获得了 50 经验值！", Colors.CYAN)
            else:
                colored_print("💭 什么也没有发生...", Colors.YELLOW)
        else:
            colored_print("🚶 你明智地选择了离开。", Colors.CYAN)
    
    elif action == "crystal_oracle":
        colored_print("\n🔮 水晶球开始闪烁...", Colors.MAGENTA)
        oracle_messages = [
            "未来的道路充满挑战，但胜利属于勇者！",
            "小心火山深处的危险，但宝藏就在那里等待！",
            "你的宠物将在关键时刻拯救你的生命！",
            "一个强大的敌人正在等待，准备好你的最强装备！",
            "友善对待遇到的每一个生物，善有善报！"
        ]
        message = random.choice(oracle_messages)
        colored_print(f"   💬 神谕: {message}", Colors.MAGENTA)
        
        # 给予一个小奖励
        if random.random() < 0.5:
            player.mana = min(player.max_mana, player.mana + 15)
            colored_print("   🔮 预言的力量恢复了你的法力！", Colors.MAGENTA)
    
    elif action == "luck_dice":
        colored_print("\n🎲 你投掷了幸运骰子...", Colors.YELLOW)
        dice_roll = random.randint(1, 6)
        colored_print(f"   🎲 骰子显示: {dice_roll}！", Colors.YELLOW)
        
        if dice_roll == 6:
            colored_print("🍀 大吉！你获得了丰厚的奖励！", Colors.GREEN)
            player.gold += 100
            player.gain_exp(80)
            colored_print("   💰 获得了 100 金币和 80 经验值！", Colors.YELLOW)
        elif dice_roll >= 4:
            colored_print("😊 小吉！你获得了一些奖励！", Colors.GREEN)
            reward = random.choice(["金币", "经验", "治疗"])
            if reward == "金币":
                bonus = random.randint(30, 50)
                player.gold += bonus
                colored_print(f"   💰 获得了 {bonus} 金币！", Colors.YELLOW)
            elif reward == "经验":
                bonus = random.randint(30, 50)
                player.gain_exp(bonus)
                colored_print(f"   ✨ 获得了 {bonus} 经验值！", Colors.CYAN)
            else:
                player.health = min(100, player.health + 25)
                colored_print("   💚 恢复了 25 生命值！", Colors.GREEN)
        else:
            colored_print("😔 运气不佳...什么也没有发生。", Colors.RED)
    
    elif action == "help_animal":
        colored_print("\n🐾 你温柔地接近这只小动物...", Colors.GREEN)
        choice = input("你要如何帮助它？(1-用面包喂食 / 2-用治疗术 / 3-轻抚安慰): ")
        
        helped = False
        if choice == "1" and "🍞 面包" in player.inventory:
            player.inventory.remove("🍞 面包")
            helped = True
            colored_print("🍞 你用面包喂食了小动物！", Colors.GREEN)
        elif choice == "2" and player.mana >= 6:
            player.mana -= 6
            helped = True
            colored_print("💚 你用治疗术帮助了小动物！", Colors.GREEN)
        elif choice == "3":
            helped = True
            colored_print("🤗 你轻抚安慰了小动物！", Colors.GREEN)
        
        if helped:
            colored_print("😊 小动物恢复了活力，感激地看着你！", Colors.GREEN)
            # 有概率获得新宠物
            if random.random() < 0.3 and len(player.pets) < 3:
                pet_types = ["🐱 小猫", "🐶 小狗", "🐰 兔子", "🦜 鹦鹉"]
                pet_type = random.choice(pet_types)
                pet_name = f"救助的{pet_type.split()[1]}"
                player.add_pet(pet_type, pet_name)
                colored_print(f"   🎉 {pet_name} 决定跟随你的冒险！", Colors.CYAN)
            else:
                luck_bonus = random.randint(20, 40)
                player.gold += luck_bonus
                colored_print(f"   🍀 善良获得了回报！获得了 {luck_bonus} 金币！", Colors.YELLOW)
        else:
            colored_print("😔 你没有合适的方式帮助它...", Colors.RED)
    
    elif action == "ancient_scroll":
        colored_print("\n📜 你仔细研读这份古老的卷轴...", Colors.CYAN)
        scroll_types = ["skill", "map", "recipe", "lore"]
        scroll_type = random.choice(scroll_types)
        
        if scroll_type == "skill":
            colored_print("✨ 这是一份技能卷轴！你学会了新的战斗技巧！", Colors.CYAN)
            # 随机提升一个技能等级
            available_skills = [skill for skill, data in player.skills.items() if data["level"] == 0]
            if available_skills:
                skill = random.choice(available_skills)
                player.skills[skill]["level"] = 1
                colored_print(f"   🔮 学会了技能: {skill}！", Colors.MAGENTA)
            else:
                player.gain_exp(60)
                colored_print("   ✨ 获得了 60 经验值！", Colors.CYAN)
        elif scroll_type == "map":
            colored_print("🗺️ 这是一份古老的地图！标记了一个宝藏位置！", Colors.YELLOW)
            treasure = random.randint(80, 120)
            player.gold += treasure
            colored_print(f"   💰 根据地图找到了 {treasure} 金币的宝藏！", Colors.YELLOW)
        elif scroll_type == "recipe":
            colored_print("🧪 这是一份炼金配方！", Colors.GREEN)
            player.inventory.append("🧪 神秘药水")
            colored_print("   🧪 获得了神秘药水！", Colors.GREEN)
        else:
            colored_print("📚 这记载了古老的传说，增长了你的见识！", Colors.CYAN)
            player.gain_exp(40)
            colored_print("   ✨ 获得了 40 经验值！", Colors.CYAN)


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
    
    # Initialize combat system
    combat_system = CombatSystem()
    
    locations = [
        ("🌲 神秘森林", [("🐺 野狼", 45, 16), ("🕷️ 巨蜘蛛", 35, 14), ("🐻 黑熊", 85, 24)]),
        ("🏔️ 山洞", [("🦇 蝙蝠", 30, 12), ("👹 哥布林", 55, 20), ("🐉 洞穴龙", 130, 30)]),
        ("🏰 古堡", [("💀 骷髅战士", 65, 22), ("🐉 小龙", 110, 27), ("👻 幽灵", 50, 18)]),
        ("🌋 火山", [("🔥 火元素", 75, 26), ("🌋 岩浆怪", 95, 28), ("🐲 火龙", 160, 38)]),
        ("❄️ 冰窟", [("🧊 冰元素", 70, 22), ("🐧 冰企鹅", 40, 16), ("🐻‍❄️ 冰熊", 120, 32)]),
        ("🌊 深海", [("🐙 章鱼", 80, 25), ("🦈 鲨鱼", 90, 28), ("🐋 海怪", 150, 35)]),
        ("🏜️ 沙漠", [("🦂 沙漠蝎", 60, 20), ("🐍 毒蛇", 55, 22), ("🐪 沙漠之王", 140, 33)]),
        ("🏛️ 地下城", [("🧟 僵尸", 70, 24), ("🐲 地龙", 120, 29), ("👑 地下君主", 180, 40)]),
        # 新增区域
        ("🌌 星空神殿", [("⭐ 星灵", 90, 30), ("🌟 流星", 85, 28), ("🌙 月神使者", 200, 45)]),
        ("🎪 奇幻马戏团", [("🤡 魔法小丑", 75, 25), ("🎭 变形师", 80, 27), ("🎪 马戏团长", 170, 42)]),
        ("🏚️ 废弃工厂", [("🤖 失控机器人", 95, 32), ("⚙️ 机械蜘蛛", 70, 26), ("🏭 工厂守卫", 190, 48)]),
        ("🌺 魔法花园", [("🌸 花仙子", 50, 18), ("🦋 魔法蝴蝶", 45, 15), ("🌳 古树精灵", 160, 35)]),
        ("🌪️ 风暴之眼", [("⚡ 雷电精灵", 85, 29), ("🌪️ 风暴元素", 100, 34), ("☁️ 云端巨人", 220, 50)]),
        ("🗻 天空之城", [("👼 天使战士", 110, 36), ("🕊️ 圣光鸽", 65, 22), ("👑 天空王", 250, 55)])
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
        print("6. 🌊 深海探险")
        print("7. 🏜️ 沙漠远征")
        print("8. 🏛️ 地下城冒险")
        print("9. 🌌 星空神殿")
        print("10. 🎪 奇幻马戏团")
        print("11. 🏚️ 废弃工厂")
        print("12. 🌺 魔法花园")
        print("13. 🌪️ 风暴之眼")
        print("14. 🗻 天空之城")
        print("15. 🏘️ 访问城镇")
        print("16. 🏪 访问商店")
        print("17. 👑 Boss挑战")
        print("18. 📊 查看状态")
        print("19. 🎒 管理装备")
        print("20. 🐾 宠物管理")
        print("21. 🏆 查看成就")
        print("22. 📜 战斗日志")
        print("23. 📈 详细属性")
        print("24. 💾 保存游戏")
        print("25. 🚪 退出游戏")
        
        try:
            choice = int(input("\n请选择 (1-25): "))
            
            if choice in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
                location_name, enemies = locations[choice-1]
                print(f"\n🚶 进入 {location_name}...")
                
                # 新区域特殊描述
                if choice == 6:  # 深海
                    print("🌊 你潜入深蓝色的海底世界，珊瑚礁和神秘的海洋生物环绕着你...")
                elif choice == 7:  # 沙漠
                    print("🏜️ 炙热的沙漠风吹过你的脸庞，远处的绿洲若隐若现...")
                elif choice == 8:  # 地下城
                    print("🏛️ 古老的石阶通向地下深处，空气中弥漫着神秘的魔法气息...")
                elif choice == 9:  # 星空神殿
                    print("🌌 你踏入璀璨的星空神殿，星辰的光芒洒在古老的石柱上...")
                elif choice == 10:  # 奇幻马戏团
                    print("🎪 色彩斑斓的帐篷映入眼帘，空气中回荡着神秘的音乐...")
                elif choice == 11:  # 废弃工厂
                    print("🏚️ 锈迹斑斑的机器静静伫立，偶尔传来金属碰撞声...")
                elif choice == 12:  # 魔法花园
                    print("🌺 芬芳的花香扑鼻而来，各种奇异的植物散发着魔法光芒...")
                elif choice == 13:  # 风暴之眼
                    print("🌪️ 雷电交加的风暴中心，强烈的魔法能量在空中涌动...")
                elif choice == 14:  # 天空之城
                    print("🗻 漂浮在云端的城市，圣洁的光芒从城墙中透出...")
                
                if random.random() < 0.8:  # 80% 概率遇到敌人
                    enemy_name, enemy_health, enemy_attack = random.choice(enemies)
                    result = combat_system.start_battle(player, enemy_name, enemy_health, enemy_attack, location_name)
                    
                    if result == "game_over":
                        print("\n💀 游戏结束！")
                        break
                    elif result == True and player.active_pet:
                        # 宠物获得经验
                        pet_exp = random.randint(10, 20)
                        player.active_pet.gain_exp(pet_exp)
                        colored_print(f"🐾 {player.active_pet.name} 获得 {pet_exp} 经验！", Colors.CYAN)
                        
                        # 更新任务进度
                        if choice == 1:  # 森林
                            player.update_quest("forest", enemy_name)
                        elif choice == 3:  # 古堡
                            player.update_quest("castle", enemy_name)
                        elif choice == 4:  # 火山
                            player.update_quest("volcano", enemy_name)
                        elif choice == 5:  # 冰窟
                            player.update_quest("ice", enemy_name)
                        elif choice == 6:  # 深海
                            player.update_quest("ocean", enemy_name)
                        elif choice == 7:  # 沙漠
                            player.update_quest("desert", enemy_name)
                        elif choice == 8:  # 地下城
                            player.update_quest("dungeon", enemy_name)
                        elif choice == 9:  # 星空神殿
                            player.update_quest("star", enemy_name)
                        elif choice == 10:  # 奇幻马戏团
                            player.update_quest("circus", enemy_name)
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
            
            elif choice == 15:
                visit_town(player)
            
            elif choice == 16:
                shop(player)
            
            elif choice == 17:
                # Boss挑战
                boss_combat = BossCombatSystem()
                boss_encounters = [
                    ("🐉 远古巨龙", 280, 35, "dragon"),
                    ("💀 死灵巫师", 240, 32, "lich"),
                    ("🏔️ 山岳巨人", 320, 38, "giant"),
                    ("👑 堕落国王", 260, 34, "standard")
                ]
                
                colored_print("\n👑 === Boss挑战 ===", Colors.BOLD + Colors.RED)
                colored_print("选择你想挑战的Boss:", Colors.YELLOW)
                
                for i, (name, health, attack, boss_type) in enumerate(boss_encounters):
                    print(f"{i+1}. {name} (生命值: {health}, 攻击力: {attack})")
                
                print("0. 返回")
                
                try:
                    boss_choice = int(input("选择Boss (0-4): "))
                    if boss_choice == 0:
                        continue
                    elif 1 <= boss_choice <= len(boss_encounters):
                        boss_name, boss_health, boss_attack, boss_type = boss_encounters[boss_choice-1]
                        
                        # 检查玩家等级要求
                        min_level = 3 + boss_choice
                        if player.level < min_level:
                            colored_print(f"❌ 挑战 {boss_name} 需要至少 {min_level} 级！", Colors.RED)
                            continue
                        
                        colored_print(f"🎯 你选择挑战 {boss_name}！", Colors.CYAN)
                        result = boss_combat.start_boss_battle(player, boss_name, boss_health, boss_attack, boss_type)
                        
                        if result == "game_over":
                            print("\n💀 游戏结束！")
                            break
                    else:
                        colored_print("❌ 无效选择", Colors.RED)
                except ValueError:
                    colored_print("❌ 请输入数字", Colors.RED)
            
            elif choice == 18:
                player.show_status()
            
            elif choice == 19:
                equip_items = [item for item in player.inventory 
                              if item in ["🗡️ 木剑", "⚔️ 铁剑", "🗡️ 精钢剑", "🏹 长弓", "⚔️ 双手剑", "🛡️ 盾牌", "🛡️ 铁甲", "💀 死灵法杖", "🏔️ 巨人之锤", "👑 王者徽章", "🐉 龙鳞护甲", "⚔️ 传说之剑"]]
                if equip_items:
                    print("\n🎒 可装备物品:")
                    for i, item in enumerate(equip_items):
                        print(f"{i+1}. {item}")
                    print("0. 返回")
                    print("C. 装备比较模式")
                    
                    try:
                        choice_input = input("选择装备 (数字/C): ").strip()
                        
                        if choice_input.upper() == 'C':
                            # 装备比较模式
                            print("\n🔍 装备比较模式 - 选择要比较的装备:")
                            for i, item in enumerate(equip_items):
                                print(f"{i+1}. {item}")
                            try:
                                compare_choice = int(input("选择要比较的装备 (0-返回): "))
                                if 1 <= compare_choice <= len(equip_items):
                                    selected_item = equip_items[compare_choice-1]
                                    player.show_equipment_comparison(selected_item)
                                    
                                    # 询问是否装备
                                    confirm = input("\n是否装备这件装备？(y/n): ").lower()
                                    if confirm == 'y':
                                        player.equip_item(selected_item)
                                elif compare_choice == 0:
                                    pass
                                else:
                                    print("❌ 无效选择")
                            except ValueError:
                                print("❌ 请输入数字")
                        
                        elif choice_input == '0':
                            pass
                        else:
                            equip_choice = int(choice_input)
                            if 1 <= equip_choice <= len(equip_items):
                                selected_item = equip_items[equip_choice-1]
                                # 显示装备比较
                                player.show_equipment_comparison(selected_item)
                                
                                # 询问是否装备
                                confirm = input("\n确认装备？(y/n): ").lower()
                                if confirm == 'y':
                                    player.equip_item(selected_item)
                            else:
                                print("❌ 无效选择")
                                
                    except ValueError:
                        print("❌ 请输入有效选项")
                else:
                    print("❌ 没有可装备的物品")
            
            elif choice == 20:
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
            
            elif choice == 21:
                player.show_achievements()
            
            elif choice == 22:
                player.show_battle_log()
            
            elif choice == 23:
                player.show_detailed_stats()
            
            elif choice == 24:
                player.save_game()
            
            elif choice == 25:
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