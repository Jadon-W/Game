import pygame
import sys
from game import Game
import config

def main():
    # Initialize Pygame
    pygame.init()

    # Set up display (Full-Screen)
    WINDOW = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_info = pygame.display.Info()
    config.WIDTH = screen_info.current_w
    config.HEIGHT = screen_info.current_h
    pygame.display.set_caption("Elysian Realms")

    # Set up the clock for a decent framerate
    CLOCK = pygame.time.Clock()

    # Create and run the game
    game = Game(WINDOW, CLOCK)
    game.run()


if __name__ == "__main__":
    main()
