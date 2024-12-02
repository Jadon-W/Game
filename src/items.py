
import pygame
import config
import random

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.x = x
        self.y = y
        self.item_type = item_type
        self.images = self.load_images()
        self.image = self.get_image()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.usable = True if item_type == 'mushroom' else False  # Define usability
    
    def load_images(self):
        images = {}
        try:
            if self.item_type == 'mushroom':
                mushroom_sheet = pygame.image.load(config.MUSHROOM_IMAGE).convert_alpha()
                sheet_width, sheet_height = mushroom_sheet.get_size()
                frame_width = 16
                frame_height = 16
                images_list = []
                for row in range(sheet_height // frame_height):
                    for col in range(sheet_width // frame_width):
                        frame = mushroom_sheet.subsurface(
                            (col * frame_width, row * frame_height, frame_width, frame_height)
                        )
                        scaled_frame = pygame.transform.scale(frame, (config.TILE_SIZE, config.TILE_SIZE))
                        images_list.append(scaled_frame)
                images['mushroom'] = images_list
        except pygame.error as e:
            print(f"Unable to load {self.item_type} image at {config.MUSHROOM_IMAGE}: {e}")
            # Fallback to a red square if image fails to load
            images['mushroom'] = [pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))]
            images['mushroom'][0].fill((255, 0, 0))
        return images

    def get_image(self):
        if self.item_type == 'mushroom' and 'mushroom' in self.images:
            return random.choice(self.images['mushroom'])
        # Add more item types as needed
        return pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))  # Fallback

    def draw(self, surface, camera):
        draw_x = self.x - camera.offset_x
        draw_y = self.y - camera.offset_y
        surface.blit(self.image, (draw_x, draw_y))
