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
        
        # Set weapon based on enemy type
        self.setup_weapon(enemy_type)
        
        # Pathfinding
        self.path_update_timer = 0
        self.path_update_interval = 0.5  # Update path every 0.5 seconds
        
        # Visual
        self.setup_appearance()
        
        # Hit effects
        self.hit_effect_time = 0.0
        self.hit_effect_duration = 0.3  # Flash for 0.3 seconds when hit
        
        print(f"Created {enemy_type} enemy (level {player_level}) with {self.current_health} HP")
    
    def setup_stats(self, enemy_type: str, player_level: int):
        """Set up enemy stats based on type and player level."""
        base_stats = {
            "basic": {"health": 50, "damage": 15, "xp": 25, "attack_speed": 1.5, "weapon": "fist"},
            "fast": {"health": 30, "damage": 12, "xp": 20, "attack_speed": 1.0, "weapon": "dagger"},
            "heavy": {"health": 80, "damage": 25, "xp": 40, "attack_speed": 2.5, "weapon": "sword"},
            "ranged": {"health": 40, "damage": 20, "xp": 35, "attack_speed": 2.0, "weapon": "ranged"},
            "mobile_ranged": {"health": 35, "damage": 18, "xp": 30, "attack_speed": 1.8, "weapon": "ranged"}
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
        
        # Mind control status
        self.mind_controlled = False
        self.mind_control_end_time = 0.0
        
        # Visual indicators for enchantment
        self.enchanted_color = (255, 165, 0)  # Orange for mind control
    
    def setup_weapon(self, enemy_type: str):
        """Set up weapon properties based on enemy type."""
        weapon_configs = {
            "basic": {  # Weakest - uses fist
                "weapon_type": "fist",
                "range": 20,
                "arc": 60,
                "speed_multiplier": 1.0
            },
            "fast": {  # Dagger - low damage, low range, 100 degree range, super fast
                "weapon_type": "dagger",
                "range": 25,
                "arc": 100,
                "speed_multiplier": 2.0,
                "damage_multiplier": 0.8
            },
            "heavy": {  # Uses mace, spear, or sword
                "weapon_type": random.choice(["mace", "spear", "sword"]),
                "range": 35,
                "arc": 90,
                "speed_multiplier": 0.8
            },
            "ranged": {  # Ranged attacker
                "weapon_type": "ranged",
                "range": 100,
                "arc": 15,
                "speed_multiplier": 1.0
            },
            "mobile_ranged": {  # Fast moving ranged attacker that kites player
                "weapon_type": "ranged",
                "range": 80,
                "arc": 20,
                "speed_multiplier": 1.5,
                "kite_behavior": True  # Moves away from player
            }
        }
        
        config = weapon_configs.get(enemy_type, weapon_configs["basic"])
        self.weapon_type = config["weapon_type"]
        self.weapon_range = config["range"]
        self.weapon_arc = config["arc"]
        self.weapon_speed_multiplier = config.get("speed_multiplier", 1.0)
        self.weapon_damage_multiplier = config.get("damage_multiplier", 1.0)
        self.kite_behavior = config.get("kite_behavior", False)
        
        # Adjust attack speed based on weapon
        self.attack_cooldown /= self.weapon_speed_multiplier
    
    def update(self, dt: float, player, level, can_see_player: bool):
        """Update enemy AI and behavior."""
        if not self.is_alive():
            return
        
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Check mind control status
        if self.mind_controlled and current_time >= self.mind_control_end_time:
            self.mind_controlled = False
            print(f"{self.enemy_type} enemy is no longer mind controlled")
        
        # Update projectiles for ranged enemies
        if hasattr(self, 'projectiles'):
            for projectile in self.projectiles[:]:
                projectile.update(dt)
                if projectile.should_remove():
                    self.projectiles.remove(projectile)
                elif projectile.check_collision_with_target(player, player.radius):
                    if player.take_damage(projectile.damage):
                        print(f"Ranged projectile hit player for {projectile.damage} damage!")
                    self.projectiles.remove(projectile)
        
        # Update AI state based on player visibility (mind controlled enemies act differently)
        if not self.mind_controlled:
            self.update_ai_state(player, can_see_player, current_time)
        else:
            # Mind controlled enemies attack other enemies instead
            self.mind_control_behavior(dt, level, current_time)
        
        # Execute behavior based on current state
        if self.state == "idle":
            self.idle_behavior(dt)
        elif self.state == "chasing":
            self.chase_behavior(dt, player, level, current_time)
        elif self.state == "attacking":
            self.attack_behavior(dt, player, current_time)
        
        # Apply movement
        self.apply_movement(dt, level)
        
        # Update attack animations
        if hasattr(self, 'attack_animations'):
            for animation in self.attack_animations[:]:
                animation['lifetime'] -= dt
                if animation['lifetime'] <= 0:
                    self.attack_animations.remove(animation)
    
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
        
        # Mobile ranged enemies use kiting behavior
        if self.kite_behavior and distance < self.weapon_range * 0.8:
            # Move away from player to maintain distance
            self.velocity[0] = -(dx / distance) * self.speed
            self.velocity[1] = -(dy / distance) * self.speed
        elif distance > 5:  # Normal chase behavior
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
        """Attack the player using their weapon type with visual effects."""
        damage = int(self.damage * self.weapon_damage_multiplier)
        
        # Calculate attack direction to player
        dx = player.position[0] - self.position[0]
        dy = player.position[1] - self.position[1]
        attack_angle = math.atan2(dy, dx)
        
        if self.weapon_type == "ranged":
            # Create visual projectile for ranged enemies
            from combat import Projectile
            projectile = Projectile(
                self.position[:],  # Start from enemy position
                player.position[:],  # Target player position
                damage,
                300  # Projectile speed
            )
            if not hasattr(self, 'projectiles'):
                self.projectiles = []
            self.projectiles.append(projectile)
            print(f"{self.enemy_type} enemy shoots at player!")
        else:
            # Melee attack with visual animation
            self.create_attack_animation(attack_angle)
            # Check if player is in range for melee hit
            distance = math.sqrt(dx**2 + dy**2)
            if distance <= self.weapon_range:
                player.take_damage(damage)
                print(f"{self.enemy_type} enemy attacks player with {self.weapon_type}!")
            else:
                print(f"{self.enemy_type} enemy swings but misses (too far)!")
    
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
        
        # Determine current color (with hit effect and mind control)
        current_color = self.color
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Apply hit effect (white flash)
        if current_time < self.hit_effect_time + self.hit_effect_duration:
            flash_intensity = 1.0 - ((current_time - self.hit_effect_time) / self.hit_effect_duration)
            current_color = (
                int(self.color[0] + (255 - self.color[0]) * flash_intensity),
                int(self.color[1] + (255 - self.color[1]) * flash_intensity),
                int(self.color[2] + (255 - self.color[2]) * flash_intensity)
            )
        
        # Draw enemy circle
        pygame.draw.circle(screen, current_color, (screen_x, screen_y), self.radius)
        
        # Draw mind control indicator if enchanted
        if self.mind_controlled:
            pygame.draw.circle(screen, self.enchanted_color, (screen_x, screen_y), self.radius + 3, 2)
            # Pulsing effect
            pulse = int(20 * (0.5 + 0.5 * math.sin(current_time * 8)))
            pygame.draw.circle(screen, (255, 165, 0, pulse), (screen_x, screen_y), self.radius + 5, 1)
        
        pygame.draw.circle(screen, self.outline_color, (screen_x, screen_y), self.radius, 1)
        
        # Draw state indicator
        self.draw_state_indicator(screen, screen_x, screen_y)
        
        # Draw health bar if damaged
        if self.current_health < self.max_health:
            self.draw_health_bar(screen, screen_x, screen_y - self.radius - 8)
        
        # Render ranged projectiles
        if hasattr(self, 'projectiles'):
            for projectile in self.projectiles:
                projectile_x = int(projectile.position[0] + camera_x)
                projectile_y = int(projectile.position[1] + camera_y)
                # Draw enemy projectile as red dot
                pygame.draw.circle(screen, (255, 100, 100), (projectile_x, projectile_y), 4)
                pygame.draw.circle(screen, (200, 0, 0), (projectile_x, projectile_y), 4, 1)
        
        # Render attack animations
        if hasattr(self, 'attack_animations'):
            for animation in self.attack_animations:
                self.render_attack_animation(screen, camera_x, camera_y, animation)
    
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
    
    def create_attack_animation(self, attack_angle: float):
        """Create a visual effect for enemy weapon attack."""
        if not hasattr(self, 'attack_animations'):
            self.attack_animations = []
        
        # Create animation based on weapon type
        if self.weapon_type == "sword":
            animation = {
                'type': 'enemy_sword_swing',
                'angle': attack_angle,
                'lifetime': 0.25,
                'max_lifetime': 0.25,
                'range': self.weapon_range,
                'color': (150, 150, 200)  # Light blue
            }
        elif self.weapon_type == "spear":
            animation = {
                'type': 'enemy_spear_poke',
                'angle': attack_angle,
                'lifetime': 0.15,
                'max_lifetime': 0.15,
                'range': self.weapon_range,
                'color': (139, 69, 19)  # Brown
            }
        elif self.weapon_type == "mace":
            animation = {
                'type': 'enemy_mace_swing',
                'angle': attack_angle,
                'lifetime': 0.25,
                'max_lifetime': 0.25,
                'range': self.weapon_range,
                'color': (128, 128, 128)  # Gray
            }
        elif self.weapon_type == "dagger":
            animation = {
                'type': 'enemy_dagger_stab',
                'angle': attack_angle,
                'lifetime': 0.12,
                'max_lifetime': 0.12,
                'range': self.weapon_range,
                'color': (180, 180, 180)  # Silver
            }
        else:  # fist or default
            animation = {
                'type': 'enemy_punch',
                'angle': attack_angle,
                'lifetime': 0.2,
                'max_lifetime': 0.2,
                'range': self.weapon_range,
                'color': self.color  # Use enemy color
            }
        
        self.attack_animations.append(animation)
    
    def render_attack_animation(self, screen: pygame.Surface, camera_x: int, camera_y: int, animation):
        """Render enemy attack animation."""
        screen_x = int(self.position[0] + camera_x)
        screen_y = int(self.position[1] + camera_y)
        
        progress = 1.0 - (animation['lifetime'] / animation['max_lifetime'])
        
        if animation['type'] == 'enemy_sword_swing':
            # Sword swing animation
            swing_distance = animation['range'] * (0.7 + 0.3 * progress)
            end_x = screen_x + math.cos(animation['angle']) * swing_distance
            end_y = screen_y + math.sin(animation['angle']) * swing_distance
            pygame.draw.line(screen, animation['color'], (screen_x, screen_y), (end_x, end_y), 3)
            
        elif animation['type'] == 'enemy_spear_poke':
            # Spear poke animation
            poke_distance = animation['range'] * (0.5 + 0.5 * math.sin(progress * math.pi))
            end_x = screen_x + math.cos(animation['angle']) * poke_distance
            end_y = screen_y + math.sin(animation['angle']) * poke_distance
            pygame.draw.line(screen, animation['color'], (screen_x, screen_y), (end_x, end_y), 4)
            pygame.draw.circle(screen, (180, 180, 180), (int(end_x), int(end_y)), 3)
            
        elif animation['type'] == 'enemy_mace_swing':
            # Mace swing animation
            swing_distance = animation['range'] * (0.7 + 0.3 * progress)
            end_x = screen_x + math.cos(animation['angle']) * swing_distance
            end_y = screen_y + math.sin(animation['angle']) * swing_distance
            # Draw handle
            handle_end = swing_distance * 0.7
            handle_x = screen_x + math.cos(animation['angle']) * handle_end
            handle_y = screen_y + math.sin(animation['angle']) * handle_end
            pygame.draw.line(screen, (139, 69, 19), (screen_x, screen_y), (handle_x, handle_y), 3)
            # Draw mace head
            pygame.draw.circle(screen, animation['color'], (int(end_x), int(end_y)), 6)
            
        elif animation['type'] == 'enemy_dagger_stab':
            # Quick dagger stab
            stab_distance = animation['range'] * (0.8 + 0.2 * math.sin(progress * math.pi * 2))
            end_x = screen_x + math.cos(animation['angle']) * stab_distance
            end_y = screen_y + math.sin(animation['angle']) * stab_distance
            pygame.draw.line(screen, animation['color'], (screen_x, screen_y), (end_x, end_y), 2)
            
        else:  # enemy_punch
            # Fist punch animation
            punch_distance = animation['range'] * (0.6 + 0.4 * math.sin(progress * math.pi))
            end_x = screen_x + math.cos(animation['angle']) * punch_distance
            end_y = screen_y + math.sin(animation['angle']) * punch_distance
            pygame.draw.circle(screen, animation['color'], (int(end_x), int(end_y)), 5)
            pygame.draw.circle(screen, (150, 150, 150), (int(end_x), int(end_y)), 5, 1)
    
    def mind_control_behavior(self, dt: float, level, current_time: float):
        """Behavior when mind controlled - attack other enemies."""
        # Find nearest enemy that isn't mind controlled
        target_enemy = None
        min_distance = float('inf')
        
        for enemy in level.enemies:
            if (enemy != self and enemy.is_alive() and not enemy.mind_controlled):
                distance = self.distance_to_enemy(enemy)
                if distance < min_distance:
                    min_distance = distance
                    target_enemy = enemy
        
        if target_enemy:
            # Chase and attack the target enemy
            if min_distance <= self.attack_range:
                self.state = "attacking"
                if current_time - self.last_attack_time >= self.attack_cooldown:
                    # Attack the enemy
                    target_enemy.take_damage(self.damage)
                    self.last_attack_time = current_time
                    print(f"Mind controlled {self.enemy_type} attacks {target_enemy.enemy_type}!")
            else:
                self.state = "chasing"
                # Move towards target enemy
                dx = target_enemy.position[0] - self.position[0]
                dy = target_enemy.position[1] - self.position[1]
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance > 0:
                    self.velocity[0] = (dx / distance) * self.speed
                    self.velocity[1] = (dy / distance) * self.speed
        else:
            # No enemies to attack, go idle
            self.state = "idle"
            self.velocity = [0.0, 0.0]

    def distance_to_enemy(self, other_enemy) -> float:
        """Calculate distance to another enemy."""
        dx = other_enemy.position[0] - self.position[0]
        dy = other_enemy.position[1] - self.position[1]
        return math.sqrt(dx * dx + dy * dy)

def create_enemy(position: Tuple[float, float], player_level: int) -> Enemy:
    """Factory function to create a random enemy appropriate for the player level."""
    enemy_types = ["basic", "fast", "heavy"]
    
    # Add ranged enemies at higher levels
    if player_level >= 2:
        enemy_types.append("ranged")
    
    enemy_type = random.choice(enemy_types)
    return Enemy(position, enemy_type, player_level)

# Add the missing method to Enemy class
def add_hit_effect(self):
    """Add visual hit effect when enemy takes damage."""
    self.hit_effect_time = pygame.time.get_ticks() / 1000.0

# Hit effect method added above within class
