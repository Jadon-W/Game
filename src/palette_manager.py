# palette_manager.py

import pygame
import config

class PaletteManager:
    def __init__(self):
        self.current_palette = 'day'  # Default palette
    
    def set_palette(self, palette_name):
        if palette_name in config.PALETTES:
            self.current_palette = palette_name
        else:
            print(f"Palette {palette_name} not found. Using default.")
            self.current_palette = 'spring_day'
    
    def apply_palette(self, surface):
        """
        Apply the current palette to the given surface.
        Assumes surface is in grayscale for palette application.
        """
        # Create a copy to avoid modifying the original surface
        palette_surface = surface.copy()
        # Lock the surface for pixel access
        palette_surface.lock()
        for x in range(palette_surface.get_width()):
            for y in range(palette_surface.get_height()):
                pixel = palette_surface.get_at((x, y))
                # Assuming the surface is grayscale, use the red channel
                gray = pixel.r
                # Map gray to palette color
                if gray == 0:
                    color = config.PALETTES[self.current_palette][0]
                elif gray == 85:
                    color = config.PALETTES[self.current_palette][1]
                elif gray == 170:
                    color = config.PALETTES[self.current_palette][2]
                elif gray == 255:
                    color = config.PALETTES[self.current_palette][2]
                else:
                    # Interpolate or choose nearest color
                    color = config.PALETTES[self.current_palette][2]
                palette_surface.set_at((x, y), color)
        palette_surface.unlock()
        return palette_surface
