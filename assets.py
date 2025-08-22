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
        
        # Generate boss sprites
        self.generate_boss_sprites()
        
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
        
        # Item sprites
        self.generate_item_sprites()
    
    def generate_boss_sprites(self):
        """Generate boss sprites for different types."""
        # Boss sprites (larger and more detailed)
        self.sprites["boss_flame"] = self.create_boss_sprite(50, "flame")
        self.sprites["boss_ice"] = self.create_boss_sprite(50, "ice")
        self.sprites["boss_lightning"] = self.create_boss_sprite(50, "lightning")
        self.sprites["boss_shadow"] = self.create_boss_sprite(50, "shadow")
    
    def create_boss_sprite(self, size: int, boss_type: str) -> pygame.Surface:
        """Create detailed boss sprites."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        if boss_type == "flame":
            # Flame berserker (red/orange with fire effects)
            # Main body (dark red)
            pygame.draw.circle(surface, (150, 50, 30), (center, center), center - 2)
            
            # Flame crown/spikes
            for i in range(8):
                angle = i * 45  # 360/8 = 45 degrees
                flame_x = center + int((center - 5) * math.cos(math.radians(angle)))
                flame_y = center + int((center - 5) * math.sin(math.radians(angle)))
                
                flame_points = [
                    (flame_x, flame_y),
                    (flame_x - 3, flame_y + 8),
                    (flame_x + 3, flame_y + 8)
                ]
                pygame.draw.polygon(surface, (255, 100, 0), flame_points)
            
            # Glowing core
            pygame.draw.circle(surface, (255, 150, 50), (center, center), center//2)
            pygame.draw.circle(surface, (255, 200, 100), (center, center), center//3)
            
        elif boss_type == "ice":
            # Ice mage (blue/white with crystals)
            # Main body (icy blue)
            pygame.draw.circle(surface, (100, 150, 200), (center, center), center - 2)
            
            # Ice crystal formations
            for i in range(6):
                angle = i * 60  # 360/6 = 60 degrees
                crystal_x = center + int((center - 8) * math.cos(math.radians(angle)))
                crystal_y = center + int((center - 8) * math.sin(math.radians(angle)))
                
                crystal_points = [
                    (crystal_x, crystal_y - 6),
                    (crystal_x - 3, crystal_y + 3),
                    (crystal_x + 3, crystal_y + 3)
                ]
                pygame.draw.polygon(surface, (200, 230, 255), crystal_points)
            
            # Frozen core
            pygame.draw.circle(surface, (150, 200, 255), (center, center), center//2)
            pygame.draw.circle(surface, (200, 230, 255), (center, center), center//3)
            
        elif boss_type == "lightning":
            # Lightning striker (yellow/white with electric effects)
            # Main body (electric yellow)
            pygame.draw.circle(surface, (200, 200, 50), (center, center), center - 2)
            
            # Lightning bolts radiating outward
            for i in range(4):
                angle = i * 90  # 360/4 = 90 degrees
                bolt_start_x = center + int((center//2) * math.cos(math.radians(angle)))
                bolt_start_y = center + int((center//2) * math.sin(math.radians(angle)))
                bolt_end_x = center + int((center - 3) * math.cos(math.radians(angle)))
                bolt_end_y = center + int((center - 3) * math.sin(math.radians(angle)))
                
                # Jagged lightning effect
                points = [
                    (bolt_start_x, bolt_start_y),
                    (bolt_start_x + 2, bolt_start_y + 4),
                    (bolt_end_x - 2, bolt_end_y - 4),
                    (bolt_end_x, bolt_end_y)
                ]
                pygame.draw.lines(surface, (255, 255, 200), False, points, 3)
            
            # Electric core
            pygame.draw.circle(surface, (255, 255, 150), (center, center), center//2)
            pygame.draw.circle(surface, (255, 255, 200), (center, center), center//3)
            
        elif boss_type == "shadow":
            # Shadow lord (very dark with purple edges)
            # Main body (almost black)
            pygame.draw.circle(surface, (20, 10, 30), (center, center), center - 2)
            
            # Shadow tendrils
            for i in range(12):
                angle = i * 30  # 360/12 = 30 degrees
                tendril_length = center - 5 + (i % 3) * 2
                tendril_x = center + int(tendril_length * math.cos(math.radians(angle)))
                tendril_y = center + int(tendril_length * math.sin(math.radians(angle)))
                
                pygame.draw.line(surface, (60, 30, 80), 
                               (center, center), (tendril_x, tendril_y), 2)
            
            # Dark core with purple glow
            pygame.draw.circle(surface, (40, 20, 60), (center, center), center//2)
            pygame.draw.circle(surface, (80, 40, 100), (center, center), center//3)
            
        # Boss outline (golden for all bosses)
        pygame.draw.circle(surface, (255, 215, 0), (center, center), center - 2, 3)
        
        return surface
    
    def create_player_sprite(self, size: int) -> pygame.Surface:
        """Create a detailed player sprite resembling a knight."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        # Body (blue armor)
        pygame.draw.circle(surface, (70, 130, 200), (center, center), center - 3)
        
        # Armor segments (darker blue lines)
        pygame.draw.circle(surface, (50, 100, 160), (center, center), center - 3, 2)
        pygame.draw.line(surface, (50, 100, 160), 
                        (center - center//2, center), (center + center//2, center), 2)
        
        # Helmet (silver/gray)
        helmet_size = center - 6
        pygame.draw.circle(surface, (180, 180, 200), (center, center - 3), helmet_size)
        
        # Helmet visor (horizontal slit)
        visor_y = center - 5
        pygame.draw.line(surface, (30, 30, 30), 
                        (center - helmet_size//2, visor_y), 
                        (center + helmet_size//2, visor_y), 3)
        
        # Glowing eyes through visor
        eye_glow = max(1, size // 12)
        pygame.draw.circle(surface, (100, 200, 255), 
                         (center - helmet_size//3, visor_y), eye_glow)
        pygame.draw.circle(surface, (100, 200, 255), 
                         (center + helmet_size//3, visor_y), eye_glow)
        
        # Cape/cloak behind (dark red)
        cape_points = [
            (center - center//3, center + center//2),
            (center - center//2, center + center - 2),
            (center + center//2, center + center - 2),
            (center + center//3, center + center//2)
        ]
        pygame.draw.polygon(surface, (120, 40, 40), cape_points)
        
        # Armor outline (bright silver)
        pygame.draw.circle(surface, (220, 220, 240), (center, center), center - 3, 2)
        
        return surface
    
    def create_enemy_sprite(self, size: int, enemy_type: str) -> pygame.Surface:
        """Create detailed enemy sprites based on type."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        if enemy_type == "basic":
            # Skeleton warrior (bone white with red eyes)
            # Body/ribcage
            pygame.draw.circle(surface, (230, 230, 220), (center, center), center - 2)
            
            # Ribcage lines
            for i in range(3):
                y = center - 4 + i * 3
                pygame.draw.line(surface, (200, 200, 190), 
                               (center - center//2, y), (center + center//2, y), 1)
            
            # Skull
            pygame.draw.circle(surface, (240, 240, 230), (center, center - 3), center//2)
            
            # Glowing red eye sockets
            eye_size = max(2, size // 12)
            pygame.draw.circle(surface, (255, 50, 50), 
                             (center - center//4, center - 4), eye_size)
            pygame.draw.circle(surface, (255, 50, 50), 
                             (center + center//4, center - 4), eye_size)
            
            # Dark outline
            pygame.draw.circle(surface, (100, 100, 90), (center, center), center - 2, 1)
        
        elif enemy_type == "fast":
            # Shadow assassin (dark with glowing edges)
            # Main body (very dark purple)
            pygame.draw.circle(surface, (40, 20, 60), (center, center), center - 1)
            
            # Glowing purple outline
            pygame.draw.circle(surface, (120, 80, 180), (center, center), center - 1, 2)
            
            # Speed trail effect
            for i in range(3):
                trail_x = center - (i + 1) * 2
                trail_alpha = 255 - i * 60
                trail_surface = pygame.Surface((size//3, size), pygame.SRCALPHA)
                pygame.draw.ellipse(trail_surface, (120, 80, 180, trail_alpha), 
                                  (0, 0, size//3, size))
                surface.blit(trail_surface, (trail_x, 0))
            
            # Glowing eyes
            pygame.draw.circle(surface, (200, 150, 255), 
                             (center - center//4, center - center//3), 2)
            pygame.draw.circle(surface, (200, 150, 255), 
                             (center + center//4, center - center//3), 2)
        
        elif enemy_type == "heavy":
            # Armored orc (gray/green armor)
            # Main body (dark green)
            pygame.draw.circle(surface, (80, 120, 80), (center, center), center - 1)
            
            # Armor plates (overlapping gray rectangles)
            plate_width = size // 3
            for i in range(3):
                y_offset = center - 6 + i * 4
                pygame.draw.rect(surface, (160, 160, 160), 
                               (center - plate_width//2, y_offset, plate_width, 3))
            
            # Heavy helmet spikes
            spike_points = [
                (center, center - center + 2),
                (center - 3, center - center//2),
                (center + 3, center - center//2)
            ]
            pygame.draw.polygon(surface, (100, 100, 100), spike_points)
            
            # Red eyes through helmet
            pygame.draw.circle(surface, (255, 100, 100), 
                             (center - center//4, center - center//3), 2)
            pygame.draw.circle(surface, (255, 100, 100), 
                             (center + center//4, center - center//3), 2)
            
            # Thick armor outline
            pygame.draw.circle(surface, (120, 120, 120), (center, center), center - 1, 2)
        
        elif enemy_type == "ranged":
            # Dark archer/mage (purple robes)
            # Main body (dark purple robe)
            pygame.draw.circle(surface, (60, 40, 80), (center, center), center - 1)
            
            # Hood
            hood_points = [
                (center - center//2, center - center//2),
                (center, center - center + 1),
                (center + center//2, center - center//2),
                (center, center)
            ]
            pygame.draw.polygon(surface, (40, 20, 60), hood_points)
            
            # Magical orb/focus (glowing blue)
            orb_size = max(3, size // 8)
            pygame.draw.circle(surface, (100, 150, 255), 
                             (center, center + center//3), orb_size)
            pygame.draw.circle(surface, (150, 200, 255), 
                             (center, center + center//3), orb_size - 1)
            
            # Glowing eyes under hood
            pygame.draw.circle(surface, (150, 100, 255), 
                             (center - center//4, center - center//4), 1)
            pygame.draw.circle(surface, (150, 100, 255), 
                             (center + center//4, center - center//4), 1)
            
            # Dark robe outline
            pygame.draw.circle(surface, (80, 60, 100), (center, center), center - 1, 1)
        
        
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
    
    def generate_item_sprites(self):
        """Generate sprites for all item types."""
        # Melee weapons
        self.sprites["item_sword"] = self.create_item_sprite(24, "sword", (200, 200, 255))
        self.sprites["item_spear"] = self.create_item_sprite(24, "spear", (160, 82, 45))
        self.sprites["item_mace"] = self.create_item_sprite(24, "mace", (128, 128, 128))
        self.sprites["item_war_axe"] = self.create_item_sprite(24, "war_axe", (180, 50, 50))
        
        # Enchantments  
        self.sprites["item_red_enchantment"] = self.create_item_sprite(24, "diamond", (255, 100, 100))
        self.sprites["item_yellow_enchantment"] = self.create_item_sprite(24, "diamond", (255, 255, 100))
        self.sprites["item_green_enchantment"] = self.create_item_sprite(24, "diamond", (100, 255, 100))
        self.sprites["item_black_enchantment"] = self.create_item_sprite(24, "diamond", (150, 150, 150))
        
        # Spells
        self.sprites["item_haste_spell"] = self.create_item_sprite(24, "star", (100, 255, 255))
        self.sprites["item_power_pulse"] = self.create_item_sprite(24, "star", (255, 100, 255))
        self.sprites["item_turn_coat"] = self.create_item_sprite(24, "star", (255, 165, 0))
        self.sprites["item_void_blast"] = self.create_item_sprite(24, "void_star", (150, 50, 200))
        self.sprites["item_heal_burst"] = self.create_item_sprite(24, "healing_star", (255, 255, 255))
        
        # Health packs
        self.sprites["health_pack"] = self.create_item_sprite(20, "health_cross", (50, 200, 50))
    
    def create_item_sprite(self, size: int, shape: str, color: Tuple[int, int, int]) -> pygame.Surface:
        """Create an item sprite based on shape and color."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        if shape == "sword":
            # Sword shape
            blade_points = [
                (center, 2),
                (center - 3, center + 4),
                (center + 3, center + 4)
            ]
            pygame.draw.polygon(surface, color, blade_points)
            # Handle
            pygame.draw.rect(surface, (139, 69, 19), (center - 2, center + 4, 4, 8))
            # Guard
            pygame.draw.rect(surface, (192, 192, 192), (center - 6, center + 3, 12, 2))
            
        elif shape == "spear":
            # Spear shape - vertical line with point
            pygame.draw.line(surface, (139, 69, 19), (center, center + 8), (center, size - 2), 3)
            spear_points = [
                (center, 2),
                (center - 2, center),
                (center + 2, center)
            ]
            pygame.draw.polygon(surface, color, spear_points)
            
        elif shape == "mace":
            # Mace shape - handle with heavy head
            pygame.draw.line(surface, (139, 69, 19), (center, center + 2), (center, size - 2), 2)
            pygame.draw.circle(surface, color, (center, center - 3), 7)
            # Spikes
            for angle in range(0, 360, 45):
                x = center + 5 * math.cos(math.radians(angle))
                y = center - 3 + 5 * math.sin(math.radians(angle))
                pygame.draw.circle(surface, (200, 200, 200), (int(x), int(y)), 2)
                
        elif shape == "war_axe":
            # War axe shape - handle with curved blade
            pygame.draw.line(surface, (139, 69, 19), (center, center + 6), (center, size - 2), 3)
            # Axe head (asymmetric blade)
            blade_points = [
                (center, center - 4),
                (center - 8, center + 2),
                (center - 6, center + 6),
                (center + 6, center + 6),
                (center + 8, center + 2)
            ]
            pygame.draw.polygon(surface, color, blade_points)
            pygame.draw.polygon(surface, (150, 30, 30), blade_points, 2)
            
        elif shape == "void_star":
            # Dark void star with swirling effect
            points = []
            for i in range(10):
                angle = i * math.pi / 5
                if i % 2 == 0:
                    radius = center - 2
                else:
                    radius = (center - 2) // 3
                x = center + radius * math.cos(angle - math.pi/2)
                y = center + radius * math.sin(angle - math.pi/2)
                points.append((x, y))
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (100, 30, 150), points, 2)
            # Dark center
            pygame.draw.circle(surface, (50, 20, 80), (center, center), 4)
            
        elif shape == "healing_star":
            # Bright healing star with cross
            points = []
            for i in range(8):
                angle = i * math.pi / 4
                radius = center - 3 if i % 2 == 0 else (center - 3) // 2
                x = center + radius * math.cos(angle)
                y = center + radius * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (200, 200, 100), points, 1)
            # Healing cross in center
            pygame.draw.line(surface, (255, 255, 100), (center - 4, center), (center + 4, center), 2)
            pygame.draw.line(surface, (255, 255, 100), (center, center - 4), (center, center + 4), 2)
            
        elif shape == "health_cross":
            # Medical cross shape for health packs
            # Horizontal bar
            pygame.draw.rect(surface, color, (center - 8, center - 3, 16, 6))
            # Vertical bar
            pygame.draw.rect(surface, color, (center - 3, center - 8, 6, 16))
            # White outline
            pygame.draw.rect(surface, (255, 255, 255), (center - 8, center - 3, 16, 6), 1)
            pygame.draw.rect(surface, (255, 255, 255), (center - 3, center - 8, 6, 16), 1)
                
        elif shape == "diamond":
            # Diamond shape for enchantments
            diamond_points = [
                (center, 2),
                (center + center - 4, center),
                (center, size - 2),
                (4, center)
            ]
            pygame.draw.polygon(surface, color, diamond_points)
            pygame.draw.polygon(surface, (255, 255, 255), diamond_points, 2)
            
        elif shape == "star":
            # Star shape for spells
            points = []
            for i in range(10):
                angle = i * math.pi / 5
                if i % 2 == 0:
                    radius = center - 3
                else:
                    radius = (center - 3) // 2
                x = center + radius * math.cos(angle - math.pi/2)
                y = center + radius * math.sin(angle - math.pi/2)
                points.append((x, y))
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (255, 255, 255), points, 1)
            
        else:
            # Default square shape
            rect = pygame.Rect(4, 4, size - 8, size - 8)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2)
        
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
