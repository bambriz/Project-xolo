"""
UI notification system for item pickups and drops.
Shows fading text messages with item descriptions.
"""

import pygame
from typing import List, Tuple

class Notification:
    """Represents a UI notification message."""
    
    def __init__(self, message: str, notification_type: str = "pickup"):
        self.message = message
        self.notification_type = notification_type  # "pickup", "drop"
        
        # Visual properties
        if notification_type == "pickup":
            self.color = (100, 255, 100)  # Green for pickups
        else:
            self.color = (255, 200, 100)  # Orange for drops
            
        self.font_size = 24
        self.lifetime = 3.0  # Duration in seconds
        self.max_lifetime = 3.0
        
        # Position (will be set by manager)
        self.y_offset = 0
        
        # Create font
        self.font = pygame.font.Font(None, self.font_size)
        
    def update(self, dt: float) -> bool:
        """Update the notification. Returns False if it should be removed."""
        self.lifetime -= dt
        return self.lifetime > 0
    
    def render(self, screen: pygame.Surface, x: int, y: int):
        """Render the notification on screen."""
        # Calculate alpha based on lifetime
        alpha_factor = self.lifetime / self.max_lifetime
        alpha = int(255 * alpha_factor)
        
        # Create text surface
        text = self.font.render(self.message, True, self.color)
        
        # Apply alpha (fade out effect)
        if alpha < 255:
            text.set_alpha(alpha)
        
        # Render text
        screen.blit(text, (x, y + self.y_offset))
        
        return text.get_height()  # Return height for stacking

class NotificationManager:
    """Manages UI notifications."""
    
    def __init__(self, screen_width: int):
        self.notifications: List[Notification] = []
        self.screen_width = screen_width
        self.base_x = 20  # Left margin
        self.base_y = 100  # Top margin (below other UI elements)
    
    def add_pickup_notification(self, item_name: str, description: str):
        """Add an item pickup notification."""
        message = f"Picked up {item_name}: {description}"
        notification = Notification(message, "pickup")
        self.notifications.append(notification)
        self._update_positions()
    
    def add_drop_notification(self, item_name: str):
        """Add an item drop notification."""
        message = f"Dropped {item_name}"
        notification = Notification(message, "drop")
        self.notifications.append(notification)
        self._update_positions()
    
    def _update_positions(self):
        """Update Y positions for stacking notifications."""
        for i, notification in enumerate(self.notifications):
            notification.y_offset = i * 30  # Stack with 30px spacing
    
    def update(self, dt: float):
        """Update all notifications."""
        # Update existing notifications and remove expired ones
        self.notifications = [
            notification for notification in self.notifications 
            if notification.update(dt)
        ]
        # Update positions after removal
        self._update_positions()
    
    def render(self, screen: pygame.Surface):
        """Render all notifications."""
        for notification in self.notifications:
            notification.render(screen, self.base_x, self.base_y)
    
    def clear(self):
        """Clear all notifications."""
        self.notifications.clear()