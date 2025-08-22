"""
Boss-specific weapons and spells not available to players.
Adds unique challenge and variety to boss encounters.
"""

import pygame
import math
import random
from typing import Tuple, List

class BossWeapon:
    """Base class for boss-specific weapons."""
    
    def __init__(self, name: str, damage_multiplier: float, range_multiplier: float, cooldown: float):
        self.name = name
        self.damage_multiplier = damage_multiplier
        self.range_multiplier = range_multiplier
        self.cooldown = cooldown
        self.last_used = 0.0
        
    def is_ready(self, current_time: float) -> bool:
        """Check if weapon is off cooldown."""
        return current_time - self.last_used >= self.cooldown
    
    def use(self, current_time: float):
        """Use the weapon, setting cooldown."""
        self.last_used = current_time

class FlameWhip(BossWeapon):
    """Boss-only weapon: Creates a line of fire in front of boss."""
    
    def __init__(self):
        super().__init__("Flame Whip", 2.5, 2.0, 3.0)
        self.color = (255, 100, 50)  # Orange-red
        
    def create_attack_animation(self, boss_pos: Tuple[float, float], target_pos: Tuple[float, float]):
        """Create flame whip animation."""
        dx = target_pos[0] - boss_pos[0]
        dy = target_pos[1] - boss_pos[1]
        angle = math.atan2(dy, dx)
        
        return {
            'type': 'flame_whip',
            'start_pos': boss_pos,
            'angle': angle,
            'range': 120,  # Long range
            'width': 20,   # Wide attack
            'color': self.color,
            'lifetime': 1.0,
            'max_lifetime': 1.0
        }

class ShadowStrike(BossWeapon):
    """Boss-only weapon: Teleports behind player and strikes."""
    
    def __init__(self):
        super().__init__("Shadow Strike", 3.0, 1.5, 5.0)
        self.color = (100, 50, 150)  # Dark purple
        
    def create_attack_animation(self, boss_pos: Tuple[float, float], target_pos: Tuple[float, float]):
        """Create shadow strike animation."""
        # Calculate position behind player
        dx = target_pos[0] - boss_pos[0]
        dy = target_pos[1] - boss_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Position behind player
            strike_x = target_pos[0] - (dx / distance) * 40
            strike_y = target_pos[1] - (dy / distance) * 40
        else:
            strike_x, strike_y = boss_pos
        
        return {
            'type': 'shadow_strike',
            'strike_pos': (strike_x, strike_y),
            'target_pos': target_pos,
            'color': self.color,
            'lifetime': 0.5,
            'max_lifetime': 0.5
        }

class BossSpell:
    """Base class for boss-specific spells."""
    
    def __init__(self, name: str, cooldown: float):
        self.name = name
        self.cooldown = cooldown
        self.last_used = 0.0
        
    def is_ready(self, current_time: float) -> bool:
        """Check if spell is off cooldown."""
        return current_time - self.last_used >= self.cooldown
    
    def use(self, current_time: float):
        """Use the spell, setting cooldown."""
        self.last_used = current_time

class SummonMinions(BossSpell):
    """Boss-only spell: Summons 2-3 weak minions."""
    
    def __init__(self):
        super().__init__("Summon Minions", 15.0)
        self.minion_count = random.randint(2, 3)
        
    def create_minions(self, boss_pos: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Create minion spawn positions around boss."""
        positions = []
        for i in range(self.minion_count):
            angle = (2 * math.pi * i) / self.minion_count
            x = boss_pos[0] + math.cos(angle) * 80
            y = boss_pos[1] + math.sin(angle) * 80
            positions.append((x, y))
        return positions

class VoidBlast(BossSpell):
    """Boss-only spell: Creates expanding void that damages player."""
    
    def __init__(self):
        super().__init__("Void Blast", 8.0)
        self.color = (150, 50, 200)  # Purple
        
    def create_blast_animation(self, boss_pos: Tuple[float, float]):
        """Create void blast animation."""
        return {
            'type': 'void_blast',
            'center': boss_pos,
            'radius': 0,
            'max_radius': 150,
            'expansion_speed': 200,
            'color': self.color,
            'lifetime': 2.0,
            'max_lifetime': 2.0
        }

class BossWeaponManager:
    """Manages boss-specific weapons and spells."""
    
    def __init__(self):
        self.weapons = {
            'flame_whip': FlameWhip(),
            'shadow_strike': ShadowStrike()
        }
        
        self.spells = {
            'summon_minions': SummonMinions(),
            'void_blast': VoidBlast()
        }
    
    def get_random_weapon(self) -> BossWeapon:
        """Get a random boss weapon."""
        return random.choice(list(self.weapons.values()))
    
    def get_random_spell(self) -> BossSpell:
        """Get a random boss spell."""
        return random.choice(list(self.spells.values()))
    
    def render_boss_attack(self, screen: pygame.Surface, camera_x: int, camera_y: int, animation):
        """Render boss-specific attack animations."""
        if animation['type'] == 'flame_whip':
            # Draw flame whip as expanding line of fire
            start_x = int(animation['start_pos'][0] + camera_x)
            start_y = int(animation['start_pos'][1] + camera_y)
            
            progress = 1.0 - (animation['lifetime'] / animation['max_lifetime'])
            current_range = animation['range'] * progress
            
            end_x = start_x + math.cos(animation['angle']) * current_range
            end_y = start_y + math.sin(animation['angle']) * current_range
            
            # Draw main flame line
            pygame.draw.line(screen, animation['color'], (start_x, start_y), (end_x, end_y), 8)
            # Draw outer glow
            pygame.draw.line(screen, (255, 200, 100), (start_x, start_y), (end_x, end_y), 12)
            
        elif animation['type'] == 'shadow_strike':
            # Draw shadow trail and strike effect
            strike_x = int(animation['strike_pos'][0] + camera_x)
            strike_y = int(animation['strike_pos'][1] + camera_y)
            target_x = int(animation['target_pos'][0] + camera_x)
            target_y = int(animation['target_pos'][1] + camera_y)
            
            # Draw shadow trail
            pygame.draw.line(screen, animation['color'], (strike_x, strike_y), (target_x, target_y), 6)
            # Draw strike circle
            pygame.draw.circle(screen, animation['color'], (target_x, target_y), 15, 3)
            
        elif animation['type'] == 'void_blast':
            # Draw expanding void circle
            center_x = int(animation['center'][0] + camera_x)
            center_y = int(animation['center'][1] + camera_y)
            
            progress = 1.0 - (animation['lifetime'] / animation['max_lifetime'])
            current_radius = int(animation['max_radius'] * progress)
            
            if current_radius > 0:
                pygame.draw.circle(screen, animation['color'], (center_x, center_y), current_radius, 4)
                # Inner effect
                inner_radius = max(1, current_radius - 10)
                pygame.draw.circle(screen, (200, 100, 250), (center_x, center_y), inner_radius, 2)