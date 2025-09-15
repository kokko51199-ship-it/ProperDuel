"""
Sprite Animation System
Handles loading and animating sprite sheets.
"""

import pygame
import os
from typing import List, Tuple


class SpriteSheet:
    """Handles sprite sheet loading and frame extraction."""
    
    def __init__(self, filename: str):
        """Load a sprite sheet image."""
        self.filename = filename
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load sprite sheet: {filename}")
            print(f"Error: {e}")
            # Create a fallback colored rectangle
            self.sheet = pygame.Surface((256, 32))
            self.sheet.fill((100, 100, 200))
        
        self.width = self.sheet.get_width()
        self.height = self.sheet.get_height()
    
    def get_frames(self, frame_width: int, frame_height: int, frame_count: int, y_offset: int = 0) -> List[pygame.Surface]:
        """Extract frames from sprite sheet."""
        frames = []
        
        for i in range(frame_count):
            x = i * frame_width
            y = y_offset
            
            # Create frame rectangle
            frame_rect = pygame.Rect(x, y, frame_width, frame_height)
            
            # Extract frame from sheet
            if x + frame_width <= self.width and y + frame_height <= self.height:
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(self.sheet, (0, 0), frame_rect)
                frames.append(frame)
            else:
                print(f"Warning: Frame {i} is outside sprite sheet bounds")
                # Create fallback frame
                fallback = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                fallback.fill((100 + i * 20, 100, 200))
                frames.append(fallback)
        
        return frames


class Animation:
    """Handles sprite animation playback."""
    
    def __init__(self, frames: List[pygame.Surface], frame_duration: float = 0.1):
        """Initialize animation with frames and timing."""
        self.frames = frames
        self.frame_duration = frame_duration  # seconds per frame
        self.current_frame = 0
        self.time_since_last_frame = 0.0
        self.is_playing = True
        self.loop = True
    
    def update(self, dt: float):
        """Update animation timing."""
        if not self.is_playing or not self.frames:
            return
        
        self.time_since_last_frame += dt
        
        if self.time_since_last_frame >= self.frame_duration:
            self.time_since_last_frame = 0.0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.is_playing = False
    
    def get_current_frame(self) -> pygame.Surface:
        """Get the current animation frame."""
        if not self.frames:
            # Return fallback surface
            fallback = pygame.Surface((32, 48), pygame.SRCALPHA)
            fallback.fill((100, 100, 200))
            return fallback
        
        return self.frames[self.current_frame]
    
    def reset(self):
        """Reset animation to beginning."""
        self.current_frame = 0
        self.time_since_last_frame = 0.0
        self.is_playing = True
    
    def play(self):
        """Start playing animation."""
        self.is_playing = True
    
    def pause(self):
        """Pause animation."""
        self.is_playing = False
    
    def is_finished(self) -> bool:
        """Check if animation has finished (for non-looping animations)."""
        return not self.loop and not self.is_playing


class SpriteAnimator:
    """Manages multiple animations for a character."""
    
    def __init__(self):
        """Initialize sprite animator."""
        self.animations = {}
        self.current_animation = None
        self.current_animation_name = ""
    
    def add_animation(self, name: str, animation: Animation):
        """Add an animation to the animator."""
        self.animations[name] = animation
        
        # Set as current if it's the first animation
        if not self.current_animation:
            self.current_animation = animation
            self.current_animation_name = name
    
    def play_animation(self, name: str, reset: bool = True):
        """Play a specific animation."""
        if name in self.animations:
            if self.current_animation_name != name or reset:
                self.current_animation = self.animations[name]
                self.current_animation_name = name
                if reset:
                    self.current_animation.reset()
                self.current_animation.play()
    
    def update(self, dt: float):
        """Update current animation."""
        if self.current_animation:
            self.current_animation.update(dt)
    
    def get_current_frame(self) -> pygame.Surface:
        """Get current animation frame."""
        if self.current_animation:
            return self.current_animation.get_current_frame()
        
        # Return fallback surface
        fallback = pygame.Surface((32, 48), pygame.SRCALPHA)
        fallback.fill((100, 100, 200))
        return fallback