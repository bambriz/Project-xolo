"""
Weapon rendering system for players and enemies.
Shows equipped weapons visually on characters.
"""

import pygame
import math
from typing import Tuple, Optional

class WeaponRenderer:
    """Handles visual representation of weapons for players and enemies."""
    
    @staticmethod
    def render_equipped_weapon(screen: pygame.Surface, screen_x: int, screen_y: int, 
                             weapon_type: str, radius: int, facing_angle: float = 0.0,
                             is_attacking: bool = False, attack_progress: float = 0.0):
        """Render equipped weapon on character."""
        
        if weapon_type == "fist":
            # Draw two fists on sides of character
            left_fist_x = screen_x - radius - 4
            left_fist_y = screen_y
            right_fist_x = screen_x + radius + 4
            right_fist_y = screen_y
            
            # Fist color
            fist_color = (210, 180, 140)  # Skin tone
            
            # Draw fists
            pygame.draw.circle(screen, fist_color, (int(left_fist_x), int(left_fist_y)), 4)
            pygame.draw.circle(screen, (150, 130, 100), (int(left_fist_x), int(left_fist_y)), 4, 1)
            pygame.draw.circle(screen, fist_color, (int(right_fist_x), int(right_fist_y)), 4)
            pygame.draw.circle(screen, (150, 130, 100), (int(right_fist_x), int(right_fist_y)), 4, 1)
            
        elif weapon_type == "sword":
            # Draw sword on right side
            base_offset = radius + 8
            if is_attacking:
                # Sword swings during attack
                swing_angle = facing_angle + (attack_progress * math.pi / 4)
            else:
                swing_angle = facing_angle
                
            sword_x = screen_x + math.cos(swing_angle) * base_offset
            sword_y = screen_y + math.sin(swing_angle) * base_offset
            sword_tip_x = sword_x + math.cos(swing_angle) * 15  # Reduced by 25% from 20
            sword_tip_y = sword_y + math.sin(swing_angle) * 15
            
            # Draw blade
            pygame.draw.line(screen, (200, 200, 220), (int(sword_x), int(sword_y)), 
                           (int(sword_tip_x), int(sword_tip_y)), 3)
            
            # Draw hilt
            hilt_x = sword_x - math.cos(swing_angle) * 4
            hilt_y = sword_y - math.sin(swing_angle) * 4
            pygame.draw.circle(screen, (139, 69, 19), (int(hilt_x), int(hilt_y)), 3)
            
        elif weapon_type == "mace":
            # Draw mace on right side
            base_offset = radius + 8
            if is_attacking:
                swing_angle = facing_angle + (attack_progress * math.pi / 3)
            else:
                swing_angle = facing_angle
                
            handle_x = screen_x + math.cos(swing_angle) * base_offset
            handle_y = screen_y + math.sin(swing_angle) * base_offset
            head_x = handle_x + math.cos(swing_angle) * 16
            head_y = handle_y + math.sin(swing_angle) * 16
            
            # Draw handle
            pygame.draw.line(screen, (139, 69, 19), (int(screen_x), int(screen_y)), 
                           (int(handle_x), int(handle_y)), 2)
            
            # Draw mace head
            pygame.draw.circle(screen, (128, 128, 128), (int(head_x), int(head_y)), 5)
            pygame.draw.circle(screen, (100, 100, 100), (int(head_x), int(head_y)), 5, 1)
            
        elif weapon_type == "spear":
            # Draw spear on right side (longer)
            base_offset = radius + 12
            if is_attacking:
                # Spear pokes forward during attack
                poke_distance = base_offset + (attack_progress * 10)
            else:
                poke_distance = base_offset
                
            spear_x = screen_x + math.cos(facing_angle) * poke_distance
            spear_y = screen_y + math.sin(facing_angle) * poke_distance
            spear_tip_x = spear_x + math.cos(facing_angle) * 23  # Increased by 30% from 18
            spear_tip_y = spear_y + math.sin(facing_angle) * 23
            
            # Draw shaft
            pygame.draw.line(screen, (139, 69, 19), (int(screen_x), int(screen_y)), 
                           (int(spear_x), int(spear_y)), 2)
            
            # Draw spear tip
            pygame.draw.line(screen, (200, 200, 220), (int(spear_x), int(spear_y)), 
                           (int(spear_tip_x), int(spear_tip_y)), 3)
            pygame.draw.circle(screen, (180, 180, 200), (int(spear_tip_x), int(spear_tip_y)), 2)
            
        elif weapon_type == "dagger":
            # Draw small dagger on right side
            base_offset = radius + 6
            if is_attacking:
                stab_angle = facing_angle + (attack_progress * math.pi / 6)
            else:
                stab_angle = facing_angle
                
            dagger_x = screen_x + math.cos(stab_angle) * base_offset
            dagger_y = screen_y + math.sin(stab_angle) * base_offset
            dagger_tip_x = dagger_x + math.cos(stab_angle) * 12
            dagger_tip_y = dagger_y + math.sin(stab_angle) * 12
            
            # Draw blade (silver)
            pygame.draw.line(screen, (200, 200, 220), (int(dagger_x), int(dagger_y)), 
                           (int(dagger_tip_x), int(dagger_tip_y)), 3)
            # Draw small handle guard
            guard_x1 = dagger_x + math.cos(stab_angle + math.pi/2) * 3
            guard_y1 = dagger_y + math.sin(stab_angle + math.pi/2) * 3
            guard_x2 = dagger_x + math.cos(stab_angle - math.pi/2) * 3
            guard_y2 = dagger_y + math.sin(stab_angle - math.pi/2) * 3
            pygame.draw.line(screen, (150, 150, 160), (int(guard_x1), int(guard_y1)), (int(guard_x2), int(guard_y2)), 2)
            
        elif weapon_type == "war_axe":
            # Draw war axe with proper double-bladed design
            base_offset = radius + 8
            if is_attacking:
                swing_angle = facing_angle + (attack_progress * math.pi * 0.4)  # Reduced swing arc
            else:
                swing_angle = facing_angle
                
            # Handle position (from center to axe head)
            handle_x = screen_x + math.cos(swing_angle) * base_offset
            handle_y = screen_y + math.sin(swing_angle) * base_offset
            axe_head_x = handle_x + math.cos(swing_angle) * 15
            axe_head_y = handle_y + math.sin(swing_angle) * 15
            
            # Draw wooden handle (brown)
            pygame.draw.line(screen, (101, 67, 33), (int(screen_x), int(screen_y)), 
                           (int(axe_head_x), int(axe_head_y)), 4)
            
            # Create proper axe blade shape (double-bladed)
            # Upper blade
            upper_blade = [
                (axe_head_x, axe_head_y),  # Center point
                (axe_head_x + math.cos(swing_angle + math.pi/3) * 12, axe_head_y + math.sin(swing_angle + math.pi/3) * 12),
                (axe_head_x + math.cos(swing_angle + math.pi/6) * 8, axe_head_y + math.sin(swing_angle + math.pi/6) * 8)
            ]
            # Lower blade
            lower_blade = [
                (axe_head_x, axe_head_y),  # Center point
                (axe_head_x + math.cos(swing_angle - math.pi/3) * 12, axe_head_y + math.sin(swing_angle - math.pi/3) * 12),
                (axe_head_x + math.cos(swing_angle - math.pi/6) * 8, axe_head_y + math.sin(swing_angle - math.pi/6) * 8)
            ]
            
            # Convert to integer coordinates
            upper_blade = [(int(x), int(y)) for x, y in upper_blade]
            lower_blade = [(int(x), int(y)) for x, y in lower_blade]
            
            # Draw axe blades (steel gray)
            pygame.draw.polygon(screen, (160, 160, 170), upper_blade)
            pygame.draw.polygon(screen, (160, 160, 170), lower_blade)
            # Blade outlines (darker)
            pygame.draw.polygon(screen, (120, 120, 130), upper_blade, 2)
            pygame.draw.polygon(screen, (120, 120, 130), lower_blade, 2)
            
        elif weapon_type == "twin_blades":
            # Draw two small blades
            base_offset = radius + 6
            if is_attacking:
                stab_angle = facing_angle + (attack_progress * math.pi / 8)
            else:
                stab_angle = facing_angle
                
            # First blade
            blade1_x = screen_x + math.cos(stab_angle + 0.2) * base_offset
            blade1_y = screen_y + math.sin(stab_angle + 0.2) * base_offset
            blade1_tip_x = blade1_x + math.cos(stab_angle + 0.2) * 10
            blade1_tip_y = blade1_y + math.sin(stab_angle + 0.2) * 10
            
            # Second blade
            blade2_x = screen_x + math.cos(stab_angle - 0.2) * base_offset
            blade2_y = screen_y + math.sin(stab_angle - 0.2) * base_offset
            blade2_tip_x = blade2_x + math.cos(stab_angle - 0.2) * 10
            blade2_tip_y = blade2_y + math.sin(stab_angle - 0.2) * 10
            
            # Draw both blades
            pygame.draw.line(screen, (200, 200, 220), (int(blade1_x), int(blade1_y)), 
                           (int(blade1_tip_x), int(blade1_tip_y)), 2)
            pygame.draw.line(screen, (200, 200, 220), (int(blade2_x), int(blade2_y)), 
                           (int(blade2_tip_x), int(blade2_tip_y)), 2)
            
        elif weapon_type == "ranged":
            # Draw staff/wand for ranged enemies
            base_offset = radius + 6
            staff_x = screen_x + math.cos(facing_angle) * base_offset
            staff_y = screen_y + math.sin(facing_angle) * base_offset - 4
            staff_tip_x = staff_x + math.cos(facing_angle) * 20
            staff_tip_y = staff_y + math.sin(facing_angle) * 20
            
            # Draw staff
            pygame.draw.line(screen, (139, 69, 19), (int(screen_x), int(screen_y)), 
                           (int(staff_tip_x), int(staff_tip_y)), 2)
            
            # Draw magical orb at tip
            orb_color = (100, 150, 255) if not is_attacking else (255, 200, 100)
            pygame.draw.circle(screen, orb_color, (int(staff_tip_x), int(staff_tip_y)), 3)
            pygame.draw.circle(screen, (200, 200, 255), (int(staff_tip_x), int(staff_tip_y)), 3, 1)
    
    @staticmethod
    def get_weapon_facing_angle(position: Tuple[float, float], target_position: Tuple[float, float]) -> float:
        """Calculate facing angle towards target."""
        dx = target_position[0] - position[0]
        dy = target_position[1] - position[1]
        return math.atan2(dy, dx)