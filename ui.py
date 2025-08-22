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
    
    def render(self, player, level, visibility_system=None):
        """Render all UI elements."""
        # Main HUD
        self.render_health_bar(player)
        self.render_xp_bar(player)
        self.render_level_info(player)
        self.render_stats_panel(player, level)
        self.render_game_level_info(level)
        
        # Minimap
        self.render_minimap(player, level, visibility_system)
        
        # Controls help
        self.render_controls_help()
        
        # Inventory display
        self.render_inventory(player)
    
    def render_menu(self):
        """Render the main menu screen with retro roguelike styling."""
        # Clear screen with dark background
        self.screen.fill((10, 10, 20))  # Very dark blue
        
        # Title
        title_font = pygame.font.Font(None, 72)
        subtitle_font = pygame.font.Font(None, 36)
        menu_font = pygame.font.Font(None, 48)
        
        # Game title with retro styling
        title_text = title_font.render("DUNGEON CRAWLER", True, (255, 215, 0))  # Gold
        title_shadow = title_font.render("DUNGEON CRAWLER", True, (100, 50, 0))  # Dark gold shadow
        
        # Position title at center top
        title_x = self.screen_width // 2 - title_text.get_width() // 2
        title_y = 80
        
        # Draw shadow first, then title
        self.screen.blit(title_shadow, (title_x + 3, title_y + 3))
        self.screen.blit(title_text, (title_x, title_y))
        
        # Subtitle
        subtitle_text = subtitle_font.render("A Retro Roguelike Adventure", True, (200, 200, 200))
        subtitle_x = self.screen_width // 2 - subtitle_text.get_width() // 2
        self.screen.blit(subtitle_text, (subtitle_x, title_y + 80))
        
        # Menu options
        menu_y_start = 250
        menu_options = [
            "PRESS SPACE TO START",
            "PRESS ESC TO QUIT"
        ]
        
        for i, option in enumerate(menu_options):
            color = (255, 255, 255) if i == 0 else (150, 150, 150)
            text = menu_font.render(option, True, color)
            text_x = self.screen_width // 2 - text.get_width() // 2
            text_y = menu_y_start + i * 60
            self.screen.blit(text, (text_x, text_y))
        
        # Game instructions with retro ASCII-style border
        instructions_y = 400
        instruction_font = pygame.font.Font(None, 28)
        instructions = [
            "CONTROLS:",
            "WASD - Move",
            "Left Click - Attack",
            "Right Click - Spell",
            "E - Pickup Items",
            "Q - Drop Spell"
        ]
        
        # Draw border around instructions
        border_x = self.screen_width // 2 - 150
        border_y = instructions_y - 20
        border_width = 300
        border_height = len(instructions) * 25 + 40
        
        # ASCII-style border
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (border_x, border_y, border_width, border_height), 2)
        
        for i, instruction in enumerate(instructions):
            color = (255, 215, 0) if i == 0 else (200, 200, 200)  # Gold for title, white for text
            text = instruction_font.render(instruction, True, color)
            text_x = self.screen_width // 2 - text.get_width() // 2
            text_y = instructions_y + i * 25
            self.screen.blit(text, (text_x, text_y))
    
    def render_game_over(self, player, game_state):
        """Render the game over screen with stats."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((20, 0, 0))  # Dark red
        self.screen.blit(overlay, (0, 0))
        
        # Game Over title
        title_font = pygame.font.Font(None, 72)
        stats_font = pygame.font.Font(None, 36)
        menu_font = pygame.font.Font(None, 48)
        
        title_text = title_font.render("GAME OVER", True, (255, 50, 50))  # Red
        title_shadow = title_font.render("GAME OVER", True, (100, 0, 0))  # Dark red shadow
        
        title_x = self.screen_width // 2 - title_text.get_width() // 2
        title_y = 100
        
        # Draw shadow first, then title
        self.screen.blit(title_shadow, (title_x + 3, title_y + 3))
        self.screen.blit(title_text, (title_x, title_y))
        
        # Player stats
        stats_y_start = 220
        stats = [
            f"Final Level: {player.level}",
            f"XP Gained: {player.total_xp}",
            f"Health: {player.current_health}/{player.max_health}",
            f"Enemies Defeated: {game_state.stats.get('enemies_defeated', 0)}",
            f"Time Played: {int(game_state.stats.get('total_playtime', 0))}s"
        ]
        
        for i, stat in enumerate(stats):
            text = stats_font.render(stat, True, (255, 255, 255))
            text_x = self.screen_width // 2 - text.get_width() // 2
            text_y = stats_y_start + i * 40
            self.screen.blit(text, (text_x, text_y))
        
        # Menu options
        menu_y_start = 450
        menu_options = [
            "PRESS R TO RESTART",
            "PRESS ESC TO QUIT"
        ]
        
        for i, option in enumerate(menu_options):
            color = (255, 255, 100) if i == 0 else (200, 200, 200)  # Yellow for restart
            text = menu_font.render(option, True, color)
            text_x = self.screen_width // 2 - text.get_width() // 2
            text_y = menu_y_start + i * 50
            self.screen.blit(text, (text_x, text_y))
    
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
        
        # Health text (floor current HP)
        health_text = f"{int(player.current_health)}/{player.max_health}"
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
    
    def render_minimap(self, player, level, visibility_system=None):
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
        
        # Draw walls and paths (more accurate minimap)
        for y in range(level.height):
            for x in range(level.width):
                tile = level.tiles[y][x]
                
                # Only draw every 2nd tile for performance, but ensure accuracy
                if x % 2 == 0 and y % 2 == 0:
                    tile_x = map_x + int(x * level.tile_size * scale)
                    tile_y = map_y + int(y * level.tile_size * scale)
                    tile_size = max(1, int(level.tile_size * scale * 2))
                    
                    if tile.type == "wall":
                        pygame.draw.rect(self.screen, (100, 100, 100), 
                                       (tile_x, tile_y, tile_size, tile_size))
                    elif tile.type == "floor":
                        # Draw floor paths in a darker color for visibility
                        pygame.draw.rect(self.screen, (70, 70, 70), 
                                       (tile_x, tile_y, tile_size, tile_size))
        
        # Draw player
        player_x = map_x + int(player.position[0] * scale)
        player_y = map_y + int(player.position[1] * scale)
        pygame.draw.circle(self.screen, (100, 150, 255), (player_x, player_y), 3)
        
        # Draw enemies (only if in visibility range)
        for enemy in level.enemies:
            if enemy.is_alive():
                # Only show enemy if it's within fog of war visibility
                if visibility_system:
                    enemy_tile_x = int(enemy.position[0] // level.tile_size)
                    enemy_tile_y = int(enemy.position[1] // level.tile_size)
                    if (enemy_tile_x, enemy_tile_y) not in visibility_system.visible_tiles:
                        continue
                
                enemy_x = map_x + int(enemy.position[0] * scale)
                enemy_y = map_y + int(enemy.position[1] * scale)
                pygame.draw.circle(self.screen, (200, 100, 100), (enemy_x, enemy_y), 2)
        
        # Draw boss (larger, different color)
        if level.boss and level.boss.is_alive():
            # Show boss if it's visible
            if visibility_system:
                boss_tile_x = int(level.boss.position[0] // level.tile_size)
                boss_tile_y = int(level.boss.position[1] // level.tile_size)
                if (boss_tile_x, boss_tile_y) in visibility_system.visible_tiles:
                    boss_x = map_x + int(level.boss.position[0] * scale)
                    boss_y = map_y + int(level.boss.position[1] * scale)
                    pygame.draw.circle(self.screen, (255, 50, 50), (boss_x, boss_y), 4)  # Larger red circle
            else:
                boss_x = map_x + int(level.boss.position[0] * scale)
                boss_y = map_y + int(level.boss.position[1] * scale)
                pygame.draw.circle(self.screen, (255, 50, 50), (boss_x, boss_y), 4)
        
        # Draw key if not collected
        if not level.key_collected and level.key_position:
            if not visibility_system or visibility_system.is_visible(level.key_position):
                key_x = map_x + int(level.key_position[0] * scale)
                key_y = map_y + int(level.key_position[1] * scale)
                pygame.draw.circle(self.screen, (255, 215, 0), (key_x, key_y), 3)  # Gold circle
        
        # Draw altar
        if level.altar_position:
            if not visibility_system or visibility_system.is_visible(level.altar_position):
                altar_x = map_x + int(level.altar_position[0] * scale)
                altar_y = map_y + int(level.altar_position[1] * scale)
                altar_color = (100, 255, 100) if level.key_collected else (150, 150, 150)
                pygame.draw.rect(self.screen, altar_color, (altar_x - 2, altar_y - 2, 4, 4))
    
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
            "Right Click: Ranged/Spell",
            "E: Pickup Item/Use Altar",
            "Q: Drop Spell",
            "P: Pause, ESC: Quit"
        ]
        
        for i, control in enumerate(controls):
            text_surface = self.asset_manager.render_text(control, "small", self.text_color)
            self.screen.blit(text_surface, (x, y + i * 18))
    
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
    
    def render_inventory(self, player):
        """Render the player's equipped items."""
        x = self.margin
        y = self.screen_height - 120
        
        # Background panel
        panel_width = 280
        panel_height = 100
        self.draw_panel(x - 5, y - 5, panel_width, panel_height)
        
        # Title
        title = self.asset_manager.render_text("Equipped Items:", "small", self.text_color)
        self.screen.blit(title, (x, y))
        
        current_y = y + 25
        
        # Melee weapon
        weapon_text = "Melee: "
        if player.inventory.melee_weapon:
            weapon_text += player.inventory.melee_weapon.name
            color = player.inventory.melee_weapon.color
        else:
            weapon_text += "Default Fists"
            color = (200, 200, 200)
        
        weapon_surface = self.asset_manager.render_text(weapon_text, "small", color)
        self.screen.blit(weapon_surface, (x, current_y))
        current_y += 20
        
        # Enchantment
        enchant_text = "Enchant: "
        if player.inventory.enchantment:
            enchant_text += player.inventory.enchantment.name
            color = player.inventory.enchantment.color
        else:
            enchant_text += "None"
            color = (200, 200, 200)
            
        enchant_surface = self.asset_manager.render_text(enchant_text, "small", color)
        self.screen.blit(enchant_surface, (x, current_y))
        current_y += 20
        
        # Spell
        spell_text = "Spell: "
        if player.inventory.spell:
            spell_text += player.inventory.spell.name
            color = player.inventory.spell.color
            
            # Show cooldown if on cooldown
            current_time = pygame.time.get_ticks() / 1000.0
            if not player.inventory.spell.is_ready(current_time):
                remaining = player.inventory.spell.cooldown - (current_time - player.inventory.spell.last_used)
                spell_text += f" ({remaining:.1f}s)"
                color = (150, 150, 150)
        else:
            spell_text += "Default Ranged"
            color = (200, 200, 200)
            
        spell_surface = self.asset_manager.render_text(spell_text, "small", color)
        self.screen.blit(spell_surface, (x, current_y))
    
    def render_game_level_info(self, level):
        """Render current game level information."""
        x = self.screen_width - 150
        y = self.margin
        
        # Background panel
        panel_width = 130
        panel_height = 60
        self.draw_panel(x - 5, y - 5, panel_width, panel_height)
        
        # Level number
        current_level = getattr(level, 'current_game_level', 1)
        max_level = getattr(level, 'max_game_level', 10)
        level_text = f"Level {current_level}/{max_level}"
        level_surface = self.asset_manager.render_text(level_text, "medium", self.text_color)
        self.screen.blit(level_surface, (x, y))
        
        # Key status
        key_text = "Key: " + ("✓" if level.key_collected else "✗")
        key_color = (100, 255, 100) if level.key_collected else (255, 100, 100)
        key_surface = self.asset_manager.render_text(key_text, "small", key_color)
        self.screen.blit(key_surface, (x, y + 25))
        
        # Boss status
        boss_text = "Boss: "
        if level.boss:
            if level.boss.is_alive():
                boss_text += "Alive"
                boss_color = (255, 100, 100)
            else:
                boss_text += "Dead"
                boss_color = (100, 255, 100)
        else:
            boss_text += "None"
            boss_color = (150, 150, 150)
        
        boss_surface = self.asset_manager.render_text(boss_text, "small", boss_color)
        self.screen.blit(boss_surface, (x, y + 40))
