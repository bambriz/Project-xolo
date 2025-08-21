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
from sound_manager import SoundManager

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
        self.sound_manager = SoundManager()
        
        # Initialize first level
        self.current_level = 1
        self.max_level = 10
        self.level = Level(30 + self.current_level * 3, 25 + self.current_level * 2, self.current_level)
        self.player = Player(self.level.get_spawn_position())
        self.visibility_system = VisibilitySystem(self.level)
        self.ui = UI(self.screen, self.asset_manager)
        
        # Start background music
        self.sound_manager.play_music(self.sound_manager.get_music_for_level(self.current_level))
        
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
        
        # Update boss if it exists
        if self.level.boss and self.level.boss.is_alive():
            can_see_player = self.visibility_system.has_line_of_sight(
                (self.level.boss.position[0], self.level.boss.position[1]), 
                (self.player.position[0], self.player.position[1])
            )
            self.level.boss.update(dt, self.player, self.level, can_see_player)
        
        # Update projectiles
        self.player.combat_system.update_projectiles(dt, self.level)
        
        # Update boss projectiles and effects
        self.level.update_boss_projectiles(dt, self.player)
        
        # Check key collection
        if self.level.check_key_collection(self.player):
            self.sound_manager.play_sound('key_pickup')
        
        # Check altar activation for level progression
        if self.level.check_altar_activation(self.player):
            self.sound_manager.play_sound('altar_activate')
            self.advance_to_next_level()
        
        # Remove dead enemies and award XP
        for enemy in self.level.enemies[:]:  # Create a copy to iterate over
            if not enemy.is_alive():
                xp_gained = enemy.xp_value
                self.player.gain_xp(xp_gained)
                self.level.enemies.remove(enemy)
                self.sound_manager.play_sound('enemy_death')
                print(f"Enemy defeated! Gained {xp_gained} XP")
        
        # Check if boss is defeated
        if self.level.boss and not self.level.boss.is_alive():
            if hasattr(self.level.boss, 'death_processed') and not self.level.boss.death_processed:
                xp_gained = self.level.boss.xp_value
                self.player.gain_xp(xp_gained)
                self.sound_manager.play_sound('boss_death')
                self.level.boss.death_processed = True  # Prevent multiple XP gains
                print(f"Boss defeated! Gained {xp_gained} XP")
    
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
        self.level.render(self.screen, camera_x, camera_y, self.visibility_system, self.player)
        
        # Render enemies (only if visible)
        for enemy in self.level.enemies:
            if self.visibility_system.is_visible(enemy.position):
                enemy.render(self.screen, camera_x, camera_y, self.asset_manager)
        
        # Render boss (only if visible) 
        if self.level.boss and self.visibility_system.is_visible((self.level.boss.position[0], self.level.boss.position[1])):
            self.level.boss.render(self.screen, camera_x, camera_y, self.asset_manager)
        
        # Render player
        self.player.render(self.screen, camera_x, camera_y, self.asset_manager)
        
        # Render projectiles
        self.player.combat_system.render_projectiles(self.screen, camera_x, camera_y, self.asset_manager)
        
        # Render melee attack animations
        self.player.combat_system.render_melee_attacks(self.screen, camera_x, camera_y)
        
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
    
    def advance_to_next_level(self):
        """Advance to the next level."""
        self.current_level += 1
        
        if self.current_level > self.max_level:
            # Game completed!
            self.sound_manager.play_music('victory_music', loop=False)
            print("🎉 CONGRATULATIONS! You completed all 10 levels! 🎉")
            print("You are the ultimate dungeon crawler champion!")
            return
        
        # Create new level with increasing difficulty
        width = 30 + self.current_level * 3
        height = 25 + self.current_level * 2
        
        # Create new level
        self.level = Level(width, height, self.current_level)
        
        # Reset player position but keep stats
        spawn_pos = self.level.get_spawn_position()
        self.player.position = list(spawn_pos)
        
        # Update visibility system for new level
        self.visibility_system = VisibilitySystem(self.level)
        
        # Play appropriate music for new level
        self.sound_manager.play_music(self.sound_manager.get_music_for_level(self.current_level))
        
        # Track level completion
        self.game_state.levels_completed.append({
            'level': self.current_level - 1,
            'completion_time': self.game_state.total_play_time
        })
        
        print(f"Advanced to level {self.current_level}/{self.max_level} - Size: {width}x{height}")
        
        # Play boss spawn sound if this is a boss level
        if self.current_level % 3 == 0 or self.current_level == 10:
            self.sound_manager.play_sound('boss_spawn')
    
    def restart_game(self):
        """Restart the game from the beginning."""
        self.current_level = 1
        self.level = Level(30 + self.current_level * 3, 25 + self.current_level * 2, self.current_level)
        self.player = Player(self.level.get_spawn_position())
        self.visibility_system = VisibilitySystem(self.level)
        self.game_state = GameState()
        self.sound_manager.play_music(self.sound_manager.get_music_for_level(self.current_level))
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
