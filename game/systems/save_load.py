"""
Save/Load System Module - Game state persistence

This module contains the SaveLoadSystem class which manages:
- Game state serialization and deserialization
- Save file management
- Data validation and error handling
- Multiple save slot support

Dependencies:
    - game.core.utils: Colors, colored_print
    - json: For data serialization
    - os: For file operations
"""

import json
import os
from datetime import datetime

# Handle relative imports
try:
    from ..core.utils import Colors, colored_print
except ImportError:
    # Standalone execution - adjust path and import
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from game.core.utils import Colors, colored_print


class SaveLoadSystem:
    """
    Save/Load system for game state persistence.
    
    This class handles saving and loading game state to/from files.
    """
    
    def __init__(self, save_dir="saves"):
        """
        Initialize the save/load system.
        
        Args:
            save_dir (str): Directory to store save files
        """
        self.save_dir = save_dir
        self.ensure_save_directory()
    
    def ensure_save_directory(self):
        """Ensure save directory exists."""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def save_game(self, player, filename=None):
        """
        Save player game state to file.
        
        Args:
            player: Player instance to save
            filename (str): Optional filename, defaults to player name
            
        Returns:
            bool: True if save successful, False otherwise
        """
        if filename is None:
            filename = f"{player.name}.json"
        
        filepath = os.path.join(self.save_dir, filename)
        
        try:
            save_data = {
                "player_name": player.name,
                "health": player.health,
                "gold": player.gold,
                "inventory": player.inventory,
                "level": player.level,
                "exp": player.exp,
                "skills": player.skills,
                "pets": [pet.to_dict() for pet in player.pets] if hasattr(player, 'pets') else [],
                "achievements": list(player.achievements) if hasattr(player, 'achievements') else [],
                "stats": player.stats,
                "quests": player.quests if hasattr(player, 'quests') else {},
                "save_time": datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            colored_print(f"✅ 游戏已保存到: {filepath}", Colors.GREEN)
            return True
            
        except Exception as e:
            colored_print(f"❌ 保存失败: {str(e)}", Colors.RED)
            return False
    
    def load_game(self, player, filename=None):
        """
        Load player game state from file.
        
        Args:
            player: Player instance to load data into
            filename (str): Optional filename, defaults to player name
            
        Returns:
            bool: True if load successful, False otherwise
        """
        if filename is None:
            filename = f"{player.name}.json"
        
        filepath = os.path.join(self.save_dir, filename)
        
        if not os.path.exists(filepath):
            colored_print(f"❌ 存档文件不存在: {filepath}", Colors.RED)
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Load basic player data
            player.health = save_data.get("health", 100)
            player.gold = save_data.get("gold", 50)
            player.inventory = save_data.get("inventory", [])
            player.level = save_data.get("level", 1)
            player.exp = save_data.get("exp", 0)
            player.skills = save_data.get("skills", {})
            player.stats = save_data.get("stats", {})
            
            # Load optional data
            if "quests" in save_data and hasattr(player, 'quests'):
                player.quests = save_data["quests"]
            
            if "achievements" in save_data and hasattr(player, 'achievements'):
                player.achievements = set(save_data["achievements"])
            
            # Load pets if available
            if "pets" in save_data and hasattr(player, 'pets'):
                player.pets = []
                for pet_data in save_data["pets"]:
                    # This would need to be implemented in the Pet class
                    pass
            
            save_time = save_data.get("save_time", "未知")
            colored_print(f"✅ 游戏已加载 (保存时间: {save_time})", Colors.GREEN)
            return True
            
        except Exception as e:
            colored_print(f"❌ 加载失败: {str(e)}", Colors.RED)
            return False
    
    def list_save_files(self):
        """
        List all available save files.
        
        Returns:
            list: List of save file names
        """
        try:
            save_files = [f for f in os.listdir(self.save_dir) if f.endswith('.json')]
            return save_files
        except Exception:
            return []
    
    def delete_save_file(self, filename):
        """
        Delete a save file.
        
        Args:
            filename (str): Name of the save file to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        filepath = os.path.join(self.save_dir, filename)
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                colored_print(f"✅ 已删除存档: {filename}", Colors.GREEN)
                return True
            else:
                colored_print(f"❌ 存档文件不存在: {filename}", Colors.RED)
                return False
        except Exception as e:
            colored_print(f"❌ 删除失败: {str(e)}", Colors.RED)
            return False