"""
Player class and related functionality.
Handles player movement, stats, leveling, and input processing.
"""

import pygame
import math
from typing import Tuple, List
from combat import CombatSystem
from items import PlayerInventory
from weapon_renderer import WeaponRenderer
from damage_numbers import DamageNumberManager

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
        self.total_xp = 0  # Track total XP earned for stats
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
        
        # Initialize inventory
        self.inventory = PlayerInventory()
        
        # Visual properties
        self.color = (100, 150, 255)  # Light blue
        self.outline_color = (255, 255, 255)
        
        print(f"Player created with {self.current_health}/{self.max_health} HP")
    
    @property
    def damage(self) -> int:
        """Calculate current damage based on level, base damage, and equipped weapon."""
        base = int(self.base_damage * (1 + (self.level - 1) * 0.2))
        
        # Apply weapon multiplier if equipped
        if self.inventory.melee_weapon:
            base = int(base * self.inventory.melee_weapon.damage_multiplier)
        
        return base
    
    @property
    def effective_max_health(self) -> int:
        """Get max health considering enchantments."""
        base_health = self.max_health
        
        # Red enchantment increases max HP to 125%
        if (self.inventory.enchantment and 
            self.inventory.enchantment.effect == "hp_boost"):
            base_health = int(base_health * 1.25)
            
        return base_health
    
    @property
    def effective_speed(self) -> float:
        """Get movement speed considering active effects."""
        return self.speed
    
    def get_current_speed(self, mouse_buttons) -> float:
        """Get current movement speed considering haste spell."""
        base_speed = self.speed
        
        # Check for haste spell boost while right clicking
        if mouse_buttons[2] and self.inventory.spell and self.inventory.spell.effect == "speed_boost":
            return base_speed * 1.8  # 80% speed boost
        
        return base_speed
    
    def update(self, dt: float, keys, mouse_pos: Tuple[int, int], 
               mouse_buttons: Tuple[bool, bool, bool], level):
        """Update player state, movement, and combat."""
        # Store mouse buttons for visual effects
        self._last_mouse_buttons = mouse_buttons
        
        # Handle movement input
        self.handle_movement(dt, keys, level, mouse_buttons)
        
        # Handle combat input
        self.handle_combat_input(dt, mouse_pos, mouse_buttons, level)
        
        # Update combat system
        self.combat_system.update(dt)
        
        # Health regeneration (only if not recently damaged)
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.last_damage_time > 3.0:  # 3 seconds without damage
            self.heal(self.health_regen_rate * dt)
    
    def handle_movement(self, dt: float, keys, level, mouse_buttons=None):
        """Handle player movement based on input."""
        # Reset velocity
        self.velocity = [0.0, 0.0]
        
        # Get current speed (considering haste boost)
        if mouse_buttons:
            current_speed = self.get_current_speed(mouse_buttons)
        else:
            current_speed = self.speed
        
        # Check movement keys
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity[1] -= current_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity[1] += current_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity[0] -= current_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity[0] += current_speed
        
        # Normalize diagonal movement
        vel_magnitude = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        if vel_magnitude > current_speed:
            self.velocity[0] = (self.velocity[0] / vel_magnitude) * current_speed
            self.velocity[1] = (self.velocity[1] / vel_magnitude) * current_speed
        
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
        
        # Right click for ranged attack or spell
        if mouse_buttons[2]:  # Right mouse button
            target_pos = (world_mouse_x, world_mouse_y)
            
            # Check if player has a spell equipped
            if self.inventory.spell:
                current_time = pygame.time.get_ticks() / 1000.0
                if self.inventory.spell.is_ready(current_time):
                    self.cast_spell(target_pos, current_time, level)
                else:
                    print(f"{self.inventory.spell.name} is on cooldown")
            else:
                # Default ranged attack
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
        self.total_xp += amount  # Track total XP for stats
        
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
    
    def cast_spell(self, target_pos: Tuple[float, float], current_time: float, level):
        """Cast the equipped spell."""
        if not self.inventory.spell:
            return
            
        spell = self.inventory.spell
        spell.use(current_time)
        
        if spell.effect == "speed_boost":  # Haste
            # Haste works continuously while holding right-click (no activation message needed)
            pass
            
        elif spell.effect == "area_damage":  # Power Pulse
            # Deal massive damage in large circle around player with 8x player length range
            damage = int(self.damage * 3.0)  # Higher damage for longer cooldown
            radius = self.radius * 8  # 8x player length (doubled from 4x) for better range
            
            # Create visual effect for power pulse
            pulse_effect = {
                'type': 'power_pulse',
                'center': tuple(self.position),
                'radius': radius,
                'lifetime': 0.8,
                'max_lifetime': 0.8
            }
            self.combat_system.attack_animations.append(pulse_effect)
            
            for enemy in level.enemies:
                if enemy.is_alive():
                    dx = enemy.position[0] - self.position[0]
                    dy = enemy.position[1] - self.position[1]
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance <= radius:
                        enemy.take_damage(damage)
                        # Add hit effect on enemy
                        enemy.add_hit_effect()
                        print(f"Power Pulse hit {enemy.enemy_type} enemy for {damage} damage!")
                        
        elif spell.effect == "mind_control":  # Turn Coat
            # Find closest enemy and make it attack other enemies
            closest_enemy = None
            min_distance = float('inf')
            
            for enemy in level.enemies:
                if enemy.is_alive():
                    dx = enemy.position[0] - self.position[0]
                    dy = enemy.position[1] - self.position[1]
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance < min_distance:
                        min_distance = distance
                        closest_enemy = enemy
            
            if closest_enemy:
                # Create projectile with unique coloring for Turn Coat
                from combat import Projectile
                turn_coat_projectile = Projectile(
                    (self.position[0], self.position[1]), 
                    (closest_enemy.position[0], closest_enemy.position[1]), 
                    0,  # No damage, just visual
                    600,  # Fast projectile
                    2.0,  # 2 second lifetime
                    (255, 165, 0)  # Orange color
                )
                turn_coat_projectile.is_turn_coat = True
                turn_coat_projectile.target_enemy = closest_enemy
                self.combat_system.projectiles.append(turn_coat_projectile)
                
                print(f"Turn Coat projectile launched at {closest_enemy.enemy_type} enemy!")
    
    def try_pickup_item(self, level):
        """Try to pickup nearby item."""
        item = level.item_manager.check_item_pickup(tuple(self.position))
        if item:
            # Handle health items specially - they are consumed immediately
            if item.item_type.value == "health":
                from items import HealthItem
                if isinstance(item, HealthItem):
                    if item.use_on_player(self):
                        level.item_manager.pickup_item(item)
                        heal_percent = int(item.heal_percentage * 100)
                        print(f"Picked up health pack! Healed {heal_percent}%")
                        # Add notification
                        if hasattr(level, 'notification_manager'):
                            level.notification_manager.add_pickup_notification(item.name, f"Healed {heal_percent}% health")
                    else:
                        print("Already at full health!")
                        if hasattr(level, 'notification_manager'):
                            level.notification_manager.add_pickup_notification("Health Pack", "Already at full health")
                return
            
            # Handle equipment items (weapons, enchantments, spells)
            old_item = self.inventory.equip_item(item)
            level.item_manager.pickup_item(item)
            
            if old_item:
                # Drop the old item at player position
                level.item_manager.drop_item(old_item, tuple(self.position))
                print(f"Picked up {item.name}, dropped {old_item.name}")
                # Add notifications
                if hasattr(level, 'notification_manager'):
                    level.notification_manager.add_pickup_notification(item.name, item.description)
                    level.notification_manager.add_drop_notification(old_item.name)
            else:
                print(f"Picked up {item.name}")
                # Add notification
                if hasattr(level, 'notification_manager'):
                    level.notification_manager.add_pickup_notification(item.name, item.description)
    
    def drop_spell(self, level):
        """Drop the equipped spell."""
        if self.inventory.spell:
            spell = self.inventory.drop_spell()
            if spell:
                level.item_manager.drop_item(spell, tuple(self.position))
                print(f"Dropped {spell.name}")
                # Add notification
                if hasattr(level, 'notification_manager'):
                    level.notification_manager.add_drop_notification(spell.name)
        else:
            print("No spell equipped to drop")
    
    def render(self, screen: pygame.Surface, camera_x: int, camera_y: int, asset_manager):
        """Render the player on screen."""
        # Calculate screen position
        screen_x = int(self.position[0] + camera_x)
        screen_y = int(self.position[1] + camera_y)
        
        # Check if haste effect is active for visual effects
        is_hasted = (hasattr(self, '_last_mouse_buttons') and 
                    self._last_mouse_buttons[2] and 
                    self.inventory.spell and 
                    self.inventory.spell.effect == "speed_boost")
        
        # Add speed trail effect when hasted
        if is_hasted and hasattr(self, 'velocity'):
            vel_magnitude = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
            if vel_magnitude > 50:  # Only show trail when moving fast
                # Draw speed lines behind player
                for i in range(3):
                    trail_x = screen_x - (self.velocity[0] / vel_magnitude) * (12 + i * 8)
                    trail_y = screen_y - (self.velocity[1] / vel_magnitude) * (12 + i * 8)
                    alpha = 180 - (i * 60)
                    trail_color = (100, 255, 255)  # Cyan trail
                    pygame.draw.circle(screen, trail_color, (int(trail_x), int(trail_y)), 4 - i)
        
        # Add haste glow effect
        if is_hasted:
            pygame.draw.circle(screen, (100, 255, 255), (screen_x, screen_y), self.radius + 4, 2)
            color = (150, 200, 255)  # Brighter when hasted
        else:
            color = self.color
        
        # Draw player as a circle with outline
        pygame.draw.circle(screen, color, (screen_x, screen_y), self.radius)
        pygame.draw.circle(screen, self.outline_color, (screen_x, screen_y), self.radius, 2)
        
        # Draw a small directional indicator
        if self.velocity[0] != 0 or self.velocity[1] != 0:
            # Calculate direction
            direction = math.atan2(self.velocity[1], self.velocity[0])
            end_x = screen_x + math.cos(direction) * (self.radius - 3)
            end_y = screen_y + math.sin(direction) * (self.radius - 3)
            pygame.draw.line(screen, (255, 255, 255), (screen_x, screen_y), (end_x, end_y), 2)
        
        # Render equipped weapon when not attacking
        if not self.combat_system.attack_animations:
            # Calculate facing angle based on movement or last attack direction
            facing_angle = 0  # Default facing right
            if self.velocity[0] != 0 or self.velocity[1] != 0:
                facing_angle = math.atan2(self.velocity[1], self.velocity[0])
            # Use a simple right-facing default
            facing_angle = 0
                
            # Get current weapon type as string
            weapon_type = "fist"  # Default
            if self.inventory.melee_weapon:
                weapon_type = str(self.inventory.melee_weapon.weapon_type)
                
            WeaponRenderer.render_equipped_weapon(
                screen, screen_x, screen_y, weapon_type, self.radius, facing_angle
            )
        
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
