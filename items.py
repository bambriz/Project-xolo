"""
Item system for the dungeon crawler game.
Manages three categories: melee weapons, enchantments, and spells.
"""

import pygame
import math
import random
from typing import Dict, List, Tuple, Optional
from enum import Enum

class ItemType(Enum):
    """Types of items available."""
    MELEE_WEAPON = "melee_weapon"
    ENCHANTMENT = "enchantment"  
    SPELL = "spell"

class MeleeWeaponType(Enum):
    """Types of melee weapons."""
    SWORD = "sword"
    SPEAR = "spear"
    MACE = "mace"

class EnchantmentType(Enum):
    """Types of enchantments."""
    RED = "red"      # Increases max HP to 125%
    YELLOW = "yellow"  # Reduces enemy max HP by 15%
    GREEN = "green"    # Slows enemy speed by 25%
    BLACK = "black"    # Reduces damage taken by 10%

class SpellType(Enum):
    """Types of spells that replace right-click behavior."""
    HASTE = "haste"          # Increases player speed by 25% while holding right click
    POWER_PULSE = "power_pulse"  # Long cooldown, high damage in circle around player
    TURN_COAT = "turn_coat"      # Medium cooldown, makes enemy attack other enemies

class Item:
    """Base class for all items."""
    
    def __init__(self, item_type: ItemType, name: str, description: str, color: Tuple[int, int, int]):
        self.item_type = item_type
        self.name = name
        self.description = description
        self.color = color
        self.position = (0.0, 0.0)
        self.size = 24  # Item pickup size
        
    def get_sprite_data(self) -> Dict:
        """Get data for sprite generation."""
        return {
            "color": self.color,
            "size": self.size,
            "shape": "square"  # Default shape
        }

class MeleeWeapon(Item):
    """Melee weapon items."""
    
    def __init__(self, weapon_type: MeleeWeaponType):
        self.weapon_type = weapon_type
        
        # Weapon stats
        weapon_data = {
            MeleeWeaponType.SWORD: {
                "name": "Sword",
                "description": "Mid range, 90° arc, high damage",
                "color": (200, 200, 255),  # Light blue
                "damage_multiplier": 1.5,
                "range_multiplier": 1.0,
                "attack_arc": 90,
                "attack_speed": 1.0,
                "shape": "sword"
            },
            MeleeWeaponType.SPEAR: {
                "name": "Spear", 
                "description": "2.5x range, straight line, fast attacks",
                "color": (160, 82, 45),  # Brown
                "damage_multiplier": 0.8,
                "range_multiplier": 2.5,  # 2.5 times player length as requested
                "attack_arc": 15,  # Very narrow
                "attack_speed": 1.5,
                "shape": "spear"
            },
            MeleeWeaponType.MACE: {
                "name": "Mace",
                "description": "Short range, knockback, mid damage",
                "color": (128, 128, 128),  # Gray
                "damage_multiplier": 1.2,
                "range_multiplier": 0.8,
                "attack_arc": 110,
                "attack_speed": 0.9,
                "knockback": True,
                "shape": "mace"
            }
        }
        
        data = weapon_data[weapon_type]
        super().__init__(ItemType.MELEE_WEAPON, data["name"], data["description"], data["color"])
        
        self.damage_multiplier = data["damage_multiplier"]
        self.range_multiplier = data["range_multiplier"]
        self.attack_arc = data["attack_arc"]
        self.attack_speed = data["attack_speed"]
        self.knockback = data.get("knockback", False)
        self.shape = data["shape"]
    
    def get_sprite_data(self) -> Dict:
        """Get data for weapon sprite generation."""
        return {
            "color": self.color,
            "size": self.size,
            "shape": self.shape
        }

