# camera.py

import config

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.offset_x = 0
        self.offset_y = 0

    def update(self, player, world):
        """
        Update the camera's offset based on the player's position.
        """
        # Center the camera on the player
        self.offset_x = player.rect.centerx - self.width // 2
        self.offset_y = player.rect.centery - self.height // 2

        # Clamp the camera to the world boundaries
        self.offset_x = max(0, min(self.offset_x, world.width - self.width))
        self.offset_y = max(0, min(self.offset_y, world.height - self.height))
        
 
