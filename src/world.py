# world.py
from items import Item
import pygame
import random
import config
import noise  # Ensure the noise library is installed


class Tile:
    def __init__(self, x, y, tile_type, images):
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.images = images  # Dictionary of loaded images
        self.image = self.get_image()
        self.is_special = False
        self.special_type = None
        self.overlay = None  # For biome-specific elements
        self.has_fruit = False  # Indicates if the tile has a fruit
        self.fruit_image = None  # Holds the assigned fruit image

        # Assign overlay based on tile type
        if self.tile_type == 'forest':
            # 50% chance to place a tree on a forest tile
            if random.random() < 0.5:
                self.overlay = 'tree'
                # 1% chance to place a fruit near a tree
                if random.random() < 0.01:
                    self.has_fruit = True
                    if 'fruit' in self.images and len(self.images['fruit']) > 0:
                        self.fruit_image = random.choice(self.images['fruit'])
        elif self.tile_type == 'grass':
            # 0.5% chance to place a flower on a grass tile
            if random.random() < 0.005:
                self.overlay = 'flower'
        elif self.tile_type == 'mountain':
            # 2% chance to place a rock on a mountain tile
            if random.random() < 0.02:
                self.overlay = 'rock'
        elif self.tile_type == 'sand':
            # 0.1% chance to place a sandcastle on a sand tile
            if random.random() < 0.001:
                self.overlay = 'sandcastle'
            # 10% chance to place an oasis on a sand tile
            elif random.random() < 0.1:
                # Oasis image is not included, so skip
                pass
        # Add more biome-specific overlays as needed

    def get_image(self):
        if self.tile_type in config.TERRAIN_TILES:
            if self.tile_type == 'water' and isinstance(self.images['water'], list):
                return self.images['water'][0]  # Return the first frame as default
            else:
                return self.images[self.tile_type]
        else:
            # Fallback to grass if type unknown
            return self.images['grass']

    def draw(self, surface, camera, animated=False, animation_frame=0):
        # Calculate position relative to camera
        draw_x = self.x - camera.offset_x
        draw_y = self.y - camera.offset_y

        # Only draw if within the visible screen
        if -config.TILE_SIZE < draw_x < config.WIDTH and -config.TILE_SIZE < draw_y < config.HEIGHT:
            # For animated tiles, use the current animation frame
            if self.tile_type == 'water' and animated:
                # Ensure animation_frame is within bounds
                if animation_frame < len(self.images['water']):
                    animated_image = self.images['water'][animation_frame]
                else:
                    animated_image = self.images['water'][0]  # Fallback to first frame
                surface.blit(animated_image, (draw_x, draw_y))
            else:
                # Ensure self.image is a Surface before blitting
                if isinstance(self.image, pygame.Surface):
                    surface.blit(self.image, (draw_x, draw_y))
                else:
                    # If self.image is unexpectedly a list, fallback to first frame
                    if isinstance(self.image, list) and len(self.image) > 0:
                        surface.blit(self.image[0], (draw_x, draw_y))
                    else:
                        # Fallback to a white square if all else fails
                        fallback_surface = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))
                        fallback_surface.fill(config.WHITE)
                        surface.blit(fallback_surface, (draw_x, draw_y))

            # Add biome-specific patterns
            if self.tile_type == 'mountain':
                # Example: Add mountain peaks or shading
                pygame.draw.polygon(surface, (100, 100, 100),
                                    [(draw_x, draw_y + config.TILE_SIZE),
                                     (draw_x + config.TILE_SIZE // 2, draw_y),
                                     (draw_x + config.TILE_SIZE, draw_y + config.TILE_SIZE)],
                                    1)
            elif self.tile_type == 'forest':
                # Optionally, add additional forest-specific patterns
                pass
            elif self.tile_type == 'sand':
                # Example: Add sand dunes or ripples
                pygame.draw.line(surface, (210, 180, 140),
                                 (draw_x, draw_y + config.TILE_SIZE - 2),
                                 (draw_x + config.TILE_SIZE, draw_y + 2), 1)

            # Draw overlays
            if self.overlay == 'tree':
                surface.blit(self.images['tree'], (draw_x, draw_y))
            elif self.overlay == 'path_vertical':
                surface.blit(self.images['path_vertical'], (draw_x, draw_y))
            elif self.overlay == 'path_horizontal':
                surface.blit(self.images['path_horizontal'], (draw_x, draw_y))
            elif self.overlay == 'rock':
                surface.blit(self.images['rock'], (draw_x, draw_y))
            elif self.overlay == 'sandcastle':
                surface.blit(self.images['sandcastle'], (draw_x, draw_y))
            elif self.overlay == 'flower':
                surface.blit(self.images['flower'], (draw_x, draw_y))
            # Draw fruit if present
            if self.has_fruit and self.fruit_image:
                surface.blit(self.fruit_image, (draw_x, draw_y))
            # Add more overlays as needed

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = []
        # Initialize special_locations to prevent AttributeError
        self.special_locations = {}
        self.load_images()
        self.generate_world()
        self.generate_paths()  # Add path generation
        self.animation_frame = 0  # For animated tiles
        self.animation_timer = 0
        self.active_items = pygame.sprite.Group()

    def load_images(self):
        # Load all terrain images
        self.images = {}
        for tile_type, path in config.TERRAIN_TILES.items():
            try:
                image = pygame.image.load(path).convert_alpha()
                # Scale image to TILE_SIZE
                image = pygame.transform.scale(image, (config.TILE_SIZE, config.TILE_SIZE))
                self.images[tile_type] = image
            except pygame.error as e:
                print(f"Unable to load {tile_type} image at {path}: {e}")
                # Fallback to white surface
                self.images[tile_type] = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))
                self.images[tile_type].fill(config.WHITE)

        # Load additional elements
        overlay_elements = ['tree', 'path', 'rock', 'sandcastle', 'flower', 'fruit']  # Removed 'oasis', 'town', 'cave'
        for element in overlay_elements:
            try:
                image_path = getattr(config, f"{element.upper()}_IMAGE")
                image = pygame.image.load(image_path).convert_alpha()
                # Handle sprite sheets for 'fruit'
                if element == 'fruit':
                    # Assuming 'fruit.png' is a 4x4 sprite sheet
                    sheet_width, sheet_height = image.get_size()
                    frame_width = config.TILE_SIZE
                    frame_height = config.TILE_SIZE
                    num_frames = (sheet_width // frame_width) * (sheet_height // frame_height)
                    fruit_frames = []
                    for row in range(sheet_height // frame_height):
                        for col in range(sheet_width // frame_width):
                            frame = image.subsurface(
                                (col * frame_width, row * frame_height, frame_width, frame_height)
                            )
                            fruit_frames.append(pygame.transform.scale(frame, (config.TILE_SIZE, config.TILE_SIZE)))
                    self.images['fruit'] = fruit_frames
                elif element == 'path':
                    # Load both vertical and horizontal path images
                    path_vertical = pygame.transform.scale(image, (config.TILE_SIZE, config.TILE_SIZE))
                    path_horizontal = pygame.transform.rotate(path_vertical, 90)
                    self.images['path_vertical'] = path_vertical
                    self.images['path_horizontal'] = path_horizontal
                else:
                    self.images[element] = pygame.transform.scale(image, (config.TILE_SIZE, config.TILE_SIZE))
            except pygame.error as e:
                print(f"Unable to load {element} image at {getattr(config, f'{element.upper()}_IMAGE')}: {e}")
                # Fallback to transparent surface
                if element == 'fruit':
                    self.images[element] = []
                else:
                    self.images[element] = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE), pygame.SRCALPHA)
                    self.images[element].fill((0, 0, 0, 0))  # Transparent fallback

        # Load ocean animation frames if ocean.png is a sprite sheet
        self.water_frames = []
        try:
            # Assuming ocean.png is a sprite sheet with frames horizontally aligned
            ocean_sprite_sheet = pygame.image.load(config.OCEAN_ANIMATION).convert_alpha()
            sheet_width, sheet_height = ocean_sprite_sheet.get_size()
            frame_width = config.TILE_SIZE
            frame_height = config.TILE_SIZE
            num_frames = sheet_width // frame_width
            for i in range(num_frames):
                frame = ocean_sprite_sheet.subsurface(
                    (i * frame_width, 0, frame_width, frame_height)
                )
                self.water_frames.append(pygame.transform.scale(frame, (config.TILE_SIZE, config.TILE_SIZE)))
            if not self.water_frames:
                raise ValueError("No frames extracted from ocean.png")
            self.images['water'] = self.water_frames
            print(f"Loaded {len(self.water_frames)} frames for animated water.")
        except pygame.error as e:
            print(f"Unable to load ocean animation at {config.OCEAN_ANIMATION}: {e}")
            # Fallback to static water image
            try:
                water_static = pygame.image.load(config.TERRAIN_TILES['water']).convert_alpha()
                water_static = pygame.transform.scale(water_static, (config.TILE_SIZE, config.TILE_SIZE))
                self.images['water'] = [water_static]
                print("Using static water image as fallback.")
            except pygame.error as ex:
                print(f"Unable to load fallback water image: {ex}")
                self.images['water'] = [pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))]
                self.images['water'][0].fill(config.BLUE)

    def generate_world(self):
        # Use Perlin noise for smooth biome transitions
        scale = 150.0  # Adjust scale for larger biome regions
        octaves = 4    # Reduced octaves for smoother transitions
        persistence = 0.5
        lacunarity = 2.0

        self.tiles = []
        for row in range(self.height // config.TILE_SIZE):
            for col in range(self.width // config.TILE_SIZE):
                x = col * config.TILE_SIZE
                y = row * config.TILE_SIZE
                noise_val = noise.pnoise2(col / scale,
                                          row / scale,
                                          octaves=octaves,
                                          persistence=persistence,
                                          lacunarity=lacunarity,
                                          repeatx=1024,
                                          repeaty=1024,
                                          base=0)
                # Normalize noise value to [0,1]
                noise_val = (noise_val + 0.5)
                tile_type = self.get_biome_from_noise(noise_val)
                tile = Tile(x, y, tile_type, self.images)
                self.tiles.append(tile)

    def get_biome_from_noise(self, noise_val):
        """
        Determine biome type based on normalized noise value.
        Adjust thresholds as needed for desired biome distribution.
        """
        if noise_val < 0.2:
            return 'water'
        elif noise_val < 0.4:
            return 'sand'
        elif noise_val < 0.6:
            return 'grass'
        elif noise_val < 0.8:
            return 'forest'
        else:
            return 'mountain'

    def generate_paths(self):
        """
        Generate connected paths in grass and forest biomes.
        Create multiple paths from the center in different directions.
        Paths will either lead to the edge of the world or loop back.
        """
        start_x = self.width // 2
        start_y = self.height // 2

        num_paths = 4  # Number of main paths
        path_length = 300  # Increased path length for better connectivity

        directions = ['up', 'down', 'left', 'right']

        for direction in directions[:num_paths]:
            current_x = start_x
            current_y = start_y

            for _ in range(path_length):
                if direction == 'up':
                    new_x = current_x
                    new_y = current_y - config.TILE_SIZE
                    path_overlay = 'path_vertical'
                elif direction == 'down':
                    new_x = current_x
                    new_y = current_y + config.TILE_SIZE
                    path_overlay = 'path_vertical'
                elif direction == 'left':
                    new_x = current_x - config.TILE_SIZE
                    new_y = current_y
                    path_overlay = 'path_horizontal'
                elif direction == 'right':
                    new_x = current_x + config.TILE_SIZE
                    new_y = current_y
                    path_overlay = 'path_horizontal'

                # Check if new position is within the world
                if 0 <= new_x < self.width and 0 <= new_y < self.height:
                    # Find the tile at the new position
                    tile_index = (new_y // config.TILE_SIZE) * (self.width // config.TILE_SIZE) + (new_x // config.TILE_SIZE)
                    tile = self.tiles[tile_index]

                    # Only modify tiles that are grass or forest
                    if tile.tile_type in ['grass', 'forest']:
                        # Set overlay to 'path_vertical' or 'path_horizontal'
                        tile.overlay = path_overlay
                        # Move to the new position
                        current_x = new_x
                        current_y = new_y
                    else:
                        # If tile is not grass or forest, stop path in this direction
                        break
                else:
                    # If out of bounds, stop path
                    break

    def draw(self, surface, camera):
        for tile in self.tiles:
            animated = False
            frame = 0
            if tile.tile_type == 'water' and len(self.images['water']) > 1:
                animated = True
                frame = self.animation_frame % len(self.images['water'])
            tile.draw(surface, camera, animated, frame)
        
        # Handle animated tiles (e.g., ocean)
        if len(self.images['water']) > 1:
            self.animation_timer += 1
            if self.animation_timer >= 10:  # Adjust frame rate as needed
                self.animation_timer = 0
                self.animation_frame += 1
        
        # Draw active items (e.g., mushrooms)
        for item in self.active_items:
            item.draw(surface, camera)

    def get_tile_type(self, x, y):
        """
        Get the biome type at the given pixel coordinates.
        """
        col = x // config.TILE_SIZE
        row = y // config.TILE_SIZE
        if 0 <= col < self.width // config.TILE_SIZE and 0 <= row < self.height // config.TILE_SIZE:
            tile_index = row * (self.width // config.TILE_SIZE) + col
            return self.tiles[tile_index].tile_type
        else:
            return 'water'  # Treat out-of-bounds as water
    
    def is_walkable(self, x, y):
        """
        Determine if the tile at pixel coordinates (x, y) is walkable.
        """
        col = x // config.TILE_SIZE
        row = y // config.TILE_SIZE
        if 0 <= col < self.width // config.TILE_SIZE and 0 <= row < self.height // config.TILE_SIZE:
            tile_index = row * (self.width // config.TILE_SIZE) + col
            tile = self.tiles[tile_index]
            return tile.tile_type != 'water'
        else:
            # Treat out-of-bounds as non-walkable
            return False
    
    def spawn_mushrooms(self, count):
        """
        Spawn a specified number of mushrooms at random grass or forest tiles.
        """
        spawned = 0
        attempts = 0
        max_attempts = count * 10  # Prevent infinite loops
        while spawned < count and attempts < max_attempts:
            col = random.randint(0, (self.width // config.TILE_SIZE) - 1)
            row = random.randint(0, (self.height // config.TILE_SIZE) - 1)
            tile_index = row * (self.width // config.TILE_SIZE) + col
            tile = self.tiles[tile_index]
            if tile.tile_type in ['grass', 'forest'] and not tile.overlay:
                x = tile.x + (config.TILE_SIZE - config.TILE_SIZE // 2) // 2  # Center the item
                y = tile.y + (config.TILE_SIZE - config.TILE_SIZE // 2) // 2
                mushroom = Item(x, y, 'mushroom')
                self.active_items.add(mushroom)
                spawned += 1
            attempts += 1
