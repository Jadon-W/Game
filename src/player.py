# player.py

import pygame
import config
import os
from inventory import Inventory
from items import Item

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load sprite sheet using the absolute path from config
        try:
            self.sprite_sheet = pygame.image.load(config.PLAYER_SPRITE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load player sprite at {config.PLAYER_SPRITE_PATH}: {e}")
            # Handle the missing sprite sheet gracefully
            self.sprite_sheet = pygame.Surface((config.PLAYER_SPRITE_WIDTH, config.PLAYER_SPRITE_HEIGHT))
            self.sprite_sheet.fill(config.WHITE)  # Fallback color
        self.frames = self.load_frames()
        self.current_frame = 0
        self.direction = 'down'  # Initial direction
        self.image = self.frames[self.direction][self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 5
        self.animation_timer = 0
        self.moving = False
        self.xp = 0
        self.gold = 0
        self.inventory = Inventory()  # Initialize inventory
        self.abilities = []  # List to store unlocked abilities
        self.health = 100  # Initialize player health
        self.max_health = 100  # Define max health

    def load_frames(self):
        """
        Extract frames from the sprite sheet.
        Assumes the sprite sheet has rows corresponding to directions:
        0 - Up, 1 - Right, 2 - Down, 3 - Left
        Each row has 4 frames for walking animation.
        """
        frames = {'up': [], 'right': [], 'down': [], 'left': []}
        directions = ['up', 'right', 'down', 'left']
        for row, direction in enumerate(directions):
            for col in range(4):  # 4 frames per direction
                frame_rect = (
                    col * config.PLAYER_SPRITE_WIDTH,
                    row * config.PLAYER_SPRITE_HEIGHT,
                    config.PLAYER_SPRITE_WIDTH,
                    config.PLAYER_SPRITE_HEIGHT
                )
                try:
                    frame = self.sprite_sheet.subsurface(frame_rect)
                    # Scale the frame up for better visibility
                    scaled_frame = pygame.transform.scale(
                        frame,
                        (config.PLAYER_SPRITE_WIDTH * 2, config.PLAYER_SPRITE_HEIGHT * 2)
                    )
                    frames[direction].append(scaled_frame)
                except ValueError as ve:
                    print(f"Error extracting frame at {frame_rect}: {ve}")
        return frames

    def handle_movement(self, keys_pressed, world):
        self.moving = False
        dx, dy = 0, 0

        if keys_pressed[pygame.K_LEFT]:
            dx -= self.speed
            self.direction = 'left'
            self.moving = True
        if keys_pressed[pygame.K_RIGHT]:
            dx += self.speed
            self.direction = 'right'
            self.moving = True
        if keys_pressed[pygame.K_UP]:
            dy -= self.speed
            self.direction = 'up'
            self.moving = True
        if keys_pressed[pygame.K_DOWN]:
            dy += self.speed
            self.direction = 'down'
            self.moving = True

        # Calculate intended new position
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy

        # Determine the center of the player's rectangle for accurate tile checking
        center_x = new_x + self.rect.width // 2
        center_y = new_y + self.rect.height // 2

        # Check if the new position is walkable
        if world.is_walkable(center_x, center_y):
            # Update position if walkable
            self.rect.x = new_x
            self.rect.y = new_y
        else:
            # Prevent movement; provide feedback
            print("Cannot move onto water!")

    def update(self, dt):
        if self.moving:
            self.animation_timer += config.PLAYER_ANIMATION_SPEED
            if self.animation_timer >= len(self.frames[self.direction]):
                self.animation_timer = 0
            self.current_frame = int(self.animation_timer)
            self.image = self.frames[self.direction][self.current_frame]
        else:
            # Idle frame (first frame of the current direction)
            self.image = self.frames[self.direction][0]

    def draw(self, surface, camera):
        # Calculate player's position relative to the camera
        draw_x = self.rect.x - camera.offset_x
        draw_y = self.rect.y - camera.offset_y
        surface.blit(self.image, (draw_x, draw_y))

    def receive_reward(self, reward):
        """
        Receive rewards from quest completion.
        """
        xp = reward.get('xp', 0)
        gold = reward.get('gold', 0)
        abilities = reward.get('abilities', [])
        items = reward.get('items', [])
        self.xp += xp
        self.gold += gold
        # Grant abilities
        for ability in abilities:
            self.grant_ability(ability)
        # Grant items
        for item in items:
            self.inventory.add_item(item)
        print(f"Received Reward: {xp} XP, {gold} Gold, {abilities}, {items}")
        self.check_level_up()  # Check for level-up after receiving rewards

    def grant_ability(self, ability):
        """
        Grant a new ability to the player.
        """
        # Implement ability granting logic
        if ability and ability not in self.abilities:
            self.abilities.append(ability)
            print(f"New Ability Granted: {ability}")

    def add_item_to_inventory(self, item):
        """
        Add an item to the player's inventory.
        """
        # Implement inventory logic
        print(f"New Item Acquired: {item}")
    
    def attack(self):
        if 'attack' in self.abilities:
            print("Player attacks!")
            # Implement attack logic here
        else:
            print("You need to unlock the attack ability first!")
    
    def check_level_up(self):
        """
        Check if the player has enough XP to level up and unlock new abilities.
        """
        level_thresholds = [100, 300, 600, 1000]  # Example thresholds
        current_level = len(self.abilities) + 1
        if current_level <= len(level_thresholds) and self.xp >= level_thresholds[current_level - 1]:
            new_ability = self.get_new_ability(current_level)
            if new_ability:
                self.grant_ability(new_ability)
                print(f"Leveled Up to Level {current_level}! Unlocked ability: {new_ability}")

    def get_new_ability(self, level):
        """
        Define abilities unlocked at each level.
        """
        abilities = {
            1: 'attack',
            2: 'jump',
            3: 'defend',
            4: 'double_jump'
        }
        return abilities.get(level, None)
    
    def consume_mushroom(self, item):
        """
        Consume a mushroom to restore health.
        """
        health_restore = 20  # Define how much health is restored per mushroom
        self.health += health_restore
        if self.health > self.max_health:
            self.health = self.max_health  # Cap health at max_health
        print(f"Consumed {item.item_type}. Health restored by {health_restore}. Current Health: {self.health}")
    
    def take_damage(self, damage):
        """
        Reduce player's health by damage amount.
        """
        self.health -= damage
        if self.health < 0:
            self.health = 0  # Prevent negative health
        print(f"Player took {damage} damage. Current Health: {self.health}")
