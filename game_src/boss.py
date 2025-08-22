"""
Boss enemies with unique abilities and enhanced stats.
Handles different boss types with special attacks and mechanics.
"""

import pygame
import math
import random
from typing import Tuple, List
from .enemy import Enemy

class Boss(Enemy):
    """Boss enemy class with unique abilities and enhanced stats."""
    
    def __init__(self, position: Tuple[float, float], level: int):
        """Initialize boss based on level."""
        self.level = level
        self.boss_type = self.get_boss_type(level)
        
        # Initialize as a heavy enemy first
        super().__init__(position, "heavy", level)
        
        # Ensure mind control attributes are properly set (inherited from Enemy)
        # These should already exist from Enemy.__init__, but let's be explicit
        if not hasattr(self, 'mind_controlled'):
            self.mind_controlled = False
            self.mind_control_end_time = 0.0
        
        # Override with boss stats
        self.setup_boss_stats()
        self.setup_boss_abilities()
        
        # Boss-specific properties
        self.is_boss = True
        self.special_attack_cooldown = 3.0
        self.last_special_attack = 0.0
        self.enrage_threshold = 0.3  # Enrage at 30% health
        self.enraged = False
        self.death_processed = False  # Prevent duplicate XP gain
        
        print(f"Created level {level} boss: {self.boss_type} with {self.current_health} HP")
    
    def get_boss_type(self, level: int) -> str:
        """Determine boss type based on level."""
        if level == 10:
            return "shadow_lord"
        elif level % 3 == 0:  # Every 3rd level gets a special boss
            boss_types = ["flame_berserker", "ice_mage", "lightning_striker"]
            return boss_types[(level // 3 - 1) % len(boss_types)]
        else:
            return "elite_guardian"
    
    def setup_boss_stats(self):
        """Set up enhanced boss stats."""
        # Base multipliers
        health_multiplier = 3.0 + (self.level * 0.5)
        damage_multiplier = 1.5 + (self.level * 0.2)
        
        # Special boss multipliers
        if self.boss_type == "shadow_lord":
            health_multiplier *= 2.0
            damage_multiplier *= 1.8
        elif self.boss_type in ["flame_berserker", "ice_mage", "lightning_striker"]:
            health_multiplier *= 1.5
            damage_multiplier *= 1.3
        
        # Apply multipliers
        self.max_health = int(self.max_health * health_multiplier)
        self.current_health = self.max_health
        self.damage = int(self.damage * damage_multiplier)
        self.xp_value = int(self.xp_value * 3.0)  # Bosses give 3x XP
        
        # Enhanced physical stats
        self.radius = 20 if self.boss_type == "shadow_lord" else 16
        self.speed *= 1.3  # Bosses are now faster and more aggressive (was 0.8)
        self.attack_range *= 1.2
    
    def setup_boss_abilities(self):
        """Set up boss-specific abilities."""
        self.abilities = {}
        
        if self.boss_type == "flame_berserker":
            self.abilities = {
                "fire_spin": {"cooldown": 4.0, "last_used": 0.0},
                "flame_charge": {"cooldown": 6.0, "last_used": 0.0}
            }
        elif self.boss_type == "ice_mage":
            self.abilities = {
                "ice_shard": {"cooldown": 2.5, "last_used": 0.0},
                "frost_nova": {"cooldown": 8.0, "last_used": 0.0}
            }
        elif self.boss_type == "lightning_striker":
            self.abilities = {
                "lightning_bolt": {"cooldown": 3.0, "last_used": 0.0},
                "chain_lightning": {"cooldown": 7.0, "last_used": 0.0}
            }
        elif self.boss_type == "shadow_lord":
            self.abilities = {
                "shadow_bolt": {"cooldown": 2.0, "last_used": 0.0},
                "dark_storm": {"cooldown": 10.0, "last_used": 0.0},
                "summon_minions": {"cooldown": 15.0, "last_used": 0.0}
            }
    
    def setup_appearance(self):
        """Set up boss visual appearance."""
        boss_colors = {
            "elite_guardian": (150, 50, 50),      # Dark red
            "flame_berserker": (255, 100, 0),    # Orange-red
            "ice_mage": (100, 200, 255),         # Light blue
            "lightning_striker": (255, 255, 100), # Yellow
            "shadow_lord": (80, 0, 150)          # Dark purple
        }
        
        self.color = boss_colors.get(self.boss_type, (150, 50, 50))
        self.outline_color = (255, 255, 255)
    
    def update(self, dt: float, player, level, can_see_player: bool):
        """Update boss behavior with special abilities."""
        if not self.is_alive():
            return
        
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Check for enrage mode
        if not self.enraged and self.get_health_percentage() <= self.enrage_threshold:
            self.enrage()
        
        # Use special abilities if player is visible
        if can_see_player and current_time - self.last_special_attack >= self.special_attack_cooldown:
            self.use_special_ability(player, current_time, level)
        
        # Regular enemy update
        super().update(dt, player, level, can_see_player)
    
    def enrage(self):
        """Activate enrage mode - increased speed and attack rate."""
        self.enraged = True
        self.speed *= 2.0  # Even faster when enraged (was 1.5)
        self.attack_cooldown *= 0.5  # Much faster attacks (was 0.7)
        self.special_attack_cooldown *= 0.6  # Faster specials (was 0.8)
        print(f"Boss {self.boss_type} is now ENRAGED! Max speed and aggression!")
    
    def use_special_ability(self, player, current_time: float, level):
        """Use boss-specific special abilities."""
        player_distance = self.distance_to_player(player)
        
        if self.boss_type == "flame_berserker":
            if player_distance <= 80:
                self.flame_charge(player, current_time, level)
            else:
                self.fire_spin(current_time, level)
        
        elif self.boss_type == "ice_mage":
            if player_distance <= 120:
                self.frost_nova(current_time, level)
            else:
                self.ice_shard(player, current_time, level)
        
        elif self.boss_type == "lightning_striker":
            if self.enraged:
                self.chain_lightning(current_time, level)
            else:
                self.lightning_bolt(player, current_time, level)
        
        elif self.boss_type == "shadow_lord":
            if player_distance <= 100:
                self.dark_storm(current_time, level)
            elif current_time - self.abilities["summon_minions"]["last_used"] >= 15.0:
                self.summon_minions(current_time, level)
            else:
                self.shadow_bolt(player, current_time, level)
    
    def flame_charge(self, player, current_time: float, level):
        """Charge toward player with flame trail."""
        if current_time - self.abilities["flame_charge"]["last_used"] >= self.abilities["flame_charge"]["cooldown"]:
            # Create charging velocity toward player
            dx = player.position[0] - self.position[0]
            dy = player.position[1] - self.position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 0:
                charge_speed = self.speed * 3.0
                self.velocity[0] = (dx / distance) * charge_speed
                self.velocity[1] = (dy / distance) * charge_speed
            
            self.abilities["flame_charge"]["last_used"] = current_time
            self.last_special_attack = current_time
            print(f"Boss uses FLAME CHARGE!")
    
    def fire_spin(self, current_time: float, level):
        """Create spinning fire projectiles."""
        if current_time - self.abilities["fire_spin"]["last_used"] >= self.abilities["fire_spin"]["cooldown"]:
            # Create 8 fire projectiles in a circle
            for i in range(8):
                angle = (i * math.pi * 2) / 8
                projectile_data = {
                    'position': self.position[:],
                    'velocity': [math.cos(angle) * 150, math.sin(angle) * 150],
                    'damage': self.damage,
                    'lifetime': 3.0,
                    'type': 'fire_spin'
                }
                level.boss_projectiles.append(projectile_data)
            
            self.abilities["fire_spin"]["last_used"] = current_time
            self.last_special_attack = current_time
            print(f"Boss uses FIRE SPIN!")
    
    def ice_shard(self, player, current_time: float, level):
        """Launch ice shard at player."""
        if current_time - self.abilities["ice_shard"]["last_used"] >= self.abilities["ice_shard"]["cooldown"]:
            dx = player.position[0] - self.position[0]
            dy = player.position[1] - self.position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 0:
                projectile_data = {
                    'position': self.position[:],
                    'velocity': [(dx / distance) * 200, (dy / distance) * 200],
                    'damage': int(self.damage * 1.5),
                    'lifetime': 4.0,
                    'type': 'ice_shard'
                }
                level.boss_projectiles.append(projectile_data)
            
            self.abilities["ice_shard"]["last_used"] = current_time
            self.last_special_attack = current_time
            print(f"Boss uses ICE SHARD!")
    
    def frost_nova(self, current_time: float, level):
        """Create freezing nova around boss."""
        if current_time - self.abilities["frost_nova"]["last_used"] >= self.abilities["frost_nova"]["cooldown"]:
            # Create expanding frost effect
            frost_effect = {
                'position': self.position[:],
                'radius': 0,
                'max_radius': 100,
                'damage': self.damage,
                'lifetime': 2.0,
                'type': 'frost_nova',
                'created_time': current_time
            }
            level.boss_effects.append(frost_effect)
            
            self.abilities["frost_nova"]["last_used"] = current_time
            self.last_special_attack = current_time
            print(f"Boss uses FROST NOVA!")
    
    def lightning_bolt(self, player, current_time: float, level):
        """Strike player with lightning."""
        if current_time - self.abilities["lightning_bolt"]["last_used"] >= self.abilities["lightning_bolt"]["cooldown"]:
            # Create instant lightning strike
            lightning = {
                'start_pos': self.position[:],
                'end_pos': player.position[:],
                'damage': int(self.damage * 1.8),
                'lifetime': 0.3,
                'type': 'lightning_bolt',
                'created_time': current_time
            }
            level.boss_effects.append(lightning)
            
            self.abilities["lightning_bolt"]["last_used"] = current_time
            self.last_special_attack = current_time
            print(f"Boss uses LIGHTNING BOLT!")
    
    def chain_lightning(self, current_time: float, level):
        """Chain lightning between enemies and player."""
        if current_time - self.abilities["chain_lightning"]["last_used"] >= self.abilities["chain_lightning"]["cooldown"]:
            # Create chain lightning effect
            chain = {
                'origin': self.position[:],
                'damage': self.damage,
                'lifetime': 1.0,
                'type': 'chain_lightning',
                'created_time': current_time
            }
            level.boss_effects.append(chain)
            
            self.abilities["chain_lightning"]["last_used"] = current_time
            self.last_special_attack = current_time
            print(f"Boss uses CHAIN LIGHTNING!")
    
    def shadow_bolt(self, player, current_time: float, level):
        """Launch homing shadow projectile."""
        if current_time - self.abilities["shadow_bolt"]["last_used"] >= self.abilities["shadow_bolt"]["cooldown"]:
            projectile_data = {
                'position': self.position[:],
                'target': player.position[:],
                'velocity': [0, 0],  # Will be calculated as homing
                'damage': int(self.damage * 1.3),
                'lifetime': 5.0,
                'type': 'shadow_bolt',
                'homing': True
            }
            level.boss_projectiles.append(projectile_data)
            
            self.abilities["shadow_bolt"]["last_used"] = current_time
            self.last_special_attack = current_time
            print(f"Boss uses SHADOW BOLT!")
    
    def dark_storm(self, current_time: float, level):
        """Create dark energy storm."""
        if current_time - self.abilities["dark_storm"]["last_used"] >= self.abilities["dark_storm"]["cooldown"]:
            storm = {
                'position': self.position[:],
                'radius': 150,
                'damage': int(self.damage * 0.5),  # Lower damage but continuous
                'lifetime': 5.0,
                'type': 'dark_storm',
                'created_time': current_time
            }
            level.boss_effects.append(storm)
            
            self.abilities["dark_storm"]["last_used"] = current_time
            self.last_special_attack = current_time
            print(f"Boss uses DARK STORM!")
    
    def summon_minions(self, current_time: float, level):
        """Summon shadow minions."""
        if current_time - self.abilities["summon_minions"]["last_used"] >= self.abilities["summon_minions"]["cooldown"]:
            # Spawn 3 shadow minions around the boss
            for i in range(3):
                angle = (i * math.pi * 2) / 3
                offset_x = math.cos(angle) * 60
                offset_y = math.sin(angle) * 60
                
                minion_pos = (self.position[0] + offset_x, self.position[1] + offset_y)
                
                # Create shadow minion (weaker enemy)
                minion = Enemy(minion_pos, "fast", max(1, self.level // 2))
                minion.color = (50, 0, 100)  # Dark purple
                minion.max_health = int(minion.max_health * 0.6)
                minion.current_health = minion.max_health
                level.enemies.append(minion)
            
            self.abilities["summon_minions"]["last_used"] = current_time
            self.last_special_attack = current_time
            print(f"Boss summons SHADOW MINIONS!")
    
    def render(self, screen: pygame.Surface, camera_x: int, camera_y: int, asset_manager):
        """Render boss with special effects."""
        if not self.is_alive():
            return
        
        screen_x = int(self.position[0] + camera_x)
        screen_y = int(self.position[1] + camera_y)
        
        # Draw boss with special glow effect
        color = self.color
        if self.enraged:
            # Add red glow when enraged
            glow_color = (255, 100, 100)
            pygame.draw.circle(screen, glow_color, (screen_x, screen_y), self.radius + 4, 2)
        
        # Draw boss circle
        pygame.draw.circle(screen, color, (screen_x, screen_y), self.radius)
        pygame.draw.circle(screen, self.outline_color, (screen_x, screen_y), self.radius, 2)
        
        # Draw crown symbol for boss
        crown_points = [
            (screen_x - 8, screen_y - self.radius - 5),
            (screen_x - 4, screen_y - self.radius - 10),
            (screen_x, screen_y - self.radius - 12),
            (screen_x + 4, screen_y - self.radius - 10),
            (screen_x + 8, screen_y - self.radius - 5)
        ]
        pygame.draw.polygon(screen, (255, 215, 0), crown_points)  # Gold crown
        
        # Draw health bar (larger for boss)
        if self.current_health < self.max_health:
            bar_width = 40
            bar_height = 6
            bar_x = screen_x - bar_width // 2
            bar_y = screen_y - self.radius - 20
            
            # Background
            pygame.draw.rect(screen, (100, 30, 30), (bar_x, bar_y, bar_width, bar_height))
            
            # Health fill
            health_percentage = self.current_health / self.max_health
            fill_width = int(bar_width * health_percentage)
            if fill_width > 0:
                health_color = (255, 100, 100) if self.enraged else (50, 200, 50)
                pygame.draw.rect(screen, health_color, (bar_x, bar_y, fill_width, bar_height))