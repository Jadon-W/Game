# config.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Terrain Images
TERRAIN_TILES = {
    'grass': os.path.join(BASE_DIR, 'assets', 'images', 'grass.png'),
    'water': os.path.join(BASE_DIR, 'assets', 'images', 'water.png'),
    'mountain': os.path.join(BASE_DIR, 'assets', 'images', 'mountain.png'),
    'sand': os.path.join(BASE_DIR, 'assets', 'images', 'sand.png'),
    'forest': os.path.join(BASE_DIR, 'assets', 'images', 'forest.png')
}

# Additional Terrain Elements
TREE_IMAGE = os.path.join(BASE_DIR, 'assets', 'images', 'tree.png')
PATH_IMAGE = os.path.join(BASE_DIR, 'assets', 'images', 'path.png')
ROCK_IMAGE = os.path.join(BASE_DIR, 'assets', 'images', 'rock.png')  # New
SANDCASTLE_IMAGE = os.path.join(BASE_DIR, 'assets', 'images', 'sandcastle.png')  # New
FRUIT_IMAGE = os.path.join(BASE_DIR, 'assets', 'images', 'fruit.png')  # 4x4 sprite sheet
FLOWER_IMAGE = os.path.join(BASE_DIR, 'assets', 'images', 'flower.png')
MUSHROOM_IMAGE = os.path.join(BASE_DIR, 'assets', 'images', 'mushroom.png')
# Animated Tiles
OCEAN_ANIMATION = os.path.join(BASE_DIR, 'assets', 'images', 'ocean.png')  # Changed from ocean.gif

# Screen dimensions
WIDTH = 800
HEIGHT = 600

# Colors (Retained for fallback and other uses)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)

# Player configuration
PLAYER_COLOR = (255, 0, 0)  # Bright Red
PLAYER_OUTLINE_COLOR = (255, 255, 255)  # White

PLAYER_SPRITE_PATH = os.path.join(BASE_DIR, 'assets', 'images', 'player_sprites.png')
PLAYER_SPRITE_WIDTH = 16  # Width of each sprite frame
PLAYER_SPRITE_HEIGHT = 18  # Height of each sprite frame
PLAYER_ANIMATION_SPEED = 0.1  # Adjust for animation smoothness

# Frames per second
FPS = 60

# Tile configuration
TILE_SIZE = 16  # 16x16 pixels

# World dimensions
WORLD_WIDTH = 300 * TILE_SIZE  # Increased to 6400 pixels
WORLD_HEIGHT = 300 * TILE_SIZE  # Increased to 6400 pixels

# Quest configuration
QUEST_TYPES = ['collection', 'exploration', 'combat', 'delivery']

QUEST_DESCRIPTIONS = {
    'collection': "Collect 10 mushrooms from the forest.",
    'exploration': "Discover a hidden cave in the mountains.",
    'combat': "Defeat 5 bandits near the city.",
    'delivery': "Deliver a message to the neighboring town."
}

QUEST_OBJECTIVES = {
    'collection': "Collect 10 mushrooms.",
    'exploration': "Find and explore the hidden cave.",
    'combat': "Defeat 5 bandits.",
    'delivery': "Deliver the message to the next town."
}

QUEST_REWARDS = {
    'collection': {'xp': 100, 'gold': 50},
    'exploration': {'xp': 150, 'gold': 75},
    'combat': {'xp': 200, 'gold': 100},
    'delivery': {'xp': 120, 'gold': 60}
}
