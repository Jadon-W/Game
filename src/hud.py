# hud.py

import pygame
import config

class HUD:
    def __init__(self, player, quest_manager, time_manager):
        self.player = player
        self.quest_manager = quest_manager
        self.time_manager = time_manager
        self.font = pygame.font.SysFont('Arial', 20)
        self.large_font = pygame.font.SysFont('Arial', 30)
        self.health_bar_color_low = (255, 0, 0)    # Red
        self.health_bar_color_high = (0, 255, 0)   # Green
        self.xp_bar_color = (0, 122, 204)          # A modern blue shade
        self.gold_color = (255, 215, 0)            # Gold color for gold display
        self.text_shadow_color = (0, 0, 0)         # Black shadow for text
        self.shadow_offset = 2                      # Offset for text shadow
        
        # For smooth health bar transitions
        self.displayed_health = self.player.health
        self.health_transition_speed = 100  # Health points per second

        # Pre-create semi-transparent panels to avoid creating them every frame
        self.health_panel = self.create_panel(250 + 6, 30 + 6)
        self.xp_panel = self.create_panel(250 + 6, 30 + 6)
        self.gold_panel = self.create_panel(160 + 6, 40 + 6)
        self.time_panel = self.create_panel(220 + 6, 40 + 6)
        self.level_panel = self.create_panel(120 + 6, 40 + 6)

    def create_panel(self, width, height):
        """
        Create a semi-transparent panel with rounded corners.
        """
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, 150), (0, 0, width, height), border_radius=8)
        return panel

    def draw(self, surface):
        """
        Draw all HUD elements on the given surface.
        """
        self.update_health_display()
        self.draw_health_bar(surface, 20, 20, 250, 30)
        self.draw_xp_bar(surface, 20, 70, 250, 30)
        self.draw_gold(surface, 20, 120)
        self.draw_time(surface, 20, 170)
        self.draw_player_level(surface, 20, 220)
    
    def update_health_display(self):
        """
        Smoothly update the displayed health towards the actual health.
        """
        if self.displayed_health < self.player.health:
            self.displayed_health += self.health_transition_speed * self.player.delta_time
            if self.displayed_health > self.player.health:
                self.displayed_health = self.player.health
        elif self.displayed_health > self.player.health:
            self.displayed_health -= self.health_transition_speed * self.player.delta_time
            if self.displayed_health < self.player.health:
                self.displayed_health = self.player.health

    def draw_health_bar(self, surface, x, y, width, height):
        """
        Draw the player's health bar with smooth color transitions and shadowed text.
        """
        # Blit pre-created panel
        surface.blit(self.health_panel, (x - 3, y - 3))
        
        # Border
        pygame.draw.rect(surface, config.WHITE, (x, y, width, height), 2, border_radius=6)
        
        # Calculate fill ratio
        fill_ratio = max(self.displayed_health / self.player.max_health, 0)
        fill_width = fill_ratio * (width - 4)
        
        # Smooth color transition from green to red based on health
        fill_color = self.interpolate_color(self.health_bar_color_low, self.health_bar_color_high, fill_ratio)
        
        # Draw filled part of the health bar
        pygame.draw.rect(surface, fill_color, (x + 2, y + 2, fill_width, height - 4), border_radius=4)
        
        # Health Text with Shadow
        health_text = self.font.render(f"HP: {int(self.displayed_health)}/{self.player.max_health}", True, config.WHITE)
        shadow_text = self.font.render(f"HP: {int(self.displayed_health)}/{self.player.max_health}", True, self.text_shadow_color)
        surface.blit(shadow_text, (x + width + 12 + self.shadow_offset, y + (height - health_text.get_height()) // 2 + self.shadow_offset))
        surface.blit(health_text, (x + width + 12, y + (height - health_text.get_height()) // 2))
    
    def interpolate_color(self, start_color, end_color, ratio):
        """
        Interpolate between two colors based on the given ratio.
        """
        return (
            int(start_color[0] * (1 - ratio) + end_color[0] * ratio),
            int(start_color[1] * (1 - ratio) + end_color[1] * ratio),
            int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        )
    
    def draw_xp_bar(self, surface, x, y, width, height):
        """
        Draw the player's XP bar with modern styling.
        """
        # Blit pre-created panel
        surface.blit(self.xp_panel, (x - 3, y - 3))
        
        # Border
        pygame.draw.rect(surface, config.WHITE, (x, y, width, height), 2, border_radius=6)
        
        # Determine XP for current level
        current_level = self.player.level
        if current_level - 1 < len(self.player.xp_thresholds):
            xp_for_next_level = self.player.xp_thresholds[current_level - 1]
        else:
            xp_for_next_level = self.player.xp_thresholds[-1] + 100 * (current_level - len(self.player.xp_thresholds))
        
        # Calculate fill ratio
        fill_ratio = min(self.player.xp / xp_for_next_level, 1)
        fill_width = fill_ratio * (width - 4)
        
        # Draw filled part of the XP bar
        pygame.draw.rect(surface, self.xp_bar_color, (x + 2, y + 2, fill_width, height - 4), border_radius=4)
        
        # XP Text with Shadow
        xp_text = self.font.render(f"XP: {self.player.xp}/{xp_for_next_level}", True, config.WHITE)
        shadow_text = self.font.render(f"XP: {self.player.xp}/{xp_for_next_level}", True, self.text_shadow_color)
        surface.blit(shadow_text, (x + width + 12 + self.shadow_offset, y + (height - xp_text.get_height()) // 2 + self.shadow_offset))
        surface.blit(xp_text, (x + width + 12, y + (height - xp_text.get_height()) // 2))
    
    def draw_gold(self, surface, x, y):
        """
        Draw the player's gold with modern styling.
        """
        # Blit pre-created panel
        surface.blit(self.gold_panel, (x - 3, y - 3))
        
        # Border
        pygame.draw.rect(surface, config.WHITE, (x, y, 160, 40), 2, border_radius=6)
        
        # Gold Text with Shadow
        gold_text = self.font.render(f"Gold: {self.player.gold}", True, self.gold_color)
        shadow_text = self.font.render(f"Gold: {self.player.gold}", True, self.text_shadow_color)
        surface.blit(shadow_text, (x + 10 + self.shadow_offset, y + 5 + self.shadow_offset))
        surface.blit(gold_text, (x + 10, y + 5))
    
    def draw_time(self, surface, x, y):
        """
        Draw the current in-game time with modern styling.
        """
        # Blit pre-created panel
        surface.blit(self.time_panel, (x - 3, y - 3))
        
        # Border
        pygame.draw.rect(surface, config.WHITE, (x, y, 220, 40), 2, border_radius=6)
        
        # Time Text with Shadow
        time_text = self.font.render(f"Time: {self.time_manager.get_time_display()}", True, config.WHITE)
        shadow_text = self.font.render(f"Time: {self.time_manager.get_time_display()}", True, self.text_shadow_color)
        surface.blit(shadow_text, (x + 10 + self.shadow_offset, y + 5 + self.shadow_offset))
        surface.blit(time_text, (x + 10, y + 5))
    
    def draw_player_level(self, surface, x, y):
        """
        Draw the player's current level with modern styling.
        """
        # Blit pre-created panel
        surface.blit(self.level_panel, (x - 3, y - 3))
        
        # Border
        pygame.draw.rect(surface, config.WHITE, (x, y, 120, 40), 2, border_radius=6)
        
        # Level Text with Shadow
        level_text = self.font.render(f"Level: {self.player.level}", True, config.WHITE)
        shadow_text = self.font.render(f"Level: {self.player.level}", True, self.text_shadow_color)
        surface.blit(shadow_text, (x + 10 + self.shadow_offset, y + 5 + self.shadow_offset))
        surface.blit(level_text, (x + 10, y + 5)) 
