#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奇幻冒险游戏 - 跨平台启动器
支持 Windows、WSL、Linux、macOS
"""

import sys
import os
import platform
import subprocess

def detect_platform():
    """检测运行平台"""
    system = platform.system().lower()
    
    # 检测WSL
    if system == "linux":
        try:
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    return "wsl"
        except:
            pass
        return "linux"
    elif system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    else:
        return "unknown"

def setup_encoding():
    """设置编码环境"""
    platform_name = detect_platform()
    
    if platform_name == "windows":
        # Windows编码设置
        try:
            # 设置控制台代码页为UTF-8
            subprocess.run(['chcp', '65001'], 
                         capture_output=True, shell=True)
        except:
            pass
        
        try:
            # 设置Python输出编码
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass
    
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    return platform_name

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("❌ 需要Python 3.6或更高版本")
        print(f"   当前版本: Python {version.major}.{version.minor}.{version.micro}")
        return False
    return True

def check_dependencies():
    """检查依赖文件"""
    missing_files = []
    
    # 检查核心文件
    required_files = [
        'adventure_game.py'
    ]
    
    # 检查模块化文件（可选）
    optional_files = [
        'game/__init__.py',
        'game/core/__init__.py',
        'game/core/player.py',
        'game/core/enemy.py',
        'game/core/utils.py',
        'game/systems/__init__.py',
        'game/systems/combat.py',
        'game/world/__init__.py'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少核心文件:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    # 检查可选模块化文件
    modules_available = all(os.path.exists(f) for f in optional_files)
    
    return True, modules_available

def show_platform_info(platform_name):
    """显示平台信息"""
    platform_emoji = {
        "windows": "🪟",
        "wsl": "🐧",
        "linux": "🐧", 
        "macos": "🍎",
        "unknown": "❓"
    }
    
    platform_names = {
        "windows": "Windows",
        "wsl": "WSL (Windows Subsystem for Linux)",
        "linux": "Linux",
        "macos": "macOS",
        "unknown": "未知系统"
    }
    
    emoji = platform_emoji.get(platform_name, "❓")
    name = platform_names.get(platform_name, "未知系统")
    
    print(f"{emoji} 检测到平台: {name}")
    print(f"🐍 Python版本: {sys.version.split()[0]}")

def run_game_modular():
    """运行模块化版本"""
    try:
        print("📦 加载模块化版本...")
        import adventure_game
        adventure_game.main()
        return True
    except ImportError as e:
        print(f"❌ 模块化版本加载失败: {e}")
        return False

def run_game_standalone():
    """运行独立版本"""
    try:
        print("📄 运行独立版本...")
        with open('adventure_game.py', 'r', encoding='utf-8') as f:
            code = f.read()
        exec(code)
        return True
    except Exception as e:
        print(f"❌ 独立版本运行失败: {e}")
        return False

def main():
    """主函数"""
    # 设置编码和检测平台
    platform_name = setup_encoding()
    
    print("🎮 奇幻冒险游戏 - 跨平台启动器")
    print("=" * 50)
    
    # 显示平台信息
    show_platform_info(platform_name)
    print()
    
    # 检查Python版本
    if not check_python_version():
        input("按回车键退出...")
        return
    
    # 检查依赖
    deps_result = check_dependencies()
    if isinstance(deps_result, tuple):
        core_ok, modules_ok = deps_result
    else:
        core_ok = deps_result
        modules_ok = False
    
    if not core_ok:
        input("按回车键退出...")
        return
    
    print("✅ 文件检查完成")
    
    if modules_ok:
        print("📦 模块化版本可用")
    else:
        print("📄 仅独立版本可用")
    
    print()
    print("🚀 启动游戏...")
    print("-" * 30)
    
    # 尝试运行游戏
    success = False
    
    if modules_ok:
        success = run_game_modular()
    
    if not success:
        success = run_game_standalone()
    
    if not success:
        print("\n❌ 游戏启动失败")
        print("\n可能的解决方案:")
        print("1. 检查Python版本 (需要3.6+)")
        print("2. 确保adventure_game.py文件存在")
        print("3. 检查文件编码是否为UTF-8")
        
        if platform_name == "windows":
            print("4. 尝试使用Windows Terminal")
            print("5. 在命令提示符中运行: chcp 65001")
        elif platform_name == "wsl":
            print("4. 确保WSL环境配置正确")
            print("5. 检查文件权限")
        
        input("\n按回车键退出...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 游戏被中断，再见！")
    except Exception as e:
        print(f"\n❌ 启动器错误: {e}")
        input("按回车键退出...")