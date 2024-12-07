# pause_menu.py

from settings_menu import SettingsMenu  # Import the SettingsMenu class
import pygame
import config
import sys

class PauseMenu:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont('Arial', 40)
        self.option_font = pygame.font.SysFont('Arial', 30)
        self.options = ['Resume Game', 'Settings', 'Quit Game']
        self.selected = 0
        self.menu_active = False
        self.settings_menu = SettingsMenu(game)
    
    def toggle_menu(self):
        self.menu_active = not self.menu_active
        self.game.paused = self.menu_active
        if not self.menu_active:
            # When unpausing, ensure settings menu is also closed
            if self.settings_menu.active:
                self.settings_menu.toggle_menu()
    
    def handle_event(self, event):
        if self.menu_active:
            if self.settings_menu.active:
                self.settings_menu.handle_event(event)
            else:
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
        Handle mouse clicks on menu options.
        """
        if self.settings_menu.active:
            self.settings_menu.handle_mouse_click(mouse_pos)
            return

        for idx, option in enumerate(self.options):
            text = self.option_font.render(option, True, config.WHITE)
            rect = text.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 50 + idx * 50))
            if rect.collidepoint(mouse_pos):
                self.selected = idx
                self.execute_option()
    
    def execute_option(self):
        """
        Execute the selected menu option.
        """
        selected_option = self.options[self.selected]
        if selected_option == 'Resume Game':
            self.toggle_menu()
        elif selected_option == 'Settings':
            self.settings_menu.toggle_menu()
        elif selected_option == 'Quit Game':
            pygame.quit()
            sys.exit()
    
    def draw(self, surface):
        if not self.menu_active:
            return

        if self.settings_menu.active:
            self.settings_menu.draw(surface)
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Dark semi-transparent
        surface.blit(overlay, (0, 0))
        
        # Menu Title
        title_text = self.font.render("Paused", True, config.WHITE)
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
