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
    """带颜色的打印函数，支持跨平台"""
    import platform
    import os
    
    # 检测是否支持颜色
    supports_color = True
    
    # Windows平台检查
    if platform.system().lower() == "windows":
        # Windows 10以上支持ANSI
        import sys
        try:
            # 尝试启用ANSI支持
            import subprocess
            subprocess.run([''], shell=True)
            
            # 检查是否在支持颜色的终端中
            if not (hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()):
                supports_color = False
        except:
            supports_color = False
    
    # 如果支持颜色就使用，否则只打印文本
    if supports_color and os.getenv('NO_COLOR') is None:
        print(f"{color}{text}{Colors.END}")
    else:
        print(text)

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

def progress_bar(current, maximum, length=20, prefix="", suffix="", show_percentage=True):
    """
    生成可视化进度条
    
    Args:
        current (int): 当前值
        maximum (int): 最大值
        length (int): 进度条长度（字符数）
        prefix (str): 前缀文本
        suffix (str): 后缀文本
        show_percentage (bool): 是否显示百分比
        
    Returns:
        str: 格式化的进度条字符串
    """
    if maximum <= 0:
        return f"{prefix}[{'░' * length}] 0/0 (0%){suffix}"
    
    # 计算填充长度
    filled = int(length * current / maximum)
    filled = max(0, min(filled, length))  # 确保在有效范围内
    
    # 生成进度条
    bar = '█' * filled + '░' * (length - filled)
    
    # 根据进度选择颜色
    percentage = current / maximum
    if percentage >= 1.0:
        color = Colors.GREEN
    elif percentage >= 0.7:
        color = Colors.CYAN
    elif percentage >= 0.4:
        color = Colors.YELLOW
    else:
        color = Colors.RED
    
    # 构建进度条字符串
    result = f"{prefix}{color}[{bar}]{Colors.END} {current}/{maximum}"
    
    if show_percentage:
        result += f" ({percentage * 100:.1f}%)"
    
    result += suffix
    
    return result

def exp_progress_bar(current_exp, level, length=20):
    """
    生成经验值进度条
    
    Args:
        current_exp (int): 当前经验值
        level (int): 当前等级
        length (int): 进度条长度
        
    Returns:
        str: 经验值进度条
    """
    exp_needed = 100  # 每级需要100经验
    return progress_bar(
        current_exp, 
        exp_needed, 
        length, 
        prefix=f"⭐ Lv.{level} ",
        suffix=" EXP"
    )

def quest_progress_bar(current, target, quest_name, length=15):
    """
    生成任务进度条
    
    Args:
        current (int): 当前进度
        target (int): 目标值
        quest_name (str): 任务名称
        length (int): 进度条长度
        
    Returns:
        str: 任务进度条
    """
    # 截断任务名称以适应显示
    display_name = quest_name[:20] + "..." if len(quest_name) > 20 else quest_name
    
    return progress_bar(
        current, 
        target, 
        length, 
        prefix=f"{display_name}: ",
        show_percentage=False
    )

def stat_progress_bar(current, maximum, stat_name, length=12):
    """
    生成属性进度条（如生命值、法力值）
    
    Args:
        current (int): 当前值
        maximum (int): 最大值
        stat_name (str): 属性名称
        length (int): 进度条长度
        
    Returns:
        str: 属性进度条
    """
    # 为不同属性选择图标
    icons = {
        "health": "❤️",
        "mana": "💙", 
        "loyalty": "💖",
        "exp": "✨"
    }
    
    icon = icons.get(stat_name.lower(), "📊")
    
    return progress_bar(
        current, 
        maximum, 
        length, 
        prefix=f"{icon} ",
        show_percentage=False
    )