"""
Resource Path Utility
Handles correct path resolution for both development and PyInstaller bundled environments.
"""

import os
import sys


def get_resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource, works for both development and PyInstaller bundle.
    
    Args:
        relative_path: Path relative to the project root (e.g., "assets/sprites/Idle.png")
        
    Returns:
        Absolute path to the resource file
    """
    try:
        # When running in a PyInstaller bundle, sys._MEIPASS contains the temp directory
        base_path = sys._MEIPASS
    except AttributeError:
        # When running in development, use the script's directory
        base_path = os.path.abspath(".")
        
    return os.path.join(base_path, relative_path)


def asset_path(filename: str) -> str:
    """
    Get path to an asset file.
    
    Args:
        filename: Asset filename with subdirectory (e.g., "sprites/Idle.png" or "audio/menu.mp3")
        
    Returns:
        Absolute path to the asset file
    """
    return get_resource_path(os.path.join("assets", filename))


def sprite_path(filename: str) -> str:
    """
    Get path to a sprite file.
    
    Args:
        filename: Sprite filename (e.g., "Idle.png")
        
    Returns:
        Absolute path to the sprite file
    """
    return asset_path(os.path.join("sprites", filename))


def audio_path(filename: str) -> str:
    """
    Get path to an audio file.
    
    Args:
        filename: Audio filename (e.g., "menu.mp3")
        
    Returns:
        Absolute path to the audio file
    """
    return asset_path(os.path.join("audio", filename))