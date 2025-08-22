"""
Sound and music management system.
Handles loading and playing sound effects and background music.
"""

import pygame
import os
from typing import Dict, Optional

class SoundManager:
    """Manages game audio including sound effects and music."""
    
    def __init__(self):
        """Initialize the sound manager."""
        self.enabled = True
        self.sound_effects: Dict[str, pygame.mixer.Sound] = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        
        # Initialize pygame mixer if not already done
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                print("Sound system initialized")
            except pygame.error:
                print("Sound system failed to initialize - running without audio")
                self.enabled = False
                return
        
        # Define expected sound files
        self.expected_sounds = {
            # Player sounds
            'player_hit': 'player_hit.ogg',
            'player_death': 'player_death.ogg',
            'level_up': 'level_up.ogg',
            
            # Combat sounds
            'sword_swing': 'sword_swing.ogg',
            'spear_thrust': 'spear_thrust.ogg',
            'mace_smash': 'mace_smash.ogg',
            'ranged_attack': 'ranged_attack.ogg',
            'enemy_hit': 'enemy_hit.ogg',
            'enemy_death': 'enemy_death.ogg',
            
            # Spell sounds
            'haste_cast': 'haste_cast.ogg',
            'power_pulse': 'power_pulse.ogg',
            'turn_coat': 'turn_coat.ogg',
            
            # Boss sounds
            'boss_spawn': 'boss_spawn.ogg',
            'boss_death': 'boss_death.ogg',
            'flame_charge': 'flame_charge.ogg',
            'fire_spin': 'fire_spin.ogg',
            'ice_shard': 'ice_shard.ogg',
            'frost_nova': 'frost_nova.ogg',
            'lightning_bolt': 'lightning_bolt.ogg',
            'chain_lightning': 'chain_lightning.ogg',
            'shadow_bolt': 'shadow_bolt.ogg',
            'dark_storm': 'dark_storm.ogg',
            
            # Item sounds
            'item_pickup': 'item_pickup.ogg',
            'key_pickup': 'key_pickup.ogg',
            'altar_activate': 'altar_activate.ogg',
            
            # Music tracks
            'menu_music': 'menu_music.ogg',
            'level_1_music': 'level_1_music.ogg',
            'level_3_music': 'level_3_music.ogg',
            'level_6_music': 'level_6_music.ogg',
            'boss_music': 'boss_music.ogg',
            'final_boss_music': 'final_boss_music.ogg',
            'victory_music': 'victory_music.ogg'
        }
        
        # Load available sounds
        self.load_sounds()
    
    def load_sounds(self):
        """Load available sound files from the sounds directory."""
        sounds_dir = "sounds"
        
        if not os.path.exists(sounds_dir):
            print(f"Sounds directory '{sounds_dir}' not found - creating directory")
            os.makedirs(sounds_dir, exist_ok=True)
            self.print_missing_sounds_info()
            return
        
        loaded_count = 0
        
        for sound_name, filename in self.expected_sounds.items():
            filepath = os.path.join(sounds_dir, filename)
            
            if os.path.exists(filepath):
                try:
                    sound = pygame.mixer.Sound(filepath)
                    sound.set_volume(self.sfx_volume)
                    self.sound_effects[sound_name] = sound
                    loaded_count += 1
                except pygame.error as e:
                    print(f"Failed to load {filename}: {e}")
        
        print(f"Loaded {loaded_count}/{len(self.expected_sounds)} sound files")
        
        if loaded_count == 0:
            self.print_missing_sounds_info()
    
    def print_missing_sounds_info(self):
        """Print information about missing sound files."""
        print("\n" + "="*60)
        print("SOUND FILES NOT FOUND - RUNNING IN SILENT MODE")
        print("="*60)
        print("To add sound effects, place these files in the 'sounds/' directory:")
        print("\nPlayer Sounds:")
        print("  • player_hit.ogg - Player takes damage")
        print("  • player_death.ogg - Player dies")
        print("  • level_up.ogg - Player gains a level")
        
        print("\nCombat Sounds:")
        print("  • sword_swing.ogg - Sword attack")
        print("  • spear_thrust.ogg - Spear attack")
        print("  • mace_smash.ogg - Mace attack")
        print("  • ranged_attack.ogg - Ranged projectile")
        print("  • enemy_hit.ogg - Enemy takes damage")
        print("  • enemy_death.ogg - Enemy dies")
        
        print("\nSpell Sounds:")
        print("  • haste_cast.ogg - Haste spell")
        print("  • power_pulse.ogg - Power Pulse spell")
        print("  • turn_coat.ogg - Turn Coat spell")
        
        print("\nBoss Sounds:")
        print("  • boss_spawn.ogg - Boss appears")
        print("  • boss_death.ogg - Boss defeated")
        print("  • flame_charge.ogg - Flame Berserker charge")
        print("  • fire_spin.ogg - Fire spin attack")
        print("  • ice_shard.ogg - Ice projectile")
        print("  • frost_nova.ogg - Frost explosion")
        print("  • lightning_bolt.ogg - Lightning strike")
        print("  • chain_lightning.ogg - Chain lightning")
        print("  • shadow_bolt.ogg - Shadow projectile")
        print("  • dark_storm.ogg - Dark energy storm")
        
        print("\nItem Sounds:")
        print("  • item_pickup.ogg - Pick up weapon/enchantment/spell")
        print("  • key_pickup.ogg - Pick up level key")
        print("  • altar_activate.ogg - Activate altar")
        
        print("\nMusic Tracks:")
        print("  • menu_music.ogg - Title/menu screen")
        print("  • level_1_music.ogg - Levels 1-2")
        print("  • level_3_music.ogg - Levels 3-5")
        print("  • level_6_music.ogg - Levels 6-9")
        print("  • boss_music.ogg - Boss fights (levels 3,6,9)")
        print("  • final_boss_music.ogg - Final boss (level 10)")
        print("  • victory_music.ogg - Game complete")
        
        print("\nSupported formats: OGG Vorbis (recommended), MP3, WAV")
        print("="*60)
    
    def play_sound(self, sound_name: str, volume: Optional[float] = None):
        """Play a sound effect."""
        if not self.enabled or sound_name not in self.sound_effects:
            return
        
        try:
            sound = self.sound_effects[sound_name]
            if volume is not None:
                sound.set_volume(volume)
            else:
                sound.set_volume(self.sfx_volume)
            sound.play()
        except pygame.error:
            pass  # Silently fail if sound can't play
    
    def play_music(self, music_name: str, loop: bool = True):
        """Play background music."""
        if not self.enabled or music_name not in self.expected_sounds:
            return
        
        filepath = os.path.join("sounds", self.expected_sounds[music_name])
        
        if os.path.exists(filepath):
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1 if loop else 0)
            except pygame.error:
                pass
    
    def stop_music(self):
        """Stop the current music."""
        if self.enabled:
            pygame.mixer.music.stop()
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sound_effects.values():
            sound.set_volume(self.sfx_volume)
    
    def get_music_for_level(self, level: int) -> str:
        """Get appropriate music track for a level."""
        if level == 10:
            return 'final_boss_music'
        elif level % 3 == 0:  # Boss levels
            return 'boss_music'
        elif level >= 6:
            return 'level_6_music'
        elif level >= 3:
            return 'level_3_music'
        else:
            return 'level_1_music'
    
    def play_combat_sound(self, weapon_type: str):
        """Play appropriate combat sound based on weapon type."""
        sound_map = {
            'sword': 'sword_swing',
            'spear': 'spear_thrust',
            'mace': 'mace_smash',
            'default': 'ranged_attack'  # For fists/ranged
        }
        
        sound_name = sound_map.get(weapon_type, 'ranged_attack')
        self.play_sound(sound_name)
    
    def play_spell_sound(self, spell_type: str):
        """Play appropriate spell sound."""
        spell_sounds = {
            'haste': 'haste_cast',
            'power_pulse': 'power_pulse',
            'turn_coat': 'turn_coat'
        }
        
        sound_name = spell_sounds.get(spell_type, 'ranged_attack')
        self.play_sound(sound_name)
    
    def play_boss_ability_sound(self, ability_name: str):
        """Play boss ability sound effect."""
        ability_sounds = {
            'flame_charge': 'flame_charge',
            'fire_spin': 'fire_spin',
            'ice_shard': 'ice_shard',
            'frost_nova': 'frost_nova',
            'lightning_bolt': 'lightning_bolt',
            'chain_lightning': 'chain_lightning',
            'shadow_bolt': 'shadow_bolt',
            'dark_storm': 'dark_storm'
        }
        
        sound_name = ability_sounds.get(ability_name)
        if sound_name:
            self.play_sound(sound_name)