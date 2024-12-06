# time_manager.py

import pygame
import config

class TimeManager:
    def __init__(self):
        self.current_time = 0  # Time in minutes
        self.day_length = 1440  # Minutes per in-game day (24*60)
        self.time_speed = 1  # Game time progresses 1 minute per real second
        
        # Seasons: 4 seasons, each lasting a certain number of days
        self.seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
        self.current_season_index = 0
        self.days_per_season = 30
        self.current_day = 1
        
        # Lighting overlays
        self.overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        self.update_overlays()
    
    def update(self, dt):
        """
        Update the time based on delta time.
        """
        # Increment time
        self.current_time += dt * self.time_speed
        
        # Handle day transitions
        if self.current_time >= self.day_length:
            self.current_time -= self.day_length
            self.current_day += 1
            self.change_season()
        
        self.update_overlays()
    
    def change_season(self):
        """
        Advance to the next season.
        """
        self.current_season_index = (self.current_season_index + 1) % len(self.seasons)
        print(f"Season changed to {self.get_current_season()}!")
        # Potentially change biome properties based on season
        # For example, adjust tile colors or spawn rates
    
    def get_current_season(self):
        return self.seasons[self.current_season_index]
    
    def get_time_of_day(self):
        """
        Determine the phase of the day.
        """
        # Define phases: dawn, day, dusk, night
        hour = (self.current_time / self.day_length) * 24
        if 5 <= hour < 7:
            return 'dawn'
        elif 7 <= hour < 18:
            return 'day'
        elif 18 <= hour < 20:
            return 'dusk'
        else:
            return 'night'
    
    def update_overlays(self):
        """
        Update lighting overlays and seasonal color shifts based on time.
        """
        phase = self.get_time_of_day()
        
        # Reset overlay
        self.overlay.fill((0, 0, 0, 0))
        
        # Apply seasonal color shifts
        self.apply_seasonal_tint()
        
        # Handle day/night transitions
        if phase == 'day':
            # No overlay needed
            pass
        elif phase == 'dawn':
            # Gradually decrease darkness
            progress = (self.current_time - 300) / 120  # 5:00 to 7:00
            alpha = int(150 * (1 - progress))  # 150 to 0
            self.overlay.fill((0, 0, 0, alpha))
        elif phase == 'dusk':
            # Gradually increase darkness
            progress = (self.current_time - 1080) / 120  # 18:00 to 20:00
            alpha = int(150 * progress)  # 0 to 150
            self.overlay.fill((0, 0, 0, alpha))
        elif phase == 'night':
            # Full darkness
            self.overlay.fill((0, 0, 0, 150))
    def apply_seasonal_tint(self):
        """
        Apply a color tint based on the current season.
        """
        season = self.get_current_season()
        tint_color = (0, 0, 0, 0)  # Default no tint
        
        if season == 'Spring':
            tint_color = (34, 139, 34, 30)  # Light green tint
        elif season == 'Summer':
            tint_color = (255, 215, 0, 30)  # Gold tint
        elif season == 'Autumn':
            tint_color = (255, 140, 0, 30)  # Orange tint
        elif season == 'Winter':
            tint_color = (173, 216, 230, 30)  # Light blue tint
        
        if tint_color != (0, 0, 0, 0):
            tint_overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            tint_overlay.fill(tint_color)
            self.overlay.blit(tint_overlay, (0, 0))
    
    def draw_lighting(self, surface):
        """
        Draw lighting overlays onto the game surface.
        """
        surface.blit(self.overlay, (0, 0))
    
    def get_time_display(self):
        """
        Return a formatted string of the current time and season.
        """
        hour = int((self.current_time / self.day_length) * 24)
        minute = int(((self.current_time / self.day_length) * 24 - hour) * 60)
        return f"{hour:02d}:{minute:02d} {self.get_current_season()}"
