#!/usr/bin/env python3
"""
Proper Duel - Pixel Art Samurai Fighting Game
Main entry point for the fighting game.
"""

import pygame
import sys
from game.engine import GameEngine


def main():
    """Initialize and run the game."""
    # Initialize Pygame
    pygame.init()
    
    # Create game engine instance
    game = GameEngine()
    
    try:
        # Run the game
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    finally:
        # Clean up
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()