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
        self.attack_cooldown = 0  # Cooldown timer for attacks
        self.attack_speed = 30  # Frames between attacks
        self.xp_thresholds = [100, 300, 600, 1000]  # XP needed for each level
        self.level = 1  # Optional: Track player level
        self.is_flashing = False
        self.flash_duration = 10  # Frames to flash
        self.flash_timer = 0
        self.original_image = self.image.copy()
        self.flash_color = (255, 0, 0)  # Red color for flash
        self.recoil_distance_factor = 5  # Adjust this factor to control recoil sensitivity
        self.flash_overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        self.flash_overlay.fill((255, 0, 0, 100))  # Semi-transparent red

        # Load attack sound (optional)
        try:
            self.attack_sound = pygame.mixer.Sound(os.path.join(config.BASE_DIR, 'assets', 'sounds', 'attack.wav'))
        except pygame.error as e:
            print(f"Unable to load attack sound: {e}")
            self.attack_sound = None  # Handle missing sound gracefully

        # Load hit sound (optional)
        try:
            self.hit_sound = pygame.mixer.Sound(os.path.join(config.BASE_DIR, 'assets', 'sounds', 'player_hit.wav'))
        except pygame.error as e:
            print(f"Unable to load hit sound: {e}")
            self.hit_sound = None  # Handle missing sound gracefully

    
    def receive_xp(self, amount):
        """
        Add XP to the player and handle level-up if thresholds are met.
        """
        self.xp += amount
        print(f"Player received {amount} XP. Total XP: {self.xp}")
        self.check_level_up()

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

        # Implementing WASD movement
        if keys_pressed[pygame.K_a]:
            dx -= self.speed
            self.direction = 'left'
            self.moving = True
        if keys_pressed[pygame.K_d]:
            dx += self.speed
            self.direction = 'right'
            self.moving = True
        if keys_pressed[pygame.K_w]:
            dy -= self.speed
            self.direction = 'up'
            self.moving = True
        if keys_pressed[pygame.K_s]:
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
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.is_flashing:
            print("Flash effect active.")
            self.flash_timer -= 1
            if self.flash_timer <= 0:
                self.is_flashing = False
    def draw(self, surface, camera):
        # Calculate player's position relative to the camera
        draw_x = self.rect.x - camera.offset_x
        draw_y = self.rect.y - camera.offset_y
        surface.blit(self.image, (draw_x, draw_y))
        
        # Draw flash overlay if flashing
        if self.is_flashing:
            surface.blit(self.flash_overlay, (draw_x, draw_y))

    def get_attack_effect_position(self):
        """
        Determine where to place the attack effect based on the player's direction.
        """
        effect_offset = 20  # Distance from the player to place the effect
        if self.direction == 'up':
            pos = (self.rect.x + self.rect.width // 2 - self.attack_effect_image.get_width() // 2,
                   self.rect.y - self.attack_effect_image.get_height())
        elif self.direction == 'down':
            pos = (self.rect.x + self.rect.width // 2 - self.attack_effect_image.get_width() // 2,
                   self.rect.y + self.rect.height)
        elif self.direction == 'left':
            pos = (self.rect.x - self.attack_effect_image.get_width(),
                   self.rect.y + self.rect.height // 2 - self.attack_effect_image.get_height() // 2)
        elif self.direction == 'right':
            pos = (self.rect.x + self.rect.width,
                   self.rect.y + self.rect.height // 2 - self.attack_effect_image.get_height() // 2)
        else:
            pos = self.rect.topleft  # Default position
        return pos

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

    def check_level_up(self):
        """
        Check if the player has enough XP to level up.
        """
        if self.level <= len(self.xp_thresholds):
            if self.xp >= self.xp_thresholds[self.level - 1]:
                self.level += 1
                new_ability = self.get_new_ability(self.level)
                if new_ability:
                    self.grant_ability(new_ability)
                print(f"Leveled Up to Level {self.level}! Unlocked ability: {new_ability}")

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

    def take_damage(self, damage, attacker_direction=None):
        """
        Reduce player's health by damage amount and trigger flash effect and recoil.
        
        Parameters:
            damage (int): Amount of damage taken.
            attacker_direction (str): Direction from which the attack originated ('up', 'down', 'left', 'right').
        """
        self.health -= damage
        if self.health < 0:
            self.health = 0  # Prevent negative health
        if config.DEBUG:
            print(f"Player took {damage} damage. Current Health: {self.health}")
        
        # Play hit sound if available
        if self.hit_sound:
            self.hit_sound.play()
        
        # Trigger flash effect
        self.is_flashing = True
        self.flash_timer = self.flash_duration
        
        # Apply recoil effect based on damage and attacker's direction
        self.recoil(damage, attacker_direction)
    
    def recoil(self, damage, attacker_direction):
        """
        Apply a recoil effect when the player is hit.
        The recoil distance increases with the damage taken.
        
        Parameters:
            damage (int): Amount of damage taken.
            attacker_direction (str): Direction from which the attack originated.
        """
        # Calculate recoil distance based on damage
        recoil_distance = damage * self.recoil_distance_factor
        
        # Determine recoil direction based on attacker's direction
        if attacker_direction == 'up':
            # Enemy is above; recoil player down
            self.rect.y += recoil_distance
        elif attacker_direction == 'down':
            # Enemy is below; recoil player up
            self.rect.y -= recoil_distance
        elif attacker_direction == 'left':
            # Enemy is to the left; recoil player right
            self.rect.x += recoil_distance
        elif attacker_direction == 'right':
            # Enemy is to the right; recoil player left
            self.rect.x -= recoil_distance
        else:
            # Default recoil direction (optional: random or based on player's last movement)
            pass
        
        # Ensure the player doesn't move out of bounds
        self.rect.x = max(0, min(self.rect.x, config.WORLD_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, config.WORLD_HEIGHT - self.rect.height))
    def attack(self, enemies):
        """
        Perform an attack on enemies within range.
        """
        if 'attack' in self.abilities and self.attack_cooldown == 0:
            print("Player attacks!")
            # Play attack sound if available
            if self.attack_sound:
                self.attack_sound.play()
            # Define attack range and damage
            attack_range = 50  # Define the range of the attack
            attack_rect = self.get_attack_rect(attack_range)
            # Check collision with enemies within the attack_rect
            hits = [enemy for enemy in enemies if attack_rect.colliderect(enemy.rect)]
            if hits:
                for enemy in hits:
                    enemy.take_damage(10)  # Define damage amount
            else:
                print("No enemies in attack range.")
            self.attack_cooldown = self.attack_speed  # Reset cooldown
            # Remove attack animation trigger
            # self.is_attacking = True
            # self.attack_animation_timer = self.attack_animation_duration
        elif 'attack' not in self.abilities:
            print("You need to unlock the attack ability first!")
        else:
            print("Attack is on cooldown.")
    
    def get_attack_rect(self, attack_range):
        """
        Get the attack rectangle based on the player's current direction.
        """
        if self.direction == 'up':
            attack_rect = pygame.Rect(
                self.rect.x,
                self.rect.y - attack_range,
                self.rect.width,
                attack_range
            )
        elif self.direction == 'down':
            attack_rect = pygame.Rect(
                self.rect.x,
                self.rect.y + self.rect.height,
                self.rect.width,
                attack_range
            )
        elif self.direction == 'left':
            attack_rect = pygame.Rect(
                self.rect.x - attack_range,
                self.rect.y,
                attack_range,
                self.rect.height
            )
        elif self.direction == 'right':
            attack_rect = pygame.Rect(
                self.rect.x + self.rect.width,
                self.rect.y,
                attack_range,
                self.rect.height
            )
        else:
            # Default attack_rect if direction is undefined
            attack_rect = self.rect.inflate(attack_range, attack_range)
        return attack_rect