class Enchantment(Item):
    """Enchantment items that provide passive effects."""
    
    def __init__(self, enchantment_type: EnchantmentType):
        self.enchantment_type = enchantment_type
        
        # Enchantment stats
        enchant_data = {
            EnchantmentType.RED: {
                "name": "Red Enchantment",
                "description": "Max HP increased to 125%",
                "color": (255, 100, 100),  # Red
                "effect": "hp_boost"
            },
            EnchantmentType.YELLOW: {
                "name": "Yellow Enchantment", 
                "description": "Enemy max HP reduced by 15%",
                "color": (255, 255, 100),  # Yellow
                "effect": "enemy_hp_reduction"
            },
            EnchantmentType.GREEN: {
                "name": "Green Enchantment",
                "description": "Enemy speed reduced by 25%",
                "color": (100, 255, 100),  # Green
                "effect": "enemy_slow"
            },
            EnchantmentType.BLACK: {
                "name": "Black Enchantment",
                "description": "Damage taken reduced by 10%",
                "color": (150, 150, 150),  # Dark gray
                "effect": "damage_reduction"
            }
        }
        
        data = enchant_data[enchantment_type]
        super().__init__(ItemType.ENCHANTMENT, data["name"], data["description"], data["color"])
        self.effect = data["effect"]
        
    def get_sprite_data(self) -> Dict:
        """Get data for enchantment sprite generation."""
        return {
            "color": self.color,
            "size": self.size,
            "shape": "diamond"
        }

class Spell(Item):
    """Spell items that replace right-click behavior."""
    
    def __init__(self, spell_type: SpellType):
        self.spell_type = spell_type
        
        # Spell stats
        spell_data = {
            SpellType.HASTE: {
                "name": "Haste Spell",
                "description": "25% speed boost while holding right click",
                "color": (100, 255, 255),  # Cyan
                "cooldown": 0.0,
                "effect": "speed_boost"
            },
            SpellType.POWER_PULSE: {
                "name": "Power Pulse",
                "description": "High damage in circle around player",
                "color": (255, 100, 255),  # Magenta
                "cooldown": 8.0,  # Long cooldown
                "effect": "area_damage"
            },
            SpellType.TURN_COAT: {
                "name": "Turn Coat",
                "description": "Makes enemy attack other enemies for 10s",
                "color": (255, 165, 0),  # Orange
                "cooldown": 4.0,  # Medium cooldown
                "effect": "mind_control"
            }
        }
        
        data = spell_data[spell_type]
        super().__init__(ItemType.SPELL, data["name"], data["description"], data["color"])
        self.cooldown = data["cooldown"]
        self.effect = data["effect"]
        self.last_used = 0.0
        
    def get_sprite_data(self) -> Dict:
        """Get data for spell sprite generation."""
        return {
            "color": self.color,
            "size": self.size,
            "shape": "star"
        }
    
    def is_ready(self, current_time: float) -> bool:
        """Check if spell is off cooldown."""
        return current_time - self.last_used >= self.cooldown
    
    def use(self, current_time: float):
        """Use the spell, setting cooldown."""
        self.last_used = current_time

