"""
Player class and related functionality.
Handles player movement, stats, leveling, and input processing.
"""

import pygame
import math
from typing import Tuple, List
from combat import CombatSystem

class Player:
    """Player character with movement, stats, and combat capabilities."""
    
    def __init__(self, spawn_position: Tuple[float, float]):
        """Initialize the player at the given spawn position."""
        # Position and movement
        self.position = list(spawn_position)
        self.velocity = [0.0, 0.0]
        self.speed = 200.0  # pixels per second
        self.radius = 15
        
        # Base stats
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        
        # Health system
        self.max_health = 100
        self.current_health = self.max_health
        self.health_regen_rate = 2.0  # HP per second
        self.last_damage_time = 0
        self.damage_immunity_duration = 0.5  # seconds
        
        # Combat stats
        self.base_damage = 25
        self.attack_speed_multiplier = 1.0
        
        # Initialize combat system
        self.combat_system = CombatSystem(self)
        
        # Visual properties
        self.color = (100, 150, 255)  # Light blue
        self.outline_color = (255, 255, 255)
        
        print(f"Player created with {self.current_health}/{self.max_health} HP")
    
    @property
    def damage(self) -> int:
        """Calculate current damage based on level and base damage."""
        return int(self.base_damage * (1 + (self.level - 1) * 0.2))
    
    def update(self, dt: float, keys, mouse_pos: Tuple[int, int], 
               mouse_buttons: Tuple[bool, bool, bool], level):
        """Update player state, movement, and combat."""
        # Handle movement input
        self.handle_movement(dt, keys, level)
        
        # Handle combat input
        self.handle_combat_input(dt, mouse_pos, mouse_buttons, level)
        
        # Update combat system
        self.combat_system.update(dt)
        
        # Health regeneration (only if not recently damaged)
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.last_damage_time > 3.0:  # 3 seconds without damage
            self.heal(self.health_regen_rate * dt)
    
    def handle_movement(self, dt: float, keys, level):
        """Handle player movement based on input."""
        # Reset velocity
        self.velocity = [0.0, 0.0]
        
        # Check movement keys
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity[1] -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity[1] += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity[0] -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity[0] += self.speed
        
        # Normalize diagonal movement
        vel_magnitude = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        if vel_magnitude > self.speed:
            self.velocity[0] = (self.velocity[0] / vel_magnitude) * self.speed
            self.velocity[1] = (self.velocity[1] / vel_magnitude) * self.speed
        
        # Apply movement with collision detection
        self.move_with_collision(dt, level)
    
    def move_with_collision(self, dt: float, level):
        """Move the player while checking for wall collisions."""
        # Try to move horizontally first
        new_x = self.position[0] + self.velocity[0] * dt
        if not level.check_wall_collision((new_x, self.position[1]), self.radius):
            self.position[0] = new_x
        
        # Then try to move vertically
        new_y = self.position[1] + self.velocity[1] * dt
        if not level.check_wall_collision((self.position[0], new_y), self.radius):
            self.position[1] = new_y
    
    def handle_combat_input(self, dt: float, mouse_pos: Tuple[int, int], 
                           mouse_buttons: Tuple[bool, bool, bool], level):
        """Handle combat input (mouse clicks for attacks)."""
        # Calculate world mouse position (accounting for camera)
        screen_center_x = 512  # SCREEN_WIDTH // 2
        screen_center_y = 384  # SCREEN_HEIGHT // 2
        world_mouse_x = mouse_pos[0] - screen_center_x + self.position[0]
        world_mouse_y = mouse_pos[1] - screen_center_y + self.position[1]
        
        # Left click for melee attack
        if mouse_buttons[0]:  # Left mouse button
            target_pos = (world_mouse_x, world_mouse_y)
            self.combat_system.attempt_melee_attack(target_pos, level)
        
        # Right click for ranged attack
        if mouse_buttons[2]:  # Right mouse button
            target_pos = (world_mouse_x, world_mouse_y)
            self.combat_system.attempt_ranged_attack(target_pos)
    
    def take_damage(self, amount: int) -> bool:
        """Take damage and return True if player dies."""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Check damage immunity
        if current_time - self.last_damage_time < self.damage_immunity_duration:
            return False
        
        self.current_health = max(0, self.current_health - amount)
        self.last_damage_time = current_time
        
        print(f"Player took {amount} damage! Health: {self.current_health}/{self.max_health}")
        
        if self.current_health <= 0:
            print("Player died!")
            return True
        
        return False
    
    def heal(self, amount: float):
        """Heal the player by the given amount."""
        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        
        # Only log if actual healing occurred
        if self.current_health > old_health:
            pass  # Uncomment for healing debug: print(f"Player healed for {self.current_health - old_health:.1f}")
    
    def gain_xp(self, amount: int):
        """Gain XP and handle leveling up."""
        self.xp += amount
        
        # Check for level up
        while self.xp >= self.xp_to_next_level:
            self.level_up()
    
    def level_up(self):
        """Handle leveling up - increase stats."""
        self.xp -= self.xp_to_next_level
        self.level += 1
        
        # Increase stats
        old_max_health = self.max_health
        self.max_health += 20  # +20 HP per level
        health_gained = self.max_health - old_max_health
        self.current_health += health_gained  # Gain the health bonus immediately
        
        self.base_damage += 5  # +5 damage per level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)  # XP requirement increases
        
        print(f"LEVEL UP! Now level {self.level}")
        print(f"Health: {self.current_health}/{self.max_health} (+{health_gained})")
        print(f"Damage: {self.damage}")
        print(f"Next level: {self.xp}/{self.xp_to_next_level} XP")
    
    def get_health_percentage(self) -> float:
        """Get health as a percentage (0.0 to 1.0)."""
        return self.current_health / self.max_health if self.max_health > 0 else 0.0
    
    def get_xp_percentage(self) -> float:
        """Get XP progress to next level as a percentage (0.0 to 1.0)."""
        return self.xp / self.xp_to_next_level if self.xp_to_next_level > 0 else 0.0
    
    def render(self, screen: pygame.Surface, camera_x: int, camera_y: int, asset_manager):
        """Render the player on screen."""
        # Calculate screen position
        screen_x = int(self.position[0] + camera_x)
        screen_y = int(self.position[1] + camera_y)
        
        # Draw player as a circle with outline
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.radius)
        pygame.draw.circle(screen, self.outline_color, (screen_x, screen_y), self.radius, 2)
        
        # Draw a small directional indicator
        if self.velocity[0] != 0 or self.velocity[1] != 0:
            # Calculate direction
            direction = math.atan2(self.velocity[1], self.velocity[0])
            end_x = screen_x + math.cos(direction) * (self.radius - 3)
            end_y = screen_y + math.sin(direction) * (self.radius - 3)
            pygame.draw.line(screen, (255, 255, 255), (screen_x, screen_y), (end_x, end_y), 2)
        
        # Draw health bar above player if damaged
        if self.current_health < self.max_health:
            self.draw_health_bar(screen, screen_x, screen_y - self.radius - 10)
    
    def draw_health_bar(self, screen: pygame.Surface, x: int, y: int):
        """Draw a health bar above the player."""
        bar_width = 30
        bar_height = 4
        health_percentage = self.get_health_percentage()
        
        # Background (red)
        pygame.draw.rect(screen, (200, 50, 50), 
                        (x - bar_width // 2, y, bar_width, bar_height))
        
        # Health (green)
        health_width = int(bar_width * health_percentage)
        if health_width > 0:
            pygame.draw.rect(screen, (50, 200, 50), 
                            (x - bar_width // 2, y, health_width, bar_height))
