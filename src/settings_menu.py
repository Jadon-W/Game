# settings_menu.py

import pygame
import config

class SettingsMenu:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont('Arial', 30)
        self.option_font = pygame.font.SysFont('Arial', 25)
        self.options = ['Audio', 'Display', 'Controls', 'Back']
        self.selected = 0
        self.active = False
    
    def toggle_menu(self):
        self.active = not self.active
    
    def handle_event(self, event):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.execute_option()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                self.handle_mouse_click(mouse_pos)
    
    def handle_mouse_click(self, mouse_pos):
        """
        Handle mouse clicks on settings options.
        """
        for idx, option in enumerate(self.options):
            text = self.option_font.render(option, True, config.WHITE)
            rect = text.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 50 + idx * 50))
            if rect.collidepoint(mouse_pos):
                self.selected = idx
                self.execute_option()
    
    def execute_option(self):
        """
        Execute the selected settings option.
        """
        selected_option = self.options[self.selected]
        if selected_option == 'Audio':
            self.open_audio_settings()
        elif selected_option == 'Display':
            self.open_display_settings()
        elif selected_option == 'Controls':
            self.open_controls_settings()
        elif selected_option == 'Back':
            self.toggle_menu()
    
    def open_audio_settings(self):
        """
        Implement audio settings adjustments.
        """
        # Placeholder implementation
        # You can expand this with actual audio settings controls
        print("Audio settings opened.")
    
    def open_display_settings(self):
        """
        Implement display settings adjustments.
        """
        # Placeholder implementation
        # You can expand this with actual display settings controls
        print("Display settings opened.")
    
    def open_controls_settings(self):
        """
        Implement control settings adjustments.
        """
        # Placeholder implementation
        # You can expand this with actual control settings controls
        print("Control settings opened.")
    
    def draw(self, surface):
        if not self.active:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Dark semi-transparent
        surface.blit(overlay, (0, 0))
        
        # Menu Title
        title_text = self.font.render("Settings", True, config.WHITE)
        title_rect = title_text.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 150))
        surface.blit(title_text, title_rect)
        
        # Menu Options
        for idx, option in enumerate(self.options):
            if idx == self.selected:
                color = config.YELLOW
            else:
                color = config.WHITE
            option_text = self.option_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 50 + idx * 50))
            surface.blit(option_text, option_rect)
