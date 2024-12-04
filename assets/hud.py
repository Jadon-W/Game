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
    
    def draw(self, surface):
        """
        Draw all HUD elements on the given surface.
        """
        self.draw_health_bar(surface, 20, 20, 200, 25)
        self.draw_xp_bar(surface, 20, 60, 200, 25)
        self.draw_gold(surface, 20, 100)
        self.draw_time(surface, 20, 140)
        # Quest Log is handled separately
        # Additional HUD elements can be added here
        self.draw_player_level(surface, 20, 180)
    
    def draw_health_bar(self, surface, x, y, width, height):
        """
        Draw the player's health bar with a background panel.
        """
        # Background Panel
        panel = pygame.Surface((width + 4, height + 4), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 100))  # Semi-transparent black
        surface.blit(panel, (x - 2, y - 2))
        
        # Border
        pygame.draw.rect(surface, config.WHITE, (x, y, width, height), 2)
        
        # Fill based on health
        fill_ratio = self.player.health / self.player.max_health
        fill_width = fill_ratio * (width - 4)
        # Gradient color from green to red based on health
        fill_color = (
            int(255 * (1 - fill_ratio)),
            int(255 * fill_ratio),
            0
        )
        pygame.draw.rect(surface, fill_color, (x + 2, y + 2, fill_width, height - 4))
        
        # Health Text
        health_text = self.font.render(f"HP: {self.player.health}/{self.player.max_health}", True, config.WHITE)
        surface.blit(health_text, (x + width + 10, y))
    
    def draw_xp_bar(self, surface, x, y, width, height):
        """
        Draw the player's XP bar with a background panel.
        """
        # Background Panel
        panel = pygame.Surface((width + 4, height + 4), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 100))  # Semi-transparent black
        surface.blit(panel, (x - 2, y - 2))
        
        # Border
        pygame.draw.rect(surface, config.WHITE, (x, y, width, height), 2)
        
        # Determine XP for current level
        current_level = self.player.level
        if current_level - 1 < len(self.player.xp_thresholds):
            xp_for_next_level = self.player.xp_thresholds[current_level - 1]
        else:
            xp_for_next_level = self.player.xp_thresholds[-1] + 100 * (current_level - len(self.player.xp_thresholds))
        fill_ratio = min(self.player.xp / xp_for_next_level, 1)
        fill_width = fill_ratio * (width - 4)
        fill_color = config.BLUE
        pygame.draw.rect(surface, fill_color, (x + 2, y + 2, fill_width, height - 4))
        
        # XP Text
        xp_text = self.font.render(f"XP: {self.player.xp}/{xp_for_next_level}", True, config.WHITE)
        surface.blit(xp_text, (x + width + 10, y))
    
    def draw_gold(self, surface, x, y):
        """
        Draw the player's gold with a background panel.
        """
        # Background Panel
        panel = pygame.Surface((150, 30), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 100))  # Semi-transparent black
        surface.blit(panel, (x - 2, y - 2))
        
        # Border
        pygame.draw.rect(surface, config.WHITE, (x, y, 150, 30), 2)
        
        # Gold Text
        gold_text = self.font.render(f"Gold: {self.player.gold}", True, config.YELLOW)
        surface.blit(gold_text, (x + 10, y + 5))
    
    def draw_time(self, surface, x, y):
        """
        Draw the current in-game time with a background panel.
        """
        # Background Panel
        panel = pygame.Surface((200, 30), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 100))  # Semi-transparent black
        surface.blit(panel, (x - 2, y - 2))
        
        # Border
        pygame.draw.rect(surface, config.WHITE, (x, y, 200, 30), 2)
        
        # Time Text
        time_text = self.font.render(f"Time: {self.time_manager.get_time_display()}", True, config.WHITE)
        surface.blit(time_text, (x + 10, y + 5))
    
    def draw_player_level(self, surface, x, y):
        """
        Draw the player's current level.
        """
        # Background Panel
        panel = pygame.Surface((100, 30), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 100))  # Semi-transparent black
        surface.blit(panel, (x - 2, y - 2))
        
        # Border
        pygame.draw.rect(surface, config.WHITE, (x, y, 100, 30), 2)
        
        # Level Text
        level_text = self.font.render(f"Level: {self.player.level}", True, config.WHITE)
        surface.blit(level_text, (x + 10, y + 5))
    
    def draw_quest_log(self, surface, x, y):
        """
        Draw the active quests in a separate area.
        """
        quests = self.quest_manager.active_quests
        title_text = self.large_font.render("Quests", True, config.WHITE)
        surface.blit(title_text, (x + 50, y))
        y += 50
        for quest in quests:
            # Simple bullet point
            bullet = self.font.render("•", True, config.YELLOW)
            surface.blit(bullet, (x, y))
            # Quest status
            quest_text = self.font.render(f" {quest.get_status()}", True, config.WHITE)
            surface.blit(quest_text, (x + 20, y))
            y += 30
