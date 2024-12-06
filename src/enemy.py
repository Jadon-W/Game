# enemy.py

import pygame
import config
import random
import math  # Import math for distance calculations
import os
import game
from items import Item  # Ensure Item is correctly imported

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type, player):
        super().__init__()
        self.player = player  # Reference to the Player instance
        self.game = game  # Reference to Game instance
        self.enemy_type = enemy_type
        self.x = x
        self.y = y
        self.images = self.load_images()
        self.direction = 'down'  # Initialize direction before using it
        self.animation_frame = 0
        self.animation_timer = 0
        self.speed = 2  # Enemy movement speed
        self.image = self.get_image(0)  # Now safe to call since self.direction is set
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = 50  # Define enemy health
        self.max_health = 50
        self.attack_cooldown = 0  # Cooldown timer for attacks
        self.attack_speed = 60  # Frames between attacks (e.g., 1 second at 60 FPS)
        self.ai_state = 'idle'  # Possible states: 'idle', 'chasing', 'attacking'
        self.is_flashing = False
        self.flash_duration = 10  # Frames to flash
        self.flash_timer = 0

        # Load hit sound (optional)
        try:
            self.hit_sound = pygame.mixer.Sound(os.path.join(config.BASE_DIR, 'assets', 'sounds', f'{self.enemy_type}_hit.wav'))
        except pygame.error as e:
            print(f"Unable to load hit sound for {self.enemy_type}: {e}")
            self.hit_sound = None  # Handle missing sound gracefully

    def load_images(self):
        images = {}
        try:
            if self.enemy_type == 'eye-rock':
                sprite_sheet = pygame.image.load(config.EYE_ROCK_IMAGE).convert_alpha()
                rows, cols = 4, 3  # 4 rows, 3 columns
                frame_width = sprite_sheet.get_width() // cols
                frame_height = sprite_sheet.get_height() // rows
                images['down'] = [sprite_sheet.subsurface((col * frame_width, 0, frame_width, frame_height)) for col in range(cols)]
                images['left'] = [sprite_sheet.subsurface((col * frame_width, frame_height, frame_width, frame_height)) for col in range(cols)]
                images['right'] = [sprite_sheet.subsurface((col * frame_width, 2 * frame_height, frame_width, frame_height)) for col in range(cols)]
                images['up'] = [sprite_sheet.subsurface((col * frame_width, 3 * frame_height, frame_width, frame_height)) for col in range(cols)]
            elif self.enemy_type == 'foot-soldier':
                sprite_sheet = pygame.image.load(config.FOOT_SOLDIER_IMAGE).convert_alpha()
                rows, cols = 4, 3  # 4 rows, 3 columns
                frame_width = sprite_sheet.get_width() // cols
                frame_height = sprite_sheet.get_height() // rows
                images['down'] = [sprite_sheet.subsurface((col * frame_width, 0, frame_width, frame_height)) for col in range(cols)]
                images['up'] = [sprite_sheet.subsurface((col * frame_width, frame_height, frame_width, frame_height)) for col in range(cols)]
                images['right'] = [sprite_sheet.subsurface((col * frame_width, 2 * frame_height, frame_width, frame_height)) for col in range(cols)]
                images['left'] = [sprite_sheet.subsurface((col * frame_width, 3 * frame_height, frame_width, frame_height)) for col in range(cols)]
        except pygame.error as e:
            print(f"Unable to load {self.enemy_type} image at {config.EYE_ROCK_IMAGE if self.enemy_type == 'eye-rock' else config.FOOT_SOLDIER_IMAGE}: {e}")
            # Fallback to a simple square if image fails to load
            images[self.direction] = [pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))]
            images[self.direction][0].fill((255, 0, 0))
        return images

    def get_image(self, frame):
        """
        Get the current frame image based on direction and animation frame.
        """
        return self.images[self.direction][frame % len(self.images[self.direction])]

    def update(self, player):
        """
        Update enemy position and handle interactions.
        """
        self.animate()
        self.move(player)
        self.check_collision_with_player(player)

    def animate(self):
        """
        Handle animation frame updates.
        """
        self.animation_timer += 1
        if self.animation_timer >= 10:  # Adjust animation speed as needed
            self.animation_timer = 0
            self.animation_frame += 1
            self.image = self.get_image(self.animation_frame)
        if self.is_flashing:
            # Apply the flash effect
            flash_color = (255, 0, 0)  # Red color for flash
            self.image.fill(flash_color, special_flags=pygame.BLEND_RGBA_ADD)
            self.flash_timer -= 1
            if self.flash_timer <= 0:
                self.is_flashing = False
                # Reset to the current animation frame without the flash
                self.image = self.get_image(self.animation_frame)

    def move(self, player):
        """
        Enemy movement based on AI state.
        """
        # Calculate distance to player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        
        # Update AI state based on distance
        if distance < 150:
            self.ai_state = 'chasing'
        else:
            self.ai_state = 'idle'

        if self.ai_state == 'chasing':
            # Normalize direction
            if distance != 0:
                dx /= distance
                dy /= distance
            # Move towards player
            self.x += dx * self.speed
            self.y += dy * self.speed
            # Update direction for animation
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'
        elif self.ai_state == 'idle':
            # Random movement
            if random.randint(0, 100) < 2:  # 2% chance to change direction each frame
                self.direction = random.choice(['up', 'down', 'left', 'right'])
            
            if self.direction == 'up':
                self.y -= self.speed
            elif self.direction == 'down':
                self.y += self.speed
            elif self.direction == 'left':
                self.x -= self.speed
            elif self.direction == 'right':
                self.x += self.speed
        
        # Update rect position
        self.rect.topleft = (self.x, self.y)
        
        # Keep enemy within world bounds
        self.x = max(0, min(self.x, config.WORLD_WIDTH - config.TILE_SIZE))
        self.y = max(0, min(self.y, config.WORLD_HEIGHT - config.TILE_SIZE))
        self.rect.topleft = (self.x, self.y)

    def check_collision_with_player(self, player):
        """
        Check collision with the player and apply damage if collided.
        """
        if self.rect.colliderect(player.rect):
            if self.attack_cooldown == 0:
                # Determine the direction of the player relative to the enemy
                if self.rect.centerx < player.rect.centerx:
                    attacker_direction = 'left'
                elif self.rect.centerx > player.rect.centerx:
                    attacker_direction = 'right'
                elif self.rect.centery < player.rect.centery:
                    attacker_direction = 'up'
                else:
                    attacker_direction = 'down'
                
                player.take_damage(5, attacker_direction)  # Pass the attacker's direction
                print(f"Player collided with {self.enemy_type}. Took 5 damage.")
                self.attack_cooldown = self.attack_speed  # Reset cooldown
            else:
                # Cooldown active; do not apply damage
                pass

        # Handle cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
    def take_damage(self, damage):
        """
        Reduce enemy's health by damage amount and trigger flash effect.
        """
        self.health -= damage
        print(f"{self.enemy_type.capitalize()} took {damage} damage. Current Health: {self.health}")
        if self.hit_sound:
            self.hit_sound.play()
        # Trigger flash effect
        self.is_flashing = True
        self.flash_timer = self.flash_duration
        if self.health <= 0:
            self.die()

    def die(self):
        """
        Handle enemy death.
        """
        print(f"{self.enemy_type.capitalize()} has been defeated!")
        self.kill()  # Remove the enemy from all groups
        # Award XP to the player
        xp_awarded = self.get_xp_reward()
        self.player.receive_xp(xp_awarded)
        print(f"Player received {xp_awarded} XP from defeating {self.enemy_type}.")
        # Trigger notification in the game
        self.player.game.add_notification(f"Defeated a {self.enemy_type}!")
        # Implement item drops (optional for future)

    def get_xp_reward(self):
        """
        Return the XP reward based on enemy type.
        """
        xp_rewards = {
            'eye-rock': 20,
            'foot-soldier': 30
        }
        return xp_rewards.get(self.enemy_type, 10)  # Default XP if type is undefined
