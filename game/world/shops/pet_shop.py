"""
PetShop class for the adventure game.

Handles pet-related services including food, healing, training, and rare pet adoption.
"""

# Import necessary modules from the main game
import random
from ...core.utils import Colors, colored_print


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