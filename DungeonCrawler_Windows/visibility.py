"""
Line-of-sight and fog of war system.
Implements raycasting for visibility calculations and exploration tracking.
"""

import pygame
import math
from typing import Tuple, Set, List

class VisibilitySystem:
    """Handles line-of-sight calculations and fog of war."""
    
    def __init__(self, level):
        """Initialize the visibility system for a given level."""
        self.level = level
        self.sight_range = 200  # Maximum sight distance in pixels
        self.fov_angle = math.pi * 1.5  # Field of view in radians (270 degrees)
        
        # Fog of war tracking
        self.visible_tiles: Set[Tuple[int, int]] = set()
        self.explored_tiles: Set[Tuple[int, int]] = set()
        
        # Raycast precision
        self.ray_count = 360  # Number of rays to cast
        self.ray_step = 2  # Step size for raycast
    
    def update_visibility(self, player_position: Tuple[float, float]):
        """Update visibility based on player position."""
        self.visible_tiles.clear()
        
        # Cast rays in all directions
        angle_step = 2 * math.pi / self.ray_count
        
        for i in range(self.ray_count):
            angle = i * angle_step
            self.cast_ray(player_position, angle)
        
        # Add explored tiles
        self.explored_tiles.update(self.visible_tiles)
    
    def cast_ray(self, start_pos: Tuple[float, float], angle: float):
        """Cast a ray from start position at given angle and mark visible tiles."""
        x, y = start_pos
        dx = math.cos(angle) * self.ray_step
        dy = math.sin(angle) * self.ray_step
        
        current_distance = 0
        
        while current_distance < self.sight_range:
            # Current ray position
            ray_x = x + dx * (current_distance / self.ray_step)
            ray_y = y + dy * (current_distance / self.ray_step)
            
            # Convert to tile coordinates
            tile_x = int(ray_x // self.level.tile_size)
            tile_y = int(ray_y // self.level.tile_size)
            
            # Check bounds
            if (tile_x < 0 or tile_x >= self.level.width or 
                tile_y < 0 or tile_y >= self.level.height):
                break
            
            # Mark tile as visible
            self.visible_tiles.add((tile_x, tile_y))
            
            # Stop if we hit a wall
            if self.level.tiles[tile_y][tile_x].type == "wall":
                break
            
            current_distance += self.ray_step
    
    def is_visible(self, world_pos: Tuple[float, float]) -> bool:
        """Check if a world position is currently visible."""
        tile_x = int(world_pos[0] // self.level.tile_size)
        tile_y = int(world_pos[1] // self.level.tile_size)
        return (tile_x, tile_y) in self.visible_tiles
    
    def is_explored(self, world_pos: Tuple[float, float]) -> bool:
        """Check if a world position has been explored before."""
        tile_x = int(world_pos[0] // self.level.tile_size)
        tile_y = int(world_pos[1] // self.level.tile_size)
        return (tile_x, tile_y) in self.explored_tiles
    
    def has_line_of_sight(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> bool:
        """Check if there's a clear line of sight between two positions."""
        x1, y1 = pos1
        x2, y2 = pos2
        
        # Calculate distance
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # If too far, no line of sight
        if distance > self.sight_range:
            return False
        
        # Cast ray from pos1 to pos2
        steps = max(1, int(distance / self.ray_step))
        dx = (x2 - x1) / steps
        dy = (y2 - y1) / steps
        
        for step in range(steps):
            # Current position along the ray
            current_x = x1 + dx * step
            current_y = y1 + dy * step
            
            # Check if this position is in a wall
            if self.level.check_wall_collision((current_x, current_y), 1):
                return False
        
        return True
    
    def get_visible_area_bounds(self) -> Tuple[int, int, int, int]:
        """Get the bounds of the currently visible area."""
        if not self.visible_tiles:
            return (0, 0, 0, 0)
        
        min_x = min(tile[0] for tile in self.visible_tiles)
        max_x = max(tile[0] for tile in self.visible_tiles)
        min_y = min(tile[1] for tile in self.visible_tiles)
        max_y = max(tile[1] for tile in self.visible_tiles)
        
        return (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    
    def render_fog_overlay(self, screen: pygame.Surface, camera_x: int, camera_y: int):
        """Render fog of war overlay (optional, for debugging)."""
        # Create a surface for the fog overlay
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        
        # Cut out visible areas
        for tile_x, tile_y in self.visible_tiles:
            world_x = tile_x * self.level.tile_size
            world_y = tile_y * self.level.tile_size
            screen_x = world_x + camera_x
            screen_y = world_y + camera_y
            
            # Draw transparent rectangle to "cut out" the fog
            pygame.draw.rect(overlay, (0, 0, 0, 0), 
                           (screen_x, screen_y, self.level.tile_size, self.level.tile_size))
        
        # Blit the overlay
        screen.blit(overlay, (0, 0))
    
    def get_visibility_info(self) -> dict:
        """Get debug information about the visibility system."""
        return {
            "visible_tiles": len(self.visible_tiles),
            "explored_tiles": len(self.explored_tiles),
            "sight_range": self.sight_range,
            "ray_count": self.ray_count
        }
