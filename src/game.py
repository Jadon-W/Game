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
                elif event.key == pygame.K_d:
                    # Implement dropping the last item in the inventory
                    if self.player.inventory.items:
                        item = self.player.inventory.items[-1]
                        self.player.inventory.remove_item(item)
                        # Drop the item at the player's current position
                        item.x = self.player.rect.x
                        item.y = self.player.rect.y
                        self.world.active_items.add(item)
                        print(f"Dropped {item.item_type} at ({item.x}, {item.y})")

    def update(self):
        keys_pressed = pygame.key.get_pressed()
        self.player.handle_movement(keys_pressed, self.world)  # Pass the world to handle_movement
        dt = self.clock.get_time() / 1000  # Delta time in seconds
        self.player.update(dt)
        self.quest_manager.update_quests(self.player, self.world)
        self.camera.update(self.player, self.world)

    def render(self):
        self.world.draw(self.window, self.camera)  # Pass the camera to world.draw()
        self.player.draw(self.window, self.camera)  # Pass the camera to player.draw()
        self.display_quests()
        if self.inventory_visible:
            self.display_inventory()
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
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(config.FPS)
    
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
