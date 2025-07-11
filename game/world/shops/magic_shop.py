"""
MagicShop class for the adventure game.

Handles the sale of magic items, potions, and spell scrolls.
"""

# Import necessary modules from the main game
from ...core.utils import Colors, colored_print


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
                            player.mana = min(player.max_mana, player.mana + 25)
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