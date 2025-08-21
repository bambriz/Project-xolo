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
        
        if distance > self.melee_range:
            return False
        
        # Calculate angle to target
        target_angle = math.atan2(dy, dx)
        angle_diff = abs(target_angle - attack_angle)
        
        # Normalize angle difference to [0, pi]
        angle_diff = min(angle_diff, 2 * math.pi - angle_diff)
        
        return angle_diff <= self.melee_arc / 2
    
    def create_melee_animation(self, attack_angle: float):
        """Create a visual effect for melee attack."""
        animation = {
            'type': 'melee_sweep',
            'angle': attack_angle,
            'lifetime': 0.2,  # 200ms animation
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
    
    def render_projectiles(self, screen: pygame.Surface, camera_x: int, camera_y: int, asset_manager):
        """Render all projectiles."""
        for projectile in self.projectiles:
            projectile.render(screen, camera_x, camera_y)
    
    def render_melee_attacks(self, screen: pygame.Surface, camera_x: int, camera_y: int):
        """Render melee attack animations."""
        for animation in self.attack_animations:
            if animation['type'] == 'melee_sweep':
                self.render_melee_sweep(screen, camera_x, camera_y, animation)
    
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
        
        # Create arc points
        arc_points = []
        arc_steps = 10
        for i in range(arc_steps + 1):
            angle = start_angle + (end_angle - start_angle) * i / arc_steps
            x = screen_x + math.cos(angle) * arc_radius * progress
            y = screen_y + math.sin(angle) * arc_radius * progress
            arc_points.append((x, y))
        
        # Draw the arc
        if len(arc_points) > 1:
            alpha = int(255 * (1.0 - progress))
            color = (255, 255, 255, alpha)
            for i in range(len(arc_points) - 1):
                pygame.draw.line(screen, color[:3], arc_points[i], arc_points[i + 1], 3)

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
