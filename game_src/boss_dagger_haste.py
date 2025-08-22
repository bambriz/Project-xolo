"""
Boss with dagger and haste ability.
Enhanced boss enemy with speed boost capabilities.
"""

import pygame
import math
import random
from typing import Tuple, Optional
from .boss import Boss

class DaggerHasteBoss(Boss):
    """Boss enemy that uses daggers and has haste ability."""
    
    def __init__(self, position: Tuple[float, float], player_level: int = 1):
        """Initialize dagger haste boss."""
        super().__init__(position, player_level)
        
        # Override boss type for dagger setup
        self.boss_type = "shadow_lord"  # Use existing boss type as base
        
        # Haste ability properties
        self.haste_active = False
        self.haste_duration = 5.0  # 5 seconds of haste
        self.haste_cooldown = 15.0  # 15 second cooldown
        self.last_haste_time = 0.0
        self.original_speed = self.speed
        self.original_attack_cooldown = self.attack_cooldown
        
        # Dagger properties
        self.weapon_type = "dagger"
        self.weapon_range = 45
        self.weapon_arc = 165  # Wide dagger arc
        self.attack_speed_multiplier = 2.0  # Fast dagger attacks
        
        # Enhanced stats for boss
        self.max_health = int(self.max_health * 1.3)  # 30% more health
        self.current_health = self.max_health
        self.damage = int(self.damage * 1.1)  # 10% more damage
        
        print(f"Created Dagger Haste Boss with {self.current_health} HP")
    
    def update(self, dt: float, player, level, can_see_player: bool):
        """Update boss with haste ability management."""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Check if haste should end
        if self.haste_active and current_time - self.last_haste_time >= self.haste_duration:
            self.end_haste()
        
        # Try to activate haste if available
        if (not self.haste_active and 
            current_time - self.last_haste_time >= self.haste_cooldown and
            can_see_player):
            
            # Activate haste when player is within range
            dx = player.position[0] - self.position[0]
            dy = player.position[1] - self.position[1] 
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance <= self.weapon_range * 2:  # Activate when getting close
                self.activate_haste(current_time)
        
        # Update base boss behavior
        super().update(dt, player, level, can_see_player)
    
    def activate_haste(self, current_time: float):
        """Activate haste ability."""
        self.haste_active = True
        self.last_haste_time = current_time
        
        # Boost speed and attack speed
        self.speed = self.original_speed * 2.0  # 2x speed
        self.attack_cooldown = self.original_attack_cooldown * 0.5  # 2x attack speed
        
        print(f"Dagger Boss activated HASTE! Speed and attack doubled for {self.haste_duration}s")
    
    def end_haste(self):
        """End haste ability."""
        self.haste_active = False
        
        # Restore original stats
        self.speed = self.original_speed
        self.attack_cooldown = self.original_attack_cooldown
        
        print("Dagger Boss haste ended")
    
    def render(self, screen: pygame.Surface, camera_x: int, camera_y: int, asset_manager):
        """Render boss with haste visual effects."""
        # Calculate screen position
        screen_x = int(self.position[0] + camera_x)
        screen_y = int(self.position[1] + camera_y)
        
        # Add haste visual effects
        if self.haste_active:
            # Speed trail effect
            if hasattr(self, 'velocity'):
                vel_magnitude = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
                if vel_magnitude > 50:
                    # Draw speed lines behind boss
                    for i in range(4):
                        trail_x = screen_x - (self.velocity[0] / vel_magnitude) * (15 + i * 10)
                        trail_y = screen_y - (self.velocity[1] / vel_magnitude) * (15 + i * 10)
                        alpha = 200 - (i * 50)
                        trail_color = (255, 200, 100)  # Orange trail
                        trail_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
                        pygame.draw.circle(trail_surface, (*trail_color, alpha), (4, 4), 4 - i)
                        screen.blit(trail_surface, (trail_x - 4, trail_y - 4))
            
            # Haste glow effect
            glow_radius = self.radius + 6
            glow_color = (255, 200, 100)  # Orange glow
            pygame.draw.circle(screen, glow_color, (screen_x, screen_y), glow_radius, 3)
            
            # Pulsing inner glow
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 0.5 + 0.5
            inner_glow = (int(255 * pulse), int(200 * pulse), int(100 * pulse))
            pygame.draw.circle(screen, inner_glow, (screen_x, screen_y), self.radius + 2, 1)
        
        # Render base boss
        super().render(screen, camera_x, camera_y, asset_manager)
        
        # Add dagger visual indicator
        if not self.haste_active:  # Only show weapon when not hasted (for clarity)
            # Draw twin daggers
            for angle_offset in [-0.3, 0.3]:
                dagger_angle = math.atan2(
                    screen_y - (screen_y - 20), 
                    screen_x - (screen_x + 15)
                ) + angle_offset
                
                dagger_x = screen_x + math.cos(dagger_angle) * (self.radius + 8)
                dagger_y = screen_y + math.sin(dagger_angle) * (self.radius + 8)
                dagger_tip_x = dagger_x + math.cos(dagger_angle) * 12
                dagger_tip_y = dagger_y + math.sin(dagger_angle) * 12
                
                # Draw dagger blade
                pygame.draw.line(screen, (200, 200, 220), 
                               (int(dagger_x), int(dagger_y)), 
                               (int(dagger_tip_x), int(dagger_tip_y)), 2)
        
        # Show haste cooldown indicator
        if not self.haste_active:
            current_time = pygame.time.get_ticks() / 1000.0
            cooldown_remaining = self.haste_cooldown - (current_time - self.last_haste_time)
            
            if cooldown_remaining > 0:
                # Show cooldown bar above boss
                bar_width = 40
                bar_height = 4
                bar_x = screen_x - bar_width // 2
                bar_y = screen_y - self.radius - 25
                
                # Background
                pygame.draw.rect(screen, (100, 100, 100), 
                               (bar_x, bar_y, bar_width, bar_height))
                
                # Progress
                progress = 1.0 - (cooldown_remaining / self.haste_cooldown)
                pygame.draw.rect(screen, (255, 200, 100), 
                               (bar_x, bar_y, int(bar_width * progress), bar_height))
    
    def get_boss_name(self) -> str:
        """Return boss name."""
        return "Shadow Assassin"
    
    def get_special_ability_name(self) -> str:
        """Return special ability name."""
        return "Dagger Haste"