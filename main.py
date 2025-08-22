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
from damage_numbers import DamageNumberManager
from notifications import NotificationManager

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
        self.damage_numbers = DamageNumberManager()
        self.notifications = NotificationManager(SCREEN_WIDTH)
        
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
                if self.game_state.phase == "menu":
                    self.handle_menu_events(event)
                elif self.game_state.phase == "game_over":
                    self.handle_game_over_events(event)
                elif self.game_state.phase == "playing":
                    self.handle_playing_events(event)
    
    def handle_menu_events(self, event):
        """Handle events during menu phase."""
        if event.key == pygame.K_SPACE:
            self.start_new_game()
        elif event.key == pygame.K_ESCAPE:
            self.running = False
    
    def handle_game_over_events(self, event):
        """Handle events during game over phase."""
        if event.key == pygame.K_r:
            self.start_new_game()
        elif event.key == pygame.K_ESCAPE:
            self.running = False
    
    def handle_playing_events(self, event):
        """Handle events during playing phase."""
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
        # Always update game state
        self.game_state.update(dt)
        
        # Only update game logic during playing phase
        if self.game_state.phase != "playing" or self.paused:
            return
        
        # Check if player died
        if self.player.current_health <= 0:
            self.game_state.set_phase("game_over")
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
        
        # Update items (health packs moving toward player)
        self.level.item_manager.update_items(dt, (self.player.position[0], self.player.position[1]))
        
        # Update damage numbers and notifications
        self.damage_numbers.update(dt)
        self.notifications.update(dt)
        
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
                # Drop health items when enemy dies
                self.level.item_manager.drop_enemy_loot(tuple(enemy.position), is_boss=False)
                
                xp_gained = enemy.xp_value
                self.player.gain_xp(xp_gained)
                self.level.enemies.remove(enemy)
                self.sound_manager.play_sound('enemy_death')
                print(f"Enemy defeated! Gained {xp_gained} XP")
        
        # Check if boss is defeated
        if self.level.boss and not self.level.boss.is_alive():
            if hasattr(self.level.boss, 'death_processed') and not self.level.boss.death_processed:
                # Drop boss health items (2-4 items as requested)
                boss_pos = (self.level.boss.position[0], self.level.boss.position[1])
                self.level.item_manager.drop_enemy_loot(boss_pos, is_boss=True)
                
                xp_gained = self.level.boss.xp_value
                self.player.gain_xp(xp_gained)
                self.sound_manager.play_sound('boss_death')
                self.level.boss.death_processed = True  # Prevent multiple XP gains
                print(f"Boss defeated! Gained {xp_gained} XP")
    
    def render(self):
        """Render all game objects to the screen."""
        if self.game_state.phase == "menu":
            self.ui.render_menu()
        elif self.game_state.phase == "game_over":
            # Render last game state in background
            self.render_game_world()
            # Overlay game over screen
            self.ui.render_game_over(self.player, self.game_state)
        elif self.game_state.phase == "playing":
            self.render_game_world()
            # Render UI on top
            self.ui.render(self.player, self.level, self.visibility_system)
            # Render pause overlay if paused
            if self.paused:
                self.render_pause_overlay()
        
        # Update display
        pygame.display.flip()
    
    def render_game_world(self):
        """Render the main game world."""
        # Clear screen
        self.screen.fill((20, 20, 20))  # Dark background
        
        # Calculate camera offset to center on player
        camera_x = int(SCREEN_WIDTH // 2 - self.player.position[0])
        camera_y = int(SCREEN_HEIGHT // 2 - self.player.position[1])
        
        # Update visibility (fog of war)
        self.visibility_system.update_visibility((self.player.position[0], self.player.position[1]))
        
        # Render level (walls, floors, etc.)
        self.level.render(self.screen, camera_x, camera_y, self.visibility_system, self.player)
        
        # Render enemies (only if visible) - but not their attack animations yet
        for enemy in self.level.enemies:
            if self.visibility_system.is_visible(enemy.position):
                enemy.render_body(self.screen, camera_x, camera_y, self.asset_manager)
        
        # Render boss (only if visible) - but not their attack animations yet
        if self.level.boss and self.visibility_system.is_visible((self.level.boss.position[0], self.level.boss.position[1])):
            self.level.boss.render_body(self.screen, camera_x, camera_y, self.asset_manager)
        
        # Render player
        self.player.render(self.screen, camera_x, camera_y, self.asset_manager)
        
        # Render enemy attack animations ABOVE player
        for enemy in self.level.enemies:
            if self.visibility_system.is_visible(enemy.position):
                enemy.render_attack_animations_only(self.screen, camera_x, camera_y)
                
        # Render boss attack animations ABOVE player
        if self.level.boss and self.visibility_system.is_visible((self.level.boss.position[0], self.level.boss.position[1])):
            self.level.boss.render_attack_animations_only(self.screen, camera_x, camera_y)
        
        # Render projectiles
        self.player.combat_system.render_projectiles(self.screen, camera_x, camera_y, self.asset_manager)
        
        # Render melee attack animations
        self.player.combat_system.render_melee_attacks(self.screen, camera_x, camera_y)
        
        # Render items
        self.level.item_manager.render_items(self.screen, camera_x, camera_y, self.asset_manager)
        
        # Render damage numbers
        self.damage_numbers.render(self.screen, camera_x, camera_y)
        
        # Render notifications (UI overlay)
        self.notifications.render(self.screen)
    
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
        
        # Create new level with much bigger size for better gameplay
        width = 40 + self.current_level * 5  # Increased from 30 + level * 3
        height = 35 + self.current_level * 4  # Increased from 25 + level * 2
        
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
    
    def start_new_game(self):
        """Start a new game from the menu."""
        print("Starting new game...")
        
        # Reset to level 1
        self.current_level = 1
        self.level = Level(30 + self.current_level * 3, 25 + self.current_level * 2, self.current_level)
        self.player = Player(self.level.get_spawn_position())
        self.visibility_system = VisibilitySystem(self.level)
        
        # Reset game state
        self.paused = False
        self.game_state.set_phase("playing")
        
        # Reset statistics
        self.game_state.stats["enemies_defeated"] = 0
        self.game_state.stats["total_playtime"] = 0.0
        self.game_state.stats["levels_completed"] = 0
        
        # Restart background music
        self.sound_manager.play_music(self.sound_manager.get_music_for_level(self.current_level))
        
        print(f"New game started! Player spawned at: {self.player.position}")
    
    def restart_game(self):
        """Restart the game from the beginning."""
        self.start_new_game()
    
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
