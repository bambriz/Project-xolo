"""
Asset management and sprite generation.
Handles creation of simple textures and visual elements for the game.
"""

import pygame
import math
from typing import Dict, Tuple

class AssetManager:
    """Manages game assets including generated sprites and textures."""
    
    def __init__(self):
        """Initialize the asset manager."""
        self.sprites: Dict[str, pygame.Surface] = {}
        self.colors: Dict[str, Tuple[int, int, int]] = {
            "player": (100, 150, 255),
            "enemy_basic": (200, 100, 100),
            "enemy_fast": (100, 200, 100),
            "enemy_heavy": (150, 150, 150),
            "enemy_ranged": (200, 200, 100),
            "projectile": (255, 255, 100),
            "wall": (60, 60, 60),
            "floor": (40, 40, 40),
            "health": (50, 200, 50),
            "damage": (200, 50, 50),
            "xp": (255, 215, 0)
        }
        
        # Initialize font
        pygame.font.init()
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 48)
        
        # Generate all sprites
        self.generate_sprites()
        
        print("Asset manager initialized with generated sprites")
    
    def generate_sprites(self):
        """Generate all sprite textures."""
        # Player sprite
        self.sprites["player"] = self.create_player_sprite(30)
        
        # Enemy sprites
        self.sprites["enemy_basic"] = self.create_enemy_sprite(24, "basic")
        self.sprites["enemy_fast"] = self.create_enemy_sprite(20, "fast")
        self.sprites["enemy_heavy"] = self.create_enemy_sprite(32, "heavy")
        self.sprites["enemy_ranged"] = self.create_enemy_sprite(24, "ranged")
        
        # Projectile sprite
        self.sprites["projectile"] = self.create_projectile_sprite(6)
        
        # UI elements
        self.sprites["health_icon"] = self.create_icon_sprite(16, "health")
        self.sprites["xp_icon"] = self.create_icon_sprite(16, "xp")
    
    def create_player_sprite(self, size: int) -> pygame.Surface:
        """Create a player sprite."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        # Main circle
        pygame.draw.circle(surface, self.colors["player"], (center, center), center - 2)
        
        # White outline
        pygame.draw.circle(surface, (255, 255, 255), (center, center), center - 2, 2)
        
        # Eyes
        eye_size = max(2, size // 8)
        eye_offset = size // 4
        pygame.draw.circle(surface, (255, 255, 255), 
                         (center - eye_offset, center - eye_offset), eye_size)
        pygame.draw.circle(surface, (255, 255, 255), 
                         (center + eye_offset, center - eye_offset), eye_size)
        
        # Pupils
        pupil_size = max(1, eye_size // 2)
        pygame.draw.circle(surface, (0, 0, 0), 
                         (center - eye_offset, center - eye_offset), pupil_size)
        pygame.draw.circle(surface, (0, 0, 0), 
                         (center + eye_offset, center - eye_offset), pupil_size)
        
        return surface
    
    def create_enemy_sprite(self, size: int, enemy_type: str) -> pygame.Surface:
        """Create an enemy sprite based on type."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        color = self.colors.get(f"enemy_{enemy_type}", (200, 100, 100))
        
        # Main circle
        pygame.draw.circle(surface, color, (center, center), center - 1)
        
        # White outline
        pygame.draw.circle(surface, (255, 255, 255), (center, center), center - 1, 1)
        
        # Type-specific features
        if enemy_type == "basic":
            # Simple angry eyes
            eye_size = max(1, size // 10)
            pygame.draw.circle(surface, (255, 0, 0), 
                             (center - size // 4, center - size // 4), eye_size)
            pygame.draw.circle(surface, (255, 0, 0), 
                             (center + size // 4, center - size // 4), eye_size)
        
        elif enemy_type == "fast":
            # Lightning bolt pattern
            points = [
                (center - size // 4, center - size // 3),
                (center, center - size // 6),
                (center - size // 6, center),
                (center + size // 4, center + size // 3),
                (center, center + size // 6),
                (center + size // 6, center)
            ]
            pygame.draw.polygon(surface, (255, 255, 255), points)
        
        elif enemy_type == "heavy":
            # Armor-like segments
            for i in range(3):
                radius = center - 2 - i * 3
                if radius > 0:
                    pygame.draw.circle(surface, (200, 200, 200), (center, center), radius, 1)
        
        elif enemy_type == "ranged":
            # Crosshair
            line_length = size // 3
            pygame.draw.line(surface, (255, 255, 255), 
                           (center - line_length, center), 
                           (center + line_length, center), 2)
            pygame.draw.line(surface, (255, 255, 255), 
                           (center, center - line_length), 
                           (center, center + line_length), 2)
        
        return surface
    
    def create_projectile_sprite(self, size: int) -> pygame.Surface:
        """Create a projectile sprite."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        # Glowing orb effect
        for i in range(3):
            alpha = 255 - i * 60
            radius = center - i
            if radius > 0:
                color_with_alpha = (*self.colors["projectile"], alpha)
                # Create a temporary surface for alpha blending
                temp_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, color_with_alpha, (center, center), radius)
                surface.blit(temp_surface, (0, 0))
        
        return surface
    
    def create_icon_sprite(self, size: int, icon_type: str) -> pygame.Surface:
        """Create UI icon sprites."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        if icon_type == "health":
            # Heart shape (simplified)
            color = self.colors["health"]
            
            # Draw heart using circles and a triangle
            pygame.draw.circle(surface, color, (center - size // 4, center - size // 6), size // 4)
            pygame.draw.circle(surface, color, (center + size // 4, center - size // 6), size // 4)
            
            # Triangle for bottom of heart
            points = [
                (center - size // 2 + 2, center),
                (center + size // 2 - 2, center),
                (center, center + size // 2 - 2)
            ]
            pygame.draw.polygon(surface, color, points)
        
        elif icon_type == "xp":
            # Star shape
            color = self.colors["xp"]
            
            # Draw star using lines
            angles = [i * 2 * math.pi / 5 for i in range(5)]
            outer_points = []
            inner_points = []
            
            outer_radius = center - 2
            inner_radius = (center - 2) // 2
            
            for angle in angles:
                outer_x = center + math.cos(angle) * outer_radius
                outer_y = center + math.sin(angle) * outer_radius
                outer_points.append((outer_x, outer_y))
                
                inner_angle = angle + math.pi / 5
                inner_x = center + math.cos(inner_angle) * inner_radius
                inner_y = center + math.sin(inner_angle) * inner_radius
                inner_points.append((inner_x, inner_y))
            
            # Combine points to create star
            star_points = []
            for i in range(5):
                star_points.append(outer_points[i])
                star_points.append(inner_points[i])
            
            pygame.draw.polygon(surface, color, star_points)
        
        return surface
    
    def get_sprite(self, sprite_name: str) -> pygame.Surface:
        """Get a sprite by name."""
        sprite = self.sprites.get(sprite_name)
        if sprite is None:
            # Return a default empty surface if sprite not found
            return pygame.Surface((16, 16), pygame.SRCALPHA)
        return sprite
    
    def get_color(self, color_name: str) -> Tuple[int, int, int]:
        """Get a color by name."""
        return self.colors.get(color_name, (255, 255, 255))
    
    def render_text(self, text: str, size: str = "medium", color: Tuple[int, int, int] = (255, 255, 255)) -> pygame.Surface:
        """Render text with the specified size and color."""
        font_map = {
            "small": self.font_small,
            "medium": self.font_medium,
            "large": self.font_large
        }
        
        font = font_map.get(size, self.font_medium)
        return font.render(text, True, color)
    
    def create_progress_bar(self, width: int, height: int, progress: float, 
                           bg_color: Tuple[int, int, int], 
                           fill_color: Tuple[int, int, int]) -> pygame.Surface:
        """Create a progress bar surface."""
        surface = pygame.Surface((width, height))
        
        # Background
        surface.fill(bg_color)
        
        # Fill
        fill_width = int(width * max(0, min(1, progress)))
        if fill_width > 0:
            pygame.draw.rect(surface, fill_color, (0, 0, fill_width, height))
        
        # Border
        pygame.draw.rect(surface, (255, 255, 255), (0, 0, width, height), 1)
        
        return surface
