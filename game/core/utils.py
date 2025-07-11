"""
游戏工具函数
"""

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

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_for_input(prompt="按回车键继续..."):
    """等待用户输入"""
    input(prompt)

def random_choice_weighted(choices):
    """权重随机选择"""
    if not choices:
        return None
    
    total_weight = sum(weight for _, weight in choices)
    r = random.uniform(0, total_weight)
    
    for choice, weight in choices:
        r -= weight
        if r <= 0:
            return choice
    
    return choices[-1][0]  # 备用返回最后一个选择