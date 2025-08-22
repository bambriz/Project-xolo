"""
New enemy types with advanced abilities.
Includes ricochet spell user and enhanced boss capabilities.
"""

import pygame
import math
import random
from typing import Tuple, List, Optional
from enemy import Enemy

class RicochetEnemy(Enemy):
    """Enemy that uses ricochet spell for enhanced ranged attacks."""
    
    def __init__(self, position: Tuple[float, float], player_level: int = 1):
        """Initialize ricochet enemy."""
        super().__init__(position, "ricochet", player_level)
        
        # Ricochet spell properties
        self.ricochet_projectiles = []
        self.max_ricochets = 2  # Number of bounces
        self.ricochet_damage = self.damage
    
    def setup_stats(self, enemy_type: str, player_level: int):
        """Override to set ricochet enemy stats."""
        base_stats = {
            "ricochet": {"health": 45, "damage": 22, "xp": 50, "attack_speed": 2.2, "weapon": "ranged"}
        }
        
        stats = base_stats.get(enemy_type, base_stats["ricochet"])
        
        # Scale stats with player level
        level_multiplier = 1 + (player_level - 1) * 0.3
        
        self.max_health = int(stats["health"] * level_multiplier)
        self.current_health = self.max_health
        self.damage = int(stats["damage"] * level_multiplier)
        self.xp_value = int(stats["xp"] * level_multiplier)
        self.attack_cooldown = stats["attack_speed"]
        
        # Enhanced for ricochet ability
        self.speed *= 0.9  # Slightly slower
        self.sight_range *= 1.4  # Better vision
        self.attack_range = 120  # Longer range
    
    def setup_weapon(self, enemy_type: str):
        """Override to set ricochet weapon properties."""
        self.weapon_type = "ranged"
        self.weapon_range = 120
        self.weapon_arc = 25
        self.weapon_speed_multiplier = 1.0
        self.weapon_damage_multiplier = 1.2
        self.kite_behavior = True
    
    def setup_appearance(self):
        """Set ricochet enemy appearance."""
        self.color = (150, 100, 200)  # Purple for ricochet enemy
        self.outline_color = (255, 255, 255)
        
        # Mind control status
        self.mind_controlled = False
        self.mind_control_end_time = 0.0
        self.mind_control_target = None
        self.can_be_damaged_by_enemies = False
        
        # Visual indicators
        self.enchanted_color = (255, 165, 0)
    
    def attack_player(self, player):
        """Launch ricochet spell attack."""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Calculate direction to player
        dx = player.position[0] - self.position[0]
        dy = player.position[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance <= self.weapon_range:
            # Create ricochet projectile
            if distance > 0:
                direction = (dx / distance, dy / distance)
                projectile = RicochetProjectile(
                    (self.position[0], self.position[1]),
                    direction,
                    self.ricochet_damage,
                    self.max_ricochets
                )
                self.ricochet_projectiles.append(projectile)
                
                # Add visual feedback for attack
                print(f"Ricochet attack at angle {math.atan2(dy, dx)}")
                
                print(f"Ricochet enemy launched ricochet spell!")
    
    def update(self, dt: float, player, level, can_see_player: bool):
        """Update ricochet enemy with projectile management."""
        # Update base enemy behavior
        super().update(dt, player, level, can_see_player)
        
        # Update ricochet projectiles
        for projectile in self.ricochet_projectiles[:]:
            projectile.update(dt, level)
            
            # Check collision with player
            if projectile.check_collision_with_target(player, player.radius):
                if player.take_damage(projectile.damage):
                    print(f"Ricochet projectile hit player for {projectile.damage} damage!")
                self.ricochet_projectiles.remove(projectile)
            elif projectile.should_remove():
                self.ricochet_projectiles.remove(projectile)
    
    def render(self, screen: pygame.Surface, camera_x: int, camera_y: int, asset_manager):
        """Render ricochet enemy and projectiles."""
        # Render base enemy
        super().render(screen, camera_x, camera_y, asset_manager)
        
        # Render ricochet projectiles
        for projectile in self.ricochet_projectiles:
            projectile.render(screen, camera_x, camera_y)


class RicochetProjectile:
    """Projectile that bounces off walls."""
    
    def __init__(self, position: Tuple[float, float], direction: Tuple[float, float], 
                 damage: int, max_ricochets: int):
        """Initialize ricochet projectile."""
        self.position = list(position)
        self.direction = list(direction)
        self.damage = damage
        self.max_ricochets = max_ricochets
        self.ricochets_left = max_ricochets
        
        self.speed = 250
        self.radius = 4
        self.lifetime = 0.0
        self.max_lifetime = 5.0
        
        # Visual properties
        self.color = (200, 100, 255)  # Purple projectile
        self.trail_positions = []
        self.max_trail_length = 8
    
    def update(self, dt: float, level):
        """Update projectile position and handle ricochets."""
        self.lifetime += dt
        
        # Store trail position
        self.trail_positions.append((self.position[0], self.position[1]))
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)
        
        # Move projectile
        old_x, old_y = self.position[0], self.position[1]
        self.position[0] += self.direction[0] * self.speed * dt
        self.position[1] += self.direction[1] * self.speed * dt
        
        # Check wall collisions for ricochet
        if level.is_wall(int(self.position[0]), int(self.position[1])) and self.ricochets_left > 0:
            # Simple ricochet - reverse direction
            # For more realistic physics, we'd need to calculate the wall normal
            
            # Check which axis hit the wall
            if level.is_wall(int(old_x), int(self.position[1])):
                # Hit vertical wall, reverse horizontal direction
                self.direction[0] = -self.direction[0]
                self.position[0] = old_x  # Reset to previous position
            elif level.is_wall(int(self.position[0]), int(old_y)):
                # Hit horizontal wall, reverse vertical direction
                self.direction[1] = -self.direction[1]
                self.position[1] = old_y  # Reset to previous position
            else:
                # Corner hit, reverse both directions
                self.direction[0] = -self.direction[0]
                self.direction[1] = -self.direction[1]
                self.position[0] = old_x
                self.position[1] = old_y
            
            self.ricochets_left -= 1
            print(f"Ricochet! {self.ricochets_left} bounces left")
            
            # Reduce damage slightly with each ricochet
            self.damage = int(self.damage * 0.9)
    
    def check_collision_with_target(self, target, target_radius: float) -> bool:
        """Check if projectile hits target."""
        dx = target.position[0] - self.position[0]
        dy = target.position[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        return distance <= (self.radius + target_radius)
    
    def should_remove(self) -> bool:
        """Check if projectile should be removed."""
        return self.lifetime >= self.max_lifetime or self.ricochets_left < 0
    
    def render(self, screen: pygame.Surface, camera_x: int, camera_y: int):
        """Render ricochet projectile with trail."""
        # Render trail
        for i, (trail_x, trail_y) in enumerate(self.trail_positions):
            screen_x = int(trail_x + camera_x)
            screen_y = int(trail_y + camera_y)
            
            # Fade trail based on age
            alpha = int(255 * (i / len(self.trail_positions)) * 0.5)
            trail_color = (*self.color, alpha)
            
            # Create a surface for the trail point with alpha
            trail_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, trail_color, (2, 2), 2)
            screen.blit(trail_surface, (screen_x - 2, screen_y - 2))
        
        # Render main projectile
        screen_x = int(self.position[0] + camera_x)
        screen_y = int(self.position[1] + camera_y)
        
        # Main projectile
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), self.radius, 1)
        
        # Glowing effect
        glow_surface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.color, 50), (self.radius * 2, self.radius * 2), self.radius * 2)
        screen.blit(glow_surface, (screen_x - self.radius * 2, screen_y - self.radius * 2))