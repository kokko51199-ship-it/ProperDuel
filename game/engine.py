"""
Game Engine
Core game loop and rendering system.
"""

import pygame
import os
from typing import Optional, Union
from game.scenes import FightScene, MainMenuScene, SplashScene, Level2Scene, LevelSelectScene
from game.input_handler import InputHandler
from game.resource_utils import audio_path


class GameEngine:
    """Main game engine handling the game loop and scene management."""
    
    def __init__(self):
        """Initialize the game engine."""
        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.FPS = 60
        
        # Initialize display
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Proper Duel - Pixel Fighting Game")
        
        # Game state
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False  # Pause state
        self.current_scene: Optional[Union[SplashScene, MainMenuScene, FightScene]] = None
        self.scene_type = "splash"  # "splash", "menu" or "fight"
        self.scene_transition_cooldown = 0.0  # Prevent immediate key detection after transition
        
        # Input handler
        self.input_handler = InputHandler()
        
        # Initialize the VIC VEGA splash scene first
        self.current_scene = SplashScene(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Initialize background music and sound effects
        self._load_audio()
        
        # Start with menu music
        self._play_menu_music()
    
    def handle_events(self):
        """Handle pygame events."""
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Handle ESC key for pause/unpause in fight scene
                if self.scene_type == "fight":
                    self.paused = not self.paused
                elif self.scene_type == "menu":
                    # ESC in menu quits to desktop
                    self.running = False
            else:
                events.append(event)
                # Pass events to input handler only in fight scene and when not paused
                if self.scene_type == "fight" and not self.paused:
                    self.input_handler.handle_event(event)
        
        return events
    
    def update(self, dt: float, events: list):
        """Update game state."""
        # Update transition cooldown
        if self.scene_transition_cooldown > 0:
            self.scene_transition_cooldown -= dt
        
        if self.current_scene:
            if self.scene_type == "splash":
                # Handle splash input and get action
                keys_pressed = pygame.key.get_pressed()
                action = self.current_scene.handle_input(keys_pressed, events)
                
                # Update splash animations
                self.current_scene.update(dt)
                
                # Check if splash is finished
                if self.current_scene.is_finished() or action == "skip":
                    self._switch_to_menu_scene()
                    
            elif self.scene_type == "menu":
                # Handle menu input and get action
                keys_pressed = pygame.key.get_pressed()
                action = self.current_scene.handle_input(keys_pressed, events)
                
                if action == "start_game":
                    self._switch_to_fight_scene()
                elif action == "level_select":
                    self._switch_to_level_select_scene()
                elif action == "quit":
                    self.running = False
                
                # Update menu animations
                self.current_scene.update(dt)
                
            elif self.scene_type == "level_select":
                # Handle level select input and get action
                keys_pressed = pygame.key.get_pressed()
                action = self.current_scene.handle_input(keys_pressed, events)
                
                if action == "start_level1":
                    self._switch_to_fight_scene()
                elif action == "start_level2":
                    self._switch_to_level2_scene()
                elif action == "menu":
                    self._switch_to_menu_scene()
                
                # Update level select animations
                self.current_scene.update(dt)
                
            elif self.scene_type == "level2":
                # Handle Level 2 input
                keys_pressed = pygame.key.get_pressed()
                action = self.current_scene.handle_input(keys_pressed, events)
                
                if action == "menu":
                    self._switch_to_menu_scene()
                elif action == "quit":
                    self.running = False
                
                # Get input for player if not showing intro
                if not self.current_scene.showing_intro:
                    # Always update input handler for Level 2
                    if not self.paused:
                        self.input_handler.update(dt, None, self.current_scene.player1)  # No AI enemy yet
                    
                    # Get input states for player 1
                    player1_input = self.input_handler.get_player1_input()
                    
                    # Update Level 2 scene with player input
                    self.current_scene.update(dt, player1_input, None)
                else:
                    # Just update intro timer (with default parameters)
                    self.current_scene.update(dt, None, None)
                
            elif self.scene_type == "fight":
                try:
                    # Handle dialogue input if showing dialogue
                    if hasattr(self.current_scene, 'showing_dialogue') and self.current_scene.showing_dialogue:
                        if hasattr(self.current_scene, 'handle_dialogue_input'):
                            self.current_scene.handle_dialogue_input(events)
                    
                    # Process cheat input for player 1
                    for event in events:
                        if event.type == pygame.KEYDOWN:
                            if event.unicode.isalpha():  # Only process letter keys
                                self.current_scene.player1.process_cheat_input(event.unicode, dt)
                    
                    # Always update input handler and get input states
                    if not self.paused:
                        self.input_handler.update(dt, self.current_scene.player2, self.current_scene.player1)
                    
                    # Get input states for player 1 and AI
                    player1_input = self.input_handler.get_player1_input()
                    player2_input = self.input_handler.get_player2_input(dt, self.current_scene.player2, self.current_scene.player1)
                    
                    # Update current scene (but freeze game logic during dialogue/pause)
                    if not self.paused and not (hasattr(self.current_scene, 'showing_dialogue') and self.current_scene.showing_dialogue):
                        self.current_scene.update(dt, player1_input, player2_input)
                    else:
                        # Still call update but with zero delta time to freeze game logic
                        self.current_scene.update(0.0, player1_input, player2_input)
                    
                    # Check if match is over and fade out battle music
                    if hasattr(self.current_scene, 'match_over') and self.current_scene.match_over:
                        if not hasattr(self, '_music_faded') or not self._music_faded:
                            self._fade_out_music()
                            self._music_faded = True
                        
                        # Check if dialogue is complete to transition to Level 2
                        if hasattr(self.current_scene, 'dialogue_complete') and self.current_scene.dialogue_complete:
                            self._switch_to_level2_scene()
                    
                    # Always update pause state for blinking effect
                    if hasattr(self.current_scene, 'update_pause'):
                        self.current_scene.update_pause(dt, self.paused)
                    
                    # Update dialogue system
                    if hasattr(self.current_scene, 'update_dialogue'):
                        self.current_scene.update_dialogue(dt)
                
                except Exception as e:
                    print(f"ERROR in fight scene update: {e}")
                    import traceback
                    traceback.print_exc()
                    # Return to menu on error
                    self._switch_to_menu_scene()
    
    def _switch_to_fight_scene(self):
        """Switch from menu to fight scene."""
        try:
            self.current_scene = FightScene(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
            self.scene_type = "fight"
            self.scene_transition_cooldown = 0.5  # 0.5 second cooldown
            
            # Reset music fade flag for new match
            self._music_faded = False
            
            # Switch to battle music for intense combat
            self._play_battle_music()
            
            # Apply audio to the new fight scene
            if hasattr(self, 'attack_sound') and hasattr(self.current_scene, 'set_sounds'):
                self.current_scene.set_sounds(self.attack_sound, self.block_sound, self.pain_sound)
        except Exception as e:
            print(f"ERROR creating fight scene: {e}")
            import traceback
            traceback.print_exc()
            # Fall back to menu
            self.current_scene = MainMenuScene(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
            self.scene_type = "menu"
    
    def _switch_to_menu_scene(self):
        """Switch from splash or fight scene to menu."""
        self.current_scene = MainMenuScene(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.scene_type = "menu"
        self.scene_transition_cooldown = 0.5  # 0.5 second cooldown
        
    def _switch_to_level_select_scene(self):
        """Switch from menu to level select."""
        self.current_scene = LevelSelectScene(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.scene_type = "level_select"
        self.scene_transition_cooldown = 0.5  # 0.5 second cooldown
        
    def _switch_to_level2_scene(self):
        """Switch from fight scene to Level 2."""
        try:
            self.current_scene = Level2Scene(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
            self.scene_type = "level2"
            self.scene_transition_cooldown = 0.5  # 0.5 second cooldown
            
            # Apply audio to the new Level 2 scene
            if hasattr(self, 'attack_sound') and hasattr(self.current_scene, 'set_sounds'):
                self.current_scene.set_sounds(self.attack_sound, self.block_sound, self.pain_sound)
            
            print("Transitioning to Level 2...")
        except Exception as e:
            print(f"ERROR creating Level 2 scene: {e}")
            import traceback
            traceback.print_exc()
            # Fall back to menu
            self._switch_to_menu_scene()
        
        # Switch to menu music (if not already playing)
        self._play_menu_music()
    
    def render(self):
        """Render the current frame."""
        try:
            # Clear screen with a dark background
            self.screen.fill((20, 20, 30))
            
            # Render current scene
            if self.current_scene:
                self.current_scene.render(self.screen)
            
            # Update display
            pygame.display.flip()
        except Exception as e:
            print(f"ERROR in render: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_audio(self):
        """Load background music and sound effects."""
        try:
            # Initialize pygame mixer for audio
            pygame.mixer.init()
            
            # Load menu music
            self.menu_music_path = audio_path("menu.mp3")
            
            # Load fight music (forest.mp3 for exploration, battle.mp3 for intense combat)
            self.fight_music_path = audio_path("forest.mp3")
            self.battle_music_path = audio_path("battle.mp3")
            
            print(f"Audio paths loaded - Menu: {self.menu_music_path}, Fight: {self.fight_music_path}, Battle: {self.battle_music_path}")
            
            # Load sound effects
            self._load_sound_effects()
            
        except Exception as e:
            print(f"Could not load audio: {e}")
    
    def _load_sound_effects(self):
        """Load game sound effects."""
        try:
            # Load attack sound
            katana_path = audio_path("katana.mp3")
            self.attack_sound = pygame.mixer.Sound(katana_path)
            self.attack_sound.set_volume(0.7)  # 70% volume for impact
            
            print(f"Attack sound loaded: {katana_path}")
            
            # Load block sound
            block_path = audio_path("block.mp3")
            self.block_sound = pygame.mixer.Sound(block_path)
            self.block_sound.set_volume(0.6)  # 60% volume for blocking
            
            print(f"Block sound loaded: {block_path}")
            
            # Load pain sound
            pain_path = audio_path("pain.mp3")
            self.pain_sound = pygame.mixer.Sound(pain_path)
            self.pain_sound.set_volume(0.8)  # 80% volume for impact feedback
            
            print(f"Pain sound loaded: {pain_path}")
            
            # Make sounds available to the scene (if it's a fight scene)
            if (self.current_scene and hasattr(self.current_scene, 'set_sounds') and 
                self.scene_type == "fight"):
                self.current_scene.set_sounds(self.attack_sound, self.block_sound, self.pain_sound)
                
        except Exception as e:
            print(f"Could not load sound effects: {e}")
            # Create dummy sound objects to prevent errors
            self.attack_sound = None
            self.block_sound = None
            self.pain_sound = None
            if (self.current_scene and hasattr(self.current_scene, 'set_sounds') and 
                self.scene_type == "fight"):
                self.current_scene.set_sounds(None, None, None)
    
    def _play_menu_music(self):
        """Play menu theme music."""
        try:
            pygame.mixer.music.load(self.menu_music_path)
            pygame.mixer.music.set_volume(0.4)  # 40% volume for menu
            pygame.mixer.music.play(-1)  # Loop indefinitely
            print(f"Menu music loaded and playing: {self.menu_music_path}")
        except Exception as e:
            print(f"Could not play menu music: {e}")
    
    def _play_fight_music(self):
        """Play fight scene music."""
        try:
            pygame.mixer.music.load(self.fight_music_path)
            pygame.mixer.music.set_volume(0.3)  # 30% volume for fight (quieter for sound effects)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            print(f"Fight music loaded and playing: {self.fight_music_path}")
        except Exception as e:
            print(f"Could not play fight music: {e}")
    
    def _play_battle_music(self):
        """Play intense battle music during fights."""
        try:
            pygame.mixer.music.load(self.battle_music_path)
            pygame.mixer.music.set_volume(0.15)  # 15% volume for battle intensity
            pygame.mixer.music.play(-1)  # Loop indefinitely
            print(f"Battle music loaded and playing: {self.battle_music_path}")
        except Exception as e:
            print(f"Could not play battle music: {e}")
    
    def _fade_out_music(self, fade_time_ms=3000):
        """Fade out the current music over specified time."""
        try:
            pygame.mixer.music.fadeout(fade_time_ms)
            print(f"Music fading out over {fade_time_ms}ms")
        except Exception as e:
            print(f"Could not fade out music: {e}")
    
    def run(self):
        """Main game loop."""
        print("Starting Proper Duel...")
        
        try:
            while self.running:
                # Calculate delta time
                dt = self.clock.tick(self.FPS) / 1000.0  # Convert to seconds
                
                # Handle events
                try:
                    events = self.handle_events()
                except Exception as e:
                    print(f"ERROR in handle_events: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
                
                # Update game state
                try:
                    self.update(dt, events)
                except Exception as e:
                    print(f"ERROR in update: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
                
                # Render frame
                try:
                    self.render()
                except Exception as e:
                    print(f"ERROR in render: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        
        except Exception as e:
            print(f"FATAL ERROR in game loop: {e}")
            import traceback
            traceback.print_exc()
        
        print("Game ended.")