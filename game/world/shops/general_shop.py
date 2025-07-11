"""
General shop functions for the adventure game.

Contains the main shop function and special discount shop.
"""


def shop(player):
    """Main shop function for general items"""
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
                    player.mana = min(player.max_mana, player.mana + 25)
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


def discount_shop(player):
    """Special discount shop function (half price)"""
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
                    player.mana = min(player.max_mana, player.mana + 25)
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