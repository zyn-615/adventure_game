"""
Shops module for the adventure game.

This module contains all shop-related classes and functions including:
- WeaponShop: For purchasing weapons and armor
- MagicShop: For purchasing magic items and potions
- PetShop: For pet-related services
- Main shop function and discount shop function
"""

from .weapon_shop import WeaponShop
from .magic_shop import MagicShop
from .pet_shop import PetShop
from .general_shop import shop, discount_shop

__all__ = ['WeaponShop', 'MagicShop', 'PetShop', 'shop', 'discount_shop']