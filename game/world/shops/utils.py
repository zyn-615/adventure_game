"""
Shared utilities for shop modules.

Contains common functions and classes used by all shop modules.
"""


class Colors:
    """Color codes for console output"""
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