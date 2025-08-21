"""
Combat system handling melee and ranged attacks, projectiles, and damage calculations.
"""

import pygame
import math
import random
from typing import Tuple, List, Optional

class Projectile:
    """A projectile fired by the player or enemies."""
    
    def __init__(self, start_pos: Tuple[float, float], target_pos: Tuple[float, float], 
                 damage: int, speed: float = 400.0, lifetime: float = 3.0):
        """Initialize a projectile."""
        self.position = list(start_pos)
        self.damage = damage
        self.speed = speed
        self.lifetime = lifetime
        self.age = 0.0
        self.radius = 3
        
        # Calculate direction
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.velocity = [dx / distance * speed, dy / distance * speed]
        else:
            self.velocity = [0, 0]
        
        # Visual properties
        self.color = (255, 255, 100)  # Yellow
        self.trail = []
        self.max_trail_length = 5
    
    def update(self, dt: float) -> bool:
        """Update projectile position and return False if it should be removed."""
        # Update position
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        
        # Update trail
        self.trail.append(tuple(self.position))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        
        # Update age
        self.age += dt
        
        # Remove if lifetime exceeded
        return self.age < self.lifetime
    
    def check_collision(self, target_pos: Tuple[float, float], target_radius: float) -> bool:
        """Check if projectile collides with a circular target."""
        dx = self.position[0] - target_pos[0]
        dy = self.position[1] - target_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        return distance <= (self.radius + target_radius)
    
    def render(self, screen: pygame.Surface, camera_x: int, camera_y: int):
        """Render the projectile and its trail."""
        # Draw trail
        for i, trail_pos in enumerate(self.trail):
            alpha = int(255 * (i + 1) / len(self.trail) * 0.5)
            trail_color = (*self.color[:3], alpha)
            screen_x = int(trail_pos[0] + camera_x)
            screen_y = int(trail_pos[1] + camera_y)
            pygame.draw.circle(screen, trail_color, (screen_x, screen_y), max(1, self.radius - 1))
        
        # Draw projectile
        screen_x = int(self.position[0] + camera_x)
        screen_y = int(self.position[1] + camera_y)
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), self.radius, 1)

