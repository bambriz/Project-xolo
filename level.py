"""
Level generation and dungeon layout management.
Handles wall placement, enemy spawning, and collision detection.
"""

import pygame
import random
import math
from typing import Tuple, List, Set
from enemy import create_enemy

class Tile:
    """Represents a single tile in the dungeon."""
    
    def __init__(self, x: int, y: int, tile_type: str = "wall"):
        self.x = x
        self.y = y
        self.type = tile_type  # "wall", "floor", "door"
        self.color = self.get_color()
    
    def get_color(self) -> Tuple[int, int, int]:
        """Get the color for this tile type."""
        colors = {
            "wall": (60, 60, 60),
            "floor": (40, 40, 40),
            "door": (80, 60, 40)
        }
        return colors.get(self.type, (60, 60, 60))

class Level:
    """Manages the dungeon level, including layout and enemies."""
    
    def __init__(self, width: int, height: int, player_level: int = 1):
        """Initialize a new dungeon level."""
        self.width = width
        self.height = height
        self.tile_size = 32
        self.player_level = player_level
        
        # Create the tile grid
        self.tiles: List[List[Tile]] = []
        self.spawn_position = (0, 0)
        
        # Enemy management
        self.enemies = []
        self.max_enemies = 8 + player_level * 2
        
        # Generate the level
        self.generate_level()
        self.spawn_enemies()
        
        print(f"Generated level {width}x{height} for player level {player_level}")
        print(f"Spawned {len(self.enemies)} enemies")
    
    def generate_level(self):
        """Generate a random dungeon layout."""
        # Initialize with all walls
        self.tiles = [[Tile(x, y, "wall") for x in range(self.width)] 
                     for y in range(self.height)]
        
        # Generate rooms using a simple algorithm
        rooms = self.generate_rooms()
        
        # Connect rooms with corridors
        self.connect_rooms(rooms)
        
        # Set spawn position in the first room
        if rooms:
            room = rooms[0]
            self.spawn_position = (
                (room[0] + room[2] // 2) * self.tile_size,
                (room[1] + room[3] // 2) * self.tile_size
            )
        else:
            # Fallback spawn position
            self.spawn_position = (self.tile_size * 2, self.tile_size * 2)
    
    def generate_rooms(self) -> List[Tuple[int, int, int, int]]:
        """Generate random rooms. Returns list of (x, y, width, height) tuples."""
        rooms = []
        attempts = 100
        min_room_size = min(4, max(2, self.width // 4))
        max_room_size = min(12, max(min_room_size + 1, self.width // 3, self.height // 3))
        
        for _ in range(attempts):
            # Random room size and position
            room_width = random.randint(min_room_size, max_room_size)
            room_height = random.randint(min_room_size, max_room_size)
            
            # Ensure room fits within level bounds
            max_x = max(1, self.width - room_width - 1)
            max_y = max(1, self.height - room_height - 1)
            
            if max_x < 1 or max_y < 1:
                continue  # Skip if level too small for this room
                
            room_x = random.randint(1, max_x)
            room_y = random.randint(1, max_y)
            
            # Check if room overlaps with existing rooms
            new_room = (room_x, room_y, room_width, room_height)
            if not self.room_overlaps(new_room, rooms):
                rooms.append(new_room)
                self.carve_room(room_x, room_y, room_width, room_height)
                
                # Stop when we have enough rooms
                if len(rooms) >= 8:
                    break
        
        return rooms
    
    def room_overlaps(self, new_room: Tuple[int, int, int, int], 
                     existing_rooms: List[Tuple[int, int, int, int]]) -> bool:
        """Check if a new room overlaps with existing rooms."""
        x1, y1, w1, h1 = new_room
        
        for x2, y2, w2, h2 in existing_rooms:
            # Add padding between rooms
            if (x1 < x2 + w2 + 1 and x1 + w1 + 1 > x2 and
                y1 < y2 + h2 + 1 and y1 + h1 + 1 > y2):
                return True
        
        return False
    
    def carve_room(self, x: int, y: int, width: int, height: int):
        """Carve out a room (make tiles into floor)."""
        for room_y in range(y, y + height):
            for room_x in range(x, x + width):
                if 0 <= room_x < self.width and 0 <= room_y < self.height:
                    self.tiles[room_y][room_x] = Tile(room_x, room_y, "floor")
    
    def connect_rooms(self, rooms: List[Tuple[int, int, int, int]]):
        """Connect rooms with corridors."""
        for i in range(len(rooms) - 1):
            room1 = rooms[i]
            room2 = rooms[i + 1]
            
            # Get room centers
            x1 = room1[0] + room1[2] // 2
            y1 = room1[1] + room1[3] // 2
            x2 = room2[0] + room2[2] // 2
            y2 = room2[1] + room2[3] // 2
            
            # Create L-shaped corridor
            if random.choice([True, False]):
                # Horizontal first, then vertical
                self.carve_corridor(x1, y1, x2, y1)
                self.carve_corridor(x2, y1, x2, y2)
            else:
                # Vertical first, then horizontal
                self.carve_corridor(x1, y1, x1, y2)
                self.carve_corridor(x1, y2, x2, y2)
    
    def carve_corridor(self, x1: int, y1: int, x2: int, y2: int):
        """Carve a corridor between two points."""
        if x1 == x2:  # Vertical corridor
            start_y, end_y = min(y1, y2), max(y1, y2)
            for y in range(start_y, end_y + 1):
                if 0 <= x1 < self.width and 0 <= y < self.height:
                    self.tiles[y][x1] = Tile(x1, y, "floor")
        else:  # Horizontal corridor
            start_x, end_x = min(x1, x2), max(x1, x2)
            for x in range(start_x, end_x + 1):
                if 0 <= x < self.width and 0 <= y1 < self.height:
                    self.tiles[y1][x] = Tile(x, y1, "floor")
    
    def spawn_enemies(self):
        """Spawn enemies in random floor locations."""
        floor_tiles = []
        
        # Find all floor tiles
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x].type == "floor":
                    floor_tiles.append((x, y))
        
        # Spawn enemies
        spawn_attempts = 0
        max_spawn_attempts = 200
        
        while len(self.enemies) < self.max_enemies and spawn_attempts < max_spawn_attempts:
            spawn_attempts += 1
            
            if not floor_tiles:
                break
            
            # Pick random floor tile
            tile_x, tile_y = random.choice(floor_tiles)
            world_x = tile_x * self.tile_size + self.tile_size // 2
            world_y = tile_y * self.tile_size + self.tile_size // 2
            
            # Make sure enemy isn't too close to spawn
            spawn_distance = math.sqrt(
                (world_x - self.spawn_position[0])**2 + 
                (world_y - self.spawn_position[1])**2
            )
            
            if spawn_distance > 100:  # Minimum distance from spawn
                enemy = create_enemy((world_x, world_y), self.player_level)
                self.enemies.append(enemy)
    
    def get_spawn_position(self) -> Tuple[float, float]:
        """Get the player spawn position."""
        return self.spawn_position
    
    def check_wall_collision(self, position: Tuple[float, float], radius: float) -> bool:
        """Check if a circular object collides with walls."""
        x, y = position
        
        # Calculate tile bounds that the circle might overlap
        left_tile = int((x - radius) // self.tile_size)
        right_tile = int((x + radius) // self.tile_size)
        top_tile = int((y - radius) // self.tile_size)
        bottom_tile = int((y + radius) // self.tile_size)
        
        # Check each potentially overlapping tile
        for tile_y in range(max(0, top_tile), min(self.height, bottom_tile + 1)):
            for tile_x in range(max(0, left_tile), min(self.width, right_tile + 1)):
                if self.tiles[tile_y][tile_x].type == "wall":
                    # Check if circle overlaps with this wall tile
                    tile_world_x = tile_x * self.tile_size
                    tile_world_y = tile_y * self.tile_size
                    
                    if self.circle_rect_collision(
                        x, y, radius,
                        tile_world_x, tile_world_y, self.tile_size, self.tile_size
                    ):
                        return True
        
        return False
    
    def circle_rect_collision(self, cx: float, cy: float, radius: float,
                             rx: float, ry: float, rw: float, rh: float) -> bool:
        """Check collision between circle and rectangle."""
        # Find the closest point to the circle within the rectangle
        closest_x = max(rx, min(cx, rx + rw))
        closest_y = max(ry, min(cy, ry + rh))
        
        # Calculate the distance between the circle's center and this closest point
        distance_x = cx - closest_x
        distance_y = cy - closest_y
        
        # If the distance is less than the circle's radius, an intersection occurs
        distance_squared = distance_x**2 + distance_y**2
        return distance_squared < radius**2
    
    def get_tile_at_world_pos(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world position to tile coordinates."""
        tile_x = int(world_x // self.tile_size)
        tile_y = int(world_y // self.tile_size)
        return tile_x, tile_y
    
    def is_floor_tile(self, tile_x: int, tile_y: int) -> bool:
        """Check if a tile is a floor tile."""
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            return self.tiles[tile_y][tile_x].type == "floor"
        return False
    
    def render(self, screen: pygame.Surface, camera_x: int, camera_y: int, visibility_system):
        """Render the level to the screen."""
        # Calculate which tiles are visible on screen
        screen_width, screen_height = screen.get_size()
        
        # World bounds that are visible
        left_world = -camera_x
        right_world = -camera_x + screen_width
        top_world = -camera_y
        bottom_world = -camera_y + screen_height
        
        # Convert to tile coordinates
        left_tile = max(0, int(left_world // self.tile_size))
        right_tile = min(self.width, int(right_world // self.tile_size) + 1)
        top_tile = max(0, int(top_world // self.tile_size))
        bottom_tile = min(self.height, int(bottom_world // self.tile_size) + 1)
        
        # Render tiles
        for tile_y in range(top_tile, bottom_tile):
            for tile_x in range(left_tile, right_tile):
                tile = self.tiles[tile_y][tile_x]
                
                # Calculate world position
                world_x = tile_x * self.tile_size
                world_y = tile_y * self.tile_size
                
                # Check visibility (fog of war)
                if not visibility_system.is_visible((world_x + self.tile_size // 2, 
                                                   world_y + self.tile_size // 2)):
                    # Draw darker version if explored but not currently visible
                    if visibility_system.is_explored((world_x + self.tile_size // 2, 
                                                     world_y + self.tile_size // 2)):
                        color = tuple(c // 3 for c in tile.color)  # Much darker
                    else:
                        continue  # Don't draw unexplored areas
                else:
                    color = tile.color
                
                # Calculate screen position
                screen_x = world_x + camera_x
                screen_y = world_y + camera_y
                
                # Draw tile
                pygame.draw.rect(screen, color, 
                               (screen_x, screen_y, self.tile_size, self.tile_size))
                
                # Draw grid lines for walls (debugging/visual clarity)
                if tile.type == "wall" and visibility_system.is_visible((world_x + self.tile_size // 2, 
                                                                        world_y + self.tile_size // 2)):
                    pygame.draw.rect(screen, (80, 80, 80), 
                                   (screen_x, screen_y, self.tile_size, self.tile_size), 1)
