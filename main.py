"""
Main game loop and initialization for the 2D dungeon crawler.
Handles pygame initialization, event processing, and game state management.
"""

import pygame
import sys
from typing import Optional

from game_state import GameState
from player import Player
from level import Level
from ui import UI
from assets import AssetManager
from visibility import VisibilitySystem

# Game constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "Dungeon Crawler"

class Game:
    """Main game class that manages the game loop and core systems."""
    
    def __init__(self):
        """Initialize the game and all subsystems."""
        pygame.init()
        
        # Initialize display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # Initialize game systems
        self.asset_manager = AssetManager()
        self.game_state = GameState()
        self.level = Level(50, 40)  # 50x40 tile dungeon
        self.player = Player(self.level.get_spawn_position())
        self.visibility_system = VisibilitySystem(self.level)
        self.ui = UI(self.screen, self.asset_manager)
        
        # Game state
        self.running = True
        self.paused = False
        
        print("Game initialized successfully!")
        print(f"Player spawned at: {self.player.position}")
    
    def handle_events(self):
        """Process all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.restart_game()
                elif event.key == pygame.K_e:  # E key to pickup items
                    self.player.try_pickup_item(self.level)
                elif event.key == pygame.K_q:  # Q key to drop spell
                    self.player.drop_spell(self.level)
    
    def update(self, dt: float):
        """Update all game objects and systems."""
        if self.paused:
            return
        
        # Get current input state
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Update player
        self.player.update(dt, keys, mouse_pos, mouse_buttons, self.level)
        
        # Update enemies
        for enemy in self.level.enemies:
            if enemy.is_alive():
                # Check if enemy can see player
                can_see_player = self.visibility_system.has_line_of_sight(
                    (enemy.position[0], enemy.position[1]), (self.player.position[0], self.player.position[1])
                )
                enemy.update(dt, self.player, self.level, can_see_player)
        
        # Update projectiles
        self.player.combat_system.update_projectiles(dt, self.level)
        
        # Remove dead enemies and award XP
        for enemy in self.level.enemies[:]:  # Create a copy to iterate over
            if not enemy.is_alive():
                xp_gained = enemy.xp_value
                self.player.gain_xp(xp_gained)
                self.level.enemies.remove(enemy)
                print(f"Enemy defeated! Gained {xp_gained} XP")
        
        # Check for level completion (all enemies defeated)
        if not self.level.enemies:
            self.generate_new_level()
    
    def render(self):
        """Render all game objects to the screen."""
        # Clear screen
        self.screen.fill((20, 20, 20))  # Dark background
        
        # Calculate camera offset to center on player
        camera_x = int(SCREEN_WIDTH // 2 - self.player.position[0])
        camera_y = int(SCREEN_HEIGHT // 2 - self.player.position[1])
        
        # Update visibility (fog of war)
        self.visibility_system.update_visibility((self.player.position[0], self.player.position[1]))
        
        # Render level (walls, floors, etc.)
        self.level.render(self.screen, camera_x, camera_y, self.visibility_system)
        
        # Render enemies (only if visible)
        for enemy in self.level.enemies:
            if self.visibility_system.is_visible(enemy.position):
                enemy.render(self.screen, camera_x, camera_y, self.asset_manager)
        
        # Render player
        self.player.render(self.screen, camera_x, camera_y, self.asset_manager)
        
        # Render projectiles
        self.player.combat_system.render_projectiles(self.screen, camera_x, camera_y, self.asset_manager)
        
        # Render items
        self.level.item_manager.render_items(self.screen, camera_x, camera_y, self.asset_manager)
        
        # Render UI (health, XP, level, etc.)
        self.ui.render(self.player, self.level, self.visibility_system)
        
        # Render pause overlay if paused
        if self.paused:
            self.render_pause_overlay()
        
        # Update display
        pygame.display.flip()
    
    def render_pause_overlay(self):
        """Render the pause screen overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 74)
        text = font.render("PAUSED", True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
        
        font_small = pygame.font.Font(None, 36)
        text_small = font_small.render("Press P to resume, ESC to quit", True, (255, 255, 255))
        text_small_rect = text_small.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(text_small, text_small_rect)
    
    def generate_new_level(self):
        """Generate a new level with scaled enemies."""
        print(f"Level complete! Generating new level for player level {self.player.level}")
        self.level = Level(50, 40, self.player.level)
        self.player.position = list(self.level.get_spawn_position())
        self.visibility_system = VisibilitySystem(self.level)
    
    def restart_game(self):
        """Restart the game from the beginning."""
        self.level = Level(50, 40)
        self.player = Player(self.level.get_spawn_position())
        self.visibility_system = VisibilitySystem(self.level)
        print("Game restarted!")
    
    def run(self):
        """Main game loop."""
        print("Starting game loop...")
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            
            # Process events
            self.handle_events()
            
            # Update game state
            self.update(dt)
            
            # Render everything
            self.render()
        
        # Cleanup
        pygame.quit()
        sys.exit()

def main():
    """Entry point for the game."""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Game crashed with error: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
