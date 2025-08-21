"""
User interface components and HUD rendering.
Handles health bars, XP display, minimap, and game UI elements.
"""

import pygame
import math
from typing import Tuple

class UI:
    """Manages all user interface elements."""
    
    def __init__(self, screen: pygame.Surface, asset_manager):
        """Initialize the UI system."""
        self.screen = screen
        self.asset_manager = asset_manager
        self.screen_width, self.screen_height = screen.get_size()
        
        # UI layout constants
        self.margin = 20
        self.bar_width = 200
        self.bar_height = 20
        self.minimap_size = 150
        
        # UI colors
        self.ui_bg_color = (0, 0, 0, 180)  # Semi-transparent black
        self.text_color = (255, 255, 255)
        self.health_color = (50, 200, 50)
        self.health_bg_color = (100, 30, 30)
        self.xp_color = (255, 215, 0)
        self.xp_bg_color = (100, 100, 30)
        
        print("UI system initialized")
    
    def render(self, player, level):
        """Render all UI elements."""
        # Main HUD
        self.render_health_bar(player)
        self.render_xp_bar(player)
        self.render_level_info(player)
        self.render_stats_panel(player, level)
        
        # Minimap
        self.render_minimap(player, level)
        
        # Controls help
        self.render_controls_help()
    
    def render_health_bar(self, player):
        """Render the player's health bar."""
        x = self.margin
        y = self.margin
        
        # Background panel
        panel_width = self.bar_width + 60
        panel_height = 30
        self.draw_panel(x - 5, y - 5, panel_width, panel_height)
        
        # Health icon
        health_icon = self.asset_manager.get_sprite("health_icon")
        if health_icon:
            self.screen.blit(health_icon, (x, y + 5))
        
        # Health bar
        bar_x = x + 25
        health_percentage = player.get_health_percentage()
        
        # Background
        pygame.draw.rect(self.screen, self.health_bg_color, 
                        (bar_x, y, self.bar_width, self.bar_height))
        
        # Health fill
        fill_width = int(self.bar_width * health_percentage)
        if fill_width > 0:
            pygame.draw.rect(self.screen, self.health_color, 
                            (bar_x, y, fill_width, self.bar_height))
        
        # Border
        pygame.draw.rect(self.screen, self.text_color, 
                        (bar_x, y, self.bar_width, self.bar_height), 1)
        
        # Health text
        health_text = f"{player.current_health}/{player.max_health}"
        text_surface = self.asset_manager.render_text(health_text, "small", self.text_color)
        text_x = bar_x + self.bar_width // 2 - text_surface.get_width() // 2
        text_y = y + self.bar_height // 2 - text_surface.get_height() // 2
        self.screen.blit(text_surface, (text_x, text_y))
    
    def render_xp_bar(self, player):
        """Render the player's XP bar."""
        x = self.margin
        y = self.margin + 40
        
        # Background panel
        panel_width = self.bar_width + 60
        panel_height = 30
        self.draw_panel(x - 5, y - 5, panel_width, panel_height)
        
        # XP icon
        xp_icon = self.asset_manager.get_sprite("xp_icon")
        if xp_icon:
            self.screen.blit(xp_icon, (x, y + 5))
        
        # XP bar
        bar_x = x + 25
        xp_percentage = player.get_xp_percentage()
        
        # Background
        pygame.draw.rect(self.screen, self.xp_bg_color, 
                        (bar_x, y, self.bar_width, self.bar_height))
        
        # XP fill
        fill_width = int(self.bar_width * xp_percentage)
        if fill_width > 0:
            pygame.draw.rect(self.screen, self.xp_color, 
                            (bar_x, y, fill_width, self.bar_height))
        
        # Border
        pygame.draw.rect(self.screen, self.text_color, 
                        (bar_x, y, self.bar_width, self.bar_height), 1)
        
        # XP text
        xp_text = f"{player.xp}/{player.xp_to_next_level}"
        text_surface = self.asset_manager.render_text(xp_text, "small", self.text_color)
        text_x = bar_x + self.bar_width // 2 - text_surface.get_width() // 2
        text_y = y + self.bar_height // 2 - text_surface.get_height() // 2
        self.screen.blit(text_surface, (text_x, text_y))
    
    def render_level_info(self, player):
        """Render player level and damage info."""
        x = self.margin
        y = self.margin + 80
        
        # Background panel
        panel_width = 150
        panel_height = 50
        self.draw_panel(x - 5, y - 5, panel_width, panel_height)
        
        # Level text
        level_text = f"Level {player.level}"
        level_surface = self.asset_manager.render_text(level_text, "medium", self.text_color)
        self.screen.blit(level_surface, (x, y))
        
        # Damage text
        damage_text = f"Damage: {player.damage}"
        damage_surface = self.asset_manager.render_text(damage_text, "small", self.text_color)
        self.screen.blit(damage_surface, (x, y + 25))
    
    def render_stats_panel(self, player, level):
        """Render additional stats and info."""
        x = self.margin
        y = self.screen_height - 120
        
        # Background panel
        panel_width = 200
        panel_height = 100
        self.draw_panel(x - 5, y - 5, panel_width, panel_height)
        
        # Enemy count
        enemies_alive = len([e for e in level.enemies if e.is_alive()])
        enemy_text = f"Enemies: {enemies_alive}"
        enemy_surface = self.asset_manager.render_text(enemy_text, "small", self.text_color)
        self.screen.blit(enemy_surface, (x, y))
        
        # Combat info
        melee_cooldown = max(0, player.combat_system.melee_cooldown - 
                           (pygame.time.get_ticks() / 1000.0 - player.combat_system.last_melee_attack))
        ranged_cooldown = max(0, player.combat_system.ranged_cooldown - 
                            (pygame.time.get_ticks() / 1000.0 - player.combat_system.last_ranged_attack))
        
        if melee_cooldown > 0:
            melee_text = f"Melee: {melee_cooldown:.1f}s"
            melee_surface = self.asset_manager.render_text(melee_text, "small", (200, 200, 200))
            self.screen.blit(melee_surface, (x, y + 20))
        
        if ranged_cooldown > 0:
            ranged_text = f"Ranged: {ranged_cooldown:.1f}s"
            ranged_surface = self.asset_manager.render_text(ranged_text, "small", (200, 200, 200))
            self.screen.blit(ranged_surface, (x, y + 40))
        
        # Projectile count
        projectile_count = len(player.combat_system.projectiles)
        if projectile_count > 0:
            proj_text = f"Projectiles: {projectile_count}"
            proj_surface = self.asset_manager.render_text(proj_text, "small", self.text_color)
            self.screen.blit(proj_surface, (x, y + 60))
    
    def render_minimap(self, player, level):
        """Render a simple minimap."""
        map_x = self.screen_width - self.minimap_size - self.margin
        map_y = self.margin
        
        # Background panel
        self.draw_panel(map_x - 5, map_y - 5, self.minimap_size + 10, self.minimap_size + 10)
        
        # Calculate scale
        scale_x = self.minimap_size / (level.width * level.tile_size)
        scale_y = self.minimap_size / (level.height * level.tile_size)
        scale = min(scale_x, scale_y)
        
        # Draw level outline
        level_width = int(level.width * level.tile_size * scale)
        level_height = int(level.height * level.tile_size * scale)
        level_rect = pygame.Rect(map_x, map_y, level_width, level_height)
        pygame.draw.rect(self.screen, (50, 50, 50), level_rect)
        pygame.draw.rect(self.screen, self.text_color, level_rect, 1)
        
        # Draw walls (simplified)
        for y in range(0, level.height, 2):  # Sample every 2nd tile for performance
            for x in range(0, level.width, 2):
                if level.tiles[y][x].type == "wall":
                    wall_x = map_x + int(x * level.tile_size * scale)
                    wall_y = map_y + int(y * level.tile_size * scale)
                    wall_size = max(1, int(level.tile_size * scale * 2))
                    pygame.draw.rect(self.screen, (100, 100, 100), 
                                   (wall_x, wall_y, wall_size, wall_size))
        
        # Draw player
        player_x = map_x + int(player.position[0] * scale)
        player_y = map_y + int(player.position[1] * scale)
        pygame.draw.circle(self.screen, (100, 150, 255), (player_x, player_y), 3)
        
        # Draw enemies
        for enemy in level.enemies:
            if enemy.is_alive():
                enemy_x = map_x + int(enemy.position[0] * scale)
                enemy_y = map_y + int(enemy.position[1] * scale)
                pygame.draw.circle(self.screen, (200, 100, 100), (enemy_x, enemy_y), 2)
    
    def render_controls_help(self):
        """Render control instructions."""
        x = self.screen_width - 250
        y = self.screen_height - 150
        
        # Background panel
        panel_width = 230
        panel_height = 130
        self.draw_panel(x - 5, y - 5, panel_width, panel_height)
        
        # Controls text
        controls = [
            "WASD/Arrows: Move",
            "Left Click: Melee Attack",
            "Right Click: Ranged Attack",
            "P: Pause",
            "ESC: Quit"
        ]
        
        for i, control in enumerate(controls):
            text_surface = self.asset_manager.render_text(control, "small", self.text_color)
            self.screen.blit(text_surface, (x, y + i * 20))
    
    def draw_panel(self, x: int, y: int, width: int, height: int):
        """Draw a semi-transparent panel background."""
        panel_surface = pygame.Surface((width, height))
        panel_surface.set_alpha(180)
        panel_surface.fill((0, 0, 0))
        self.screen.blit(panel_surface, (x, y))
        
        # Border
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, width, height), 1)
    
    def render_damage_number(self, position: Tuple[float, float], damage: int, 
                           camera_x: int, camera_y: int):
        """Render floating damage numbers."""
        screen_x = int(position[0] + camera_x)
        screen_y = int(position[1] + camera_y)
        
        damage_text = str(damage)
        color = (255, 100, 100) if damage > 0 else (100, 255, 100)
        
        text_surface = self.asset_manager.render_text(damage_text, "small", color)
        
        # Center the text
        text_x = screen_x - text_surface.get_width() // 2
        text_y = screen_y - text_surface.get_height() // 2 - 20
        
        self.screen.blit(text_surface, (text_x, text_y))
    
    def render_level_complete(self):
        """Render level complete message."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Level complete text
        text = "LEVEL COMPLETE!"
        text_surface = self.asset_manager.render_text(text, "large", (0, 255, 0))
        text_x = self.screen_width // 2 - text_surface.get_width() // 2
        text_y = self.screen_height // 2 - text_surface.get_height() // 2
        self.screen.blit(text_surface, (text_x, text_y))
        
        # Continue instruction
        continue_text = "Press any key to continue..."
        continue_surface = self.asset_manager.render_text(continue_text, "medium", self.text_color)
        continue_x = self.screen_width // 2 - continue_surface.get_width() // 2
        continue_y = text_y + 60
        self.screen.blit(continue_surface, (continue_x, continue_y))
    
    def render_game_over(self):
        """Render game over screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        text = "GAME OVER"
        text_surface = self.asset_manager.render_text(text, "large", (255, 0, 0))
        text_x = self.screen_width // 2 - text_surface.get_width() // 2
        text_y = self.screen_height // 2 - text_surface.get_height() // 2
        self.screen.blit(text_surface, (text_x, text_y))
        
        # Restart instruction
        restart_text = "Press R to restart or ESC to quit"
        restart_surface = self.asset_manager.render_text(restart_text, "medium", self.text_color)
        restart_x = self.screen_width // 2 - restart_surface.get_width() // 2
        restart_y = text_y + 60
        self.screen.blit(restart_surface, (restart_x, restart_y))
