"""
Floating damage numbers system for visual feedback.
Shows damage dealt/taken and healing received.
"""

import pygame
import random
from typing import List, Tuple

class DamageNumber:
    """Represents a floating damage/healing number."""
    
    def __init__(self, position: Tuple[float, float], value: int, number_type: str = "damage"):
        self.position = list(position)
        self.value = int(value)  # Ensure whole numbers only
        self.number_type = number_type  # "damage", "heal", "critical"
        
        # Visual properties
        if number_type == "heal":
            self.color = (100, 255, 100)  # Green for healing
        elif number_type == "critical":
            self.color = (255, 100, 100)  # Bright red for critical damage
        else:
            self.color = (255, 255, 100)  # Yellow for normal damage
            
        self.font_size = 16 if number_type != "critical" else 20
        self.lifetime = 2.0  # Duration in seconds
        self.max_lifetime = 2.0
        
        # Movement properties
        self.velocity = [
            random.uniform(-20, 20),  # Random horizontal drift
            random.uniform(-40, -60)  # Always float upward
        ]
        
        # Create font
        self.font = pygame.font.Font(None, self.font_size)
        
    def update(self, dt: float) -> bool:
        """Update the damage number. Returns False if it should be removed."""
        # Update position
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        
        # Slow down horizontal movement
        self.velocity[0] *= 0.95
        
        # Update lifetime
        self.lifetime -= dt
        
        return self.lifetime > 0
    
    def render(self, screen: pygame.Surface, camera_x: int, camera_y: int):
        """Render the damage number on screen."""
        # Calculate screen position
        screen_x = int(self.position[0] + camera_x)
        screen_y = int(self.position[1] + camera_y)
        
        # Calculate alpha based on lifetime
        alpha_factor = self.lifetime / self.max_lifetime
        alpha = int(255 * alpha_factor)
        
        # Create text surface
        text = self.font.render(f"{self.value}", True, self.color)
        
        # Apply alpha (fade out effect)
        if alpha < 255:
            text.set_alpha(alpha)
        
        # Calculate text position (centered)
        text_rect = text.get_rect()
        text_rect.center = (screen_x, screen_y)
        
        # Render text
        screen.blit(text, text_rect)

class DamageNumberManager:
    """Manages all floating damage numbers."""
    
    def __init__(self):
        self.damage_numbers: List[DamageNumber] = []
    
    def add_damage_number(self, position: Tuple[float, float], value: int, is_critical: bool = False):
        """Add a damage number."""
        number_type = "critical" if is_critical else "damage"
        damage_number = DamageNumber(position, value, number_type)
        self.damage_numbers.append(damage_number)
    
    def add_heal_number(self, position: Tuple[float, float], value: int):
        """Add a healing number."""
        damage_number = DamageNumber(position, value, "heal")
        self.damage_numbers.append(damage_number)
    
    def update(self, dt: float):
        """Update all damage numbers."""
        # Update existing numbers and remove expired ones
        self.damage_numbers = [
            number for number in self.damage_numbers 
            if number.update(dt)
        ]
    
    def render(self, screen: pygame.Surface, camera_x: int, camera_y: int):
        """Render all damage numbers."""
        for number in self.damage_numbers:
            number.render(screen, camera_x, camera_y)
    
    def clear(self):
        """Clear all damage numbers."""
        self.damage_numbers.clear()