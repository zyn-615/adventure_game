"""
WeaponShop class for the adventure game.

Handles the sale of weapons and armor.
"""

# Import necessary modules from the main game
from ...core.utils import Colors, colored_print


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