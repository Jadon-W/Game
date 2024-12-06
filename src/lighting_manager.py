# lighting_manager.py

import pygame
import config
import math

class LightingManager:
    def __init__(self, time_manager):
        self.time_manager = time_manager
        # Create surfaces for lighting
        self.daylight = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        self.nightlight = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        self.season_overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        self.update_lighting()
    
    def update_lighting(self):
        """
        Update lighting based on the current time and season with smooth transitions.
        """
        # Reset overlays
        self.daylight.fill((0, 0, 0, 0))
        self.nightlight.fill((0, 0, 0, 0))
        self.season_overlay.fill((0, 0, 0, 0))
        
        # Daylight and nightlight based on time
        if not self.time_manager.is_night():
            # Smooth brightness based on time
            hour = (self.time_manager.current_time / self.time_manager.day_length) * 24
            if hour < 12:
                # Morning: increasing brightness
                brightness = hour / 12  # 0 to 1
            elif hour < 18:
                # Afternoon: full brightness
                brightness = 1
            else:
                # Evening: decreasing brightness
                brightness = (24 - hour) / 6  # 1 to 0
            brightness = max(0, min(brightness, 1))
            alpha = int(255 * brightness)
            self.daylight.fill((255, 255, 255, alpha))
        else:
            # Night: gradual increase in darkness
            hour = (self.time_manager.current_time / self.time_manager.day_length) * 24
            if hour < 6:
                # Early night: increasing darkness
                darkness = hour / 6  # 0 to 1
            elif hour < 12:
                # Late night: constant darkness
                darkness = 1
            else:
                darkness = 1  # Should not occur
            darkness = max(0, min(darkness, 1))
            alpha = int(150 * darkness)
            self.nightlight.fill((0, 0, 50, alpha))
    
        # Season overlays with smooth transitions
        season = self.time_manager.get_current_season()
        if season == 'Spring':
            # Slight green tint
            self.season_overlay.fill((0, 100, 0, 50))
        elif season == 'Summer':
            # Warm tint
            self.season_overlay.fill((255, 165, 0, 30))  # Orange
        elif season == 'Autumn':
            # Orange/brown tint
            self.season_overlay.fill((255, 140, 0, 40))
        elif season == 'Winter':
            # Blue tint
            self.season_overlay.fill((0, 100, 255, 60))
    
    def draw_lighting(self, surface):
        """
        Draw the lighting overlays onto the surface.
        """
        # Draw daylight or nightlight
        if not self.time_manager.is_night():
            surface.blit(self.daylight, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            surface.blit(self.nightlight, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Draw season overlay
        surface.blit(self.season_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
