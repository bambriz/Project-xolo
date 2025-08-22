"""
Enemy classes and AI behavior.
Handles different enemy types, AI states, and combat behavior.
"""

import pygame
import math
import random
from typing import Tuple, List, Optional
from weapon_renderer import WeaponRenderer

class Enemy:
    """Base enemy class with AI behavior and combat capabilities."""
    
    def __init__(self, position: Tuple[float, float], enemy_type: str = "basic", player_level: int = 1):
        """Initialize enemy with position and type."""
        self.position = list(position)
        self.enemy_type = enemy_type
        self.radius = 12
        
        # AI state
        self.state = "idle"  # Enhanced states: idle, chasing, attacking, mind_controlled, kiting, flanking, knocked_back
        self.ai_strategy = self.determine_ai_strategy()  # Strategy based on enemy type
        self.target_position = None
        self.last_seen_player_pos = None
        self.last_attack_time = 0
        self.sight_range = 150
        self.attack_range = 35  # Increased for better spacing
        self.give_up_time = 5.0  # seconds to chase last known position
        self.last_player_seen_time = 0
        
        # Movement (initialize speed first)
        self.speed = 80 + (player_level - 1) * 10  # Scales with player level
        self.velocity = [0.0, 0.0]
        
        # Set stats based on enemy type and player level
        self.setup_stats(enemy_type, player_level)
        
        # Set weapon based on enemy type
        self.setup_weapon(enemy_type)
        
        # Pathfinding and roaming
        self.path_update_timer = 0
        self.path_update_interval = 0.5  # Update path every 0.5 seconds
        self.spawn_position = list(position)  # Remember spawn location
        self.roam_radius = 120  # How far from spawn to roam
        self.roam_target = None
        self.roam_timer = 0
        self.roam_interval = random.uniform(3, 6)  # Change roam target every 3-6 seconds
        
        # Vision and raycasting
        self.vision_range = 180  # How far enemy can see
        self.last_raycast_time = 0
        self.raycast_interval = 0.3  # Raycast every 0.3 seconds
        
        # Visual
        self.setup_appearance()
        
        # Hit effects
        self.hit_effect_time = 0.0
        self.hit_effect_duration = 0.3  # Flash for 0.3 seconds when hit
        
        # Knockback state
        self.knocked_back = False
        self.knockback_timer = 0.0
        self.knockback_duration = 1.2  # Pause for 1.2 seconds after knockback
        self.knockback_velocity = [0.0, 0.0]
        self.knockback_speed = 200.0  # Speed of knockback movement
        self.knockback_immunity = False  # Can't be knocked back again while immune
        
        print(f"Created {enemy_type} enemy (level {player_level}) with {self.current_health} HP")
    
    def add_hit_effect(self):
        """Add a visual hit effect when the enemy takes damage."""
        self.hit_effect_time = self.hit_effect_duration
        
    def apply_knockback(self, direction_angle: float, force: float):
        """Apply smooth knockback to the enemy."""
        if self.knocked_back or self.knockback_immunity:
            return  # Can't be knocked back while already in knockback state or immune
            
        # Enter knockback state
        self.knocked_back = True
        self.knockback_timer = self.knockback_duration
        self.knockback_immunity = True  # Become immune to more knockback
        self.state = "knocked_back"
        
        # Calculate knockback velocity
        self.knockback_velocity[0] = math.cos(direction_angle) * force
        self.knockback_velocity[1] = math.sin(direction_angle) * force
        
        print(f"{self.enemy_type} enemy knocked back for {self.knockback_duration}s")
    
    def setup_stats(self, enemy_type: str, player_level: int):
        """Set up enemy stats based on type and player level."""
        base_stats = {
            "basic": {"health": 50, "damage": 15, "xp": 25, "attack_speed": 1.5, "weapon": "fist"},
            "fast": {"health": 30, "damage": 15, "xp": 20, "attack_speed": 0.6, "weapon": "dagger"},  # More aggressive
            "heavy": {"health": 80, "damage": 25, "xp": 40, "attack_speed": 2.5, "weapon": "sword"},
            "ranged": {"health": 40, "damage": 20, "xp": 35, "attack_speed": 2.0, "weapon": "ranged"},
            "mobile_ranged": {"health": 35, "damage": 18, "xp": 30, "attack_speed": 1.8, "weapon": "ranged"},
            "berserker": {"health": 120, "damage": 35, "xp": 60, "attack_speed": 2.0, "weapon": "war_axe"},
            "assassin": {"health": 25, "damage": 20, "xp": 45, "attack_speed": 0.8, "weapon": "twin_blades"},
            "juggernaut": {"health": 150, "damage": 30, "xp": 80, "attack_speed": 3.0, "weapon": "war_axe"},  # Tanky slow enemy
            "archer": {"health": 35, "damage": 22, "xp": 35, "attack_speed": 1.5, "weapon": "ranged"},  # Precise ranged
            "scout": {"health": 20, "damage": 10, "xp": 15, "attack_speed": 0.5, "weapon": "dagger"},  # Fast scout
            "guardian": {"health": 100, "damage": 18, "xp": 50, "attack_speed": 2.0, "weapon": "spear"}  # Defensive
        }
        
        stats = base_stats.get(enemy_type, base_stats["basic"])
        
        # Scale stats with player level
        level_multiplier = 1 + (player_level - 1) * 0.3
        
        self.max_health = int(stats["health"] * level_multiplier)
        self.current_health = self.max_health
        self.damage = int(stats["damage"] * level_multiplier)
        self.xp_value = int(stats["xp"] * level_multiplier)
        self.attack_cooldown = stats["attack_speed"]
        
        # Special abilities based on type
        if enemy_type == "fast":
            self.speed *= 2.5  # Even faster for more challenge
            self.sight_range *= 1.6  # Much better sight range
            self.preferred_terrain = "open"  # Prefer open spaces for flanking
        elif enemy_type == "heavy":
            self.radius = 16
            self.attack_range = 25
        elif enemy_type == "ranged":
            self.attack_range = 100
            self.sight_range *= 1.8  # Much better sight range
        elif enemy_type == "mobile_ranged":
            self.attack_range = 80
            self.sight_range *= 1.8  # Much better sight range for challenge
            self.kite_behavior = True  # Enhanced kiting
    
    def setup_appearance(self):
        """Set up visual appearance based on enemy type."""
        colors = {
            "basic": (200, 100, 100),    # Red
            "fast": (100, 200, 100),     # Green
            "heavy": (150, 150, 150),    # Gray
            "ranged": (200, 200, 100)    # Yellow
        }
        
        self.color = colors.get(self.enemy_type, colors["basic"])
        self.outline_color = (255, 255, 255)
        
        # Mind control status
        self.mind_controlled = False
        self.mind_control_end_time = 0.0
        self.mind_control_target = None  # Stick to one target
        self.can_be_damaged_by_enemies = False  # Can other enemies damage this one
        
        # Weapon rendering properties
        self.weapon_offset = self.calculate_weapon_offset()
        
        # Visual indicators for enchantment
        self.enchanted_color = (255, 165, 0)  # Orange for mind control
    
    def setup_weapon(self, enemy_type: str):
        """Set up weapon properties based on enemy type."""
        weapon_configs = {
            "basic": {  # Weakest - uses fist
                "weapon_type": "fist",
                "range": 45,  # Better spacing from player
                "arc": 90,
                "speed_multiplier": 1.0
            },
            "fast": {  # Dagger - low damage, increased range, super fast
                "weapon_type": "dagger",
                "range": 45,  # Better spacing from player
                "arc": 165,  # Fixed to 165° as requested
                "speed_multiplier": 2.0,
                "damage_multiplier": 0.8
            },
            "heavy": {  # Uses mace, spear, or sword
                "weapon_type": random.choice(["mace", "spear", "sword"]),
                "range": 50,  # Better spacing from player
                "arc": 145,
                "speed_multiplier": 0.8
            },
            "berserker": {  # NEW: High damage, medium speed, intimidating
                "weapon_type": "war_axe",
                "range": 55,
                "arc": 160,  # Wide sweeping attacks
                "speed_multiplier": 1.2,
                "damage_multiplier": 1.5
            },
            "assassin": {  # NEW: Very fast, low health, high crit chance
                "weapon_type": "twin_blades",
                "range": 40,
                "arc": 90,
                "speed_multiplier": 2.5,
                "damage_multiplier": 1.1
            },
            "ranged": {  # Ranged attacker
                "weapon_type": "ranged",
                "range": 100,
                "arc": 15,
                "speed_multiplier": 1.0
            },
            "mobile_ranged": {  # Fast moving ranged attacker that kites player
                "weapon_type": "ranged",
                "range": 80,
                "arc": 20,
                "speed_multiplier": 1.5,
                "kite_behavior": True  # Moves away from player
            }
        }
        
        config = weapon_configs.get(enemy_type, weapon_configs["basic"])
        self.weapon_type = config["weapon_type"]
        self.weapon_range = config["range"]
        self.weapon_arc = config["arc"]
        self.weapon_speed_multiplier = config.get("speed_multiplier", 1.0)
        self.weapon_damage_multiplier = config.get("damage_multiplier", 1.0)
        self.kite_behavior = config.get("kite_behavior", False)
        
        # Adjust attack speed based on weapon
        self.attack_cooldown /= self.weapon_speed_multiplier
        # Store base attack cooldown for flanking behavior resets
        self.base_attack_cooldown = self.attack_cooldown
    
    def determine_ai_strategy(self) -> str:
        """Determine AI strategy based on enemy type."""
        strategies = {
            "basic": "aggressive",       # Face player head-on
            "fast": "flanking",          # Move in and out, flank
            "heavy": "tank",             # Face player head-on, slow but steady
            "ranged": "kiting",          # Keep distance, move away
            "mobile_ranged": "kiting",   # Enhanced kiting behavior
            "berserker": "aggressive",   # Full frontal assault
            "assassin": "flanking"       # Hit and run tactics
        }
        return strategies.get(self.enemy_type, "aggressive")
    
    def calculate_weapon_offset(self) -> Tuple[float, float]:
        """Calculate weapon rendering offset based on weapon type."""
        if self.weapon_type == "fist":
            return (0, 0)  # Fists render on sides
        elif self.weapon_type in ["sword", "mace", "war_axe", "dagger", "twin_blades"]:
            return (self.radius + 8, 0)  # Right side of enemy
        elif self.weapon_type == "spear":
            return (self.radius + 12, 0)  # Longer weapon, more offset
        elif self.weapon_type == "ranged":
            return (self.radius + 6, -4)  # Staff/wand position
        return (0, 0)
    
    def update(self, dt: float, player, level, can_see_player: bool):
        """Update enemy AI and behavior."""
        if not self.is_alive():
            return
        
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Check mind control status
        if self.mind_controlled and current_time >= self.mind_control_end_time:
            self.mind_controlled = False
            print(f"{self.enemy_type} enemy is no longer mind controlled")
        
        # Update projectiles for ranged enemies
        if hasattr(self, 'projectiles'):
            for projectile in self.projectiles[:]:
                projectile.update(dt)
                if projectile.should_remove():
                    self.projectiles.remove(projectile)
                elif projectile.check_collision_with_target(player, player.radius):
                    if player.take_damage(projectile.damage):
                        print(f"Ranged projectile hit player for {projectile.damage} damage!")
                    self.projectiles.remove(projectile)
        
        # Update AI state based on player visibility (mind controlled enemies act differently)
        if not self.mind_controlled:
            self.update_ai_state(player, can_see_player, current_time)
        else:
            # Mind controlled enemies attack other enemies instead
            self.state = "mind_controlled"
            self.can_be_damaged_by_enemies = True  # Can be damaged by other enemies
            self.mind_control_behavior(dt, level, current_time)
        
        # Execute behavior based on current state and AI strategy
        if self.state == "idle":
            self.idle_behavior(dt)
        elif self.state == "chasing":
            self.strategic_chase_behavior(dt, player, level, current_time)
        elif self.state == "attacking":
            self.strategic_attack_behavior(dt, player, current_time)
        elif self.state == "mind_controlled":
            pass  # Already handled in mind_control_behavior
        elif self.state == "kiting":
            self.kiting_behavior(dt, player, current_time)
        elif self.state == "flanking":
            self.flanking_behavior(dt, player, current_time)
        elif self.state == "knocked_back":
            self.update_knockback(dt)
            return  # Skip other updates while knocked back
        
        # Apply movement
        self.apply_movement(dt, level)
        
        # Clear knockback immunity after recovery
        if self.knockback_immunity and not self.knocked_back:
            self.knockback_immunity = False
        
        # Update attack animations
        if hasattr(self, 'attack_animations'):
            for animation in self.attack_animations[:]:
                animation['lifetime'] -= dt
                if animation['lifetime'] <= 0:
                    self.attack_animations.remove(animation)
                    
    def update_knockback(self, dt: float):
        """Handle knockback state updates."""
        self.knockback_timer -= dt
        
        if self.knockback_timer > 0.8:  # First 0.4s: move back quickly
            # Apply knockback velocity with decay
            self.velocity[0] = self.knockback_velocity[0]
            self.velocity[1] = self.knockback_velocity[1]
            
            # Reduce knockback velocity over time
            self.knockback_velocity[0] *= 0.85
            self.knockback_velocity[1] *= 0.85
        else:
            # Stop moving and pause
            self.velocity[0] = 0
            self.velocity[1] = 0
            
        if self.knockback_timer <= 0:
            # End knockback state
            self.knocked_back = False
            self.state = "idle"
            self.velocity[0] = 0
            self.velocity[1] = 0
            print(f"{self.enemy_type} enemy recovered from knockback")
    
    def raycast_to_player(self, player, level) -> bool:
        """Use raycasting to check if enemy has line of sight to player."""
        # Check distance first
        dx = player.position[0] - self.position[0]
        dy = player.position[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > self.vision_range:
            return False
        
        # Raycast from enemy to player
        steps = int(distance / (level.tile_size / 4))  # Quarter-tile steps for accuracy
        
        for i in range(1, steps):
            progress = i / steps
            check_x = self.position[0] + dx * progress
            check_y = self.position[1] + dy * progress
            
            # Check if this point is in a wall
            if level.check_wall_collision((check_x, check_y), 1):
                return False
        
        return True
    
    def update_ai_state(self, player, can_see_player: bool, current_time: float):
        """Enhanced AI state based on player visibility, distance, and raycasting."""
        player_distance = self.distance_to_player(player)
        
        # Enhanced line of sight check with raycasting
        if can_see_player and player_distance <= self.vision_range:
            # Use raycasting for more accurate vision
            if current_time - self.last_raycast_time >= self.raycast_interval:
                self.last_raycast_time = current_time
                has_line_of_sight = True  # Assume visibility system already handles basic LOS
            else:
                has_line_of_sight = self.last_seen_player_pos is not None
            
            if has_line_of_sight:
                self.last_seen_player_pos = player.position[:]
                self.last_player_seen_time = current_time
                
                if player_distance <= self.attack_range:
                    self.state = "attacking"
                else:
                    self.state = "chasing"
        
        elif self.state == "chasing" and self.last_seen_player_pos:
            # Continue chasing last known position for a while
            if current_time - self.last_player_seen_time > self.give_up_time:
                self.state = "idle"
                self.last_seen_player_pos = None
        
        elif self.state == "attacking":
            # If we can't see player anymore, start chasing last known position
            if self.last_seen_player_pos:
                self.state = "chasing"
            else:
                self.state = "idle"
    
    def idle_behavior(self, dt: float):
        """Improved idle behavior with smart roaming around spawn area."""
        self.roam_timer += dt
        
        # Check if we need a new roam target
        if self.roam_timer >= self.roam_interval or not self.roam_target:
            self.roam_timer = 0
            self.roam_interval = random.uniform(3, 6)
            
            # Pick a random point within roam radius from spawn
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(20, self.roam_radius)
            
            new_x = self.spawn_position[0] + math.cos(angle) * distance
            new_y = self.spawn_position[1] + math.sin(angle) * distance
            self.roam_target = [new_x, new_y]
        
        # Move towards roam target
        if self.roam_target:
            dx = self.roam_target[0] - self.position[0]
            dy = self.roam_target[1] - self.position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 10:  # Move if not close enough
                self.velocity[0] = (dx / distance) * self.speed * 0.4  # Slower roaming
                self.velocity[1] = (dy / distance) * self.speed * 0.4
            else:
                # Reached target, stop and wait
                self.velocity[0] *= 0.8
                self.velocity[1] *= 0.8
        else:
            # Gradually stop moving
            self.velocity[0] *= 0.9
            self.velocity[1] *= 0.9
    
    def chase_behavior(self, dt: float, player, level, current_time: float):
        """Enhanced chase behavior with better spacing and menace."""
        target_pos = self.last_seen_player_pos if self.last_seen_player_pos else player.position
        
        # Calculate direction to target
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        # Start menacing attacks when getting close (before in range)
        if distance <= self.weapon_range * 1.3:  # Start attacking at 130% of weapon range for menace
            self.state = "attacking"
            return
        
        # Mobile ranged enemies use kiting behavior
        if self.kite_behavior and distance < self.weapon_range * 0.8:
            # Move away from player to maintain distance
            self.velocity[0] = -(dx / distance) * self.speed
            self.velocity[1] = -(dy / distance) * self.speed
        elif distance > self.weapon_range * 0.7:  # Maintain optimal distance
            # Move closer but not too close
            self.velocity[0] = (dx / distance) * self.speed * 0.9
            self.velocity[1] = (dy / distance) * self.speed * 0.9
        else:
            # At good distance, circle around player slightly
            angle_offset = math.pi * 0.2  # Small circle movement
            circle_dx = math.cos(math.atan2(dy, dx) + angle_offset)
            circle_dy = math.sin(math.atan2(dy, dx) + angle_offset)
            self.velocity[0] = circle_dx * self.speed * 0.3
            self.velocity[1] = circle_dy * self.speed * 0.3
    
    def strategic_chase_behavior(self, dt: float, player, level, current_time: float):
        """Enhanced chase behavior based on AI strategy."""
        if self.ai_strategy == "kiting":
            self.state = "kiting"
        elif self.ai_strategy == "flanking":
            self.state = "flanking"
        else:
            # Default aggressive chase behavior
            self.chase_behavior(dt, player, level, current_time)
    
    def strategic_attack_behavior(self, dt: float, player, current_time: float):
        """Enhanced attack behavior based on AI strategy."""
        if self.ai_strategy == "aggressive" or self.ai_strategy == "tank":
            # Face player head-on, stop moving when attacking
            self.velocity[0] = 0
            self.velocity[1] = 0
        # Execute attack
        self.attack_behavior(dt, player, current_time)
    
    def kiting_behavior(self, dt: float, player, current_time: float):
        """Kiting behavior - maintain distance and attack from range."""
        dx = player.position[0] - self.position[0]
        dy = player.position[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        optimal_distance = self.weapon_range * 0.8
        
        if distance < optimal_distance:
            # Move away from player
            if distance > 0:
                self.velocity[0] = -(dx / distance) * self.speed
                self.velocity[1] = -(dy / distance) * self.speed
        elif distance > self.weapon_range:
            # Move closer but not too close
            if distance > 0:
                self.velocity[0] = (dx / distance) * self.speed * 0.7
                self.velocity[1] = (dy / distance) * self.speed * 0.7
        else:
            # At good distance, attack
            self.velocity[0] *= 0.5
            self.velocity[1] *= 0.5
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self.attack_player(player)
                self.last_attack_time = current_time
    
    def flanking_behavior(self, dt: float, player, current_time: float):
        """Enhanced flanking behavior - aggressive hit-and-run tactics, especially from sides/behind."""
        dx = player.position[0] - self.position[0]
        dy = player.position[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        # Calculate relative position to player (front, side, or behind)
        player_facing = getattr(player, 'last_movement_angle', 0)  # Default facing right
        if hasattr(player, 'velocity') and (player.velocity[0] != 0 or player.velocity[1] != 0):
            player_facing = math.atan2(player.velocity[1], player.velocity[0])
        
        enemy_angle = math.atan2(dy, dx)
        relative_angle = abs(enemy_angle - player_facing)
        relative_angle = min(relative_angle, 2 * math.pi - relative_angle)  # Normalize to 0-π
        
        # Determine position relative to player
        is_behind = relative_angle > 2.5  # Behind player
        is_side = 1.0 < relative_angle <= 2.5  # To the side
        is_front = relative_angle <= 1.0  # In front
        
        # Aggressive sprint distance for flanking attacks
        sprint_distance = self.weapon_range * 1.8
        attack_distance = self.weapon_range * 1.1
        
        if distance <= self.weapon_range:
            # In attack range - aggressive multi-hit if behind or to side
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self.attack_player(player)
                self.last_attack_time = current_time
                
                # Aggressive follow-up behavior based on position
                if is_behind or is_side:
                    # Stay close for another attack if flanking
                    self.attack_cooldown *= 0.7  # Faster attacks when flanking
                    # Quick sidestep to maintain flanking position
                    sidestep_angle = enemy_angle + (math.pi/2 if random.random() > 0.5 else -math.pi/2)
                    self.velocity[0] = math.cos(sidestep_angle) * self.speed * 0.6
                    self.velocity[1] = math.sin(sidestep_angle) * self.speed * 0.6
                else:
                    # Move away quickly if attacking from front
                    escape_angle = enemy_angle + math.pi + random.uniform(-math.pi/3, math.pi/3)
                    self.velocity[0] = math.cos(escape_angle) * self.speed * 1.2
                    self.velocity[1] = math.sin(escape_angle) * self.speed * 1.2
            else:
                # Continue aggressive pressure if behind/side
                if is_behind or is_side:
                    # Stay close, circle tightly
                    circle_speed = self.speed * 0.8
                    circle_angle = enemy_angle + (math.pi/3 if random.random() > 0.5 else -math.pi/3)
                    self.velocity[0] = math.cos(circle_angle) * circle_speed
                    self.velocity[1] = math.sin(circle_angle) * circle_speed
                else:
                    # Back away if in front
                    retreat_angle = enemy_angle + math.pi
                    self.velocity[0] = math.cos(retreat_angle) * self.speed * 0.9
                    self.velocity[1] = math.sin(retreat_angle) * self.speed * 0.9
                    
        elif distance <= sprint_distance:
            # Sprint in aggressively, especially if behind or to side
            if is_behind or is_side:
                # Aggressive sprint attack - double speed
                sprint_speed = self.speed * 2.0
                attack_angle = math.atan2(dy, dx)
                self.velocity[0] = math.cos(attack_angle) * sprint_speed
                self.velocity[1] = math.sin(attack_angle) * sprint_speed
                print(f"Fast enemy sprinting in from {'behind' if is_behind else 'side'}!")
            else:
                # Normal approach from front
                self.velocity[0] = (dx / distance) * self.speed * 1.3
                self.velocity[1] = (dy / distance) * self.speed * 1.3
                
        else:
            # Position for flanking attack - move to sides or behind
            target_angle = player_facing + (math.pi * 0.75 if random.random() > 0.5 else -math.pi * 0.75)  # 3/4 around
            flanking_distance = self.weapon_range * 1.5
            
            # Calculate flanking position
            flank_x = player.position[0] + math.cos(target_angle) * flanking_distance
            flank_y = player.position[1] + math.sin(target_angle) * flanking_distance
            
            # Move toward flanking position quickly
            to_flank_x = flank_x - self.position[0]
            to_flank_y = flank_y - self.position[1]
            to_flank_dist = math.sqrt(to_flank_x**2 + to_flank_y**2)
            
            if to_flank_dist > 0:
                move_speed = self.speed * 1.4  # Fast flanking movement
                self.velocity[0] = (to_flank_x / to_flank_dist) * move_speed
                self.velocity[1] = (to_flank_y / to_flank_dist) * move_speed

    def attack_behavior(self, dt: float, player, current_time: float):
        """Attack behavior - attack player when in range."""
        # Stop moving when attacking
        self.velocity[0] = 0
        self.velocity[1] = 0
        
        # Attack if cooldown is ready
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.attack_player(player)
            self.last_attack_time = current_time
    
    def attack_player(self, player):
        """Attack the player using their weapon type with visual effects."""
        damage = int(self.damage * self.weapon_damage_multiplier)
        
        # Calculate attack direction to player
        dx = player.position[0] - self.position[0]
        dy = player.position[1] - self.position[1]
        attack_angle = math.atan2(dy, dx)
        
        if self.weapon_type == "ranged":
            # Create visual projectile for ranged enemies
            from combat import Projectile
            projectile = Projectile(
                (self.position[0], self.position[1]),  # Start from enemy position
                (player.position[0], player.position[1]),  # Target player position
                damage,
                300  # Projectile speed
            )
            if not hasattr(self, 'projectiles'):
                self.projectiles = []
            self.projectiles.append(projectile)
            print(f"{self.enemy_type} enemy shoots at player!")
        else:
            # Melee attack with visual animation
            self.create_attack_animation(attack_angle)
            # Check if player is in range for melee hit
            distance = math.sqrt(dx**2 + dy**2)
            if distance <= self.weapon_range:
                player.take_damage(damage)
                print(f"{self.enemy_type} enemy attacks player with {self.weapon_type}!")
            else:
                print(f"{self.enemy_type} enemy swings but misses (too far)!")
    
    def apply_movement(self, dt: float, level):
        """Apply movement with collision detection."""
        # Try horizontal movement
        new_x = self.position[0] + self.velocity[0] * dt
        if not level.check_wall_collision((new_x, self.position[1]), self.radius):
            self.position[0] = new_x
        else:
            self.velocity[0] = 0
        
        # Try vertical movement
        new_y = self.position[1] + self.velocity[1] * dt
        if not level.check_wall_collision((self.position[0], new_y), self.radius):
            self.position[1] = new_y
        else:
            self.velocity[1] = 0
    
    def take_damage(self, amount: int) -> bool:
        """Take damage and return True if enemy dies."""
        self.current_health = max(0, self.current_health - amount)
        
        if self.current_health <= 0:
            self.state = "dead"
            print(f"{self.enemy_type} enemy defeated!")
            return True
        
        return False
    
    def distance_to_player(self, player) -> float:
        """Calculate distance to player."""
        dx = player.position[0] - self.position[0]
        dy = player.position[1] - self.position[1]
        return math.sqrt(dx**2 + dy**2)
    
    def is_alive(self) -> bool:
        """Check if enemy is alive."""
        return self.current_health > 0 and self.state != "dead"
    
    def get_health_percentage(self) -> float:
        """Get health as a percentage."""
        return self.current_health / self.max_health if self.max_health > 0 else 0.0
    
    def render(self, screen: pygame.Surface, camera_x: int, camera_y: int, asset_manager):
        """Render the enemy on screen (full rendering)."""
        self.render_body(screen, camera_x, camera_y, asset_manager)
        self.render_attack_animations_only(screen, camera_x, camera_y)
    
    def render_body(self, screen: pygame.Surface, camera_x: int, camera_y: int, asset_manager):
        """Render just the enemy body without attack animations."""
        if not self.is_alive():
            return
        
        # Calculate screen position
        screen_x = int(self.position[0] + camera_x)
        screen_y = int(self.position[1] + camera_y)
        
        # Determine current color (with hit effect and mind control)
        current_color = self.color
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Apply hit effect (white flash)
        if current_time < self.hit_effect_time + self.hit_effect_duration:
            flash_intensity = 1.0 - ((current_time - self.hit_effect_time) / self.hit_effect_duration)
            current_color = (
                int(self.color[0] + (255 - self.color[0]) * flash_intensity),
                int(self.color[1] + (255 - self.color[1]) * flash_intensity),
                int(self.color[2] + (255 - self.color[2]) * flash_intensity)
            )
        
        # Draw enemy circle
        pygame.draw.circle(screen, current_color, (screen_x, screen_y), self.radius)
        
        # Draw mind control indicator if enchanted
        if self.mind_controlled:
            pygame.draw.circle(screen, self.enchanted_color, (screen_x, screen_y), self.radius + 3, 2)
            # Pulsing effect
            pulse = int(20 * (0.5 + 0.5 * math.sin(current_time * 8)))
            pygame.draw.circle(screen, (255, 165, 0, pulse), (screen_x, screen_y), self.radius + 5, 1)
        
        pygame.draw.circle(screen, self.outline_color, (screen_x, screen_y), self.radius, 1)
        
        # Draw state indicator
        self.draw_state_indicator(screen, screen_x, screen_y)
        
        # Draw health bar if damaged
        if self.current_health < self.max_health:
            self.draw_health_bar(screen, screen_x, screen_y - self.radius - 8)
        
        # Render equipped weapon when not attacking
        if not hasattr(self, 'attack_animations') or not self.attack_animations:
            facing_angle = 0  # Default facing right
            if hasattr(self, 'last_seen_player_pos') and self.last_seen_player_pos:
                facing_angle = WeaponRenderer.get_weapon_facing_angle(
                    (self.position[0], self.position[1]), 
                    (self.last_seen_player_pos[0], self.last_seen_player_pos[1])
                )
            WeaponRenderer.render_equipped_weapon(
                screen, screen_x, screen_y, self.weapon_type, self.radius, facing_angle
            )
        
        # Render ranged projectiles
        if hasattr(self, 'projectiles'):
            for projectile in self.projectiles:
                projectile_x = int(projectile.position[0] + camera_x)
                projectile_y = int(projectile.position[1] + camera_y)
                # Draw enemy projectile as red dot
                pygame.draw.circle(screen, (255, 100, 100), (projectile_x, projectile_y), 4)
                pygame.draw.circle(screen, (200, 0, 0), (projectile_x, projectile_y), 4, 1)
    
    def render_attack_animations_only(self, screen: pygame.Surface, camera_x: int, camera_y: int):
        """Render only the attack animations (to be drawn above player)."""
        if not self.is_alive():
            return
            
        # Render attack animations
        if hasattr(self, 'attack_animations'):
            for animation in self.attack_animations:
                self.render_attack_animation(screen, camera_x, camera_y, animation)
    
    def draw_state_indicator(self, screen: pygame.Surface, screen_x: int, screen_y: int):
        """Draw a small indicator showing enemy state."""
        indicator_colors = {
            "idle": (100, 100, 100),
            "chasing": (255, 200, 0),
            "attacking": (255, 0, 0)
        }
        
        color = indicator_colors.get(self.state, (100, 100, 100))
        pygame.draw.circle(screen, color, (screen_x, screen_y), 3)
    
    def draw_health_bar(self, screen: pygame.Surface, x: int, y: int):
        """Draw health bar above enemy."""
        bar_width = 20
        bar_height = 3
        health_percentage = self.get_health_percentage()
        
        # Background (red)
        pygame.draw.rect(screen, (200, 50, 50), 
                        (x - bar_width // 2, y, bar_width, bar_height))
        
        # Health (green)
        health_width = int(bar_width * health_percentage)
        if health_width > 0:
            pygame.draw.rect(screen, (50, 200, 50), 
                            (x - bar_width // 2, y, health_width, bar_height))
    
    def create_attack_animation(self, attack_angle: float):
        """Create attack animation using the equipped weapon's actual swing range and type."""
        if not hasattr(self, 'attack_animations'):
            self.attack_animations = []
        
        # Use the weapon's actual arc for realistic swing animations
        weapon_arc_radians = math.radians(getattr(self, 'weapon_arc', 90))
        
        # Create animation based on actual equipped weapon type with proper swing range
        if self.weapon_type == "sword":
            animation = {
                'type': 'enemy_sword_swing',
                'angle': attack_angle,
                'lifetime': 0.3,
                'max_lifetime': 0.3,
                'arc': weapon_arc_radians,
                'range': self.weapon_range,
                'swing_start': attack_angle - weapon_arc_radians / 2,
                'swing_end': attack_angle + weapon_arc_radians / 2,
                'color': (200, 200, 220)  # Silver blade
            }
        elif self.weapon_type == "spear":
            animation = {
                'type': 'enemy_spear_poke',
                'angle': attack_angle,
                'lifetime': 0.25,
                'max_lifetime': 0.25,
                'range': self.weapon_range,
                'color': (180, 180, 200)  # Spear tip
            }
        elif self.weapon_type == "mace":
            animation = {
                'type': 'enemy_mace_swing',
                'angle': attack_angle,
                'lifetime': 0.4,
                'max_lifetime': 0.4,
                'arc': weapon_arc_radians,  # Maces have 145° arc
                'range': self.weapon_range,
                'swing_start': attack_angle - weapon_arc_radians / 2,
                'swing_end': attack_angle + weapon_arc_radians / 2,
                'color': (160, 160, 160)  # Gray mace
            }
        elif self.weapon_type == "dagger":
            animation = {
                'type': 'enemy_dagger_stab',
                'angle': attack_angle,
                'lifetime': 0.15,  # Fast dagger attack
                'max_lifetime': 0.15,
                'range': self.weapon_range,
                'arc': weapon_arc_radians,  # Daggers have 165° arc
                'swing_start': attack_angle - weapon_arc_radians / 2,
                'swing_end': attack_angle + weapon_arc_radians / 2,
                'color': (220, 220, 240)  # Sharp blade
            }
        elif self.weapon_type == "war_axe":
            animation = {
                'type': 'enemy_axe_swing',
                'angle': attack_angle,
                'lifetime': 0.35,
                'max_lifetime': 0.35,
                'arc': weapon_arc_radians,  # War axes have 160° arc
                'range': self.weapon_range,
                'swing_start': attack_angle - weapon_arc_radians / 2,
                'swing_end': attack_angle + weapon_arc_radians / 2,
                'color': (180, 50, 50)  # Red axe
            }
        elif self.weapon_type == "twin_blades":
            animation = {
                'type': 'enemy_twin_stab',
                'angle': attack_angle,
                'lifetime': 0.12,  # Very fast twin blade attack
                'max_lifetime': 0.12,
                'range': self.weapon_range,
                'arc': weapon_arc_radians,  # Twin blades have 90° arc
                'swing_start': attack_angle - weapon_arc_radians / 2,
                'swing_end': attack_angle + weapon_arc_radians / 2,
                'color': (240, 240, 250)  # Bright blades
            }
        else:  # fist or default
            animation = {
                'type': 'enemy_punch',
                'angle': attack_angle,
                'lifetime': 0.2,
                'max_lifetime': 0.2,
                'arc': weapon_arc_radians,  # Fists have 90° arc
                'range': self.weapon_range,
                'swing_start': attack_angle - weapon_arc_radians / 2,
                'swing_end': attack_angle + weapon_arc_radians / 2,
                'color': (255, 150, 150)  # Light red for fist
            }
        
        self.attack_animations.append(animation)
    
    def render_attack_animation(self, screen: pygame.Surface, camera_x: int, camera_y: int, animation):
        """Render enemy attack animation matching weapon's actual swing range."""
        screen_x = int(self.position[0] + camera_x)
        screen_y = int(self.position[1] + camera_y)
        
        progress = 1.0 - (animation['lifetime'] / animation['max_lifetime'])
        
        if animation['type'] == 'enemy_sword_swing':
            # Sword swing animation with proper arc
            if 'swing_start' in animation and 'swing_end' in animation:
                # Animate the swing across the weapon's arc
                current_angle = animation['swing_start'] + (animation['swing_end'] - animation['swing_start']) * progress
                swing_distance = animation['range'] * (0.7 + 0.3 * progress)
                end_x = screen_x + math.cos(current_angle) * swing_distance
                end_y = screen_y + math.sin(current_angle) * swing_distance
                pygame.draw.line(screen, animation['color'], (screen_x, screen_y), (end_x, end_y), 3)
                # Add sword glint effect
                pygame.draw.circle(screen, (255, 255, 255), (int(end_x), int(end_y)), 2)
            
        elif animation['type'] == 'enemy_spear_poke':
            # Spear poke animation (straight thrust)
            poke_distance = animation['range'] * (0.5 + 0.5 * math.sin(progress * math.pi))
            end_x = screen_x + math.cos(animation['angle']) * poke_distance
            end_y = screen_y + math.sin(animation['angle']) * poke_distance
            pygame.draw.line(screen, animation['color'], (screen_x, screen_y), (end_x, end_y), 4)
            pygame.draw.circle(screen, (180, 180, 180), (int(end_x), int(end_y)), 3)
            
        elif animation['type'] == 'enemy_mace_swing':
            # Mace swing animation with proper arc
            if 'swing_start' in animation and 'swing_end' in animation:
                # Animate the swing across the weapon's arc (145° for maces)
                current_angle = animation['swing_start'] + (animation['swing_end'] - animation['swing_start']) * progress
                swing_distance = animation['range'] * (0.7 + 0.3 * progress)
                end_x = screen_x + math.cos(current_angle) * swing_distance
                end_y = screen_y + math.sin(current_angle) * swing_distance
                # Draw handle
                handle_end = swing_distance * 0.7
                handle_x = screen_x + math.cos(current_angle) * handle_end
                handle_y = screen_y + math.sin(current_angle) * handle_end
                pygame.draw.line(screen, (139, 69, 19), (screen_x, screen_y), (handle_x, handle_y), 3)
                # Draw mace head
                pygame.draw.circle(screen, animation['color'], (int(end_x), int(end_y)), 6)
            
        elif animation['type'] == 'enemy_dagger_stab':
            # Dagger stab animation with wide arc (165°)
            if 'swing_start' in animation and 'swing_end' in animation:
                current_angle = animation['swing_start'] + (animation['swing_end'] - animation['swing_start']) * progress
                stab_distance = animation['range'] * (0.8 + 0.2 * math.sin(progress * math.pi * 2))
                end_x = screen_x + math.cos(current_angle) * stab_distance
                end_y = screen_y + math.sin(current_angle) * stab_distance
                pygame.draw.line(screen, animation['color'], (screen_x, screen_y), (end_x, end_y), 2)
                # Add multiple stab lines for twin blades effect
                for offset in [-0.1, 0.1]:
                    offset_x = end_x + math.cos(current_angle + offset) * 5
                    offset_y = end_y + math.sin(current_angle + offset) * 5
                    pygame.draw.line(screen, animation['color'], (screen_x, screen_y), (offset_x, offset_y), 1)
            
        elif animation['type'] == 'enemy_axe_swing':
            # War axe swing animation with 160° arc
            if 'swing_start' in animation and 'swing_end' in animation:
                current_angle = animation['swing_start'] + (animation['swing_end'] - animation['swing_start']) * progress
                swing_distance = animation['range'] * (0.7 + 0.3 * progress)
                end_x = screen_x + math.cos(current_angle) * swing_distance
                end_y = screen_y + math.sin(current_angle) * swing_distance
                # Draw handle
                handle_end = swing_distance * 0.6
                handle_x = screen_x + math.cos(current_angle) * handle_end
                handle_y = screen_y + math.sin(current_angle) * handle_end
                pygame.draw.line(screen, (139, 69, 19), (screen_x, screen_y), (handle_x, handle_y), 4)
                # Draw axe head (triangular)
                axe_size = 8
                for i in range(3):
                    point_angle = current_angle + (i - 1) * 0.3
                    point_x = end_x + math.cos(point_angle) * axe_size
                    point_y = end_y + math.sin(point_angle) * axe_size
                    pygame.draw.circle(screen, animation['color'], (int(point_x), int(point_y)), 2)
            
        elif animation['type'] == 'enemy_twin_stab':
            # Twin blades stab with 90° arc
            if 'swing_start' in animation and 'swing_end' in animation:
                current_angle = animation['swing_start'] + (animation['swing_end'] - animation['swing_start']) * progress
                stab_distance = animation['range'] * (0.9 + 0.1 * math.sin(progress * math.pi * 3))
                # Draw two blades
                for blade_offset in [-0.2, 0.2]:
                    blade_angle = current_angle + blade_offset
                    end_x = screen_x + math.cos(blade_angle) * stab_distance
                    end_y = screen_y + math.sin(blade_angle) * stab_distance
                    pygame.draw.line(screen, animation['color'], (screen_x, screen_y), (end_x, end_y), 2)
            
        else:  # enemy_punch (fist)
            # Fist punch animation with 90° arc
            if 'swing_start' in animation and 'swing_end' in animation:
                current_angle = animation['swing_start'] + (animation['swing_end'] - animation['swing_start']) * progress
                punch_distance = animation['range'] * (0.6 + 0.4 * math.sin(progress * math.pi))
                end_x = screen_x + math.cos(current_angle) * punch_distance
                end_y = screen_y + math.sin(current_angle) * punch_distance
                pygame.draw.circle(screen, animation['color'], (int(end_x), int(end_y)), 5)
                pygame.draw.circle(screen, (150, 150, 150), (int(end_x), int(end_y)), 5, 1)
    
    def mind_control_behavior(self, dt: float, level, current_time: float):
        """Enhanced mind control - stick to one target until dead or spell ends."""
        # If no target or current target is dead, find a new one
        if (not self.mind_control_target or 
            not self.mind_control_target.is_alive() or 
            self.mind_control_target.mind_controlled):
            
            # Find nearest alive, non-mind-controlled enemy
            self.mind_control_target = None
            min_distance = float('inf')
            
            # Check all enemies including boss as valid targets
            for enemy in level.enemies:
                if (enemy != self and enemy.is_alive() and not enemy.mind_controlled):
                    distance = self.distance_to_enemy(enemy)
                    if distance < min_distance:
                        min_distance = distance
                        self.mind_control_target = enemy
            
            # Also check boss as a valid target
            if level.boss and level.boss != self and level.boss.is_alive() and not level.boss.mind_controlled:
                boss_distance = self.distance_to_enemy(level.boss)
                if boss_distance < min_distance:
                    self.mind_control_target = level.boss
        
        if self.mind_control_target:
            target_distance = self.distance_to_enemy(self.mind_control_target)
            
            # Attack behavior with improved spacing
            if target_distance <= self.weapon_range:
                self.state = "attacking"
                if current_time - self.last_attack_time >= self.attack_cooldown:
                    # Create attack animation
                    dx = self.mind_control_target.position[0] - self.position[0]
                    dy = self.mind_control_target.position[1] - self.position[1]
                    attack_angle = math.atan2(dy, dx)
                    self.create_attack_animation(attack_angle)
                    
                    # Attack the target enemy
                    self.mind_control_target.take_damage(self.damage)
                    self.last_attack_time = current_time
                    print(f"Mind controlled {self.enemy_type} attacks {self.mind_control_target.enemy_type}!")
            else:
                self.state = "chasing"
                # Move towards target with spacing
                optimal_distance = self.weapon_range * 0.8  # Stay at 80% of weapon range
                
                if target_distance > optimal_distance:
                    # Move closer
                    dx = self.mind_control_target.position[0] - self.position[0]
                    dy = self.mind_control_target.position[1] - self.position[1]
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance > 0:
                        self.velocity[0] = (dx / distance) * self.speed * 0.9
                        self.velocity[1] = (dy / distance) * self.speed * 0.9
                else:
                    # Maintain distance, circle around target
                    self.velocity[0] *= 0.5
                    self.velocity[1] *= 0.5
        else:
            # No valid targets, return to spawn area
            dx = self.spawn_position[0] - self.position[0]
            dy = self.spawn_position[1] - self.position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 20:
                self.velocity[0] = (dx / distance) * self.speed * 0.3
                self.velocity[1] = (dy / distance) * self.speed * 0.3
            else:
                self.state = "idle"
                self.velocity = [0.0, 0.0]

    def distance_to_enemy(self, other_enemy) -> float:
        """Calculate distance to another enemy."""
        dx = other_enemy.position[0] - self.position[0]
        dy = other_enemy.position[1] - self.position[1]
        return math.sqrt(dx * dx + dy * dy)

def create_enemy(position: Tuple[float, float], player_level: int) -> Enemy:
    """Factory function to create a random enemy appropriate for the player level."""
    enemy_types = ["basic", "fast", "heavy"]
    
    # Add ranged enemies at higher levels
    if player_level >= 2:
        enemy_types.append("ranged")
    
    enemy_type = random.choice(enemy_types)
    return Enemy(position, enemy_type, player_level)

# Add the missing method to Enemy class
def add_hit_effect(self):
    """Add visual hit effect when enemy takes damage."""
    self.hit_effect_time = pygame.time.get_ticks() / 1000.0

# Hit effect method added above within class
