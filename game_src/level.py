"""
Level generation and dungeon layout management.
Handles wall placement, enemy spawning, and collision detection.
"""

import pygame
import random
import math
from typing import Tuple, List, Set
from .enemy import create_enemy
from .boss import Boss
from .new_enemy_types import RicochetEnemy
from .boss_dagger_haste import DaggerHasteBoss
from .items import ItemManager

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
        self.tile_size = 64
        self.player_level = player_level
        
        # Create the tile grid
        self.tiles: List[List[Tile]] = []
        self.spawn_position = (0, 0)
        
        # Enemy management (significantly increased for more engaging gameplay)
        self.enemies = []
        self.max_enemies = 18 + player_level * 5  # Increased to balance more frequent item drops
        self.boss = None
        
        # Level progression items
        self.key_position = None
        self.altar_position = None
        self.key_collected = False
        self.level_complete = False
        
        # Boss projectiles and effects
        self.boss_projectiles = []
        self.boss_effects = []
        
        # Generate the level
        self.generate_level()
        self.spawn_enemies()
        self.spawn_boss()
        self.place_key_and_altar()
        
        # Initialize item management
        self.item_manager = ItemManager(self)
        
        # Initialize notification manager for item interactions
        from notifications import NotificationManager
        self.notification_manager = NotificationManager(800)  # Screen width
        
        # Level tracking attributes for UI
        self.current_game_level = player_level
        self.max_game_level = 10
        
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
        min_room_size = min(6, max(3, self.width // 6))  # Larger minimum rooms
        max_room_size = min(18, max(min_room_size + 2, self.width // 2, self.height // 2))  # Bigger maximum rooms
        
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
        
        # Spawn enemies with new types including a mobile ranged attacker
        spawn_attempts = 0
        max_spawn_attempts = 200
        
        # Define enemy types including new types
        enemy_types = ["basic", "fast", "heavy", "mobile_ranged", "juggernaut", "archer", "scout", "guardian"]
        enemy_weights = [3, 3, 2, 1, 1, 2, 2, 2]  # Increased fast enemy weight for more aggressive gameplay
        
        # Add new ricochet enemy type for higher levels
        if self.player_level >= 4:
            enemy_types.append("ricochet")
            enemy_weights.append(1)  # Rare spawn
        
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
    
    def render(self, screen: pygame.Surface, camera_x: int, camera_y: int, visibility_system, player=None):
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
        
        # Render key if not collected
        if not self.key_collected and self.key_position:
            if visibility_system.is_visible(self.key_position):
                screen_x = int(self.key_position[0] + camera_x)
                screen_y = int(self.key_position[1] + camera_y)
                
                # Draw key as a unique key shape (not diamond like enchantments)
                # Draw key shaft (horizontal rectangle)
                shaft_rect = pygame.Rect(screen_x - 12, screen_y - 3, 20, 6)
                pygame.draw.rect(screen, (255, 215, 0), shaft_rect)  # Gold shaft
                
                # Draw key head (circle)
                pygame.draw.circle(screen, (255, 215, 0), (screen_x - 10, screen_y), 8)  # Gold head
                
                # Draw key teeth (small rectangles)
                teeth_rects = [
                    pygame.Rect(screen_x + 6, screen_y - 1, 4, 3),
                    pygame.Rect(screen_x + 6, screen_y + 2, 6, 3)
                ]
                for rect in teeth_rects:
                    pygame.draw.rect(screen, (255, 215, 0), rect)
                
                # Draw outline
                pygame.draw.rect(screen, (255, 255, 255), shaft_rect, 2)  # White outline
                pygame.draw.circle(screen, (255, 255, 255), (screen_x - 10, screen_y), 8, 2)  # White outline
                for rect in teeth_rects:
                    pygame.draw.rect(screen, (255, 255, 255), rect, 1)
        
        # Render altar
        if self.altar_position:
            if visibility_system.is_visible(self.altar_position):
                screen_x = int(self.altar_position[0] + camera_x)
                screen_y = int(self.altar_position[1] + camera_y)
                
                # Draw altar as a stone platform
                altar_color = (100, 255, 100) if self.key_collected else (100, 100, 100)
                pygame.draw.rect(screen, altar_color, (screen_x - 20, screen_y - 15, 40, 30))
                pygame.draw.rect(screen, (200, 200, 200), (screen_x - 20, screen_y - 15, 40, 30), 3)
                
                # Draw glowing effect if ready
                if self.key_collected:
                    pygame.draw.circle(screen, (255, 255, 255, 100), (screen_x, screen_y), 35, 2)
                    
                    # Add text instruction if player has key and boss is defeated
                    if not self.boss or not self.boss.is_alive():
                        # Check if player is nearby
                        if player:
                            dx = player.position[0] - self.altar_position[0]
                            dy = player.position[1] - self.altar_position[1]
                            distance = math.sqrt(dx * dx + dy * dy)
                        else:
                            distance = 100
                        
                        if distance <= 60:  # Show instruction when player is close
                            font = pygame.font.Font(None, 24)
                            text = font.render("Press E to advance", True, (255, 255, 255))
                            text_rect = text.get_rect(center=(screen_x, screen_y - 50))
                            screen.blit(text, text_rect)
        
        # Render boss projectiles
        for projectile in self.boss_projectiles:
            if visibility_system.is_visible(projectile['position']):
                screen_x = int(projectile['position'][0] + camera_x)
                screen_y = int(projectile['position'][1] + camera_y)
                
                # Different colors for different projectile types
                colors = {
                    'fire_spin': (255, 100, 0),
                    'ice_shard': (100, 200, 255),
                    'shadow_bolt': (150, 0, 150)
                }
                color = colors.get(projectile['type'], (255, 255, 255))
                pygame.draw.circle(screen, color, (screen_x, screen_y), 6)
        
        # Render boss effects
        for effect in self.boss_effects:
            if visibility_system.is_visible(effect['position']):
                screen_x = int(effect['position'][0] + camera_x)
                screen_y = int(effect['position'][1] + camera_y)
                
                if effect['type'] == 'frost_nova':
                    # Draw expanding frost circle
                    pygame.draw.circle(screen, (100, 200, 255), (screen_x, screen_y), effect['radius'], 3)
                
                elif effect['type'] == 'lightning_bolt':
                    # Draw lightning line
                    end_x = int(effect['end_pos'][0] + camera_x)
                    end_y = int(effect['end_pos'][1] + camera_y)
                    pygame.draw.line(screen, (255, 255, 100), (screen_x, screen_y), (end_x, end_y), 4)
                
                elif effect['type'] == 'dark_storm':
                    # Draw swirling dark energy
                    pygame.draw.circle(screen, (80, 0, 150), (screen_x, screen_y), effect['radius'], 2)
                    pygame.draw.circle(screen, (150, 0, 200), (screen_x, screen_y), effect['radius'] // 2, 1)
    
    def spawn_boss(self):
        """Spawn the level boss in a suitable location."""
        floor_tiles = []
        
        # Find all floor tiles
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x].type == "floor":
                    floor_tiles.append((x, y))
        
        # Find a good boss spawn location (furthest from player spawn)
        best_distance = 0
        best_position = None
        
        for tile_x, tile_y in floor_tiles:
            world_x = tile_x * self.tile_size + self.tile_size // 2
            world_y = tile_y * self.tile_size + self.tile_size // 2
            
            distance = math.sqrt(
                (world_x - self.spawn_position[0])**2 + 
                (world_y - self.spawn_position[1])**2
            )
            
            if distance > best_distance:
                best_distance = distance
                best_position = (world_x, world_y)
        
        if best_position:
            self.boss = Boss(best_position, self.player_level)
            print(f"Spawned boss at distance {best_distance:.1f} from player")
    
    def place_key_and_altar(self):
        """Place the key and altar for level progression."""
        floor_tiles = []
        
        # Find all floor tiles
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x].type == "floor":
                    floor_tiles.append((x, y))
        
        if len(floor_tiles) >= 2:
            # Shuffle and pick two different locations
            random.shuffle(floor_tiles)
            
            # Key position (random floor tile)
            key_tile = floor_tiles[0]
            self.key_position = (
                key_tile[0] * self.tile_size + self.tile_size // 2,
                key_tile[1] * self.tile_size + self.tile_size // 2
            )
            
            # Altar position (different from key)
            altar_tile = floor_tiles[1]
            self.altar_position = (
                altar_tile[0] * self.tile_size + self.tile_size // 2,
                altar_tile[1] * self.tile_size + self.tile_size // 2
            )
            
            print(f"Placed key at {self.key_position} and altar at {self.altar_position}")
    
    def update_boss_projectiles(self, dt: float, player):
        """Update boss projectiles and effects."""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Update projectiles
        for projectile in self.boss_projectiles[:]:
            projectile['lifetime'] -= dt
            
            if projectile['lifetime'] <= 0:
                self.boss_projectiles.remove(projectile)
                continue
            
            # Update position based on type
            if projectile.get('homing'):
                # Homing projectile (shadow bolt)
                dx = player.position[0] - projectile['position'][0]
                dy = player.position[1] - projectile['position'][1]
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance > 0:
                    speed = 120
                    projectile['velocity'][0] = (dx / distance) * speed
                    projectile['velocity'][1] = (dy / distance) * speed
            
            # Move projectile
            projectile['position'][0] += projectile['velocity'][0] * dt
            projectile['position'][1] += projectile['velocity'][1] * dt
            
            # Check collision with player
            dx = player.position[0] - projectile['position'][0]
            dy = player.position[1] - projectile['position'][1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= player.radius + 8:  # Projectile hit radius
                player.take_damage(projectile['damage'])
                self.boss_projectiles.remove(projectile)
        
        # Update effects
        for effect in self.boss_effects[:]:
            effect['lifetime'] -= dt
            
            if effect['lifetime'] <= 0:
                self.boss_effects.remove(effect)
                continue
            
            # Handle different effect types
            if effect['type'] == 'frost_nova':
                # Expanding frost nova
                progress = 1.0 - (effect['lifetime'] / 2.0)  # 2.0 is max lifetime
                effect['radius'] = int(effect['max_radius'] * progress)
                
                # Check collision with player
                dx = player.position[0] - effect['position'][0]
                dy = player.position[1] - effect['position'][1]
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance <= effect['radius'] + player.radius:
                    player.take_damage(effect['damage'])
                    effect['lifetime'] = 0  # Remove after hitting
            
            elif effect['type'] == 'lightning_bolt':
                # Instant damage on creation, just visual effect now
                if current_time - effect['created_time'] < 0.1:  # Hit within 0.1 seconds
                    dx = player.position[0] - effect['end_pos'][0]
                    dy = player.position[1] - effect['end_pos'][1]
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance <= player.radius + 20:  # Lightning hit radius
                        player.take_damage(effect['damage'])
            
            elif effect['type'] == 'dark_storm':
                # Continuous damage in area
                dx = player.position[0] - effect['position'][0]
                dy = player.position[1] - effect['position'][1]
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance <= effect['radius']:
                    # Damage every 0.5 seconds
                    if int(current_time * 2) != int((current_time - dt) * 2):
                        player.take_damage(effect['damage'])
    
    def check_key_collection(self, player) -> bool:
        """Check if player collected the key."""
        if not self.key_collected and self.key_position:
            dx = player.position[0] - self.key_position[0]
            dy = player.position[1] - self.key_position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= player.radius + 20:
                self.key_collected = True
                print("Key collected! Defeat the boss and find the altar to advance.")
                return True
        return False
    
    def check_altar_activation(self, player) -> bool:
        """Check if player can activate the altar to complete the level."""
        if self.key_collected and not self.level_complete and self.altar_position:
            # Only allow altar activation if boss is defeated
            if self.boss and self.boss.is_alive():
                return False
            
            dx = player.position[0] - self.altar_position[0]
            dy = player.position[1] - self.altar_position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Check if player is near altar and presses a key (E key)
            keys = pygame.key.get_pressed()
            if distance <= player.radius + 25 and keys[pygame.K_e]:
                self.level_complete = True
                print("Level completed! Altar activated with E key.")
                return True
        return False
    
    def all_enemies_defeated(self) -> bool:
        """Check if all enemies including boss are defeated."""
        alive_enemies = sum(1 for enemy in self.enemies if enemy.is_alive())
        boss_alive = self.boss and self.boss.is_alive()
        return alive_enemies == 0 and not boss_alive