class ItemManager:
    """Manages item spawning, pickup, and inventory."""
    
    def __init__(self, level):
        self.level = level
        self.items_on_ground: List[Item] = []
        self.pickup_distance = 32  # Distance to pickup items
        
        # Generate random items on level
        self.spawn_random_items()
    
    def spawn_random_items(self):
        """Spawn random items throughout the level."""
        num_items = random.randint(3, 7)  # 3-7 items per level
        
        for _ in range(num_items):
            # Random item type
            item_type = random.choice(list(ItemType))
            item = self.create_random_item(item_type)
            
            # Find valid spawn position (not in walls)
            for attempt in range(100):
                x = random.randint(1, self.level.width - 2) * self.level.tile_size + self.level.tile_size // 2
                y = random.randint(1, self.level.height - 2) * self.level.tile_size + self.level.tile_size // 2
                
                # Check if position is not in wall
                tile_x = int(x // self.level.tile_size)
                tile_y = int(y // self.level.tile_size)
                
                if (0 <= tile_x < self.level.width and 
                    0 <= tile_y < self.level.height and
                    self.level.tiles[tile_y][tile_x].type == "floor"):
                    item.position = (x, y)
                    self.items_on_ground.append(item)
                    break
    
    def create_random_item(self, item_type: ItemType) -> Item:
        """Create a random item of the specified type."""
        if item_type == ItemType.MELEE_WEAPON:
            weapon_type = random.choice(list(MeleeWeaponType))
            return MeleeWeapon(weapon_type)
        elif item_type == ItemType.ENCHANTMENT:
            enchant_type = random.choice(list(EnchantmentType))
            return Enchantment(enchant_type)
        elif item_type == ItemType.SPELL:
            spell_type = random.choice(list(SpellType))
            return Spell(spell_type)
    
    def check_item_pickup(self, player_pos: Tuple[float, float]) -> Optional[Item]:
        """Check if player is near an item to pick up."""
        px, py = player_pos
        
        for item in self.items_on_ground[:]:  # Copy list to avoid modification during iteration
            ix, iy = item.position
            distance = math.sqrt((px - ix) ** 2 + (py - iy) ** 2)
            
            if distance <= self.pickup_distance:
                return item
        
        return None
    
    def pickup_item(self, item: Item) -> bool:
        """Remove item from ground."""
        if item in self.items_on_ground:
            self.items_on_ground.remove(item)
            return True
        return False
    
    def drop_item(self, item: Item, position: Tuple[float, float]):
        """Drop an item at the specified position."""
        item.position = position
        self.items_on_ground.append(item)
    
    def render_items(self, screen: pygame.Surface, camera_x: int, camera_y: int, asset_manager):
        """Render all items on the ground."""
        for item in self.items_on_ground:
            screen_x = int(item.position[0] + camera_x)
            screen_y = int(item.position[1] + camera_y)
            
            # Get item sprite from asset manager
            sprite_key = f"item_{item.name.lower().replace(' ', '_')}"
            sprite = asset_manager.get_sprite(sprite_key)
            
            if sprite:
                sprite_rect = sprite.get_rect(center=(screen_x, screen_y))
                screen.blit(sprite, sprite_rect)
            else:
                # Fallback: draw a colored rectangle
                rect = pygame.Rect(screen_x - item.size//2, screen_y - item.size//2, 
                                 item.size, item.size)
                pygame.draw.rect(screen, item.color, rect)
                pygame.draw.rect(screen, (255, 255, 255), rect, 2)

class PlayerInventory:
    """Manages the player's equipped items."""
    
    def __init__(self):
        # Player can hold one item per category
        self.melee_weapon: Optional[MeleeWeapon] = None
        self.enchantment: Optional[Enchantment] = None
        self.spell: Optional[Spell] = None
    
    def equip_item(self, item: Item) -> Optional[Item]:
        """Equip an item, returning the previously equipped item if any."""
        old_item = None
        
        if item.item_type == ItemType.MELEE_WEAPON and isinstance(item, MeleeWeapon):
            old_item = self.melee_weapon
            self.melee_weapon = item
        elif item.item_type == ItemType.ENCHANTMENT and isinstance(item, Enchantment):
            old_item = self.enchantment
            self.enchantment = item
        elif item.item_type == ItemType.SPELL and isinstance(item, Spell):
            old_item = self.spell
            self.spell = item
            
        return old_item
    
    def drop_spell(self) -> Optional[Spell]:
        """Drop the equipped spell."""
        spell = self.spell
        self.spell = None
        return spell
    
    def get_equipped_items(self) -> List[Item]:
        """Get all currently equipped items."""
        items = []
        if self.melee_weapon:
            items.append(self.melee_weapon)
        if self.enchantment:
            items.append(self.enchantment)
        if self.spell:
            items.append(self.spell)
        return items