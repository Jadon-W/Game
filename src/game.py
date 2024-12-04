# game.py

import pygame
import sys
import math  # Import the math module
from player import Player
from world import World
from quests import QuestManager
from camera import Camera
from enemy import Enemy
from time_manager import TimeManager
from hud import HUD  # Import the HUD class
import config
import random
import time

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
        self.enemies = pygame.sprite.Group()  # Group to hold all enemy instances
        self.spawn_enemies(count=5)  # Initialize enemy spawning with desired count
        self.time_manager = TimeManager()
        self.hud = HUD(self.player, self.quest_manager, self.time_manager)
        

    def spawn_enemies(self, count=5):
        """
        Spawn a specified number of enemies near the player's position.
        """
        for _ in range(count):
            enemy_type = random.choice(['eye-rock', 'foot-soldier'])
            attempts = 0
            max_attempts = 100  # Prevent infinite loop
            while attempts < max_attempts:
                # Define a spawn radius around the player (e.g., 200 pixels)
                spawn_radius = 200
                angle = random.uniform(0, 2 * math.pi)  # Use math.pi for better precision
                distance = random.randint(100, spawn_radius)  # Minimum distance of 100 pixels
                x = self.player.rect.x + distance * math.cos(angle)  # Use math.cos
                y = self.player.rect.y + distance * math.sin(angle)  # Use math.sin
                # Ensure x and y are within world bounds
                x = max(0, min(int(x), config.WORLD_WIDTH - config.TILE_SIZE))
                y = max(0, min(int(y), config.WORLD_HEIGHT - config.TILE_SIZE))
                enemy_rect = pygame.Rect(x, y, config.TILE_SIZE, config.TILE_SIZE)
                collision = False
                if self.player.rect.colliderect(enemy_rect):
                    collision = True
                for enemy in self.enemies:
                    if enemy.rect.colliderect(enemy_rect):
                        collision = True
                        break
                if not collision:
                    break  # Suitable spawn position found
                attempts += 1
            else:
                print(f"Failed to spawn {enemy_type}: No suitable position found after {max_attempts} attempts.")
                continue  # Skip spawning this enemy
            enemy = Enemy(x, y, enemy_type, self.player)
            self.enemies.add(enemy)
            print(f"Spawned {enemy_type} at ({x}, {y})")
        print(f"Spawned {count} enemies near the player.")

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
                elif event.key == pygame.K_r:
                    # Implement dropping the last item in the inventory
                    if self.player.inventory.items:
                        item = self.player.inventory.items[-1]
                        added = self.player.inventory.remove_item(item)
                        if added:
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
                if event.button == 1:  # Left click
                    if self.inventory_visible:
                        mouse_pos = pygame.mouse.get_pos()
                        self.player.inventory.handle_mouse_click(mouse_pos, self.player)
                    else:
                        self.player.attack(self.enemies)

    def update(self):
        keys_pressed = pygame.key.get_pressed()
        self.player.handle_movement(keys_pressed, self.world)
        dt = self.clock.get_time() / 1000 * 60  # Convert to in-game minutes
        self.player.update(dt)
        self.quest_manager.update_quests(self.player, self.world, self) 
        self.camera.update(self.player, self.world)
        self.enemies.update(self.player)
        self.time_manager.update(dt)  # Update time
        self.process_notifications()
    
    def render(self):
        self.window.fill(config.BLACK)  # Clear the screen
        self.world.draw(self.window, self.camera)
        
        # Draw all enemies with camera offset
        for enemy in self.enemies:
            draw_x = enemy.rect.x - self.camera.offset_x
            draw_y = enemy.rect.y - self.camera.offset_y
            self.window.blit(enemy.image, (draw_x, draw_y))
        
        self.player.draw(self.window, self.camera)
        self.display_quests()
        if self.inventory_visible:
            self.player.inventory.draw(self.window)
        self.display_notifications()
        self.hud.draw(self.window)  # Draw HUD elements
        self.time_manager.draw_lighting(self.window)  # Draw lighting overlays
        pygame.display.flip()

    def display_quests(self):
        """
        Display active quests on the screen.
        """
        pass
    def run(self):
        while True:
            frame_start = time.time()
            dt = self.clock.tick(config.FPS)
            self.handle_events()
            self.update()
            self.render()
            frame_time = time.time() - frame_start
        
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
        Display player's health, XP, gold, and current time on the screen.
        """
        font = pygame.font.SysFont('Arial', 20)
        health_text = font.render(f"Health: {self.player.health}", True, config.WHITE)
        xp_text = font.render(f"XP: {self.player.xp}", True, config.WHITE)
        gold_text = font.render(f"Gold: {self.player.gold}", True, config.WHITE)
        time_text = font.render(f"Time: {self.time_manager.get_time_display()}", True, config.WHITE)
        
        self.window.blit(health_text, (10, 40))
        self.window.blit(xp_text, (10, 65))
        self.window.blit(gold_text, (10, 90))
        self.window.blit(time_text, (10, 115))
    def take_damage(self, damage, attacker_direction=None):
        """
        Wrapper to add notifications when the player takes damage.
        """
        self.player.take_damage(damage, attacker_direction)
        self.add_notification(f"Player took {damage} damage!")

    def enemy_die(self, enemy_type):
        """
        Wrapper to add notifications when an enemy dies.
        """
        self.add_notification(f"Defeated a {enemy_type}!")
