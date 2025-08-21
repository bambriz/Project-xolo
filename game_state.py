"""
Game state management and global game data.
Handles game phases, settings, and persistent data.
"""

import pygame
from typing import Dict, Any

class GameState:
    """Manages global game state and settings."""
    
    def __init__(self):
        """Initialize game state."""
        # Game phases
        self.phase = "playing"  # "menu", "playing", "paused", "game_over"
        
        # Game settings
        self.settings = {
            "master_volume": 0.7,
            "sfx_volume": 0.8,
            "music_volume": 0.6,
            "fullscreen": False,
            "show_fps": False,
            "show_debug_info": False,
            "difficulty": "normal"  # "easy", "normal", "hard"
        }
        
        # Statistics
        self.stats = {
            "total_playtime": 0.0,
            "enemies_defeated": 0,
            "levels_completed": 0,
            "total_damage_dealt": 0,
            "total_damage_taken": 0,
            "highest_level_reached": 1,
            "total_xp_gained": 0
        }
        
        # Game session data
        self.session_start_time = pygame.time.get_ticks() / 1000.0
        self.current_level_start_time = pygame.time.get_ticks() / 1000.0
        
        print("Game state initialized")
    
    def update(self, dt: float):
        """Update game state."""
        self.stats["total_playtime"] += dt
    
    def set_phase(self, new_phase: str):
        """Change game phase."""
        old_phase = self.phase
        self.phase = new_phase
        
        if old_phase != new_phase:
            print(f"Game phase changed: {old_phase} -> {new_phase}")
            
            # Handle phase-specific logic
            if new_phase == "playing":
                self.current_level_start_time = pygame.time.get_ticks() / 1000.0
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """Set a setting value."""
        self.settings[key] = value
        print(f"Setting changed: {key} = {value}")
    
    def get_stat(self, key: str, default: Any = 0) -> Any:
        """Get a statistic value."""
        return self.stats.get(key, default)
    
    def increment_stat(self, key: str, amount: Any = 1):
        """Increment a statistic."""
        if key in self.stats:
            self.stats[key] += amount
        else:
            self.stats[key] = amount
    
    def record_enemy_defeat(self, enemy_type: str, xp_gained: int):
        """Record an enemy defeat."""
        self.increment_stat("enemies_defeated")
        self.increment_stat("total_xp_gained", xp_gained)
        print(f"Recorded enemy defeat: {enemy_type} (+{xp_gained} XP)")
    
    def record_level_completion(self):
        """Record level completion."""
        self.increment_stat("levels_completed")
        current_time = pygame.time.get_ticks() / 1000.0
        level_time = current_time - self.current_level_start_time
        print(f"Level completed in {level_time:.1f} seconds")
    
    def record_damage_dealt(self, amount: int):
        """Record damage dealt by player."""
        self.increment_stat("total_damage_dealt", amount)
    
    def record_damage_taken(self, amount: int):
        """Record damage taken by player."""
        self.increment_stat("total_damage_taken", amount)
    
    def update_highest_level(self, level: int):
        """Update highest level reached."""
        if level > self.stats["highest_level_reached"]:
            self.stats["highest_level_reached"] = level
            print(f"New highest level reached: {level}")
    
    def get_session_time(self) -> float:
        """Get current session playtime in seconds."""
        current_time = pygame.time.get_ticks() / 1000.0
        return current_time - self.session_start_time
    
    def get_level_time(self) -> float:
        """Get current level playtime in seconds."""
        current_time = pygame.time.get_ticks() / 1000.0
        return current_time - self.current_level_start_time
    
    def format_time(self, seconds: float) -> str:
        """Format time in seconds to MM:SS format."""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_difficulty_multiplier(self) -> float:
        """Get multiplier based on difficulty setting."""
        multipliers = {
            "easy": 0.8,
            "normal": 1.0,
            "hard": 1.3
        }
        return multipliers.get(self.settings["difficulty"], 1.0)
    
    def save_settings(self, filename: str = "settings.txt"):
        """Save settings to file (basic implementation)."""
        try:
            with open(filename, 'w') as f:
                for key, value in self.settings.items():
                    f.write(f"{key}={value}\n")
            print(f"Settings saved to {filename}")
        except Exception as e:
            print(f"Failed to save settings: {e}")
    
    def load_settings(self, filename: str = "settings.txt"):
        """Load settings from file (basic implementation)."""
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # Try to convert to appropriate type
                        if value.lower() in ('true', 'false'):
                            value = value.lower() == 'true'
                        elif value.replace('.', '').isdigit():
                            value = float(value) if '.' in value else int(value)
                        self.settings[key] = value
            print(f"Settings loaded from {filename}")
        except FileNotFoundError:
            print(f"Settings file {filename} not found, using defaults")
        except Exception as e:
            print(f"Failed to load settings: {e}")
    
    def reset_stats(self):
        """Reset all statistics."""
        for key in self.stats:
            if isinstance(self.stats[key], (int, float)):
                self.stats[key] = 0
        print("Statistics reset")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about game state."""
        return {
            "phase": self.phase,
            "session_time": self.format_time(self.get_session_time()),
            "level_time": self.format_time(self.get_level_time()),
            "enemies_defeated": self.stats["enemies_defeated"],
            "levels_completed": self.stats["levels_completed"],
            "difficulty": self.settings["difficulty"]
        }
