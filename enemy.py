"""
Enemy classes and AI behavior.
Handles different enemy types, AI states, and combat behavior.
"""

import pygame
import math
import random
from typing import Tuple, List, Optional

class Enemy:
    """Base enemy class with AI behavior and combat capabilities."""
    
    def __init__(self, position: Tuple[float, float], enemy_type: str = "basic", player_level: int = 1):
        """Initialize enemy with position and type."""
        self.position = list(position)
        self.enemy_type = enemy_type
        self.radius = 12
        
        # AI state
        self.state = "idle"  # idle, chasing, attacking, dead
        self.target_position = None
        self.last_seen_player_pos = None
        self.last_attack_time = 0
        self.sight_range = 150
        self.attack_range = 20
        self.give_up_time = 5.0  # seconds to chase last known position
        self.last_player_seen_time = 0
        
        # Movement (initialize speed first)
        self.speed = 80 + (player_level - 1) * 10  # Scales with player level
        self.velocity = [0.0, 0.0]
        
        # Set stats based on enemy type and player level
        self.setup_stats(enemy_type, player_level)
        
        # Pathfinding
        self.path_update_timer = 0
        self.path_update_interval = 0.5  # Update path every 0.5 seconds
        
        # Visual
        self.setup_appearance()
        
        print(f"Created {enemy_type} enemy (level {player_level}) with {self.current_health} HP")
    
    def setup_stats(self, enemy_type: str, player_level: int):
        """Set up enemy stats based on type and player level."""
        base_stats = {
            "basic": {"health": 50, "damage": 15, "xp": 25, "attack_speed": 1.5},
            "fast": {"health": 30, "damage": 12, "xp": 20, "attack_speed": 1.0},
            "heavy": {"health": 80, "damage": 25, "xp": 40, "attack_speed": 2.5},
            "ranged": {"health": 40, "damage": 20, "xp": 35, "attack_speed": 2.0}
        }
        
        stats = base_stats.get(enemy_type, base_stats["basic"])
        
        # Scale stats with player level
        level_multiplier = 1 + (player_level - 1) * 0.3
        
        self.max_health = int(stats["health"] * level_multiplier)
        self.current_health = self.max_health
        self.damage = int(stats["damage"] * level_multiplier)
        self.xp_value = int(stats["xp"] * level_multiplier)
        self.attack_cooldown = stats["attack_speed"]
        
        # Special abilities based on type
        if enemy_type == "fast":
            self.speed *= 1.5
            self.sight_range *= 1.2
        elif enemy_type == "heavy":
            self.radius = 16
            self.attack_range = 25
        elif enemy_type == "ranged":
            self.attack_range = 100
            self.sight_range *= 1.3
    
    def setup_appearance(self):
        """Set up visual appearance based on enemy type."""
        colors = {
            "basic": (200, 100, 100),    # Red
            "fast": (100, 200, 100),     # Green
            "heavy": (150, 150, 150),    # Gray
            "ranged": (200, 200, 100)    # Yellow
        }
        
        self.color = colors.get(self.enemy_type, colors["basic"])
        self.outline_color = (255, 255, 255)
    
    def update(self, dt: float, player, level, can_see_player: bool):
        """Update enemy AI and behavior."""
        if not self.is_alive():
            return
        
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Update AI state based on player visibility
        self.update_ai_state(player, can_see_player, current_time)
        
        # Execute behavior based on current state
        if self.state == "idle":
            self.idle_behavior(dt)
        elif self.state == "chasing":
            self.chase_behavior(dt, player, level, current_time)
        elif self.state == "attacking":
            self.attack_behavior(dt, player, current_time)
        
        # Apply movement
        self.apply_movement(dt, level)
    
    def update_ai_state(self, player, can_see_player: bool, current_time: float):
        """Update AI state based on player visibility and distance."""
        player_distance = self.distance_to_player(player)
        
        if can_see_player:
            self.last_seen_player_pos = player.position[:]
            self.last_player_seen_time = current_time
            
            if player_distance <= self.attack_range:
                self.state = "attacking"
            else:
                self.state = "chasing"
        
        elif self.state == "chasing" and self.last_seen_player_pos:
            # Continue chasing last known position for a while
            if current_time - self.last_player_seen_time > self.give_up_time:
                self.state = "idle"
                self.last_seen_player_pos = None
        
        elif self.state == "attacking":
            # If we can't see player anymore, start chasing last known position
            if self.last_seen_player_pos:
                self.state = "chasing"
            else:
                self.state = "idle"
    
    def idle_behavior(self, dt: float):
        """Idle behavior - minimal movement."""
        # Occasionally move randomly
        if random.random() < 0.1 * dt:  # 10% chance per second
            angle = random.uniform(0, 2 * math.pi)
            self.velocity[0] = math.cos(angle) * self.speed * 0.3
            self.velocity[1] = math.sin(angle) * self.speed * 0.3
        else:
            # Gradually stop moving
            self.velocity[0] *= 0.9
            self.velocity[1] *= 0.9
    
    def chase_behavior(self, dt: float, player, level, current_time: float):
        """Chase behavior - move towards player or last known position."""
        target_pos = self.last_seen_player_pos if self.last_seen_player_pos else player.position
        
        # Calculate direction to target
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 5:  # Don't move if very close to target
            # Normalize direction and apply speed
            self.velocity[0] = (dx / distance) * self.speed
            self.velocity[1] = (dy / distance) * self.speed
        else:
            self.velocity[0] = 0
            self.velocity[1] = 0
    
    def attack_behavior(self, dt: float, player, current_time: float):
        """Attack behavior - attack player when in range."""
        # Stop moving when attacking
        self.velocity[0] = 0
        self.velocity[1] = 0
        
        # Attack if cooldown is ready
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.attack_player(player)
            self.last_attack_time = current_time
    
    def attack_player(self, player):
        """Attack the player (different behavior for ranged vs melee)."""
        if self.enemy_type == "ranged":
            # Ranged enemies shoot projectiles (simplified - just direct damage for now)
            print(f"{self.enemy_type} enemy shoots at player!")
            player.take_damage(self.damage)
        else:
            # Melee attack
            print(f"{self.enemy_type} enemy attacks player!")
            player.take_damage(self.damage)
    
    def apply_movement(self, dt: float, level):
        """Apply movement with collision detection."""
        # Try horizontal movement
        new_x = self.position[0] + self.velocity[0] * dt
        if not level.check_wall_collision((new_x, self.position[1]), self.radius):
            self.position[0] = new_x
        else:
            self.velocity[0] = 0
        
        # Try vertical movement
        new_y = self.position[1] + self.velocity[1] * dt
        if not level.check_wall_collision((self.position[0], new_y), self.radius):
            self.position[1] = new_y
        else:
            self.velocity[1] = 0
    
    def take_damage(self, amount: int) -> bool:
        """Take damage and return True if enemy dies."""
        self.current_health = max(0, self.current_health - amount)
        
        if self.current_health <= 0:
            self.state = "dead"
            print(f"{self.enemy_type} enemy defeated!")
            return True
        
        return False
    
    def distance_to_player(self, player) -> float:
        """Calculate distance to player."""
        dx = player.position[0] - self.position[0]
        dy = player.position[1] - self.position[1]
        return math.sqrt(dx**2 + dy**2)
    
    def is_alive(self) -> bool:
        """Check if enemy is alive."""
        return self.current_health > 0 and self.state != "dead"
    
    def get_health_percentage(self) -> float:
        """Get health as a percentage."""
        return self.current_health / self.max_health if self.max_health > 0 else 0.0
    
    def render(self, screen: pygame.Surface, camera_x: int, camera_y: int, asset_manager):
        """Render the enemy on screen."""
        if not self.is_alive():
            return
        
        # Calculate screen position
        screen_x = int(self.position[0] + camera_x)
        screen_y = int(self.position[1] + camera_y)
        
        # Draw enemy circle
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.radius)
        pygame.draw.circle(screen, self.outline_color, (screen_x, screen_y), self.radius, 1)
        
        # Draw state indicator
        self.draw_state_indicator(screen, screen_x, screen_y)
        
        # Draw health bar if damaged
        if self.current_health < self.max_health:
            self.draw_health_bar(screen, screen_x, screen_y - self.radius - 8)
    
    def draw_state_indicator(self, screen: pygame.Surface, screen_x: int, screen_y: int):
        """Draw a small indicator showing enemy state."""
        indicator_colors = {
            "idle": (100, 100, 100),
            "chasing": (255, 200, 0),
            "attacking": (255, 0, 0)
        }
        
        color = indicator_colors.get(self.state, (100, 100, 100))
        pygame.draw.circle(screen, color, (screen_x, screen_y), 3)
    
    def draw_health_bar(self, screen: pygame.Surface, x: int, y: int):
        """Draw health bar above enemy."""
        bar_width = 20
        bar_height = 3
        health_percentage = self.get_health_percentage()
        
        # Background (red)
        pygame.draw.rect(screen, (200, 50, 50), 
                        (x - bar_width // 2, y, bar_width, bar_height))
        
        # Health (green)
        health_width = int(bar_width * health_percentage)
        if health_width > 0:
            pygame.draw.rect(screen, (50, 200, 50), 
                            (x - bar_width // 2, y, health_width, bar_height))

def create_enemy(position: Tuple[float, float], player_level: int) -> Enemy:
    """Factory function to create a random enemy appropriate for the player level."""
    enemy_types = ["basic", "fast", "heavy"]
    
    # Add ranged enemies at higher levels
    if player_level >= 2:
        enemy_types.append("ranged")
    
    enemy_type = random.choice(enemy_types)
    return Enemy(position, enemy_type, player_level)
