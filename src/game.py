# game.py

import pygame
import sys
from player import Player
from world import World
from quests import QuestManager
from camera import Camera
import config

class Game:
    def __init__(self, window, clock):
        self.window = window
        self.clock = clock
        self.world = World(config.WORLD_WIDTH, config.WORLD_HEIGHT)  # Uses updated world size
        self.player = Player(self.world.width // 2, self.world.height // 2)
        self.quest_manager = QuestManager()
        self.quest_manager.generate_quest(self.world)  # Start with one quest
        self.camera = Camera(config.WIDTH, config.HEIGHT)
        self.inventory_visible = False  # Flag to toggle inventory display
        self.notifications = []  # List to store active notifications

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_i:
                    self.inventory_visible = not self.inventory_visible  # Toggle inventory
                    print(f"Inventory {'Opened' if self.inventory_visible else 'Closed'}.")
                elif event.key == pygame.K_d:
                    # Implement dropping the last item in the inventory
                    if self.player.inventory.items:
                        item = self.player.inventory.items[-1]
                        self.player.inventory.remove_item(item)
                        # Drop the item at the player's current position
                        player_center_x = self.player.rect.x + self.player.rect.width // 2
                        player_center_y = self.player.rect.y + self.player.rect.height // 2
                        tile_size = config.TILE_SIZE
                        dropped_x = (player_center_x // tile_size) * tile_size
                        dropped_y = (player_center_y // tile_size) * tile_size
                        item.x = dropped_x + (tile_size - config.TILE_SIZE) // 2
                        item.y = dropped_y + (tile_size - config.TILE_SIZE) // 2
                        self.world.active_items.add(item)
                        print(f"Dropped {item.item_type} at ({item.x}, {item.y})")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.inventory_visible and event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    self.player.inventory.handle_mouse_click(mouse_pos, self.player)

    def update(self):
        keys_pressed = pygame.key.get_pressed()
        self.player.handle_movement(keys_pressed, self.world)  # Pass the world to handle_movement
        dt = self.clock.get_time() / 1000  # Delta time in seconds
        self.player.update(dt)
        self.quest_manager.update_quests(self.player, self.world, self) 
        self.camera.update(self.player, self.world)
        self.process_notifications()

    def render(self):
        self.window.fill(config.BLACK)  # Clear the screen
        self.world.draw(self.window, self.camera)  # Pass the camera to world.draw()
        self.player.draw(self.window, self.camera)  # Pass the camera to player.draw()
        self.display_quests()
        if self.inventory_visible:
            self.player.inventory.draw(self.window)  # Draw inventory
        self.display_notifications()  # Display active notifications
        self.display_hud()  # Display HUD elements
        pygame.display.flip()

    def display_quests(self):
        """
        Display active quests on the screen.
        """
        font = pygame.font.SysFont('Arial', 20)
        y_offset = 10
        for quest in self.quest_manager.active_quests:
            quest_text = font.render(quest.get_status(), True, config.WHITE)
            self.window.blit(quest_text, (10, y_offset))
            y_offset += 30  # Space between quests

    def run(self):
        while True:
            dt = self.clock.tick(config.FPS)
            self.handle_events()
            self.update()
            self.render()
    
    def display_inventory(self):
        """
        Display the player's inventory on the screen.
        """
        font = pygame.font.SysFont('Arial', 20)
        inventory_surface = pygame.Surface((200, 300))
        inventory_surface.set_alpha(200)  # Semi-transparent
        inventory_surface.fill(config.BLACK)
        self.window.blit(inventory_surface, (config.WIDTH - 220, 10))  # Position at top-right corner

        title = font.render("Inventory", True, config.WHITE)
        self.window.blit(title, (config.WIDTH - 210, 20))

        y_offset = 60
        for item in self.player.inventory.get_items():
            item_text = font.render(item.item_type.capitalize(), True, config.WHITE)
            self.window.blit(item_text, (config.WIDTH - 210, y_offset))
            y_offset += 30  # Space between items
    
    def display_notifications(self):
        """
        Render active notifications on the screen.
        """
        font = pygame.font.SysFont('Arial', 20)
        y_offset = 50  # Starting y position for notifications
        for notification in self.notifications:
            text = font.render(notification['message'], True, config.YELLOW)
            self.window.blit(text, (config.WIDTH // 2 - text.get_width() // 2, y_offset))
            notification['timer'] -= 1
            y_offset += 30  # Space between notifications

    def process_notifications(self):
        """
        Remove notifications that have expired.
        """
        self.notifications = [n for n in self.notifications if n['timer'] > 0]
    
    def add_notification(self, message, duration=60):
        """
        Add a new notification to the queue.
        """
        self.notifications.append({'message': message, 'timer': duration})
    
    def display_hud(self):
        """
        Display player's health, XP, and gold on the screen.
        """
        font = pygame.font.SysFont('Arial', 20)
        health_text = font.render(f"Health: {self.player.health}", True, config.WHITE)
        xp_text = font.render(f"XP: {self.player.xp}", True, config.WHITE)
        gold_text = font.render(f"Gold: {self.player.gold}", True, config.WHITE)
        
        self.window.blit(health_text, (10, 40))
        self.window.blit(xp_text, (10, 65))
        self.window.blit(gold_text, (10, 90))

