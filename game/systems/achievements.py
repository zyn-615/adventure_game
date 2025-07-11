"""
Achievement System Module - Achievement tracking and management

This module contains the AchievementSystem class which manages:
- Achievement definitions and tracking
- Achievement unlocking logic
- Achievement notifications
- Achievement persistence

Dependencies:
    - game.core.utils: Colors, colored_print
"""

# Handle relative imports
try:
    from ..core.utils import Colors, colored_print
except ImportError:
    # Standalone execution - adjust path and import
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from game.core.utils import Colors, colored_print


class AchievementSystem:
    """
    Achievement system for tracking and managing player achievements.
    
    This class handles achievement definitions, tracking, and notifications.
    """
    
    def __init__(self):
        """Initialize the achievement system."""
        self.achievements = {}
        self.unlocked_achievements = set()
    
    def register_achievement(self, achievement_id, name, description, condition):
        """
        Register a new achievement.
        
        Args:
            achievement_id (str): Unique identifier for the achievement
            name (str): Display name of the achievement
            description (str): Description of the achievement
            condition (callable): Function to check if achievement is unlocked
        """
        self.achievements[achievement_id] = {
            "name": name,
            "description": description,
            "condition": condition
        }
    
    def check_achievements(self, player):
        """
        Check all achievements against player state.
        
        Args:
            player: Player instance to check achievements for
        """
        for achievement_id, achievement_data in self.achievements.items():
            if (achievement_id not in self.unlocked_achievements and 
                achievement_data["condition"](player)):
                self.unlock_achievement(achievement_id)
    
    def unlock_achievement(self, achievement_id):
        """
        Unlock an achievement and show notification.
        
        Args:
            achievement_id (str): ID of the achievement to unlock
        """
        if achievement_id in self.achievements:
            self.unlocked_achievements.add(achievement_id)
            achievement = self.achievements[achievement_id]
            colored_print(f"🏆 成就解锁: {achievement['name']}", Colors.YELLOW)
            colored_print(f"   {achievement['description']}", Colors.CYAN)
    
    def get_unlocked_achievements(self):
        """Get list of unlocked achievements."""
        return list(self.unlocked_achievements)
    
    def get_achievement_progress(self):
        """Get achievement progress statistics."""
        total = len(self.achievements)
        unlocked = len(self.unlocked_achievements)
        return {
            "total": total,
            "unlocked": unlocked,
            "percentage": (unlocked / total * 100) if total > 0 else 0
        }