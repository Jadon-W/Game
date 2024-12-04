# time_manager.py

import pygame
import config

class TimeManager:
    def __init__(self):
        self.current_time = 6  # Time in minutes
        self.minutes_per_day = 1440  # Total minutes in a day (24*60)
        self.day_length = 24  # Minutes per in-game day
        self.time_speed = 0.001  # Game time progresses 1 minute per real second
        
        # Seasons: 4 seasons, each lasting a certain number of days
        self.seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
        self.current_season_index = 0
        self.days_per_season = 30
        self.current_day = 1
        
        # Calculate total minutes per season
        self.minutes_per_season = self.days_per_season * self.day_length
        
        # Lighting overlays
        self.day_overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        self.night_overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        self.update_overlays()

    def update(self, dt):
        """
        Update the time based on delta time.
        """
        # Increment time
        self.current_time += dt * self.time_speed
        
        # Handle day/night transitions
        if self.current_time >= self.day_length:
            self.current_time -= self.day_length
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
    
    def is_night(self):
        """
        Determine if it's currently night time.
        Let's say night starts after 18:00 and ends at 6:00
        """
        hour = self.current_time / (self.day_length / 24)
        return hour >= 18 or hour < 6

    def update_overlays(self):
        """
        Update lighting overlays based on time.
        """
        if self.is_night():
            # Darken the screen to simulate night
            self.night_overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        else:
            # Clear night overlay during day
            self.night_overlay.fill((0, 0, 0, 0))

    def draw_lighting(self, surface):
        """
        Draw lighting overlays onto the game surface.
        """
        surface.blit(self.night_overlay, (0, 0))

    def get_time_display(self):
        """
        Return a formatted string of the current time.
        """
        hour = int((self.current_time / self.day_length) * 24)
        minute = int((self.current_time % (self.day_length / 24)) * (60 / (self.day_length / 24)))
        return f"{hour:02d}:{minute:02d} {self.get_current_season()}"