class CombatSystem:
    """Handles all combat-related functionality for a character."""
    
    def __init__(self, owner):
        """Initialize combat system for the given owner (player or enemy)."""
        self.owner = owner
        
        # Attack cooldowns
        self.melee_cooldown = 0.5  # seconds
        self.ranged_cooldown = 1.0  # seconds
        self.last_melee_attack = 0
        self.last_ranged_attack = 0
        
        # Melee attack properties
        self.melee_range = 40
        self.melee_arc = math.pi / 3  # 60 degrees
        
        # Ranged attack properties
        self.projectile_speed = 400
        self.projectiles: List[Projectile] = []
        
        # Visual effects
        self.attack_animations = []
    
    def update(self, dt: float):
        """Update combat system (cooldowns, animations, etc.)."""
        # Update attack animations
        for animation in self.attack_animations[:]:
            animation['lifetime'] -= dt
            if animation['lifetime'] <= 0:
                self.attack_animations.remove(animation)
    
    def attempt_melee_attack(self, target_pos: Tuple[float, float], level) -> bool:
        """Attempt to perform a melee attack."""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Check cooldown
        if current_time - self.last_melee_attack < self.melee_cooldown:
            return False
        
        # Calculate attack direction
        dx = target_pos[0] - self.owner.position[0]
        dy = target_pos[1] - self.owner.position[1]
        attack_distance = math.sqrt(dx**2 + dy**2)
        
        if attack_distance > self.melee_range:
            return False  # Target too far
        
        # Perform attack
        self.last_melee_attack = current_time
        attack_angle = math.atan2(dy, dx)
        
        # Create attack animation
        self.create_melee_animation(attack_angle)
        
        # Check for enemy hits
        damage_dealt = False
        for enemy in level.enemies:
            if enemy.is_alive() and self.is_in_melee_range(enemy, attack_angle):
                if enemy.take_damage(self.owner.damage):
                    # Enemy died
                    pass
                damage_dealt = True
                print(f"Melee hit! Dealt {self.owner.damage} damage to {enemy.enemy_type}")
        
        # Check for boss hits
        if level.boss and level.boss.is_alive() and self.is_in_melee_range(level.boss, attack_angle):
            if level.boss.take_damage(self.owner.damage):
                # Boss died
                pass
            damage_dealt = True
            print(f"Melee hit! Dealt {self.owner.damage} damage to {level.boss.boss_type} boss")
        
        return damage_dealt
    
    def attempt_ranged_attack(self, target_pos: Tuple[float, float]) -> bool:
        """Attempt to fire a ranged projectile."""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Check cooldown
        if current_time - self.last_ranged_attack < self.ranged_cooldown:
            return False
        
        # Create projectile
        self.last_ranged_attack = current_time
        projectile = Projectile(
            self.owner.position, 
            target_pos, 
            self.owner.damage // 2,  # Ranged attacks do less damage
            self.projectile_speed
        )
        self.projectiles.append(projectile)
        
        print(f"Fired projectile towards {target_pos}")
        return True
    
    def is_in_melee_range(self, target, attack_angle: float) -> bool:
        """Check if target is within melee attack range and arc."""
        # Calculate distance to target
        dx = target.position[0] - self.owner.position[0]
        dy = target.position[1] - self.owner.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        # Get weapon range (use weapon range multiplier if available)
        weapon_range = self.melee_range
        if hasattr(self.owner, 'inventory') and self.owner.inventory.melee_weapon:
            weapon_range = self.melee_range * self.owner.inventory.melee_weapon.range_multiplier
        
        if distance > weapon_range:
            return False
        
        # Calculate angle to target
        target_angle = math.atan2(dy, dx)
        angle_diff = abs(target_angle - attack_angle)
        
        # Normalize angle difference to [0, pi]
        angle_diff = min(angle_diff, 2 * math.pi - angle_diff)
        
        return angle_diff <= self.melee_arc / 2
    
    def create_melee_animation(self, attack_angle: float):
        """Create a visual effect for melee attack based on weapon type."""
        # Get weapon-specific animation data
        weapon = self.owner.inventory.melee_weapon if hasattr(self.owner, 'inventory') and self.owner.inventory.melee_weapon else None
        
        if weapon:
            if weapon.shape == "spear":
                animation = {
                    'type': 'spear_poke',
                    'angle': attack_angle,
                    'lifetime': 0.15,  # Quick poke animation
                    'max_lifetime': 0.15,
                    'range': self.melee_range * weapon.range_multiplier,
                    'weapon': weapon
                }
            elif weapon.shape in ["sword", "mace"]:
                animation = {
                    'type': 'weapon_swing',
                    'angle': attack_angle,
                    'lifetime': 0.25,  # Swing animation
                    'max_lifetime': 0.25,
                    'arc': math.radians(weapon.attack_arc),
                    'range': self.melee_range * weapon.range_multiplier,
                    'weapon': weapon
                }
            else:
                animation = {
                    'type': 'melee_sweep',
                    'angle': attack_angle,
                    'lifetime': 0.2,
                    'max_lifetime': 0.2
                }
        else:
            # Default fist attack
            animation = {
                'type': 'melee_sweep',
                'angle': attack_angle,
                'lifetime': 0.2,
                'max_lifetime': 0.2
            }
        
        self.attack_animations.append(animation)
    
    def update_projectiles(self, dt: float, level):
        """Update all projectiles and handle collisions."""
        for projectile in self.projectiles[:]:
            # Update projectile
            if not projectile.update(dt):
                self.projectiles.remove(projectile)
                continue
            
            # Check wall collisions
            if level.check_wall_collision(projectile.position, projectile.radius):
                self.projectiles.remove(projectile)
                continue
            
            # Check enemy collisions
            hit_enemy = False
            for enemy in level.enemies:
                if enemy.is_alive() and projectile.check_collision(enemy.position, enemy.radius):
                    if enemy.take_damage(projectile.damage):
                        # Enemy died
                        pass
                    self.projectiles.remove(projectile)
                    hit_enemy = True
                    print(f"Projectile hit! Dealt {projectile.damage} damage to {enemy.enemy_type}")
                    break
            
            if hit_enemy:
                continue
            
            # Check boss collisions
            if level.boss and level.boss.is_alive() and projectile.check_collision(level.boss.position, level.boss.radius):
                if level.boss.take_damage(projectile.damage):
                    # Boss died
                    pass
                self.projectiles.remove(projectile)
                print(f"Projectile hit! Dealt {projectile.damage} damage to {level.boss.boss_type} boss")
                continue
    
    def render_projectiles(self, screen: pygame.Surface, camera_x: int, camera_y: int, asset_manager):
        """Render all projectiles."""
        for projectile in self.projectiles:
            projectile.render(screen, camera_x, camera_y)
    
    def render_melee_attacks(self, screen: pygame.Surface, camera_x: int, camera_y: int):
        """Render melee attack animations."""
        for animation in self.attack_animations:
            if animation['type'] == 'melee_sweep':
                self.render_melee_sweep(screen, camera_x, camera_y, animation)
            elif animation['type'] == 'spear_poke':
                self.render_spear_poke(screen, camera_x, camera_y, animation)
            elif animation['type'] == 'weapon_swing':
                self.render_weapon_swing(screen, camera_x, camera_y, animation)
    
    def render_melee_sweep(self, screen: pygame.Surface, camera_x: int, camera_y: int, animation):
        """Render a melee sweep animation."""
        # Calculate screen position
        screen_x = int(self.owner.position[0] + camera_x)
        screen_y = int(self.owner.position[1] + camera_y)
        
        # Calculate animation progress (0 to 1)
        progress = 1.0 - (animation['lifetime'] / animation['max_lifetime'])
        
        # Draw attack arc
        arc_radius = self.melee_range
        start_angle = animation['angle'] - self.melee_arc / 2
        end_angle = animation['angle'] + self.melee_arc / 2
        
        # Draw sweep arc with fading effect
        alpha = int(255 * (1.0 - progress))
        sweep_color = (255, 255, 255, alpha)
        
        # Draw multiple arc lines to show sweep
        for i in range(5):
            current_angle = start_angle + (end_angle - start_angle) * progress * (i / 4.0)
            end_x = screen_x + math.cos(current_angle) * arc_radius
            end_y = screen_y + math.sin(current_angle) * arc_radius
            pygame.draw.line(screen, (255, 255, 255), (screen_x, screen_y), (end_x, end_y), 2)
    
    def render_spear_poke(self, screen: pygame.Surface, camera_x: int, camera_y: int, animation):
        """Render a spear poke animation."""
        screen_x = int(self.owner.position[0] + camera_x)
        screen_y = int(self.owner.position[1] + camera_y)
        
        progress = 1.0 - (animation['lifetime'] / animation['max_lifetime'])
        
        # Spear extends and retracts
        poke_distance = animation['range'] * (0.5 + 0.5 * math.sin(progress * math.pi))
        
        end_x = screen_x + math.cos(animation['angle']) * poke_distance
        end_y = screen_y + math.sin(animation['angle']) * poke_distance
        
        # Draw spear shaft (thicker line)
        pygame.draw.line(screen, (160, 82, 45), (screen_x, screen_y), (end_x, end_y), 4)
        
        # Draw spear tip (small triangle)
        tip_size = 8
        tip_angle = animation['angle']
        tip_points = [
            (end_x + math.cos(tip_angle) * tip_size, end_y + math.sin(tip_angle) * tip_size),
            (end_x + math.cos(tip_angle + 2.5) * (tip_size // 2), end_y + math.sin(tip_angle + 2.5) * (tip_size // 2)),
            (end_x + math.cos(tip_angle - 2.5) * (tip_size // 2), end_y + math.sin(tip_angle - 2.5) * (tip_size // 2))
        ]
        pygame.draw.polygon(screen, (180, 180, 180), tip_points)
    
    def render_weapon_swing(self, screen: pygame.Surface, camera_x: int, camera_y: int, animation):
        """Render a weapon swing animation."""
        screen_x = int(self.owner.position[0] + camera_x)
        screen_y = int(self.owner.position[1] + camera_y)
        
        progress = 1.0 - (animation['lifetime'] / animation['max_lifetime'])
        weapon = animation['weapon']
        
        # Swing from right to left across the arc
        arc_width = animation['arc']
        swing_angle = animation['angle'] + (arc_width / 2) - (arc_width * progress)
        
        # Draw weapon shape
        weapon_length = animation['range']
        end_x = screen_x + math.cos(swing_angle) * weapon_length
        end_y = screen_y + math.sin(swing_angle) * weapon_length
        
        if weapon.shape == "sword":
            # Draw sword blade (line with slight width)
            pygame.draw.line(screen, weapon.color, (screen_x, screen_y), (end_x, end_y), 4)
            # Draw hilt (crossguard)
            hilt_x = screen_x + math.cos(swing_angle) * 15
            hilt_y = screen_y + math.sin(swing_angle) * 15
            hilt_perp_x = hilt_x + math.cos(swing_angle + math.pi/2) * 8
            hilt_perp_y = hilt_y + math.sin(swing_angle + math.pi/2) * 8
            hilt_perp_x2 = hilt_x + math.cos(swing_angle - math.pi/2) * 8
            hilt_perp_y2 = hilt_y + math.sin(swing_angle - math.pi/2) * 8
            pygame.draw.line(screen, (100, 100, 100), (hilt_perp_x, hilt_perp_y), (hilt_perp_x2, hilt_perp_y2), 3)
            
        elif weapon.shape == "mace":
            # Draw mace handle
            handle_end = weapon_length * 0.7
            handle_x = screen_x + math.cos(swing_angle) * handle_end
            handle_y = screen_y + math.sin(swing_angle) * handle_end
            pygame.draw.line(screen, (139, 69, 19), (screen_x, screen_y), (handle_x, handle_y), 3)
            
            # Draw mace head (circle)
            pygame.draw.circle(screen, weapon.color, (int(end_x), int(end_y)), 8)
            pygame.draw.circle(screen, (50, 50, 50), (int(end_x), int(end_y)), 8, 2)

def calculate_damage(base_damage: int, level: int, damage_type: str = "normal") -> int:
    """Calculate final damage based on various factors."""
    damage = base_damage
    
    # Add some randomness (±10%)
    variance = 0.1
    multiplier = 1.0 + random.uniform(-variance, variance)
    damage = int(damage * multiplier)
    
    # Critical hit chance (5% chance for double damage)
    if random.random() < 0.05:
        damage *= 2
        print("Critical hit!")
    
    return max(1, damage)  # Minimum 1 damage
